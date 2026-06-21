"""Token and signal filtering with external intelligence."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any

import httpx
from loguru import logger
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

from mirror_sniper.config import load_settings


@dataclass(slots=True)
class TokenValidation:
    approved: bool
    risk_level: str
    liquidity_usd: float
    rugcheck_score: int
    warnings: list[str]
    age_hours: float
    is_renounced: bool
    freeze_authority_disabled: bool


class TokenValidator:
    def __init__(self, rugcheck_enabled: bool = True, birdeye_api_key: str | None = None):
        self.rugcheck_enabled = rugcheck_enabled
        self.birdeye_api_key = birdeye_api_key
        self.min_liquidity_usd = 25_000.0
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}
        self._client = httpx.AsyncClient(timeout=15.0)
        self._rpc = AsyncClient(load_settings().app.rpc.http_url)

    async def validate_token(self, mint_address: str) -> TokenValidation:
        warnings: list[str] = []
        rug_score, rug_warnings = await self._check_rugcheck(mint_address)
        warnings.extend(rug_warnings)

        renounced, freeze_disabled, age_hours = await self._check_onchain(mint_address)
        liquidity_usd, _volume_24h = await self._check_liquidity(mint_address)

        if liquidity_usd < self.min_liquidity_usd:
            warnings.append(f"Low liquidity (${liquidity_usd:,.0f})")
        if rug_score != -1 and rug_score <= 50:
            warnings.append("Rugcheck score too low")
        if not renounced:
            warnings.append("Mint authority not renounced")
        if not freeze_disabled:
            warnings.append("Freeze authority still enabled")

        risk_level = "low"
        if rug_score == -1 or liquidity_usd < self.min_liquidity_usd or age_hours < 24:
            risk_level = "high"
        elif rug_score < 70 or liquidity_usd < 100_000:
            risk_level = "medium"

        approved = all(
            [
                rug_score == -1 or rug_score > 50,
                liquidity_usd >= self.min_liquidity_usd,
                age_hours >= 2,
            ]
        )

        return TokenValidation(
            approved=approved,
            risk_level=risk_level,
            liquidity_usd=liquidity_usd,
            rugcheck_score=max(rug_score, 0),
            warnings=warnings,
            age_hours=age_hours,
            is_renounced=renounced,
            freeze_authority_disabled=freeze_disabled,
        )

    async def _check_rugcheck(self, mint: str) -> tuple[int, list[str]]:
        if not self.rugcheck_enabled:
            return -1, ["Rugcheck disabled"]

        try:
            r = await self._client.get(f"https://api.rugcheck.xyz/v1/tokens/{mint}/report")
            if r.status_code >= 500:
                await asyncio.sleep(0.2)
                r = await self._client.get(f"https://api.rugcheck.xyz/v1/tokens/{mint}/report")
            r.raise_for_status()
            data = r.json()
            score = int(data.get("score", data.get("riskScore", -1)))
            warnings = [str(w) for w in data.get("warnings", []) if isinstance(w, str)]
            return score, warnings
        except Exception as exc:
            logger.warning("rugcheck_failed", mint=mint, error=str(exc))
            return -1, ["Rugcheck unavailable"]

    async def _check_onchain(self, mint: str) -> tuple[bool, bool, float]:
        try:
            mint_pubkey = Pubkey.from_string(mint)
            mint_info = await self._rpc.get_account_info_json_parsed(mint_pubkey)
            parsed = getattr(mint_info, "value", None)
            info = getattr(parsed, "data", None)
            parsed_info: dict[str, Any] = {}
            if isinstance(info, dict):
                parsed_info = info.get("parsed", {}).get("info", {})

            mint_auth = parsed_info.get("mintAuthority")
            freeze_auth = parsed_info.get("freezeAuthority")
            renounced = mint_auth is None
            freeze_disabled = freeze_auth is None

            sigs = await self._rpc.get_signatures_for_address(mint_pubkey, limit=1)
            age_hours = 999.0
            if getattr(sigs, "value", None):
                block_time = sigs.value[-1].block_time if sigs.value[-1] else None
                if block_time:
                    age_hours = max((time.time() - block_time) / 3600.0, 0.0)
            return renounced, freeze_disabled, age_hours
        except Exception as exc:
            logger.warning("onchain_check_failed", mint=mint, error=str(exc))
            return False, False, 0.0

    async def _check_liquidity(self, mint: str) -> tuple[float, float]:
        now = time.time()
        cached = self._cache.get(mint)
        if cached and now - cached[0] < 30:
            data = cached[1]
            return float(data.get("liquidity", 0.0)), float(data.get("volume", 0.0))

        if self.birdeye_api_key:
            try:
                headers = {"X-API-KEY": self.birdeye_api_key, "x-chain": "solana"}
                resp = await self._client.get(
                    "https://public-api.birdeye.so/defi/v3/token/market-data",
                    params={"address": mint},
                    headers=headers,
                )
                if resp.is_success:
                    d = resp.json().get("data", {})
                    liq = float(d.get("liquidity", 0.0))
                    vol = float(d.get("volume24h", 0.0))
                    self._cache[mint] = (now, {"liquidity": liq, "volume": vol})
                    return liq, vol
            except Exception:
                pass

        try:
            resp = await self._client.get(f"https://api.dexscreener.com/latest/dex/tokens/{mint}")
            resp.raise_for_status()
            pairs = resp.json().get("pairs", [])
            liq = 0.0
            vol = 0.0
            for pair in pairs:
                liq = max(liq, float(pair.get("liquidity", {}).get("usd", 0.0) or 0.0))
                vol = max(vol, float(pair.get("volume", {}).get("h24", 0.0) or 0.0))
            self._cache[mint] = (now, {"liquidity": liq, "volume": vol})
            return liq, vol
        except Exception as exc:
            logger.warning("liquidity_check_failed", mint=mint, error=str(exc))
            return 0.0, 0.0
