=== IN-NEED — Build Prompt ===

Build a direct crypto donation platform for homeless individuals.

PRODUCT: InNeed — "Direct help, zero overhead"

CORE FEATURES:
- Recipient onboarding: homeless individuals receive pre-configured smartphone + wallet
- QR code system: each person has unique QR code (card, sign, or phone display)
- Donor flow: scan QR → pay with card/Apple Pay/crypto → auto-convert to USDC/SOL
- Wallet: embedded Solana wallet (no seed phrase management needed)
- Spending: Solcard or similar crypto debit card for real-world purchases
- Transparency: donors see how funds were spent (optional)
- Safety: daily spending limits, merchant restrictions, fraud detection
- Partner network: pre-approved merchants (grocery, pharmacy, transit)

TECH STACK:
- Blockchain: Solana (low fees, fast finality)
- Wallet: Squads or Coinbase Embedded Wallets (custodial option)
- Payments: Stripe (fiat on-ramp), Coinbase Commerce (crypto)
- Swaps: Jupiter API for auto-conversion to USDC
- Card: Solcard.cc or Raincard integration
- Backend: Node.js + PostgreSQL
- Frontend: Next.js + Tailwind (mobile-first)
- KYC: Light verification for recipients, compliance for donors

TARGET: Homeless individuals, social workers, donors who want direct impact

PARTNERSHIPS NEEDED:
- Local shelters for distribution
- Merchants for acceptance network
- Social services for recipient support

SUCCESS CRITERIA:
- 50+ recipients onboarded in first 90 days
- $10K+ in donations processed
- 80%+ funds successfully converted to real-world purchases
- 0 fraud incidents
