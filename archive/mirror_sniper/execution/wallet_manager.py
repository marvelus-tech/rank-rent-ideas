"""Wallet operations for live trading."""

from __future__ import annotations

import base58

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import create_associated_token_account, get_associated_token_address

from mirror_sniper.execution.solana_client import SolanaClient


class WalletManager:
    def __init__(self, private_key: str):
        self.keypair = self._load_keypair(private_key)
        self.pubkey = self.keypair.pubkey()

    def _load_keypair(self, private_key: str) -> Keypair:
        raw = base58.b58decode(private_key.strip())
        if len(raw) == 64:
            return Keypair.from_bytes(raw)
        if len(raw) == 32:
            return Keypair.from_seed(raw)
        raise ValueError("Invalid private key format (expected base58-encoded 32-byte seed or 64-byte keypair)")

    async def get_sol_balance(self, client: SolanaClient) -> float:
        lamports = await client.get_balance(self.pubkey)
        return lamports / 1_000_000_000

    async def get_token_balance(self, client: SolanaClient, mint: str) -> int:
        mint_pk = Pubkey.from_string(mint)
        ata = get_associated_token_address(self.pubkey, mint_pk)
        balance = await client.get_token_account_balance(ata)
        return int(balance or 0)

    async def create_ata_if_needed(self, client: SolanaClient, mint: str) -> str | None:
        mint_pk = Pubkey.from_string(mint)
        ata = get_associated_token_address(self.pubkey, mint_pk)
        info = await client.get_account_info(ata)
        if info:
            return str(ata)

        ix = create_associated_token_account(
            payer=self.pubkey,
            owner=self.pubkey,
            mint=mint_pk,
            token_program_id=TOKEN_PROGRAM_ID,
        )

        from solders.hash import Hash
        from solders.message import MessageV0, to_bytes_versioned
        from solders.transaction import VersionedTransaction

        blockhash_str, _ = await client.get_latest_blockhash()
        msg = MessageV0.try_compile(
            payer=self.pubkey,
            instructions=[ix],
            address_lookup_table_accounts=[],
            recent_blockhash=Hash.from_string(blockhash_str),
        )
        sig = self.keypair.sign_message(to_bytes_versioned(msg))
        tx = VersionedTransaction.populate(msg, [sig])

        await client.send_transaction(tx, max_retries=3, skip_preflight=False)
        return str(ata)

    async def has_sufficient_funds(self, client: SolanaClient, required_sol: float, include_rent: bool = True) -> bool:
        bal = await self.get_sol_balance(client)
        reserve = 0.002
        if include_rent:
            reserve += (await client.get_minimum_balance_for_rent_exemption(165)) / 1_000_000_000
        return bal >= (required_sol + reserve)
