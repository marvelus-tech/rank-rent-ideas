# MirrorSniper

Solana copy trading bot with signal detection, paper trading, risk controls, and live trading infrastructure.

## Current Status

- ✅ Phase 1: Foundation + database + config + CLI
- ✅ Phase 2: Helius monitoring + transaction decode
- ✅ Phase 3: Paper trading + risk engine + orchestration
- ✅ Phase 4: Live trading infrastructure (implemented, **disabled by default**)

## Phase 4: Live Trading (Ready but Disabled)

Live trading infrastructure is fully implemented but **disabled by default**.

### To Enable Live Trading

1. **Set up wallet:**
   ```bash
   # Add to .env
   TRADING_WALLET_PRIVATE_KEY=your_private_key_here
   ```

2. **Verify wallet has SOL:**
   ```bash
   python -m mirror_sniper wallet-balance
   ```

3. **Test with dry-run:**
   ```bash
   python -m mirror_sniper live --dry-run
   ```

4. **Enable live mode:**
   Edit `config/settings.yaml`:
   ```yaml
   trading:
     execution_mode: "live"
   ```

5. **Start trading:**
   ```bash
   python -m mirror_sniper run
   ```

### Safety Features

- All transactions simulated before sending
- Configurable max slippage (default 1%)
- Kill switch: `python -m mirror_sniper kill-switch`
- Daily loss limits enforced
- Emergency stop on RPC failures

## CLI usage

```bash
mirror-sniper setup
mirror-sniper add-wallet <address> <nickname>
mirror-sniper analyze <address>
mirror-sniper run
mirror-sniper paper-report
mirror-sniper live --dry-run
mirror-sniper kill-switch
```
