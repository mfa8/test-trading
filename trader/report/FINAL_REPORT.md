# T2X v2.1 — FINAL REPORT (RP-6)
Campaign 2026-08-14 -> 2026-08-28 | Account ****8334 ("Agentic") | Outcome: **EXPIRED**

## Outcome
- END_DATE 2026-08-28 reached at 15:50 ET flat. Barrier $201 never touched (HWM $102.22, 8/21). Kill $50 never approached (min equity $98.75, final session).
- **Final equity $98.75** vs $100.00 start: **-$1.25 (-1.25%)** over 11 trading sessions.
- The manual's own install-time math put P(touch $201 in 10 sessions) at ~1-2%. The realized path was consistent with the base case: a near-flat grind, killed by the carry engine (S3) never once arming.

## Equity curve (EOD)
100.00 -> 100.26 (8/14) -> 100.20 (W1) -> 101.55 (8/19) -> 100.20 (8/20) -> 102.20 (8/21, HWM intraday 102.22) -> 101.41 (8/24) -> 101.29 (8/25) -> 99.91 (8/26) -> 99.91 (8/27) -> 98.75 (8/28 final)

## All trades (9)
| id | date | sym | setup | entry | exit | kind | R |
|---|---|---|---|---|---|---|---|
| T2X-001 | 08-17 | SOXS | S1 | 38.95 | +0.26R | time | +0.26 |
| T2X-002 | 08-18 | MUU | S1 | 31.31 | -0.24R | invalid | -0.24 |
| T2X-003 | 08-18 | SOXS | S1 | 43.85 | +0.66R | invalid(+) | +0.66 |
| T2X-004 | 08-19 | SOXS | S1 | 43.60 | -0.69R | invalid | -0.69 |
| T2X-005 | 08-21 | SOXS | S1 | 45.31 | +0.65R | invalid(+) | +0.65 |
| T2X-006 | 08-24 | SOXS | S1 | 51.76 | 50.9701 | time | -0.29 |
| T2X-007 | 08-25 | SOXS | S1 | 48.2699 | 48.2121 | time | -0.03 |
| T2X-008 | 08-26 | SOXS | S1 | 49.14 | 48.4515 | invalid | -0.52 |
| T2X-009 | 08-28 | MUU | S1V(JH) | 29.9199 | 28.7622 | STOP | -0.93 |
Sum: **-1.13R** | 3W / 5L / 1 scratch | avg win +0.52R, avg loss -0.53R | no-trade days: 8/20 (missed by late wake), 8/27 (variant filtered NVDA gap-fade — correct)

## Weekly
- WEEK-1 (8/14-8/21): +0.20% -> 100.20 (report WEEK-1.md)
- WEEK-2 (8/18-8/21 file WEEK-2.md): -> 102.20 (+2.0%)
- WEEK-3 (8/24-8/28): 102.20 -> 98.75 (**-3.38%**), 4 trades 0W-3L-1S, -1.77R — the losing week that ended the campaign at a small net loss

## Why it expired (mechanics, not luck)
1. **S3 carry never armed once.** The compounding engine required SOXS close > SMA20 on an unblocked night. The flip finally came 8/25 — the first of three consecutive hard-blocked nights before END_DATE. Without carries, per-trade R was capped at ~2-4% of E and the barrier needed ~10%/session.
2. Intraday S1/S2 was roughly a coin flip at 0.5R median magnitude, exactly as the manual models: 9 trades netted -1.13R (~-2.9% gross of E) against +1.7% from the three winners' days.
3. Every loss was contained: worst single trade -0.93R (-1.16% of E). Z-5/Z-6 floors never breached; DAY_HALT never hit; KILL never within 48 points.

## Execution quality (broker/ops)
- 9 entries: all marketable-limit, all filled at-or-better than limit (avg improvement $0.12/sh). Zero rejects across ~40 orders.
- Native GTC stop protection resting 100% of in-position time; 13 cancel-confirm-replace trail rotations, INV-9 never violated (never two live sells).
- One native stop fill in the whole campaign (T2X-009, 8/28) — slippage +$0.002 FAVORABLE. All other exits rule-driven limits.
- INV-12 intent line preceded every order (orders.jsonl complete).
- Zero missed trading boundaries across ~360 scheduled evaluations (bridged in-turn against a 1-min-floor scheduler with -2..+15 min delivery jitter); ~90 duplicate wakes absorbed; 3 worker restarts and 4 backgrounded sleeps recovered without a missed checkpoint; 1 known miss (8/20 12:00 late one-shot, W-7 forbade stale action) — cost the campaign its best S2 setup and produced ops-8.
- Account isolation: 100% of orders on ****8334; ****3273 never touched; no transfers ever initiated.

## Verdict
The system executed its manual essentially perfectly for 11 sessions; the strategy's own edge assumptions (nightly leveraged carries compounding at 6.5%/session) never got the regime they needed. -1.25% total cost for a full live test of a ~50x-target lottery structure is the expected price of the ticket.

## State
mode DONE | routines to retire: t2x-analyst, t2x-wake-a, t2x-wake-b (+ spent one-shots) | account left 100% cash, no open orders
