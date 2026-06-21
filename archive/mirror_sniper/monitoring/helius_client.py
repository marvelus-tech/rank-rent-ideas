"""Async Helius API client with retries + free-tier rate limiting."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any

import httpx
from loguru import logger


class HeliusClient:
    """Async client for Helius RPC + webhook APIs."""

    def __init__(self, api_key: str, rpc_url: str) -> None:
        self.api_key = api_key
        self.rpc_url = rpc_url.rstrip("/")
        self.base_url = "https://api.helius.xyz"
        self._timeout = httpx.Timeout(15.0, connect=5.0)
        self._semaphore = asyncio.Semaphore(10)

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | list[Any] | None = None,
        headers: dict[str, str] | None = None,
        attempts: int = 4,
    ) -> Any:
        delay = 0.4
        for attempt in range(1, attempts + 1):
            async with self._semaphore:
                try:
                    async with httpx.AsyncClient(timeout=self._timeout) as client:
                        response = await client.request(
                            method=method,
                            url=url,
                            params=params,
                            json=json_body,
                            headers=headers,
                        )
                    if response.status_code in {429, 500, 502, 503, 504}:
                        raise httpx.HTTPStatusError(
                            f"Retryable status {response.status_code}",
                            request=response.request,
                            response=response,
                        )
                    response.raise_for_status()
                    await asyncio.sleep(0.11)
                    return response.json()
                except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as exc:
                    if attempt >= attempts:
                        logger.error(
                            "helius_request_failed",
                            method=method,
                            url=url,
                            attempt=attempt,
                            error=str(exc),
                        )
                        raise
                    logger.warning(
                        "helius_request_retry",
                        method=method,
                        url=url,
                        attempt=attempt,
                        delay=delay,
                        error=str(exc),
                    )
                    await asyncio.sleep(delay)
                    delay *= 2
        return None

    async def get_signatures_for_address(
        self,
        address: str,
        limit: int = 100,
        before: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch signatures from RPC with pagination support."""

        payload: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": "mirror-sniper",
            "method": "getSignaturesForAddress",
            "params": [address, {"limit": min(limit, 1000)}],
        }
        if before:
            payload["params"][1]["before"] = before

        data = await self._request_with_retry(
            "POST",
            f"{self.rpc_url}?api-key={self.api_key}",
            json_body=payload,
        )
        result = data.get("result") if isinstance(data, dict) else []
        return result if isinstance(result, list) else []

    async def get_transaction(self, signature: str) -> dict[str, Any] | None:
        """Fetch parsed enhanced transaction from Helius."""

        params = {"api-key": self.api_key}
        data = await self._request_with_retry(
            "POST",
            f"{self.base_url}/v0/transactions",
            params=params,
            json_body={"transactions": [signature]},
        )
        if isinstance(data, Sequence) and data:
            item = data[0]
            return item if isinstance(item, dict) else None
        return None

    async def register_webhook(
        self,
        target_wallets: list[str],
        callback_url: str,
        webhook_secret: str | None = None,
    ) -> str:
        """Create a Helius webhook and return webhook ID."""

        body: dict[str, Any] = {
            "webhookURL": callback_url,
            "transactionTypes": ["ANY"],
            "accountAddresses": target_wallets,
            "webhookType": "enhanced",
        }
        if webhook_secret:
            body["authHeader"] = webhook_secret

        data = await self._request_with_retry(
            "POST",
            f"{self.base_url}/v0/webhooks",
            params={"api-key": self.api_key},
            json_body=body,
            headers={"Content-Type": "application/json"},
        )
        webhook_id = data.get("webhookID") if isinstance(data, dict) else None
        if not webhook_id:
            raise ValueError("Webhook created but webhookID missing from response")
        return str(webhook_id)

    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook by ID."""

        try:
            await self._request_with_retry(
                "DELETE",
                f"{self.base_url}/v0/webhooks/{webhook_id}",
                params={"api-key": self.api_key},
            )
            return True
        except Exception as exc:  # pragma: no cover - defensive branch
            logger.error("helius_webhook_delete_failed", webhook_id=webhook_id, error=str(exc))
            return False

    async def list_webhooks(self) -> list[dict[str, Any]]:
        """List all webhooks registered under current key."""

        data = await self._request_with_retry(
            "GET",
            f"{self.base_url}/v0/webhooks",
            params={"api-key": self.api_key},
        )
        if isinstance(data, list):
            return [row for row in data if isinstance(row, dict)]
        return []
