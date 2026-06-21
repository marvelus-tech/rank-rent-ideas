"""SQLAlchemy ORM models for MirrorSniper persistence layer."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs

from .enums import DexProgram, SignalType, TradeStatus


class Base(AsyncAttrs, DeclarativeBase):
    """Declarative base class for all ORM models."""


class TrackedWallet(Base):
    """Wallets monitored as source wallets for copy trading."""

    __tablename__ = "tracked_wallets"

    address: Mapped[str] = mapped_column(String(64), primary_key=True)
    nickname: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)

    total_trades: Mapped[int] = mapped_column(default=0)
    win_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0"))
    profit_factor: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("0"))
    roi_percent: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("0"))

    avg_hold_minutes: Mapped[int | None] = mapped_column(nullable=True)
    last_seen_signature: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    detected_signals: Mapped[list[DetectedSignal]] = relationship(
        back_populates="tracked_wallet", cascade="all, delete-orphan"
    )
    executed_trades: Mapped[list[ExecutedTrade]] = relationship(
        back_populates="tracked_wallet", cascade="all, delete-orphan"
    )
    snapshots: Mapped[list[PortfolioSnapshot]] = relationship(
        back_populates="tracked_wallet", cascade="all, delete-orphan"
    )


class TokenMetadata(Base):
    """Cached token metadata to avoid repeated chain/API lookups."""

    __tablename__ = "token_metadata"

    mint_address: Mapped[str] = mapped_column(String(64), primary_key=True)
    symbol: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    decimals: Mapped[int] = mapped_column(default=9)
    is_verified: Mapped[bool] = mapped_column(default=False)
    coingecko_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    last_price_usd: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    market_cap_usd: Mapped[Decimal | None] = mapped_column(Numeric(24, 2), nullable=True)
    liquidity_usd: Mapped[Decimal | None] = mapped_column(Numeric(24, 2), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    signals: Mapped[list[DetectedSignal]] = relationship(back_populates="token")
    trades: Mapped[list[ExecutedTrade]] = relationship(back_populates="token")
    positions: Mapped[list[Position]] = relationship(back_populates="token")


class DetectedSignal(Base):
    """Signals detected from incoming monitored wallet transactions/webhooks."""

    __tablename__ = "detected_signals"
    __table_args__ = (
        Index("ix_detected_signals_wallet_time", "tracked_wallet_address", "detected_at"),
        Index("ix_detected_signals_type_status", "signal_type", "is_processed"),
        Index("ix_detected_signals_signature", "source_signature", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tracked_wallet_address: Mapped[str] = mapped_column(ForeignKey("tracked_wallets.address"), index=True)
    token_mint: Mapped[str | None] = mapped_column(ForeignKey("token_metadata.mint_address"), nullable=True)

    signal_type: Mapped[SignalType] = mapped_column(default=SignalType.SWAP, index=True)
    dex_program: Mapped[DexProgram] = mapped_column(default=DexProgram.UNKNOWN)

    source_signature: Mapped[str] = mapped_column(String(120))
    source_slot: Mapped[int | None] = mapped_column(nullable=True)
    source_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    input_mint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_mint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    amount_in: Mapped[Decimal | None] = mapped_column(Numeric(24, 10), nullable=True)
    amount_out: Mapped[Decimal | None] = mapped_column(Numeric(24, 10), nullable=True)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(4, 3), default=Decimal("0.500"))

    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    is_processed: Mapped[bool] = mapped_column(default=False, index=True)
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    tracked_wallet: Mapped[TrackedWallet] = relationship(back_populates="detected_signals")
    token: Mapped[TokenMetadata | None] = relationship(back_populates="signals")
    executed_trades: Mapped[list[ExecutedTrade]] = relationship(back_populates="signal")
    positions: Mapped[list[Position]] = relationship(back_populates="signal")


class ExecutedTrade(Base):
    """Trade attempts/executions generated from detected signals."""

    __tablename__ = "executed_trades"
    __table_args__ = (
        Index("ix_executed_trades_status_time", "status", "created_at"),
        Index("ix_executed_trades_wallet_token", "tracked_wallet_address", "token_mint"),
        Index("ix_executed_trades_signal", "signal_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    signal_id: Mapped[int | None] = mapped_column(ForeignKey("detected_signals.id"), nullable=True)
    tracked_wallet_address: Mapped[str | None] = mapped_column(ForeignKey("tracked_wallets.address"), nullable=True)
    token_mint: Mapped[str | None] = mapped_column(ForeignKey("token_metadata.mint_address"), nullable=True)

    status: Mapped[TradeStatus] = mapped_column(default=TradeStatus.PENDING, index=True)
    dex_program: Mapped[DexProgram] = mapped_column(default=DexProgram.UNKNOWN)

    side: Mapped[SignalType] = mapped_column(default=SignalType.BUY)
    size_sol: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))
    expected_out_amount: Mapped[Decimal | None] = mapped_column(Numeric(24, 10), nullable=True)
    actual_out_amount: Mapped[Decimal | None] = mapped_column(Numeric(24, 10), nullable=True)

    expected_price_usd: Mapped[Decimal | None] = mapped_column(Numeric(20, 10), nullable=True)
    actual_price_usd: Mapped[Decimal | None] = mapped_column(Numeric(20, 10), nullable=True)
    slippage_bps: Mapped[int] = mapped_column(default=0)
    fees_paid_sol: Mapped[Decimal] = mapped_column(Numeric(20, 10), default=Decimal("0"))

    tx_signature: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    filled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    exit_price_sol: Mapped[Decimal | None] = mapped_column(Numeric(20, 10), nullable=True)
    exit_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    realized_pnl_sol: Mapped[Decimal | None] = mapped_column(Numeric(20, 10), nullable=True)
    holding_duration_ms: Mapped[int | None] = mapped_column(nullable=True)

    signal: Mapped[DetectedSignal | None] = relationship(back_populates="executed_trades")
    tracked_wallet: Mapped[TrackedWallet | None] = relationship(back_populates="executed_trades")
    token: Mapped[TokenMetadata | None] = relationship(back_populates="trades")


class Position(Base):
    """Tracks open trading positions."""

    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token_mint: Mapped[str] = mapped_column(ForeignKey("token_metadata.mint_address"), index=True)
    token_symbol: Mapped[str | None] = mapped_column(String(20), nullable=True)
    entry_price_sol: Mapped[Decimal] = mapped_column(Numeric(36, 18))
    amount_held: Mapped[int] = mapped_column(BigInteger)
    entry_value_sol: Mapped[Decimal] = mapped_column(Numeric(36, 18))
    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    signal_id: Mapped[int | None] = mapped_column(ForeignKey("detected_signals.id"), nullable=True)

    unrealized_pnl_sol: Mapped[Decimal] = mapped_column(Numeric(36, 18), default=Decimal("0"))
    highest_price_seen: Mapped[Decimal | None] = mapped_column(Numeric(36, 18), nullable=True)

    exit_price: Mapped[Decimal | None] = mapped_column(Numeric(36, 18), nullable=True)
    exit_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    realized_pnl_sol: Mapped[Decimal | None] = mapped_column(Numeric(36, 18), nullable=True)
    exit_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)

    signal: Mapped[DetectedSignal | None] = relationship(back_populates="positions")
    token: Mapped[TokenMetadata] = relationship(back_populates="positions")


class PortfolioSnapshot(Base):
    """Portfolio valuation snapshots used for reporting and risk checks."""

    __tablename__ = "portfolio_snapshots"
    __table_args__ = (
        Index("ix_portfolio_snapshots_time", "snapshot_at"),
        Index("ix_portfolio_snapshots_wallet_time", "tracked_wallet_address", "snapshot_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tracked_wallet_address: Mapped[str | None] = mapped_column(ForeignKey("tracked_wallets.address"), nullable=True)

    total_value_usd: Mapped[Decimal] = mapped_column(Numeric(24, 4), default=Decimal("0"))
    cash_value_usd: Mapped[Decimal] = mapped_column(Numeric(24, 4), default=Decimal("0"))
    invested_value_usd: Mapped[Decimal] = mapped_column(Numeric(24, 4), default=Decimal("0"))
    unrealized_pnl_usd: Mapped[Decimal] = mapped_column(Numeric(24, 4), default=Decimal("0"))
    realized_pnl_usd: Mapped[Decimal] = mapped_column(Numeric(24, 4), default=Decimal("0"))

    open_positions: Mapped[int] = mapped_column(default=0)
    snapshot_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tracked_wallet: Mapped[TrackedWallet | None] = relationship(back_populates="snapshots")


class SystemLog(Base):
    """Audit/event log for observability and post-mortem analysis."""

    __tablename__ = "system_logs"
    __table_args__ = (
        Index("ix_system_logs_level_time", "level", "created_at"),
        Index("ix_system_logs_component_time", "component", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String(16), index=True)
    component: Mapped[str] = mapped_column(String(64), index=True)
    message: Mapped[str] = mapped_column(Text)
    context_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
