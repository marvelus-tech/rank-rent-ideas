"""MirrorSniper application entry point."""

from __future__ import annotations

import asyncio
import os
import sys

from loguru import logger

from mirror_sniper.config import load_settings
from mirror_sniper.core.enums import ExecutionMode
from mirror_sniper.execution.jupiter_client import JupiterClient
from mirror_sniper.execution.live_executor import LiveExecutor
from mirror_sniper.execution.paper_trader import PaperTrader
from mirror_sniper.execution.risk_engine import RiskConfig, RiskEngine
from mirror_sniper.execution.solana_client import SolanaClient
from mirror_sniper.execution.wallet_manager import WalletManager
from mirror_sniper.interface.alerts import AlertManager
from mirror_sniper.interface.cli import cli


def configure_logging() -> None:
    logger.remove()
    logger.add(sys.stdout, serialize=True, level="INFO", backtrace=False, diagnose=False)


def confirm_live_mode() -> bool:
    val = os.getenv("MIRROR_CONFIRM_LIVE", "false").lower()
    return val in {"1", "true", "yes", "on"}


async def main_async() -> None:
    settings = load_settings()
    mode = ExecutionMode(settings.app.trading.execution_mode)

    jupiter = JupiterClient()
    alerts = AlertManager(
        telegram_token=settings.app.alerts.telegram.bot_token,
        telegram_chat_id=settings.app.alerts.telegram.chat_id,
        discord_webhook=settings.app.alerts.discord.webhook_url,
    )

    if mode == ExecutionMode.LIVE:
        if not confirm_live_mode():
            logger.warning("Live mode cancelled by safety gate. Set MIRROR_CONFIRM_LIVE=true to continue.")
            return

        private_key = os.getenv("TRADING_WALLET_PRIVATE_KEY")
        if not private_key:
            raise RuntimeError("TRADING_WALLET_PRIVATE_KEY is required in live mode")

        wallet = WalletManager(private_key)
        solana_client = SolanaClient(settings.app.rpc.primary, settings.app.rpc.backup)
        live_executor = LiveExecutor(solana_client, jupiter, wallet.keypair, settings.app.execution)
        _ = (wallet, solana_client, live_executor)

    logger.info("MirrorSniper boot complete; use CLI for run/setup commands")


def main() -> None:
    configure_logging()
    logger.info("Starting MirrorSniper")
    cli()


if __name__ == "__main__":
    main()
