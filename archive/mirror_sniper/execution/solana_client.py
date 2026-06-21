"""Production Solana RPC client with retry/failover support."""

from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TokenAccountOpts, TxOpts
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction


class SolanaClient:
    def __init__(
        self,
        primary_rpc: str,
        backup_rpc: str | None = None,
        commitment: str = "confirmed",
    ) -> None:
        self.primary_rpc = primary_rpc
        self.backup_rpc = backup_rpc
        self.commitment = commitment
        self._active_rpc = primary_rpc
        self._client = AsyncClient(self._active_rpc, commitment=commitment)

    @property
    def client(self) -> AsyncClient:
        return self._client

    async def _rpc_call(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        for attempt in range(2):
            try:
                method = getattr(self._client, method_name)
                return await method(*args, **kwargs)
            except Exception as exc:
                logger.warning("solana_rpc_call_failed", method=method_name, attempt=attempt + 1, error=str(exc))
                if attempt == 0 and self.backup_rpc:
                    await self._switch_to_backup()
                    continue
                raise

    async def get_account_info(self, pubkey: Pubkey) -> Any | None:
        resp = await self._rpc_call("get_account_info", pubkey)
        value = getattr(resp, "value", None)
        return value

    async def get_token_account_balance(self, token_account: Pubkey) -> int | None:
        resp = await self._rpc_call("get_token_account_balance", token_account)
        value = getattr(resp, "value", None)
        if not value:
            return None
        amount = getattr(value, "amount", None)
        return int(amount) if amount is not None else None

    async def get_token_accounts_by_owner(self, owner: Pubkey, mint: Pubkey | None = None) -> list[dict]:
        opts = TokenAccountOpts(program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"))
        if mint:
            opts = TokenAccountOpts(mint=mint)
        resp = await self._rpc_call("get_token_accounts_by_owner_json_parsed", owner, opts)
        value = getattr(resp, "value", []) or []
        return [v.to_json() if hasattr(v, "to_json") else v for v in value]

    async def get_minimum_balance_for_rent_exemption(self, size: int) -> int:
        resp = await self._rpc_call("get_minimum_balance_for_rent_exemption", size)
        return int(getattr(resp, "value", 0))

    async def get_latest_blockhash(self) -> tuple[str, int]:
        resp = await self._rpc_call("get_latest_blockhash", Confirmed)
        val = getattr(resp, "value", None)
        if not val:
            raise RuntimeError("Failed to fetch latest blockhash")
        return str(val.blockhash), int(val.last_valid_block_height)

    async def simulate_transaction(self, tx: VersionedTransaction) -> tuple[bool, str | None, dict | None]:
        try:
            resp = await self._rpc_call("simulate_transaction", tx)
            value = getattr(resp, "value", None)
            err = getattr(value, "err", None) if value else None
            logs = getattr(value, "logs", None) if value else None
            result = {"logs": logs, "units_consumed": getattr(value, "units_consumed", None)}
            if err:
                return False, str(err), result
            return True, None, result
        except Exception as exc:
            return False, str(exc), None

    async def send_transaction(self, tx: VersionedTransaction, max_retries: int = 3, skip_preflight: bool = False) -> str:
        opts = TxOpts(skip_preflight=skip_preflight, max_retries=max_retries, preflight_commitment=Confirmed)
        resp = await self._rpc_call("send_transaction", tx, opts)
        value = getattr(resp, "value", None)
        if not value:
            raise RuntimeError("RPC did not return transaction signature")
        return str(value)

    async def confirm_transaction(self, signature: str, max_timeout: int = 60) -> tuple[bool, int | None]:
        start = asyncio.get_running_loop().time()
        while asyncio.get_running_loop().time() - start < max_timeout:
            try:
                statuses = await self._rpc_call("get_signature_statuses", [signature])
                vals = getattr(getattr(statuses, "value", None), "__iter__", None)
                status_values = getattr(statuses, "value", None) or []
                status = status_values[0] if status_values else None
                if status and getattr(status, "confirmation_status", None) in {"confirmed", "finalized"}:
                    return True, int(getattr(status, "slot", 0) or 0)
                if status and getattr(status, "err", None):
                    return False, None
            except Exception as exc:
                logger.warning("solana_confirm_poll_error", error=str(exc))
            await asyncio.sleep(1)
        return False, None

    async def get_transaction(self, signature: str) -> dict | None:
        resp = await self._rpc_call("get_transaction", signature, commitment=Confirmed, max_supported_transaction_version=0)
        value = getattr(resp, "value", None)
        if value is None:
            return None
        if hasattr(value, "to_json"):
            return {"raw": value.to_json()}
        return {"raw": str(value)}

    async def get_balance(self, pubkey: Pubkey) -> int:
        resp = await self._rpc_call("get_balance", pubkey)
        return int(getattr(resp, "value", 0))

    async def health_check(self) -> bool:
        try:
            resp = await self._rpc_call("get_health")
            return str(getattr(resp, "value", "")).lower() in {"ok", "healthy"}
        except Exception:
            return False

    async def _switch_to_backup(self) -> None:
        if not self.backup_rpc or self._active_rpc == self.backup_rpc:
            return
        logger.warning("solana_rpc_failover", from_rpc=self._active_rpc, to_rpc=self.backup_rpc)
        await self._client.close()
        self._active_rpc = self.backup_rpc
        self._client = AsyncClient(self._active_rpc, commitment=self.commitment)


# Backward compatibility alias
SolanaRpcClient = SolanaClient
