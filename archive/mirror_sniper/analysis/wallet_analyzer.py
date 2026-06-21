"""Historical wallet analysis stubs used during Phase 1 foundation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WalletStats:
    """Basic wallet performance summary."""

    address: str
    total_trades: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0


class WalletAnalyzer:
    """Service for analyzing historical wallet performance (stub)."""

    async def analyze_wallet(self, address: str) -> WalletStats:
        """Return placeholder stats while historical pipeline is pending."""

        return WalletStats(address=address)
