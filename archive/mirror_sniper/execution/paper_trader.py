"""Paper trading simulation engine."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mirror_sniper.core.enums import SignalType, TradeStatus
from mirror_sniper.core.models import DetectedSignal, ExecutedTrade, PortfolioSnapshot, Position, SystemLog
from mirror_sniper.execution.jupiter_client import JupiterClient, WSOL_MINT


@dataclass(slots=True)
class SimulationResult:
    entry_price: float
    expected_amount_out: int
    slippage_bps: int
    executed_at: datetime
    simulated_tx_signature: str


class PaperTrader:
    def __init__(self, db: AsyncSession, jupiter_client: JupiterClient, starting_balance_sol: float = 10.0):
        self.db = db
        self.jupiter_client = jupiter_client
        self.cash_balance_sol = starting_balance_sol
        self.positions: dict[str, Position] = {}

    async def simulate_trade(self, signal: DetectedSignal, position_size_lamports: int) -> ExecutedTrade:
        token_out = signal.output_mint or signal.token_mint
        if not token_out:
            raise ValueError("signal has no target token mint")

        quote = await self.jupiter_client.get_quote(WSOL_MINT, token_out, position_size_lamports)
        if not quote:
            raise RuntimeError("failed to fetch jupiter quote")

        in_sol = quote.in_amount / 1_000_000_000
        expected_price = (quote.in_amount / max(quote.out_amount, 1)) / 1_000_000_000
        slippage_bps = self._compute_entry_slippage_bps(quote.price_impact_pct)
        actual_out = int(quote.out_amount * (1 - (slippage_bps / 10_000)))

        self.cash_balance_sol -= in_sol
        executed_at = datetime.now(tz=UTC)
        tx_sig = f"SIM-{uuid4().hex[:24]}"

        trade = ExecutedTrade(
            signal_id=signal.id,
            tracked_wallet_address=signal.tracked_wallet_address,
            token_mint=token_out,
            status=TradeStatus.FILLED,
            dex_program=signal.dex_program,
            side=SignalType.BUY,
            size_sol=Decimal(str(in_sol)),
            expected_out_amount=Decimal(str(quote.out_amount)),
            actual_out_amount=Decimal(str(actual_out)),
            slippage_bps=slippage_bps,
            tx_signature=tx_sig,
            submitted_at=executed_at,
            filled_at=executed_at,
        )
        self.db.add(trade)
        await self.db.flush()

        position = Position(
            token_mint=token_out,
            token_symbol=None,
            entry_price_sol=Decimal(str(expected_price)),
            amount_held=actual_out,
            entry_value_sol=Decimal(str(in_sol)),
            entry_time=executed_at,
            signal_id=signal.id,
            unrealized_pnl_sol=Decimal("0"),
            highest_price_seen=Decimal(str(expected_price)),
            status="open",
        )
        self.db.add(position)
        await self.db.flush()
        self.positions[token_out] = position

        await self._log("INFO", "paper_trader", "simulated_buy", {
            "signal_id": signal.id,
            "token_mint": token_out,
            "size_lamports": position_size_lamports,
            "filled_amount": actual_out,
            "slippage_bps": slippage_bps,
            "scheduled_exit_eta": "1h",
        })
        await self.take_snapshot()
        return trade

    async def simulate_exit(self, position: Position, exit_signal: DetectedSignal | None = None) -> float:
        quote = await self.jupiter_client.get_quote(
            input_mint=position.token_mint,
            output_mint=WSOL_MINT,
            amount=position.amount_held,
        )
        if not quote:
            raise RuntimeError("failed to fetch exit quote")

        slippage_bps = self._compute_exit_slippage_bps(quote.price_impact_pct)
        lamports_out = int(quote.out_amount * (1 - (slippage_bps / 10_000)))
        exit_value_sol = lamports_out / 1_000_000_000
        entry_value_sol = float(position.entry_value_sol or 0)
        realized = exit_value_sol - entry_value_sol

        self.cash_balance_sol += exit_value_sol

        position.exit_price = Decimal(str(exit_value_sol / max(position.amount_held, 1)))
        position.exit_time = datetime.now(tz=UTC)
        position.realized_pnl_sol = Decimal(str(realized))
        position.exit_reason = self._exit_reason(exit_signal)
        position.status = "closed"

        trade_res = await self.db.execute(
            select(ExecutedTrade).where(ExecutedTrade.signal_id == position.signal_id).order_by(ExecutedTrade.id.desc())
        )
        trade = trade_res.scalars().first()
        if trade:
            trade.exit_price_sol = position.exit_price
            trade.realized_pnl_sol = Decimal(str(realized))
            trade.exit_time = position.exit_time
            trade.holding_duration_ms = int((position.exit_time - position.entry_time).total_seconds() * 1000)

        self.positions.pop(position.token_mint, None)
        await self._log("INFO", "paper_trader", "simulated_exit", {
            "position_id": position.id,
            "token_mint": position.token_mint,
            "realized_pnl_sol": realized,
            "exit_reason": position.exit_reason,
        })
        await self.take_snapshot()
        return realized

    async def get_portfolio_value(self) -> float:
        total = self.cash_balance_sol
        result = await self.db.execute(select(Position).where(Position.status == "open"))
        for pos in result.scalars().all():
            price = await self.jupiter_client.get_price(pos.token_mint)
            if price is not None:
                total += price * pos.amount_held
        return total

    async def take_snapshot(self) -> PortfolioSnapshot:
        total = await self.get_portfolio_value()
        open_result = await self.db.execute(select(Position).where(Position.status == "open"))
        open_positions = open_result.scalars().all()
        invested = sum(float(p.entry_value_sol or 0) for p in open_positions)
        unrealized = 0.0
        for p in open_positions:
            price = await self.jupiter_client.get_price(p.token_mint)
            if price is None:
                continue
            unrealized += (price * p.amount_held) - float(p.entry_value_sol or 0)

        snap = PortfolioSnapshot(
            total_value_usd=Decimal(str(total)),
            cash_value_usd=Decimal(str(self.cash_balance_sol)),
            invested_value_usd=Decimal(str(invested)),
            unrealized_pnl_usd=Decimal(str(unrealized)),
            realized_pnl_usd=Decimal("0"),
            open_positions=len(open_positions),
            snapshot_data={"unit": "SOL", "source": "paper_trader"},
        )
        self.db.add(snap)
        await self.db.flush()
        return snap

    def _compute_entry_slippage_bps(self, price_impact_pct: float) -> int:
        base = random.uniform(10, 50)
        volatility = min(max(price_impact_pct * 10_000, 10), 50)
        noise = random.uniform(-5, 5)
        return max(1, int(base + volatility + noise))

    def _compute_exit_slippage_bps(self, price_impact_pct: float) -> int:
        return max(5, int(self._compute_entry_slippage_bps(price_impact_pct) * 1.25))

    def _exit_reason(self, signal: DetectedSignal | None) -> str:
        if signal and signal.signal_type.value == "sell":
            return "signal"
        return "time"

    async def _log(self, level: str, component: str, message: str, context: dict[str, object]) -> None:
        self.db.add(SystemLog(level=level, component=component, message=message, context_json=context))
        await self.db.flush()
