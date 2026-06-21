=== LIQUIDATION HUNTER PERP BOT — Build Prompt ===

Build a DeFi bot that monitors perpetual futures for liquidation opportunities.

PRODUCT: LiquidatorBot — "Profit from other traders' margin calls"

CORE FEATURES:
- Position monitoring: tracks open perp positions across Drift, Mango, 01, Hyperliquid
- Liquidation calculator: computes exact liquidation prices based on leverage + collateral
- Alert system: notifies when positions approach liquidation zone
- Auto-execution: attempts to capture liquidated assets at discount
- Funding rate arbitrage: monitors rates across exchanges, suggests long/short based on positive/negative funding
- Risk dashboard: shows current opportunities, historical performance, gas costs
- Paper trading mode: test strategies without real money
- Multi-exchange: unified view across Solana perp DEXs

TECH STACK:
- Solana: @solana/web3.js, Jupiter API, Drift SDK
- Data: Helius RPC, Birdeye API (price feeds), DefiLlama
- Execution: Custom bot logic with MEV protection
- Backend: Node.js + TypeScript
- Database: PostgreSQL (position tracking, performance)
- Frontend: Next.js + Tailwind (monitoring dashboard)
- Wallet: Phantom/Solflare integration for signing

TARGET: DeFi traders, quant enthusiasts, crypto natives comfortable with derivatives

RISK CONTROLS:
- Max position size per trade
- Daily loss limits
- Circuit breakers for extreme volatility
- Only trade with capital you can afford to lose

PRICING:
- Open source (self-hosted)
- Managed service: 10% of profits (performance fee)
- SaaS: $199/month for monitoring + alerts (auto-execution extra)

SUCCESS CRITERIA:
- Successfully captures 3+ liquidation events in first 30 days
- Average profit per capture: 2-5%
- Funding rate arbitrage generates positive yield 70%+ of time
- Zero catastrophic losses (proper risk controls)
