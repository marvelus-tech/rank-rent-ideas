"""Risk engine implementation for signal filtering and sizing."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import httpx
from loguru import logger
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from mirror_sniper.core.models import DetectedSignal, PortfolioSnapshot
from mirror_sniper.interface.alerts import AlertService


@dataclass(slots=True)
class RiskConfig:
    max_position_percent: float = 0.05
    daily_loss_limit: float = 0.10
    max_slippage_bps: int = 100
    min_liquidity_usd: float = 50000
    min_wallet_score: float = 60
    min_token_age_hours: float = 2
    blacklist: set[str] = field(default_factory=set)
    trading_hours_start: int = 0
    trading_hours_end: int = 24
    min_sol_for_gas: float = 0.02


class RiskEngine:
    def __init__(self, config: RiskConfig, db: AsyncSession, alerts: AlertService | None = None) -> None:
        self.config = config
        self.db = db
        self.alerts = alerts or AlertService()

    async def validate_signal(self, signal: DetectedSignal) -> tuple[bool, str]:
        token = signal.output_mint or ""
        if token in self.config.blacklist:
            return False, "token_blacklisted"

        token_age_hours = await self._get_token_age_hours(token)
        if token_age_hours < self.config.min_token_age_hours:
            return False, "token_too_new"

        rug_score = await self._get_rugcheck_score(token)
        if rug_score <= 50:
            return False, "rugcheck_score_too_low"

        liquidity = await self._get_liquidity_usd(token)
        if liquidity < self.config.min_liquidity_usd:
            return False, "liquidity_below_threshold"

        wallet_score = float((signal.confidence_score or Decimal("0")) * Decimal("100"))
        if wallet_score < self.config.min_wallet_score:
            return False, "wallet_score_too_low"

        if await self._daily_loss_limit_hit():
            return False, "daily_loss_limit_hit"

        now_hour = datetime.now(tz=UTC).hour
        if not (self.config.trading_hours_start <= now_hour < self.config.trading_hours_end):
            return False, "outside_trading_hours"

        if not await self._has_sufficient_sol():
            return False, "insufficient_sol"

        return True, "approved"

    async def calculate_position_size(
        self,
        signal: DetectedSignal,
        portfolio_value_sol: float,
        confidence: float,
        wallet_score: float,
    ) -> int:
        _ = signal
        base_size = portfolio_value_sol * self.config.max_position_percent
        adjusted = base_size * max(0.0, min(confidence, 1.0)) * max(0.0, min(wallet_score / 100.0, 1.0))
        capped = min(adjusted, portfolio_value_sol * self.config.max_position_percent)
        return max(0, int(capped * 1_000_000_000))

    async def check_kill_switch(self) -> bool:
        # phase-2 DB config table is not present yet; default to enabled
        return False

    async def emergency_stop(self, reason: str) -> None:
        logger.critical("emergency_stop", reason=reason)
        await self.alerts.send_kill_switch_alert(reason)

    async def get_portfolio_value_sol(self) -> float:
        result = await self.db.execute(
            select(PortfolioSnapshot).order_by(desc(PortfolioSnapshot.snapshot_at)).limit(1)
        )
        latest = result.scalars().first()
        if not latest:
            return 1.0
        usd = float(latest.total_value_usd or 0)
        # conservative SOL/USD fallback for sizing
        return max(usd / 150.0, 0.1)

    async def _http_get_json(self, url: str, attempts: int = 3) -> dict[str, Any] | list[Any] | None:
        delay = 0.4
        for attempt in range(1, attempts + 1):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    return resp.json()
            except Exception as exc:
                if attempt == attempts:
                    logger.warning("risk_http_failed", url=url, error=str(exc))
                    return None
                await httpx.AsyncClient().aclose()
                import asyncio

                await asyncio.sleep(delay)
                delay *= 2
        return None

    async def _get_rugcheck_score(self, token_mint: str) -> float:
        data = await self._http_get_json(f"https://api.rugcheck.xyz/v1/tokens/{token_mint}/report")
        if isinstance(data, dict):
            score = data.get("score") or data.get("riskScore")
            if isinstance(score, (int, float)):
                return float(score)
        return 0.0

    async def _get_liquidity_usd(self, token_mint: str) -> float:
        data = await self._http_get_json(f"https://api.dexscreener.com/latest/dex/tokens/{token_mint}")
        if isinstance(data, dict):
            pairs = data.get("pairs")
            if isinstance(pairs, list) and pairs:
                liquidity_values = []
                for pair in pairs:
                    if isinstance(pair, dict):
                        liq = pair.get("liquidity", {}).get("usd") if isinstance(pair.get("liquidity"), dict) else None
                        if isinstance(liq, (int, float)):
                            liquidity_values.append(float(liq))
                if liquidity_values:
                    return max(liquidity_values)
        return 0.0

    async def _get_token_age_hours(self, token_mint: str) -> float:
        data = await self._http_get_json(f"https://api.dexscreener.com/latest/dex/tokens/{token_mint}")
        if isinstance(data, dict) and isinstance(data.get("pairs"), list) and data["pairs"]:
            created = data["pairs"][0].get("pairCreatedAt")
            if isinstance(created, (int, float)):
                created_dt = datetime.fromtimestamp(created / 1000.0, tz=UTC)
                return max((datetime.now(tz=UTC) - created_dt).total_seconds() / 3600, 0.0)
        return 999.0

    async def _daily_loss_limit_hit(self) -> bool:
        since = datetime.now(tz=UTC) - timedelta(days=1)
        result = await self.db.execute(
            select(PortfolioSnapshot).where(PortfolioSnapshot.snapshot_at >= since).order_by(PortfolioSnapshot.snapshot_at)
        )
        rows = result.scalars().all()
        if len(rows) < 2:
            return False
        start = float(rows[0].total_value_usd or 0)
        end = float(rows[-1].total_value_usd or 0)
        if start <= 0:
            return False
        drawdown = max(0.0, (start - end) / start)
        return drawdown >= self.config.daily_loss_limit

    async def _has_sufficient_sol(self) -> bool:
        return (await self.get_portfolio_value_sol()) >= self.config.min_sol_for_gas
