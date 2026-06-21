"""Main copy-trading orchestration engine."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mirror_sniper.config import Settings, load_settings
from mirror_sniper.core.enums import ExecutionMode, SignalType, TradeStatus
from mirror_sniper.core.models import DetectedSignal, ExecutedTrade, TrackedWallet
from mirror_sniper.execution.live_executor import ExecutionResult, LiveExecutor
from mirror_sniper.execution.paper_trader import PaperTrader
from mirror_sniper.execution.risk_engine import RiskEngine
from mirror_sniper.execution.solana_client import SolanaClient
from mirror_sniper.execution.wallet_manager import WalletManager
from mirror_sniper.interface.alerts import AlertService
from mirror_sniper.strategy.position_manager import PositionManager


class CopyEngine:
    """Coordinates risk checks and execution for detected signals."""

    def __init__(
        self,
        db_session: AsyncSession,
        risk_engine: RiskEngine,
        paper_trader: PaperTrader,
        position_manager: PositionManager,
        settings: Settings | None = None,
        live_executor: LiveExecutor | None = None,
        execution_mode: ExecutionMode = ExecutionMode.PAPER,
        wallet_manager: WalletManager | None = None,
        solana_client: SolanaClient | None = None,
        alerts: AlertService | None = None,
    ) -> None:
        self.db_session = db_session
        self.risk_engine = risk_engine
        self.paper_trader = paper_trader
        self.position_manager = position_manager
        self.settings = settings or load_settings()
        self.live_executor = live_executor
        self.execution_mode = execution_mode
        self.wallet_manager = wallet_manager
        self.solana_client = solana_client
        self.alerts = alerts or AlertService()
        self._last_snapshot = datetime.now(tz=UTC)

    async def process_signal(self, signal_id: int) -> None:
        result = await self.db_session.execute(select(DetectedSignal).where(DetectedSignal.id == signal_id))
        signal = result.scalars().first()
        if not signal:
            logger.warning("copy_engine_signal_missing", signal_id=signal_id)
            return

        wallet_result = await self.db_session.execute(
            select(TrackedWallet).where(TrackedWallet.address == signal.tracked_wallet_address)
        )
        wallet = wallet_result.scalars().first()
        wallet_score = float((wallet.win_rate or 0) * Decimal("100")) if wallet else 0.0

        approved, reason = await self.risk_engine.validate_signal(signal)
        if not approved:
            signal.is_processed = True
            signal.processing_error = reason
            logger.info("copy_engine_signal_filtered", signal_id=signal.id, reason=reason)
            return

        position_lamports = await self.risk_engine.calculate_position_size(
            signal=signal,
            portfolio_value_sol=await self.paper_trader.get_portfolio_value(),
            confidence=float(signal.confidence_score or 0),
            wallet_score=wallet_score,
        )
        size_sol = Decimal(position_lamports) / Decimal(1_000_000_000)

        trade: ExecutedTrade | None = None
        live_result: ExecutionResult | None = None

        try:
            if self.execution_mode == ExecutionMode.PAPER:
                trade = await self.paper_trader.simulate_trade(signal, position_lamports)
            else:
                if not self.live_executor or not self.wallet_manager or not self.solana_client:
                    raise RuntimeError("live trading components are not initialized")

                await self.wallet_manager.create_ata_if_needed(self.solana_client, signal.output_mint or signal.token_mint or "")
                live_result = await self.live_executor.execute_swap(
                    signal=signal,
                    position_size_lamports=position_lamports,
                    max_slippage_bps=self.settings.app.execution.max_slippage_bps,
                )

                trade = ExecutedTrade(
                    signal_id=signal.id,
                    tracked_wallet_address=signal.tracked_wallet_address,
                    token_mint=signal.output_mint or signal.token_mint,
                    status=TradeStatus.FILLED if live_result.success else TradeStatus.FAILED,
                    dex_program=signal.dex_program,
                    side=SignalType.BUY,
                    size_sol=size_sol,
                    expected_out_amount=signal.amount_out,
                    actual_out_amount=signal.amount_out if live_result.success else None,
                    tx_signature=live_result.tx_signature,
                    slippage_bps=live_result.actual_slippage_bps or 0,
                    failure_reason=live_result.error,
                )
                self.db_session.add(trade)
                await self.db_session.flush()

                if live_result.success:
                    out_amount = int(signal.amount_out or 0)
                    price = live_result.executed_price or float(position_lamports / max(out_amount, 1))
                    await self.position_manager.open_position(signal, entry_price=price, amount_bought=out_amount, value_sol=float(size_sol))

        except Exception as exc:
            logger.exception("copy_engine_execution_failed", signal_id=signal.id, error=str(exc))
            trade = ExecutedTrade(
                signal_id=signal.id,
                tracked_wallet_address=signal.tracked_wallet_address,
                token_mint=signal.output_mint or signal.token_mint,
                status=TradeStatus.FAILED,
                dex_program=signal.dex_program,
                side=SignalType.BUY,
                size_sol=size_sol,
                failure_reason=str(exc),
            )
            self.db_session.add(trade)
            await self.db_session.flush()

        signal.is_processed = True
        signal.processing_error = None if trade and trade.status != TradeStatus.FAILED else (trade.failure_reason if trade else "unknown")

        if trade:
            await self.alerts.notify_trade(trade, live_result)

    async def monitor_positions_loop(self) -> None:
        while True:
            await self.position_manager.update_unrealized_pnl()
            positions = await self.position_manager.get_open_positions()
            for pos in positions:
                should_exit, reason = await self.position_manager.should_exit(pos)
                if should_exit:
                    await self.paper_trader.simulate_exit(pos)
                    pos.exit_reason = reason

            if datetime.now(tz=UTC) - self._last_snapshot >= timedelta(minutes=5):
                await self.paper_trader.take_snapshot()
                self._last_snapshot = datetime.now(tz=UTC)

            await asyncio.sleep(30)

    async def run_loop(self) -> None:
        interval = max(self.settings.app.trading.poll_interval_seconds, 0.3)
        while True:
            if await self.risk_engine.check_kill_switch():
                logger.warning("copy_engine_kill_switch_active")
                await asyncio.sleep(interval)
                continue

            result = await self.db_session.execute(
                select(DetectedSignal).where(DetectedSignal.is_processed.is_(False)).limit(20)
            )
            for signal in result.scalars().all():
                await self.process_signal(signal.id)
            await asyncio.sleep(interval)
