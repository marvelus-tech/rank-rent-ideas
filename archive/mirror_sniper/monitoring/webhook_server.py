"""FastAPI webhook server for Helius enhanced transaction ingestion."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy import select

from mirror_sniper.config import Settings, load_settings
from mirror_sniper.core.database import DatabaseManager, initialize_database
from mirror_sniper.core.enums import DexProgram, SignalType
from mirror_sniper.core.models import DetectedSignal, SystemLog, TrackedWallet
from mirror_sniper.execution.live_executor import LiveExecutor
from mirror_sniper.execution.paper_trader import PaperTrader
from mirror_sniper.execution.risk_engine import RiskConfig, RiskEngine
from mirror_sniper.strategy.copy_engine import CopyEngine

from .tx_decoder import TransactionDecoder

app = FastAPI(title="MirrorSniper Webhook Server", version="0.2.0")

_db: DatabaseManager | None = None
_settings: Settings | None = None
_decoder = TransactionDecoder()


async def _log_event(level: str, component: str, message: str, context: dict[str, Any] | None = None) -> None:
    if not _db:
        return
    async with _db.session() as session:
        session.add(
            SystemLog(
                level=level,
                component=component,
                message=message,
                context_json=context,
            )
        )


async def _get_current_slot(settings: Settings) -> int:
    rpc_url = settings.app.rpc.http_url
    payload = {"jsonrpc": "2.0", "id": "slot", "method": "getSlot", "params": []}
    import httpx

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(rpc_url, json=payload)
            r.raise_for_status()
            return int(r.json().get("result", 0))
    except Exception:
        return 0


@app.on_event("startup")
async def startup_event() -> None:
    global _db, _settings
    _settings = load_settings()
    _db = await initialize_database(settings=_settings, run_alembic=False)
    logger.info("webhook_server_startup")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    if _db:
        await _db.dispose()
    logger.info("webhook_server_shutdown")


@app.post("/webhook/helix")
@app.post("/webhook/helius")
async def handle_helius_webhook(
    request: Request,
    x_webhook_secret: str | None = Header(default=None),
) -> JSONResponse:
    if not _db or not _settings:
        raise HTTPException(status_code=503, detail="Server not initialized")

    expected_secret = _settings.secrets.helius_api_key
    if expected_secret and x_webhook_secret and x_webhook_secret != expected_secret:
        await _log_event("warning", "webhook", "Webhook secret mismatch")
        raise HTTPException(status_code=401, detail="Invalid webhook secret")

    try:
        payload = await request.json()
    except Exception as exc:
        await _log_event("error", "webhook", "Invalid JSON payload", {"error": str(exc)})
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    txs = payload if isinstance(payload, list) else [payload]
    current_slot = await _get_current_slot(_settings)

    for tx in txs:
        if not isinstance(tx, dict):
            continue
        try:
            await _process_transaction(tx, current_slot)
        except Exception as exc:
            logger.exception("webhook_tx_processing_failed", error=str(exc))
            await _log_event("error", "webhook", "Transaction processing failed", {"error": str(exc)})

    return JSONResponse(status_code=200, content={"status": "accepted"})


async def _process_transaction(tx_data: dict[str, Any], current_slot: int) -> None:
    assert _db is not None
    decoded = _decoder.decode_swap_transaction(tx_data)
    if not decoded:
        await _log_event("info", "decoder", "No swap decoded", {"signature": tx_data.get("signature")})
        return

    account_addresses = set(tx_data.get("accountData", []) or [])
    accs: set[str] = set()
    for row in account_addresses:
        if isinstance(row, dict) and isinstance(row.get("account"), str):
            accs.add(row["account"])
    if not accs and isinstance(tx_data.get("feePayer"), str):
        accs.add(tx_data["feePayer"])

    async with _db.session() as session:
        wallet = None
        if accs:
            result = await session.execute(
                select(TrackedWallet).where(TrackedWallet.address.in_(list(accs)), TrackedWallet.is_active.is_(True))
            )
            wallet = result.scalars().first()
        if not wallet:
            await _log_event("info", "webhook", "No tracked wallet match", {"signature": decoded.tx_signature})
            return

        win_rate = float(wallet.win_rate or 0)
        profit_factor = float(wallet.profit_factor or 0)
        recency_gap = max(0, current_slot - decoded.slot)
        recency_boost = 1.0 if recency_gap <= 10 else max(0.0, 1 - (recency_gap / 1000))
        confidence = (win_rate * 0.4) + (min(profit_factor, 3.0) / 3.0 * 0.3) + (recency_boost * 0.3)

        signal = DetectedSignal(
            tracked_wallet_address=wallet.address,
            token_mint=decoded.token_out,
            signal_type=SignalType.SWAP,
            dex_program=DexProgram(decoded.dex_name) if decoded.dex_name in DexProgram._value2member_map_ else DexProgram.UNKNOWN,
            source_signature=decoded.tx_signature,
            source_slot=decoded.slot,
            source_timestamp=decoded.timestamp,
            input_mint=decoded.token_in,
            output_mint=decoded.token_out,
            amount_in=Decimal(decoded.amount_in),
            amount_out=Decimal(decoded.amount_out),
            confidence_score=Decimal(str(round(max(0.0, min(confidence, 1.0)), 3))),
            raw_payload=tx_data,
            is_processed=False,
        )
        session.add(signal)
        await session.flush()
        signal_id = signal.id

    asyncio.create_task(process_signal(signal_id))
    await _log_event("info", "webhook", "Signal created", {"signal_id": signal_id})


async def process_signal(signal_id: int) -> None:
    if not _db or not _settings:
        return
    async with _db.session() as session:
        risk_engine = RiskEngine(config=RiskConfig(), db=session)
        copy_engine = CopyEngine(
            db_session=session,
            risk_engine=risk_engine,
            paper_trader=PaperTrader(),
            live_executor=LiveExecutor(),
            settings=_settings,
        )
        await copy_engine.process_signal(signal_id)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(tz=UTC).isoformat()}
