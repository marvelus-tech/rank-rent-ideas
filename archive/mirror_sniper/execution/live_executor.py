"""Live trade executor with mandatory simulation-first flow."""

from __future__ import annotations

import base64
import time
from dataclasses import dataclass

from loguru import logger
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.keypair import Keypair
from solders.message import MessageV0, to_bytes_versioned
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction

from mirror_sniper.config import ExecutionConfig
from mirror_sniper.core.models import DetectedSignal
from mirror_sniper.execution.jupiter_client import JupiterClient, WSOL_MINT
from mirror_sniper.execution.solana_client import SolanaClient


@dataclass(slots=True)
class ExecutionResult:
    success: bool
    tx_signature: str | None
    slot: int | None
    error: str | None
    executed_price: float | None
    actual_slippage_bps: int | None
    priority_fee_paid: int | None
    confirmation_time_ms: int | None


class LiveExecutor:
    def __init__(
        self,
        solana_client: SolanaClient,
        jupiter_client: JupiterClient,
        keypair: Keypair,
        config: ExecutionConfig,
    ) -> None:
        self.solana_client = solana_client
        self.jupiter_client = jupiter_client
        self.wallet = keypair
        self.config = config

    async def execute_swap(
        self,
        signal: DetectedSignal,
        position_size_lamports: int,
        max_slippage_bps: int = 100,
    ) -> ExecutionResult:
        token_out = signal.output_mint or signal.token_mint
        if not token_out:
            return ExecutionResult(False, None, None, "signal missing output token", None, None, None, None)

        quote = await self.jupiter_client.get_quote(
            input_mint=WSOL_MINT,
            output_mint=token_out,
            amount=position_size_lamports,
            slippage_bps=max_slippage_bps,
        )
        if not quote:
            return ExecutionResult(False, None, None, "failed to fetch jupiter quote", None, None, None, None)

        fee = await self._get_priority_fee()
        swap_tx = await self.jupiter_client.get_swap_transaction(
            quote=quote,
            user_public_key=str(self.wallet.pubkey()),
            priority_fee=fee,
        )
        if not swap_tx:
            return ExecutionResult(False, None, None, "failed to build swap transaction", None, None, fee, None)

        try:
            raw_bytes = base64.b64decode(swap_tx.swap_transaction)
            tx = VersionedTransaction.from_bytes(raw_bytes)
            tx = self._augment_and_sign_transaction(tx, fee)
        except Exception as exc:
            return ExecutionResult(False, None, None, f"transaction decode/sign failed: {exc}", None, None, fee, None)

        simulated, sim_err = await self._simulate_transaction(tx)
        if not simulated:
            return ExecutionResult(False, None, None, f"simulation_failed: {sim_err}", None, None, fee, None)

        start = time.monotonic()
        ok, sig_or_err, slot = await self._send_and_confirm(tx, max_timeout=self.config.confirmation_timeout)

        if not ok and sig_or_err and self._is_retryable(sig_or_err):
            retry_fee = int(fee * max(self.config.priority_fee_multiplier, 1.2))
            logger.warning("live_executor_retrying", reason=sig_or_err, priority_fee=retry_fee)
            tx = self._augment_and_sign_transaction(tx, retry_fee)
            ok, sig_or_err, slot = await self._send_and_confirm(tx, max_timeout=self.config.confirmation_timeout)
            fee = retry_fee

        if not ok:
            return ExecutionResult(False, None, slot, sig_or_err or "send/confirm failed", None, None, fee, None)

        confirmation_ms = int((time.monotonic() - start) * 1000)
        executed_price = quote.in_amount / max(quote.out_amount, 1)
        expected = quote.out_amount
        actual = quote.out_amount
        slippage = max(0, int((1 - (actual / max(expected, 1))) * 10_000))

        return ExecutionResult(
            success=True,
            tx_signature=sig_or_err,
            slot=slot,
            error=None,
            executed_price=float(executed_price),
            actual_slippage_bps=slippage,
            priority_fee_paid=fee,
            confirmation_time_ms=confirmation_ms,
        )

    async def _get_priority_fee(self) -> int:
        try:
            if hasattr(self.jupiter_client, "_request_json"):
                data = await self.jupiter_client._request_json("GET", "/priority-fee")  # type: ignore[attr-defined]
                if isinstance(data, dict):
                    fee = data.get("priorityFeeEstimate") or data.get("microLamports")
                    if isinstance(fee, (int, float)):
                        return max(1, int(fee * self.config.priority_fee_multiplier))
        except Exception as exc:
            logger.warning("priority_fee_fetch_failed", error=str(exc))
        return 50_000

    async def _simulate_transaction(self, tx: VersionedTransaction) -> tuple[bool, str | None]:
        success, err, details = await self.solana_client.simulate_transaction(tx)
        if not success:
            logger.error("live_executor_simulation_failed", error=err, details=details)
        return success, err

    async def _send_and_confirm(self, tx: VersionedTransaction, max_timeout: int = 60) -> tuple[bool, str | None, int | None]:
        try:
            signature = await self.solana_client.send_transaction(
                tx,
                max_retries=self.config.max_retries,
                skip_preflight=False,
            )
            confirmed, slot = await self.solana_client.confirm_transaction(signature, max_timeout=max_timeout)
            if not confirmed:
                return False, "confirmation timeout", slot
            return True, signature, slot
        except Exception as exc:
            logger.exception("live_executor_send_failed", error=str(exc))
            return False, str(exc), None

    def _augment_and_sign_transaction(self, tx: VersionedTransaction, priority_fee: int) -> VersionedTransaction:
        msg = tx.message
        if not isinstance(msg, MessageV0):
            return tx
        cb_limit = set_compute_unit_limit(300_000)
        cb_price = set_compute_unit_price(priority_fee)
        ix = [cb_price, cb_limit, *msg.instructions]
        new_msg = MessageV0.try_compile(msg.account_keys[0], ix, msg.address_table_lookups, msg.recent_blockhash)
        sig = self.wallet.sign_message(to_bytes_versioned(new_msg))
        return VersionedTransaction.populate(new_msg, [sig])

    def _is_retryable(self, error: str) -> bool:
        lowered = error.lower()
        return any(k in lowered for k in ["timeout", "blockhash", "429", "node is behind"])
