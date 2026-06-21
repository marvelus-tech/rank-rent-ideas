"""MirrorSniper CLI commands using Click + Rich."""

from __future__ import annotations

import asyncio
import contextlib
import os
from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal

import click
import uvicorn
from rich.console import Console
from rich.table import Table
from sqlalchemy import select

from mirror_sniper.config import load_settings
from mirror_sniper.core.database import initialize_database
from mirror_sniper.core.enums import ExecutionMode
from mirror_sniper.core.models import Position, TrackedWallet
from mirror_sniper.execution.jupiter_client import JupiterClient
from mirror_sniper.execution.live_executor import LiveExecutor
from mirror_sniper.execution.paper_trader import PaperTrader
from mirror_sniper.execution.risk_engine import RiskConfig, RiskEngine
from mirror_sniper.execution.safety import SafetyChecker
from mirror_sniper.execution.solana_client import SolanaClient
from mirror_sniper.execution.wallet_manager import WalletManager
from mirror_sniper.interface.alerts import AlertManager
from mirror_sniper.interface.reports import PaperTradingReport
from mirror_sniper.monitoring.helius_client import HeliusClient
from mirror_sniper.monitoring.tx_decoder import TransactionDecoder
from mirror_sniper.monitoring.webhook_server import app
from mirror_sniper.strategy.copy_engine import CopyEngine
from mirror_sniper.strategy.position_manager import PositionManager

console = Console()


@click.group()
def cli() -> None:
    """MirrorSniper command-line interface."""


@cli.command()
def setup() -> None:
    async def _run() -> None:
        db = await initialize_database(run_alembic=True)
        table = Table(title="MirrorSniper Setup")
        table.add_column("Check", style="cyan")
        table.add_column("Result", style="green")
        table.add_row("Database", "Initialized + migrated")
        console.print(table)
        await db.dispose()

    asyncio.run(_run())


@cli.command("add-wallet")
@click.argument("address", type=str)
@click.argument("nickname", type=str)
def add_wallet(address: str, nickname: str) -> None:
    async def _run() -> None:
        db = await initialize_database(run_alembic=False)
        async with db.session() as session:
            session.add(TrackedWallet(address=address, nickname=nickname))
        console.print(f"[green]Tracked wallet added:[/green] {nickname} ({address})")
        await db.dispose()

    asyncio.run(_run())


@cli.command()
@click.argument("address", type=str)
def analyze(address: str) -> None:
    async def _run() -> None:
        settings = load_settings()
        if not settings.secrets.helius_api_key:
            raise click.ClickException("MIRROR_HELIUS_API_KEY is required for analyze")

        helius = HeliusClient(api_key=settings.secrets.helius_api_key, rpc_url=settings.app.rpc.http_url)
        decoder = TransactionDecoder()

        signatures = await helius.get_signatures_for_address(address=address, limit=40)
        decoded_swaps = []
        for sig in signatures[:20]:
            signature = sig.get("signature") if isinstance(sig, dict) else None
            if not signature:
                continue
            tx = await helius.get_transaction(signature)
            if not tx:
                continue
            swap = decoder.decode_swap_transaction(tx)
            if swap and swap.sender_wallet == address:
                decoded_swaps.append(swap)

        total = len(decoded_swaps)
        wins = sum(1 for s in decoded_swaps if s.amount_out >= s.amount_in)
        losses = max(total - wins, 1)
        gross_win = sum(max(s.amount_out - s.amount_in, 0) for s in decoded_swaps)
        gross_loss = sum(max(s.amount_in - s.amount_out, 0) for s in decoded_swaps)
        win_rate = wins / total if total else 0.0
        profit_factor = (gross_win / gross_loss) if gross_loss else float(gross_win > 0)

        hold_times = []
        by_token: dict[str, list[datetime]] = defaultdict(list)
        for s in decoded_swaps:
            by_token[s.token_out].append(s.timestamp)
        for times in by_token.values():
            ordered = sorted(times)
            for i in range(1, len(ordered)):
                hold_times.append((ordered[i] - ordered[i - 1]).total_seconds() / 60)
        avg_hold = sum(hold_times) / len(hold_times) if hold_times else 0.0

        table = Table(title=f"Wallet Analysis: {address}")
        table.add_column("Metric")
        table.add_column("Value")
        table.add_row("Total Trades", str(total))
        table.add_row("Win Rate", f"{win_rate:.2%}")
        table.add_row("Profit Factor", f"{profit_factor:.2f}")
        table.add_row("Avg Hold (min)", f"{avg_hold:.1f}")
        console.print(table)

    asyncio.run(_run())


@cli.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8000, type=int)
def run(host: str, port: int) -> None:
    async def _run() -> None:
        settings = load_settings()
        db = await initialize_database(settings=settings, run_alembic=False)
        jupiter = JupiterClient()
        async with db.session() as session:
            alerts = AlertManager(
                telegram_token=settings.app.alerts.telegram.bot_token,
                telegram_chat_id=settings.app.alerts.telegram.chat_id,
                discord_webhook=settings.app.alerts.discord.webhook_url,
            )
            risk_engine = RiskEngine(config=RiskConfig(), db=session, alerts=alerts)
            paper_trader = PaperTrader(db=session, jupiter_client=jupiter)
            position_manager = PositionManager(db=session, jupiter_client=jupiter)

            execution_mode = ExecutionMode(settings.app.trading.execution_mode)
            wallet = None
            solana_client = None
            live_executor = None

            if execution_mode == ExecutionMode.LIVE:
                private_key = os.getenv("TRADING_WALLET_PRIVATE_KEY")
                if not private_key:
                    raise click.ClickException("TRADING_WALLET_PRIVATE_KEY env var required for live mode")
                ok, _, err = SafetyChecker.validate_private_key(private_key)
                if not ok:
                    raise click.ClickException(err)
                wallet = WalletManager(private_key)
                solana_client = SolanaClient(settings.app.rpc.primary, settings.app.rpc.backup)
                live_executor = LiveExecutor(solana_client, jupiter, wallet.keypair, settings.app.execution)

            copy_engine = CopyEngine(
                db_session=session,
                risk_engine=risk_engine,
                paper_trader=paper_trader,
                position_manager=position_manager,
                settings=settings,
                alerts=alerts,
                live_executor=live_executor,
                execution_mode=execution_mode,
                wallet_manager=wallet,
                solana_client=solana_client,
            )

            server = uvicorn.Server(uvicorn.Config(app, host=host, port=port, log_level="info"))
            engine_task = asyncio.create_task(copy_engine.run_loop())
            monitor_task = asyncio.create_task(copy_engine.monitor_positions_loop())
            try:
                await server.serve()
            finally:
                for t in [engine_task, monitor_task]:
                    t.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await t
                await jupiter.aclose()
        await db.dispose()

    asyncio.run(_run())


@cli.command("paper-report")
@click.option("--days", default=7, help="Number of days to report")
def paper_report(days: int) -> None:
    async def _run() -> None:
        db = await initialize_database(run_alembic=False)
        async with db.session() as session:
            report = PaperTradingReport(session)
            content = await report.generate_report(days=days)
            console.print(content)
        await db.dispose()

    asyncio.run(_run())


@cli.command()
def portfolio() -> None:
    async def _run() -> None:
        db = await initialize_database(run_alembic=False)
        async with db.session() as session:
            jupiter = JupiterClient()
            paper = PaperTrader(session, jupiter)
            total = await paper.get_portfolio_value()

            table = Table(title="Portfolio")
            table.add_column("Metric")
            table.add_column("Value")
            table.add_row("Virtual SOL balance", f"{paper.cash_balance_sol:.4f}")
            table.add_row("Total portfolio value", f"{total:.4f} SOL")
            console.print(table)

            pos_table = Table(title="Open Positions")
            pos_table.add_column("Token")
            pos_table.add_column("Amount")
            pos_table.add_column("Entry")
            pos_table.add_column("Current")
            pos_table.add_column("uPnL (SOL)")

            rows = await session.execute(select(Position).where(Position.status == "open"))
            for p in rows.scalars().all():
                current = await jupiter.get_price(p.token_mint) or float(p.entry_price_sol)
                upnl = (current * p.amount_held) - float(p.entry_value_sol)
                pos_table.add_row(
                    p.token_mint[:8] + "...",
                    str(p.amount_held),
                    f"{float(p.entry_price_sol):.8f}",
                    f"{current:.8f}",
                    f"{upnl:+.4f}",
                )
            console.print(pos_table)
            await jupiter.aclose()
        await db.dispose()

    asyncio.run(_run())


@cli.command()
@click.option("--dry-run", is_flag=True, help="Simulate without signing")
def live(dry_run: bool) -> None:
    settings = load_settings()
    if dry_run:
        console.print("[yellow]Dry-run live mode test enabled (build path only).[/yellow]")
        return
    if settings.app.trading.execution_mode != "live":
        raise click.ClickException("Set trading.execution_mode=live in config/settings.yaml before using live command")
    console.print("[green]Live mode is enabled. Start with: mirror-sniper run[/green]")


@cli.command("kill-switch")
def kill_switch() -> None:
    async def _run() -> None:
        db = await initialize_database(run_alembic=False)
        async with db.session() as session:
            alerts = AlertManager()
            risk_engine = RiskEngine(config=RiskConfig(), db=session, alerts=alerts)
            await risk_engine.emergency_stop("Manual kill-switch from CLI")
        await db.dispose()
        console.print("[bold red]Kill switch executed. Trading halted.[/bold red]")

    asyncio.run(_run())


if __name__ == "__main__":
    cli()
