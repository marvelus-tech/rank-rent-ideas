# Task: Solana Trading Bot — Stage 1 MVP

**Assigned:** 2026-03-24 (Queue after Emojournal)  
**Priority:** P1  
**Estimated Hours:** 4-6  
**Due:** Next available Night Owl slot after Emojournal completion

---

## Overview

Build a Solana trading bot MVP that can monitor token prices, execute basic trades, and implement simple strategies. Start minimal — prove the infrastructure works before adding complexity.

**Goal:** Functional bot that can paper trade or execute small real trades with basic strategy.

---

## Tech Stack

- **Language:** TypeScript/Node.js (or Python if preferred)
- **Blockchain:** Solana (mainnet + devnet for testing)
- **SDK:** @solana/web3.js, @raydium-io/raydium-sdk (or Jupiter SDK for swaps)
- **Price Data:** Jupiter API, Birdeye API, or DEX Screener
- **Wallet:** Keypair from environment (never hardcode)
- **Storage:** SQLite or JSON for trade history

---

## Stage 1 MVP Features

### 1. Wallet Integration
- [ ] Load wallet from private key (environment variable)
- [ ] Check SOL balance
- [ ] Display wallet address and balances

### 2. Price Monitoring
- [ ] Fetch token prices (SOL, select memecoins)
- [ ] Track price changes (1min, 5min, 15min intervals)
- [ ] Log price data to file/DB

### 3. Basic Trading
- [ ] Connect to Jupiter aggregator for swaps
- [ ] Execute buy order (specify token, amount)
- [ ] Execute sell order (specify token, percentage)
- [ ] Calculate slippage and fees

### 4. Simple Strategy (Choose One)

**Option A: Dollar-Cost Average (DCA)**
- Buy $X worth of token Y every Z hours
- Configurable: amount, token, interval

**Option B: Momentum**
- If price up 5% in 15min → consider buy
- If price down 5% from entry → sell (stop loss)

**Option C: Arbitrage (Simple)**
- Monitor price difference between Raydium and Orca
- Execute if spread > 1% (minus fees)

### 5. Safety & Logging
- [ ] Paper trading mode (simulate, don't execute)
- [ ] Real trading mode (with confirmation prompts)
- [ ] Log all trades: timestamp, token, amount, price, tx hash
- [ ] Max loss protection (daily/weekly limits)
- [ ] Stop-loss functionality

### 6. CLI / Simple UI
- [ ] Command line interface OR
- [ ] Basic web dashboard (show balance, active trades, history)
- [ ] Config file for strategies

---

## Architecture

```
solana-trader/
├── config/
│   ├── config.json              # Strategy params
│   └── tokens.json              # Watched tokens
├── src/
│   ├── index.ts                 # Entry point
│   ├── wallet/
│   │   └── wallet.ts            # Keypair, balance
│   ├── price/
│   │   └── priceFeed.ts         # Jupiter/Birdeye APIs
│   ├── dex/
│   │   └── jupiter.ts           # Swap execution
│   ├── strategies/
│   │   ├── dca.ts               # DCA strategy
│   │   ├── momentum.ts          # Momentum strategy
│   │   └── index.ts             # Strategy runner
│   ├── trades/
│   │   ├── executor.ts          # Trade execution
│   │   └── logger.ts            # Trade history
│   └── utils/
│       └── logger.ts            # App logging
├── data/
│   └── trades.db                # SQLite trade history
├── .env.example                 # Environment template
├── package.json
└── tsconfig.json
```

---

## Environment Variables

```bash
# .env
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
# Or Helius/QuickNode for better reliability

PRIVATE_KEY=base58_encoded_private_key_here
# NEVER commit this

JUPITER_API_URL=https://quote-api.jup.ag/v6
BIRDEYE_API_KEY=optional_for_premium_data

TRADING_MODE=paper  # 'paper' or 'live'
MAX_DAILY_LOSS_SOL=0.5  # Stop trading if down 0.5 SOL
```

---

## Example Usage

```bash
# Install
npm install

# Configure
cp .env.example .env
# Edit .env with your keys

# Run paper trading
npm run trade -- --strategy=dca --mode=paper

# Check balances
npm run balance

# View trade history
npm run history
```

---

## Risk Management (Critical)

**Hardcoded Limits:**
- Max 1 SOL per trade (configurable)
- Max 5 SOL per day
- Stop if 3 consecutive losses
- Only trade tokens with $100K+ liquidity

**Never:**
- Trade entire wallet
- Chase pumps (FOMO protection)
- Ignore slippage warnings
- Run without testing on devnet first

---

## Testing Strategy

1. **Devnet first** — Test all functions with fake SOL
2. **Paper trading** — Run 48 hours simulated
3. **Small live test** — $5-10 real trades
4. **Scale up** — Only after profitable paper trading

---

## Acceptance Criteria

- [ ] Can check wallet balance
- [ ] Can fetch real token prices
- [ ] Can execute swap on Jupiter (paper mode)
- [ ] At least one strategy implemented (DCA or momentum)
- [ ] All trades logged with timestamps
- [ ] Safety limits enforced (max loss, position sizing)
- [ ] Works on devnet for testing
- [ ] README with setup and usage instructions

---

## Future Upgrades (Stage 2)

- Multiple strategies running simultaneously
- Telegram/Discord alerts for trades
- Portfolio tracking (PnL over time)
- Advanced strategies (grid trading, mean reversion)
- Copy-trading (follow whale wallets)
- MEV protection
- Integration with Mission Control dashboard

---

## Context

Okeito is:
- Solana-focused for crypto
- Looking for passive income streams
- Interested in small-cap plays and hold-to-earn tokens
- Technical (can review and modify bot code)

**This bot is educational + potential profit tool.** Start small, prove it works, then scale.

---

## Resources

- **Jupiter SDK:** https://docs.jup.ag/
- **Solana Web3.js:** https://solana-labs.github.io/solana-web3.js/
- **Birdeye API:** https://docs.birdeye.so/
- **Raydium SDK:** https://github.com/raydium-io/raydium-sdk
- **Helius (RPC):** https://helius.xyz/

---

## Deliverables

1. Working TypeScript/Node.js bot
2. README with setup instructions
3. Config examples
4. Trade history showing test trades
5. Notes on what worked vs. what didn't
