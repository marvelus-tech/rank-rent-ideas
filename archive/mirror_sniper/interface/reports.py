"""Paper trading reporting service."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mirror_sniper.core.models import DetectedSignal, ExecutedTrade, Position


class PaperTradingReport:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_report(self, days: int = 7) -> str:
        trades = await self._get_closed_trades(days)
        metrics = await self.calculate_metrics(days)
        open_positions = await self.db.execute(select(Position).where(Position.status == "open"))
        open_rows = open_positions.scalars().all()

        lines = [
            f"Paper Trading Report ({days}d)",
            f"Total closed trades: {len(trades)}",
            f"Win rate: {metrics['win_rate']:.2%}",
            f"Realized PnL: {metrics['total_realized_pnl_sol']:+.4f} SOL",
            f"Avg hold: {metrics['avg_holding_minutes']:.1f} min",
            f"Profit factor: {metrics['profit_factor']:.2f}",
            f"Max drawdown: {metrics['max_drawdown']:.2%}",
            f"Sharpe: {metrics['sharpe_ratio']:.2f}",
            "",
            "Open Positions:",
        ]
        for p in open_rows:
            lines.append(
                f"- {p.token_mint[:8]}... qty={p.amount_held} entry={float(p.entry_price_sol):.8f} "
                f"uPnL={float(p.unrealized_pnl_sol or 0):+.4f} SOL"
            )
        if not open_rows:
            lines.append("- none")

        daily = metrics["daily_pnl"]
        lines.append("\nDaily PnL:")
        for day, pnl in sorted(daily.items()):
            lines.append(f"- {day}: {pnl:+.4f} SOL")

        return "\n".join(lines)

    async def get_trade_history(self, limit: int = 50, wallet_filter: str | None = None) -> list[dict]:
        query = select(ExecutedTrade).order_by(ExecutedTrade.created_at.desc()).limit(limit)
        if wallet_filter:
            query = query.where(ExecutedTrade.tracked_wallet_address == wallet_filter)
        result = await self.db.execute(query)
        rows = result.scalars().all()

        out = []
        for t in rows:
            signal = None
            if t.signal_id:
                sig_res = await self.db.execute(select(DetectedSignal).where(DetectedSignal.id == t.signal_id))
                signal = sig_res.scalars().first()
            out.append(
                {
                    "trade_id": t.id,
                    "wallet": t.tracked_wallet_address,
                    "token_mint": t.token_mint,
                    "size_sol": float(t.size_sol or 0),
                    "status": str(t.status),
                    "realized_pnl_sol": float(t.realized_pnl_sol or 0),
                    "source_signature": signal.source_signature if signal else None,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
            )
        return out

    async def calculate_metrics(self, days: int = 30) -> dict:
        trades = await self._get_closed_trades(days)
        pnls = [float(t.realized_pnl_sol or 0) for t in trades]
        winners = [p for p in pnls if p > 0]
        losers = [p for p in pnls if p < 0]

        total_realized = sum(pnls)
        win_rate = (len(winners) / len(pnls)) if pnls else 0.0
        avg_win = (sum(winners) / len(winners)) if winners else 0.0
        avg_loss = (sum(losers) / len(losers)) if losers else 0.0
        profit_factor = (sum(winners) / abs(sum(losers))) if losers else (float("inf") if winners else 0.0)

        holds = [float(t.holding_duration_ms or 0) / 60000 for t in trades if t.holding_duration_ms]
        avg_hold = sum(holds) / len(holds) if holds else 0.0

        curve = []
        c = 0.0
        for p in pnls:
            c += p
            curve.append(c)
        max_dd = 0.0
        peak = 0.0
        for v in curve:
            peak = max(peak, v)
            max_dd = max(max_dd, peak - v)
        max_drawdown = (max_dd / peak) if peak > 0 else 0.0

        mean = (sum(pnls) / len(pnls)) if pnls else 0.0
        variance = (sum((x - mean) ** 2 for x in pnls) / (len(pnls) - 1)) if len(pnls) > 1 else 0.0
        std = math.sqrt(variance) if variance > 0 else 0.0
        sharpe = ((mean / std) * math.sqrt(len(pnls))) if std > 0 else 0.0

        daily = defaultdict(float)
        for t in trades:
            if t.exit_time:
                day = t.exit_time.astimezone(UTC).date().isoformat()
                daily[day] += float(t.realized_pnl_sol or 0)

        return {
            "total_trades": len(trades),
            "win_rate": win_rate,
            "total_realized_pnl_sol": total_realized,
            "avg_holding_minutes": avg_hold,
            "best_trade": max(pnls) if pnls else 0.0,
            "worst_trade": min(pnls) if pnls else 0.0,
            "daily_pnl": dict(daily),
            "sharpe_ratio": sharpe,
            "profit_factor": profit_factor,
            "max_drawdown": max_drawdown,
            "avg_winner_size": avg_win,
            "avg_loser_size": avg_loss,
        }

    async def _get_closed_trades(self, days: int) -> list[ExecutedTrade]:
        since = datetime.now(tz=UTC) - timedelta(days=days)
        result = await self.db.execute(
            select(ExecutedTrade).where(ExecutedTrade.exit_time.is_not(None), ExecutedTrade.created_at >= since)
        )
        return list(result.scalars().all())
