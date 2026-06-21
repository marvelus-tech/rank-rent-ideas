"""Async Jupiter quote/swap client utilities."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any

import httpx
from loguru import logger

WSOL_MINT = "So11111111111111111111111111111111111111112"


@dataclass(slots=True)
class JupiterQuote:
    input_mint: str
    output_mint: str
    in_amount: int
    out_amount: int
    price_impact_pct: float
    route: list[dict[str, Any]]
    other_amount_threshold: int


@dataclass(slots=True)
class SwapTransaction:
    swap_transaction: str
    last_valid_block_height: int


class JupiterClient:
    def __init__(self) -> None:
        self.base_url = "https://quote-api.jup.ag/v6"
        self.client = httpx.AsyncClient(timeout=30.0)
        self._last_call_ts = 0.0

    async def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_call_ts
        if elapsed < 0.1:
            await asyncio.sleep(0.1 - elapsed)
        self._last_call_ts = time.monotonic()

    async def _request_json(self, method: str, path: str, **kwargs: Any) -> dict[str, Any] | None:
        attempts = 3
        backoff = 0.25
        for attempt in range(1, attempts + 1):
            await self._throttle()
            try:
                response = await self.client.request(method, f"{self.base_url}{path}", **kwargs)
                if response.status_code in {429, 502, 503, 504}:
                    if attempt == attempts:
                        return None
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                response.raise_for_status()
                data = response.json()
                return data if isinstance(data, dict) else None
            except httpx.HTTPError as exc:
                if attempt == attempts:
                    logger.warning("jupiter_request_failed", path=path, error=str(exc))
                    return None
                await asyncio.sleep(backoff)
                backoff *= 2
        return None

    async def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = 50,
        only_direct_routes: bool = False,
    ) -> JupiterQuote | None:
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount),
            "slippageBps": str(slippage_bps),
            "onlyDirectRoutes": str(only_direct_routes).lower(),
        }
        data = await self._request_json("GET", "/quote", params=params)
        if not data:
            return None

        try:
            return JupiterQuote(
                input_mint=data["inputMint"],
                output_mint=data["outputMint"],
                in_amount=int(data["inAmount"]),
                out_amount=int(data["outAmount"]),
                price_impact_pct=float(data.get("priceImpactPct", 0.0)),
                route=data.get("routePlan", []),
                other_amount_threshold=int(data.get("otherAmountThreshold", 0)),
            )
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning("jupiter_quote_parse_failed", error=str(exc), raw=data)
            return None

    async def get_swap_transaction(
        self,
        quote: JupiterQuote,
        user_public_key: str,
        priority_fee: int | None = None,
    ) -> SwapTransaction | None:
        payload: dict[str, Any] = {
            "userPublicKey": user_public_key,
            "quoteResponse": {
                "inputMint": quote.input_mint,
                "outputMint": quote.output_mint,
                "inAmount": str(quote.in_amount),
                "outAmount": str(quote.out_amount),
                "otherAmountThreshold": str(quote.other_amount_threshold),
                "priceImpactPct": str(quote.price_impact_pct),
                "routePlan": quote.route,
                "swapMode": "ExactIn",
            },
            "dynamicComputeUnitLimit": True,
        }
        if priority_fee is not None:
            payload["prioritizationFeeLamports"] = priority_fee

        data = await self._request_json("POST", "/swap", json=payload)
        if not data:
            return None

        swap_tx = data.get("swapTransaction")
        last_valid_height = data.get("lastValidBlockHeight")
        if not isinstance(swap_tx, str) or not isinstance(last_valid_height, int):
            return None
        return SwapTransaction(swap_transaction=swap_tx, last_valid_block_height=last_valid_height)

    async def get_price(self, token_mint: str) -> float | None:
        quote = await self.get_quote(
            input_mint=WSOL_MINT,
            output_mint=token_mint,
            amount=1_000_000_000,
            slippage_bps=50,
        )
        if not quote or quote.out_amount <= 0:
            return None
        return quote.in_amount / quote.out_amount

    async def aclose(self) -> None:
        await self.client.aclose()
