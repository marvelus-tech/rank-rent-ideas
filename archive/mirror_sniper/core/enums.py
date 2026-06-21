"""Shared enum definitions for MirrorSniper core domain."""

from __future__ import annotations

from enum import StrEnum


class TradeStatus(StrEnum):
    """Lifecycle status for an executed trade."""

    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


class SignalType(StrEnum):
    """Type of signal detected from monitored wallet activity."""

    BUY = "buy"
    SELL = "sell"
    SWAP = "swap"
    LIQUIDITY_ADD = "liquidity_add"
    LIQUIDITY_REMOVE = "liquidity_remove"


class ExecutionMode(StrEnum):
    """Execution mode for bot operation."""

    PAPER = "paper"
    LIVE = "live"
    DRY_RUN = "dry_run"


class DexProgram(StrEnum):
    """Known DEX programs used during decoding/execution."""

    RAYDIUM = "raydium"
    ORCA = "orca"
    METEORA = "meteora"
    JUPITER = "jupiter"
    PHOENIX = "phoenix"
    UNKNOWN = "unknown"
