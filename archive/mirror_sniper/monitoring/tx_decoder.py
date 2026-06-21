"""Transaction decoder for Helius enhanced swap payloads."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from loguru import logger

RAYDIUM_PROGRAMS = {
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    "5quBtoiQqxF9Jykx4wzj6k9A2cQX3vGN28AL5soMgqd7",
}
ORCA_PROGRAMS = {"whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3G4fRj"}
JUPITER_PROGRAMS = {"JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"}
PUMPFUN_PROGRAMS = {"6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"}


@dataclass(slots=True)
class SwapDetails:
    dex_name: str
    token_in: str
    token_out: str
    amount_in: int
    amount_out: int
    sender_wallet: str
    timestamp: datetime
    slot: int
    tx_signature: str
    program_id: str
    confidence: float


class TransactionDecoder:
    """Decode swap intent from Helius enhanced tx payloads."""

    def decode_swap_transaction(self, tx_data: dict[str, Any]) -> SwapDetails | None:
        for parser in (
            self._decode_jupiter_swap,
            self._decode_raydium_swap,
            self._decode_orca_swap,
            self._decode_pumpfun_swap,
        ):
            try:
                decoded = parser(tx_data)
                if decoded:
                    return decoded
            except Exception as exc:
                logger.warning("decoder_parser_failed", parser=parser.__name__, error=str(exc))
        logger.info("decoder_no_swap_match", signature=tx_data.get("signature"))
        return None

    def _decode_raydium_swap(self, tx_data: dict[str, Any]) -> SwapDetails | None:
        if not self._has_program(tx_data, RAYDIUM_PROGRAMS):
            return None
        return self._decode_simple_swap(tx_data, dex_name="raydium", program_ids=RAYDIUM_PROGRAMS)

    def _decode_orca_swap(self, tx_data: dict[str, Any]) -> SwapDetails | None:
        if not self._has_program(tx_data, ORCA_PROGRAMS):
            return None
        return self._decode_simple_swap(tx_data, dex_name="orca", program_ids=ORCA_PROGRAMS)

    def _decode_jupiter_swap(self, tx_data: dict[str, Any]) -> SwapDetails | None:
        if not self._has_program(tx_data, JUPITER_PROGRAMS):
            return None

        signer = self._extract_signer(tx_data)
        transfers = [t for t in tx_data.get("tokenTransfers", []) if isinstance(t, dict)]
        user_out = [
            t
            for t in transfers
            if t.get("toUserAccount") == signer and (t.get("tokenAmount") or 0) > 0
        ]
        user_in = [
            t
            for t in transfers
            if t.get("fromUserAccount") == signer and (t.get("tokenAmount") or 0) > 0
        ]

        if not user_in or not user_out:
            logger.info("decoder_jupiter_ambiguous", signature=tx_data.get("signature"))
            return None

        token_in = user_in[0].get("mint")
        token_out = user_out[-1].get("mint")
        if not token_in or not token_out:
            logger.info("decoder_jupiter_missing_mint", signature=tx_data.get("signature"))
            return None

        amount_in = int(sum(float(t.get("tokenAmount", 0)) for t in user_in))
        amount_out = int(sum(float(t.get("tokenAmount", 0)) for t in user_out))

        return self._build_swap(
            tx_data,
            dex_name="jupiter",
            token_in=token_in,
            token_out=token_out,
            amount_in=amount_in,
            amount_out=amount_out,
            sender_wallet=signer,
            program_id=next(iter(JUPITER_PROGRAMS)),
            confidence=0.85,
        )

    def _decode_pumpfun_swap(self, tx_data: dict[str, Any]) -> SwapDetails | None:
        if not self._has_program(tx_data, PUMPFUN_PROGRAMS):
            return None
        signer = self._extract_signer(tx_data)
        native = [t for t in tx_data.get("nativeTransfers", []) if isinstance(t, dict)]
        tokens = [t for t in tx_data.get("tokenTransfers", []) if isinstance(t, dict)]
        if not native or not tokens:
            logger.info("decoder_pumpfun_ambiguous", signature=tx_data.get("signature"))
            return None

        sol_out = next((n for n in native if n.get("fromUserAccount") == signer), None)
        token_in = "So11111111111111111111111111111111111111112"
        token_out = tokens[-1].get("mint")
        if not token_out or not sol_out:
            return None

        return self._build_swap(
            tx_data,
            dex_name="pumpfun",
            token_in=token_in,
            token_out=token_out,
            amount_in=int(sol_out.get("amount", 0)),
            amount_out=int(float(tokens[-1].get("tokenAmount", 0))),
            sender_wallet=signer,
            program_id=next(iter(PUMPFUN_PROGRAMS)),
            confidence=0.75,
        )

    def _decode_simple_swap(
        self,
        tx_data: dict[str, Any],
        *,
        dex_name: str,
        program_ids: set[str],
    ) -> SwapDetails | None:
        signer = self._extract_signer(tx_data)
        transfers = [t for t in tx_data.get("tokenTransfers", []) if isinstance(t, dict)]
        user_out = [t for t in transfers if t.get("fromUserAccount") == signer]
        user_in = [t for t in transfers if t.get("toUserAccount") == signer]
        if not user_out or not user_in:
            logger.info("decoder_simple_swap_ambiguous", dex=dex_name, signature=tx_data.get("signature"))
            return None

        out_t = user_out[0]
        in_t = user_in[-1]
        token_in = out_t.get("mint")
        token_out = in_t.get("mint")
        if not token_in or not token_out:
            return None

        return self._build_swap(
            tx_data,
            dex_name=dex_name,
            token_in=token_in,
            token_out=token_out,
            amount_in=int(float(out_t.get("tokenAmount", 0))),
            amount_out=int(float(in_t.get("tokenAmount", 0))),
            sender_wallet=signer,
            program_id=next(iter(program_ids)),
            confidence=0.8,
        )

    @staticmethod
    def _has_program(tx_data: dict[str, Any], programs: set[str]) -> bool:
        instructions = tx_data.get("instructions") or tx_data.get("innerInstructions") or []
        for item in instructions:
            if not isinstance(item, dict):
                continue
            pid = item.get("programId") or item.get("programIdIndex")
            if isinstance(pid, str) and pid in programs:
                return True
        account_data = tx_data.get("accountData", [])
        for entry in account_data:
            if isinstance(entry, dict) and entry.get("account") in programs:
                return True
        return False

    @staticmethod
    def _extract_signer(tx_data: dict[str, Any]) -> str:
        fee_payer = tx_data.get("feePayer")
        if isinstance(fee_payer, str):
            return fee_payer
        signers = tx_data.get("signers", [])
        if signers and isinstance(signers[0], str):
            return signers[0]
        account_data = tx_data.get("accountData", [])
        for row in account_data:
            if isinstance(row, dict) and row.get("signer"):
                account = row.get("account")
                if isinstance(account, str):
                    return account
        return "unknown"

    @staticmethod
    def _build_swap(
        tx_data: dict[str, Any],
        *,
        dex_name: str,
        token_in: str,
        token_out: str,
        amount_in: int,
        amount_out: int,
        sender_wallet: str,
        program_id: str,
        confidence: float,
    ) -> SwapDetails:
        ts = tx_data.get("timestamp")
        timestamp = datetime.fromtimestamp(ts, tz=UTC) if isinstance(ts, (int, float)) else datetime.now(tz=UTC)
        return SwapDetails(
            dex_name=dex_name,
            token_in=token_in,
            token_out=token_out,
            amount_in=max(amount_in, 0),
            amount_out=max(amount_out, 0),
            sender_wallet=sender_wallet,
            timestamp=timestamp,
            slot=int(tx_data.get("slot") or 0),
            tx_signature=str(tx_data.get("signature") or ""),
            program_id=program_id,
            confidence=max(0.0, min(confidence, 1.0)),
        )
