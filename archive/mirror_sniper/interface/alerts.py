"""Notification manager for signal/trade/system events."""

from __future__ import annotations

import json

import httpx
from loguru import logger

from mirror_sniper.core.enums import ExecutionMode
from mirror_sniper.core.models import DetectedSignal, ExecutedTrade, Position
from mirror_sniper.execution.live_executor import ExecutionResult


class AlertManager:
    def __init__(
        self,
        telegram_token: str | None = None,
        telegram_chat_id: str | None = None,
        discord_webhook: str | None = None,
    ) -> None:
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.discord_webhook = discord_webhook

    async def _send(self, message: str) -> None:
        logger.info("alert", message=message)
        async with httpx.AsyncClient(timeout=10) as client:
            if self.telegram_token and self.telegram_chat_id:
                try:
                    await client.post(
                        f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                        json={"chat_id": self.telegram_chat_id, "text": message},
                    )
                except Exception as exc:
                    logger.warning("telegram_alert_failed", error=str(exc))
            if self.discord_webhook:
                try:
                    await client.post(self.discord_webhook, json={"content": message})
                except Exception as exc:
                    logger.warning("discord_alert_failed", error=str(exc))

    async def notify_signal(self, signal: DetectedSignal, confidence: float) -> None:
        await self._send(
            f"📡 Signal detected\nWallet: {signal.tracked_wallet_address}\nToken: {signal.output_mint or signal.token_mint}\nConfidence: {confidence:.2f}"
        )

    async def notify_trade(self, trade: ExecutedTrade, result: ExecutionResult | None = None) -> None:
        is_live = result is not None or (trade.tx_signature and not str(trade.tx_signature).startswith("SIM-"))
        mode = "💰 LIVE Trade Executed" if is_live else "📊 Paper Trade Executed"
        lines = [
            mode,
            f"Status: {trade.status}",
            f"Token: {trade.token_mint}",
            f"Size: {float(trade.size_sol):.6f} SOL",
        ]
        if trade.tx_signature:
            lines.append(f"Tx: https://solscan.io/tx/{trade.tx_signature}")
        if result and result.error:
            lines.append(f"Error: {result.error}")
        await self._send("\n".join(lines))

    async def notify_position_close(self, position: Position, pnl_sol: float, reason: str) -> None:
        await self._send(
            f"📉 Position Closed\nToken: {position.token_mint}\nPnL: {pnl_sol:+.6f} SOL\nReason: {reason}"
        )

    async def notify_emergency_stop(self, reason: str) -> None:
        await self._send(f"🚨 EMERGENCY STOP ACTIVATED\nReason: {reason}")

    async def notify_error(self, component: str, error: str) -> None:
        await self._send(f"⚠️ Error in {component}: {error}")

    async def send_kill_switch_alert(self, reason: str = "") -> None:
        await self.notify_emergency_stop(reason or "manual")


AlertService = AlertManager
