# Autonomous Swing-Trading Harness

Autonomous swing-trading experiment run by Claude via the Robinhood agentic MCP.

## Hard rules (never violated)

1. Trade ONLY the "Agentic" account ending **8334**. The account ending 3273 is
   never touched — read-only, agentic-blocked, absolute rule.
2. Never initiate transfers or funding. Owner funds manually.
3. Stocks/ETFs only. No options.

## Experiment parameters

- Bankroll: $100 (owner-funded). Goal: $200.
- Explicitly high-risk / experimental. Concentrated positions allowed
  (1–2 positions at a time given the bankroll size).
- Style: swing trading — holding periods of ~1–10 sessions, not day-scalping.

## Operating loop

- **Pre-market prep** (9:00 ET weekdays): check funding/cash, open positions,
  overnight news on holdings, earnings calendar; plan the day's actions.
- **Market-hours scan** (hourly 9:30–15:30 ET weekdays): scan for setups,
  manage open positions, place/adjust entries and exits.
- Every open position gets a resting GTC stop-loss on the broker side
  immediately after entry, so downside is protected between wake-ups.
- Journal every decision in `JOURNAL.md`; machine state in `state.json`.

## Playbook (initial — will evolve)

- Entries: momentum/pullback setups on liquid stocks & ETFs. Prefer names
  under ~$60 so a $100 bankroll can take whole or meaningful fractional shares.
  Signals: trend (price vs 20/50 SMA), RSI reset within uptrend, volume
  confirmation, proximity to support; catalyst-aware (earnings dates checked
  before entry — no holding through earnings unless deliberately chosen and
  journaled).
- Position sizing: 50–100% of bankroll per position (concentration accepted
  per owner's mandate).
- Exits: initial stop ~5–8% below entry (GTC stop order at broker), first
  target ~+8–15%; trail or scale out on strength. Cut losers, let winners run.
- Orders: marketable limit orders for entries during regular hours; avoid
  market orders in extended hours; fractional shares via market orders in
  regular hours when needed.

## State files

- `state.json` — machine-readable harness state (bankroll, positions, orders).
- `JOURNAL.md` — human-readable trade journal and decision log, newest first.
