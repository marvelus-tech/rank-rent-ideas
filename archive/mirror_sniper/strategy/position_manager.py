"""Position tracking and portfolio state management."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mirror_sniper.core.models import DetectedSignal, ExecutedTrade, PortfolioSnapshot, Position
from mirror_sniper.execution.jupiter_client import JupiterClient


@dataclass(slots=True)
class PositionView:
    id: int
    token_mint: str
    token_symbol: str | None
    entry_price_sol: float
    amount_held: int
    entry_value_sol: float
    entry_time: datetime
    signal_id: int
    unrealized_pnl_sol: float = 0.0
    highest_price_seen: float = 0.0


class PositionManager:
    def __init__(self, db: AsyncSession, jupiter_client: JupiterClient):
        self.db = db
        self.jupiter_client = jupiter_client

    async def open_position(self, signal: DetectedSignal, entry_price: float, amount_bought: int, value_sol: float) -> Position:
        pos = Position(
            token_mint=signal.output_mint or signal.token_mint or "",
            token_symbol=None,
            entry_price_sol=Decimal(str(entry_price)),
            amount_held=amount_bought,
            entry_value_sol=Decimal(str(value_sol)),
            entry_time=datetime.now(tz=UTC),
            signal_id=signal.id,
            highest_price_seen=Decimal(str(entry_price)),
            status="open",
        )
        self.db.add(pos)
        await self.db.flush()
        await self._snapshot()
        return pos

    async def close_position(self, position_id: int, exit_price: float, exit_value_sol: float, reason: str = "signal") -> float:
        result = await self.db.execute(select(Position).where(Position.id == position_id))
        pos = result.scalars().first()
        if not pos:
            return 0.0

        realized = float(exit_value_sol - float(pos.entry_value_sol or 0))
        pos.exit_price = Decimal(str(exit_price))
        pos.exit_time = datetime.now(tz=UTC)
        pos.realized_pnl_sol = Decimal(str(realized))
        pos.exit_reason = reason
        pos.status = "closed"

        trade_res = await self.db.execute(
            select(ExecutedTrade).where(ExecutedTrade.signal_id == pos.signal_id).order_by(ExecutedTrade.id.desc())
        )
        trade = trade_res.scalars().first()
        if trade:
            trade.realized_pnl_sol = Decimal(str(realized))
            trade.exit_price_sol = Decimal(str(exit_price))
            trade.exit_time = pos.exit_time
            trade.holding_duration_ms = int((pos.exit_time - pos.entry_time).total_seconds() * 1000)

        await self._snapshot()
        return realized

    async def update_unrealized_pnl(self) -> list[Position]:
        rows = await self.db.execute(select(Position).where(Position.status == "open"))
        positions = rows.scalars().all()
        for pos in positions:
            price = await self.jupiter_client.get_price(pos.token_mint)
            if price is None:
                continue
            current_value = price * pos.amount_held
            entry_val = float(pos.entry_value_sol or 0)
            pnl = current_value - entry_val
            pos.unrealized_pnl_sol = Decimal(str(pnl))
            if pos.highest_price_seen is None or price > float(pos.highest_price_seen):
                pos.highest_price_seen = Decimal(str(price))
        return positions

    async def get_open_positions(self) -> list[Position]:
        result = await self.db.execute(select(Position).where(Position.status == "open"))
        return list(result.scalars().all())

    async def get_position_by_token(self, mint: str) -> Position | None:
        result = await self.db.execute(select(Position).where(Position.token_mint == mint, Position.status == "open"))
        return result.scalars().first()

    async def should_exit(self, position: Position, current_signal: DetectedSignal | None = None) -> tuple[bool, str]:
        if current_signal and current_signal.signal_type.value == "sell" and current_signal.output_mint == position.token_mint:
            return True, "signal"

        entry_price = float(position.entry_price_sol or 0)
        current_price = await self.jupiter_client.get_price(position.token_mint)
        if current_price is None or entry_price <= 0:
            return False, "hold"

        if current_price <= (entry_price * 0.8):
            return True, "stop_loss"

        if position.entry_time and datetime.now(tz=UTC) - position.entry_time > timedelta(hours=1):
            return True, "time"

        high = float(position.highest_price_seen or entry_price)
        if current_price <= (high * 0.9):
            return True, "trailing_stop"

        return False, "hold"

    async def _snapshot(self) -> PortfolioSnapshot:
        open_positions = await self.get_open_positions()
        invested = sum(float(p.entry_value_sol or 0) for p in open_positions)
        unrealized = sum(float(p.unrealized_pnl_sol or 0) for p in open_positions)
        snap = PortfolioSnapshot(
            total_value_usd=Decimal(str(invested + unrealized)),
            cash_value_usd=Decimal("0"),
            invested_value_usd=Decimal(str(invested)),
            unrealized_pnl_usd=Decimal(str(unrealized)),
            realized_pnl_usd=Decimal("0"),
            open_positions=len(open_positions),
            snapshot_data={"unit": "SOL"},
        )
        self.db.add(snap)
        await self.db.flush()
        return snap
