=== TRADING AGENT CRYPTO — Build Prompt ===

Build an AI-powered crypto trading bot with multiple strategies and risk controls.

PRODUCT: TradeMind — "AI that trades while you sleep"

CORE FEATURES:
- Strategy library:
  * Momentum: breakouts, trend following, moving average crossovers
  * Mean reversion: RSI, Bollinger Bands, statistical arbitrage
  * Arbitrage: price differences across DEXs/CEXs
  * Sentiment: Twitter/Reddit/news sentiment triggers
  * On-chain: whale movements, exchange flows, wallet clustering
- Risk management:
  * Max position size per trade (default: 5% of portfolio)
  * Stop-loss and take-profit orders
  * Daily loss limits (stop trading after -X%)
  * Circuit breakers for extreme volatility
  * Whitelist/blacklist tokens
- Paper trading: test strategies with fake money first
- Backtesting: run strategies on historical data
- Portfolio rebalancing: auto-adjust allocations
- Tax reporting: export transaction history for tax software
- Alerts: manual override opportunities, performance summaries

TECH STACK:
- Exchanges: CCXT library (unified API for Binance, Coinbase, Kraken, etc.)
- Solana: Jupiter API, Raydium SDK
- Data: CoinGecko (prices), DefiLlama (protocol data), TheBlock (news)
- Sentiment: Twitter/X API, Reddit API + custom NLP
- On-chain: Helius RPC, Birdeye
- ML: Scikit-learn or TensorFlow for price prediction
- Backend: Python (FastAPI) + PostgreSQL
- Frontend: Next.js + Tailwind + Recharts
- Execution: Self-custody (wallet) or exchange API keys

TARGET: Retail traders ($50-200/month), pro traders (performance fee model)

PRICING:
- Basic: $49/month (2 strategies, paper trading)
- Pro: $149/month (all strategies, live trading, backtesting)
- Performance: 10% of profits (no monthly fee)

SUCCESS CRITERIA:
- Paper trading shows positive returns over 30 days
- First live trade executed successfully
- Risk controls prevent catastrophic losses
- User can understand why bot made each trade
