"""Live-trading safety checks."""

from __future__ import annotations

from solders.keypair import Keypair

from mirror_sniper.execution.solana_client import SolanaClient
from mirror_sniper.execution.wallet_manager import WalletManager


class SafetyChecker:
    """Pre-flight checks before any live execution."""

    @staticmethod
    async def pre_trade_checks(wallet: WalletManager, client: SolanaClient, required_sol: float) -> tuple[bool, list[str]]:
        warnings: list[str] = []

        if not await wallet.has_sufficient_funds(client, required_sol=required_sol, include_rent=True):
            warnings.append("Insufficient SOL for trade + fees + rent")

        if not await client.health_check():
            warnings.append("RPC node health check failed")

        # Placeholder hooks for app-level checks managed by risk engine/state.
        #  - Jupiter API responsive check
        #  - Kill switch state check
        #  - Daily loss limit check

        return len(warnings) == 0, warnings

    @staticmethod
    def validate_private_key(key: str) -> tuple[bool, Keypair | None, str]:
        try:
            wallet = WalletManager(key)
            return True, wallet.keypair, "ok"
        except Exception as exc:
            return False, None, f"invalid private key format: {exc}"
