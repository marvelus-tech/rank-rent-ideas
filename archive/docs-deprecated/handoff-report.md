# Handoff: Solana Daily Scout Results
**From:** Solana Scout Sub-Agent
**To:** Penelopi (Main Session)
**Dispatched:** Thursday, May 7th, 2026 - 15:45 (Australia/Melbourne)
**Priority:** Medium

### Task
Deliver findings for 3-5 Solana small-cap tokens (under $100M market cap) with hold-to-earn/revenue-sharing mechanics.

### Context
Scout run for Okeito's Solana strategy. Benchmark: solcard.cc. Database checked for duplicates.

### Inputs
- `agents/solana-scout.md`
- `memory/scout-findings/database.md`
- Web search data (May 7, 2026)

### Expected Output
Report in `templates/handoff.md` format.

---

## Handoff: Solana Daily Scout Findings
**From:** Solana Scout Agent
**To:** Penelopi
**Dispatched:** 2026-05-07 15:45
**Priority:** Medium

### Task
Report 3-5 NEW Solana small-cap tokens with hold-to-earn/revenue-sharing mechanics.

### Context
This run focused on identifying projects with sustainable revenue models or automated reward distributions, specifically looking for mechanics similar to SolCard (revenue share) or RRS (automated rebates).

### Inputs
- Tracked Tokens database
- Real-time DexScreener/GeckoTerminal data
- Official project docs

### Expected Output
Token list with ticker, market cap, mechanic, and confidence.

### Return To
Okeito via Main Session.

### Evidence Required
Updated `memory/scout-findings/database.md`.

---

## Scout Findings: NEW Tokens Found

### 1. DefiTuna ($TUNA)
- **Market Cap:** ~$3.52M (Small Cap)
- **Description:** Advanced AMM on Solana integrating concentrated liquidity, lending, and leverage.
- **Reward Mechanic:** Staking $TUNA grants holders a share of protocol revenue (swap fees, lending interest). The treasury also stakes to align incentives.
- **Why it's interesting:** High TVL potential for its cap and clear value accrual model directly from DEX activity.
- **Links:** [Official Docs](https://docs.defituna.com/tuna/tokenomics), [Jup Verified](https://verified.jup.ag/dashboard/TUNAfXDZEdQizTMTh3uEvNvYqJmqFHZbEJt8joP4cyx)
- **Confidence:** 95/100

### 2. Revenue Rebate Service ($RRS)
- **Market Cap:** ~$4.44K (Micro Cap / High Risk)
- **Description:** Automated rebate protocol on Solana.
- **Reward Mechanic:** Randomly disburses SOL rebates to $RRS holders every two hours using Orao VRF for verifiable randomness.
- **Why it's interesting:** Purely passive "hold to earn" mechanic with automated on-chain disbursements.
- **Links:** [Website](https://www.revenuerebateservice.com/), [GeckoTerminal](https://www.geckoterminal.com/solana/pools/4rG45mqg5YLWQXDiMCKamUvnWuzx1Jk46vsJbS9Txdut)
- **Confidence:** 85/100 (Mechanic is solid, market cap is extremely low/volatile)

### 3. PocketSol ($BALL)
- **Market Cap:** ~$66.1K (Micro Cap)
- **Description:** Web3-integrated 8-ball pool game with a competitive reward loop.
- **Reward Mechanic:** Holders of $BALL/NFTs participate in a weekly competitive reward loop funded by in-game SOL fees. Active players can also earn USDC rewards.
- **Why it's interesting:** GameFi project with a functional revenue loop from player fees being funneled back to the reward pool.
- **Links:** [Website](https://www.pocketsol.fun/), [X/Twitter](https://x.com/Pocket_SOL)
- **Confidence:** 80/100

### 4. DEPINfer ($DEPIN)
- **Market Cap:** ~$17.7K (Micro Cap)
- **Description:** Decentralized GPU-sharing infrastructure (DePIN) on Solana.
- **Reward Mechanic:** Marketplace utility token used for node rewards and marketplace payments. Holders gain priority for early participation in new custom and reward token launches.
- **Why it's interesting:** Capitalizes on the AI infrastructure narrative on Solana with a direct link between compute usage and token utility.
- **Links:** [X/Twitter](https://x.com/DEPINfer_DEPIN), [Prism Media Wire](https://prismmediawire.com/tianrong-internet-products-and-services-inc-otc-tips-announces-beta-launch-of-depinfer-website-cloud-based-gpu-compute-sharing-platform-powered-by-depin-token-on-solana/)
- **Confidence:** 75/100

### 5. Solana ID ($SOLID)
- **Market Cap:** ~$407K (Small Cap)
- **Description:** Decentralized identity layer (DID) for the Solana ecosystem.
- **Reward Mechanic:** Holders of $SOLID (and Priority Pass NFTs) unlock "Personal Perks On-Chain," including airdrops from partners, discounts, and exclusive offers.
- **Why it's interesting:** Backed by the Solana Foundation; functions as a "loyalty card" for the entire ecosystem.
- **Links:** [Website](https://www.solana.id/), [Priority Pass](https://pass.solana.id/)
- **Confidence:** 90/100

---

### Update Log: Duplicate Check
The following tokens were found but **SKIPPED** as they are already tracked in the database:
- **Meteora ($MET)** (Already tracked, MC ~$85M)
- **Sallar ($ALL)** (Already tracked, MC ~$1.1M)
- **Subway Market ($SUBWAY)** (Already tracked)
- **Tensor ($TNSR)** (Already tracked)
- **Drift Protocol ($DRIFT)** (Already tracked)
