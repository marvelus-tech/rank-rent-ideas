## Handoff: Solana Daily Scout — New Hold-to-Earn Tokens Found
**From:** Solana Scout Agent (Cron Run)
**To:** Main Session / Okeito
**Dispatched:** 2026-05-28 09:32 AEDT
**Priority:** Medium

### Task
Find 3–5 NEW Solana small-cap tokens (under $100M market cap) with hold-to-earn mechanics similar to solcard.cc, not already tracked in the scout database.

### Context
- Daily scout run for Solana ecosystem.
- Database checked: `memory/scout-findings/database.md` — none of the 4 tokens below were previously tracked.
- Reference token: solcard.cc
- Search sources: CoinMarketCap, CoinGecko, OKX, official docs, web search.

### Inputs
- Database: `memory/scout-findings/database.md`
- Briefing: `agents/solana-scout.md`

### Expected Output
Report new tokens with: name, ticker, market cap, description, reward mechanic, links, and confidence (0–100).

### Return To
- Report: `memory/scout-findings/2026-05-28-daily-scout.md`
- Database update: append to `memory/scout-findings/database.md`

### Evidence Required
All tokens verified via multiple sources, market caps confirmed under $100M, and reward mechanics documented.

---

## New Tokens Found (4 total)

### 1. Jelly-My-Jelly (JELLYJELLY)
- **Market Cap:** ~$51–57M
- **Description:** Video-chat clipping platform and viral meme token on Solana. Built around “Jelly” meme culture with social/viral mechanics.
- **Reward Mechanic:** Staking available on Biconomy, Gate.io, and others at ~25% APR. Higher APYs (up to 624%) appear on Jupiter liquidity-mining pools, but standard locked staking sits around 25%.
- **Links:**
  - https://coinmarketcap.com/currencies/jelly-my-jelly/
  - https://www.coinbase.com/price/solana-jelly-my-jelly
  - https://thecoinearn.com/coins/jelly-my-jelly/staking/
- **Confidence:** 70

### 2. Zama (ZAMA)
- **Market Cap:** ~$61–76M (CMC ~$69M, OKX ~$75.8M, Phemex ~$61.5M)
- **Description:** Cross-chain confidentiality protocol using Fully Homomorphic Encryption (FHE). Sits as a privacy layer on top of existing chains, not a new L1/L2. Backed by $130M in funding and a 90-person research team.
- **Reward Mechanic:** Burn-and-mint tokenomics — 100% of protocol fees are burned, while ~5% annual inflation mints rewards for stakers. Operators must stake ZAMA to run protocol nodes (sequencers, coprocessors, KMS). Over 34% of circulating supply was staked as of late February 2026. Rewards split by role, then distributed pro-rata.
- **Links:**
  - https://coinmarketcap.com/currencies/zama/
  - https://staking.zama.org/
  - https://www.coingecko.com/en/coins/zama
  - https://phemex.com/blogs/zama-price-prediction-2026-2031
- **Confidence:** 85

### 3. AI Rig Complex (ARC)
- **Market Cap:** ~$63–67M (TokenRadar $63.9M, CryptoSlate $66.83M)
- **Description:** Open-source, modular AI-agent framework built on Solana (Rust-based). Provides high-performance compute for AI training via DePIN. ARC Forge is a curated token launchpad for AI projects.
- **Reward Mechanic:** ARC can be staked to earn ecosystem rewards. Token serves as the base fee for projects launched within the ecosystem. Prize pool & treasury allocation (5.5%) incentivizes active participation and contributor rewards.
- **Links:**
  - https://coinmarketcap.com/currencies/ai-rig-complex/
  - https://www.arc.fun/tokenomics
  - https://www.coingecko.com/en/coins/ai-rig-complex
  - https://web3.bitget.com/en/dapp/ai-rig-complex-24801
- **Confidence:** 75

### 4. RedStone (RED)
- **Market Cap:** ~$52–56M (CMC $51.97M, Bybit $52.64M, CryptoSlate $55.57M)
- **Description:** Modular blockchain oracle delivering price feeds, NAV data, Proof of Reserve, and risk ratings to DeFi and institutional finance. Recently expanded into RWA infrastructure with RedStone Settle ($30B+ tokenized asset target). RED is an ERC-20 also available on Solana.
- **Reward Mechanic:** RED can be staked by data providers and by token holders. Token holders enhance network security through direct staking in RedStone’s EigenLayer AVS. Note: staking rewards are currently inflationary (new RED minted), not fee/revenue share.
- **Links:**
  - https://coinmarketcap.com/currencies/redstone/
  - https://blog.redstone.finance/2025/03/05/red-staking/
  - https://www.coingecko.com/en/coins/redstone-oracles
  - https://www.binance.com/research/projects/redstone
- **Confidence:** 80

---

## Notes & Caveats
- **JELLYJELLY:** Very high APY figures (624%) on some platforms are liquidity-mining yields, not sustainable staking. Standard exchange staking is ~25%.
- **ZAMA:** Strong fundamentals (FHE tech, $130M raised, Binance listing). 5% inflation is moderate.
- **ARC:** AI-agent sector is hot; staking mechanics are newer and less battle-tested.
- **RED:** Inflationary staking rewards (not revenue share) means dilution risk. Strong oracle fundamentals with $10B+ TVS secured.

---

*End of report.*
