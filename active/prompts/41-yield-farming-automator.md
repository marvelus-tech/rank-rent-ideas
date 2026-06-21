=== YIELD FARMING AUTOMATOR — Build Prompt ===

Build a DeFi yield optimization bot that automates farming across Solana protocols.

PRODUCT: YieldMax — "Set it and forget it DeFi"

CORE FEATURES:
- Auto-compounding: monitors rewards, compounds at optimal intervals (balancing gas vs APY)
- APY scanning: checks rates across Kamino, Solend, Marinade, Jito, Drift, Orca, Raydium
- Auto-rebalancing: moves capital to highest-yielding opportunities
- Impermanent loss protection: monitors LP positions, suggests exits when IL exceeds gains
- Governance harvesting: auto-claims airdrops, governance tokens
- Strategy templates:
  * Conservative: mostly lending vaults (low risk, stable yield)
  * Balanced: mix of lending + LP farming
  * Aggressive: new protocols, high APY pools
- Gas optimization: batches transactions, uses Jito bundles for priority
- Exit strategies: one-click unwind all positions

TECH STACK:
- Solana: @solana/web3.js, Anchor framework
- Protocols: Kamino SDK, Solend SDK, Marinade SDK, Jupiter API
- Data: DefiLlama API (APY data), Birdeye (price feeds)
- Execution: Custom bot with MEV protection
- Backend: Python + PostgreSQL
- Frontend: Next.js + Tailwind + Recharts
- Wallet: Phantom/Solflare integration
- Notifications: Telegram bot alerts

TARGET: DeFi users with $10K+ in crypto, passive income seekers, busy professionals

PRICING:
- Free: manual strategy builder + APY dashboard
- Auto: 0.5% annual fee on managed assets (AUM model)
- Pro: $99/month (custom strategies, priority support)

RISK DISCLOSURES:
- Smart contract risk (protocols could be hacked)
- Impermanent loss for LP positions
- Token price volatility
- Not financial advice

SUCCESS CRITERIA:
- Bot maintains positive yield over 90 days
- Auto-compounding saves user 5+ hours/week
- Impermanent loss alerts prevent 2+ bad LP entries
- No funds lost to smart contract exploits
