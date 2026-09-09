# T3X v1.0 — OVERNIGHT ENGINE (active manual from 2026-09-09)
Authored by the agent at the human's instruction (2026-09-09: "rethink strategy... come up with another one... never retire the campaign or scheduler"). RULES.md (T2X v2.1) is retired but untouched per N-16. state.json.active_rules points here.

## §0 Wake protocol
Every wake: read state.json first. Phases by ET clock: ANALYST (07:45), EXIT (09:26 -> sell at 09:31), IDLE (all other intraday wakes: verify state, NOOP), ENTRY (15:48 -> buy at 15:52), EOD (16:05 report). Hard rules unchanged: trade ONLY ****8334; never ****3273; never transfers; stocks/ETFs only. Never retire the campaign or the scheduler (human, 2026-09-09).

## §1 Thesis (evidence, 62 sessions to 2026-09-08)
Leveraged-long tech/semis ETFs earn their return overnight and lose it intraday: SOXL total -31.8% = overnight +34.6% / intraday -78.6%; NVDL +19% = +34.5% / -21.1%; MUU -4% = +33% / -40%. Overnight-only NVDL: +41.1%, maxDD -16.9%, win 59%, mean +0.61%/night, worst -6.3%. After a down intraday session the next night averages ~2x better (daily mean-reversion; AC1 negative). Inverse/vol ETFs bleed overnight (SOXS -0.97%/night) — never held. T2X lost because it traded intraday-only longs on exactly these instruments.

## §2 Universe
Affordable (price <= 0.98*E for 1 share) leveraged LONG ETFs/ETNs with avg volume >= 1M and >= 40 nights of history. Seed list: NVDL (2x NVDA), MUU (2x MU), FNGU (3x FANG+), TQQQ (3x NDX), TNA (3x R2K), SPXL/TECL/SOXL when affordable. Excluded permanently overnight: any inverse or volatility product. Excluded by data: TSLL, CONL (negative overnight drift), BITX (negative median) — re-tested weekly.

## §3 Ranking & sizing (Monday ANALYST; daily sanity check)
score = mean(trailing 30 overnight returns close->next open) / stdev; eligible if mean > 0 AND win% >= 50%.
Hold the top 2 eligible DISTINCT underlyings, 1 share each, if both affordable; else 2 shares of #1 if affordable; else 1 share of #1. Target 70-100% of E invested; never > 100% (no margin use). If nothing eligible: cash, keep waking, keep reporting.
Blackout: skip an instrument on the night its underlying reports earnings (MU 2026-09-30 pm; NVDA 2026-11-17 pm); substitute next-ranked name. No other event blackouts (data shows overnight edge survives macro nights; FOMC decisions are intraday).

## §4 Entry (ENTRY wake 15:48)
Bridge to 15:52:00. Per instrument: INV-12 intent line -> marketable LIMIT buy at ask + max(0.02, 0.15%) (<= last*1.004) -> poll fill 6s. Unfilled at 15:55: re-price once to ask + 0.3%. Unfilled at 15:58: cancel, skip the night for that name. Wake arriving after 15:57: skip the night entirely (no chasing the close).

## §5 Exit (EXIT wake 09:26)
Bridge to 09:31:05. Per position: INV-12 intent -> marketable LIMIT sell at bid - max(0.02, 0.15%) -> poll 6s -> unfilled 60s: re-price to bid - 0.3% -> unfilled 60s more: market order. A LATE exit wake (even 10:30+) still exits immediately — holding into the negative intraday drift is the risk, not staleness. No overnight stop orders (gaps make them useless; risk is controlled by §6).

## §6 Risk
E0 = 98.75. KILL: E <= 50 -> flatten, HALT, alert human (hard, unchanged). PAUSE: E <= 0.80 x rolling 20-session high -> size = 1 share of #1 only for 5 sessions, then normal if E > pause trigger. Worst observed single night in sample: -21.9% (MUU) — a 2-name basket at ~85% invested caps a repeat near -10% of E. Expected: +0.3..0.6%/night gross = +6..12%/month with -15..25% drawdowns; $200 is a 6-12 month objective, not a 2-week one.

## §7 Account mechanics
Buy 15:52, sell next 09:31 = NOT a day trade. Limited-margin account: proceeds usable immediately. Whole shares only. Verify 0 open orders after each exit and each entry fill (INV-9: never two live orders per symbol).

## §8 Records
trades.csv (exit_kind "ovn"), orders.jsonl (INV-12), journal.log (W-9 line per acting wake), equity.csv (EOD), report/DAY-*.md, report/WEEK-*.md (Fri), STATUS.md. Weekly: re-rank table + edge-decay check (30-night mean per name).

## §9 Ops (carried from ADAPTATION_RH.md)
Crons: t2x-analyst 11:45Z; t3x-exit-0926 13:26Z; t3x-entry-1548 19:48Z; t2x-wake-a/b hourly backstops. Bridge with <= 9-min sleep chunks; re-check clock after any backgrounded sleep or worker restart; commit+push every state change; absorb duplicate wakes as NOOPs.

## §10 Expansion candidates (need explicit human OK — outside "stocks/ETFs only")
(a) Crypto via Robinhood crypto (24/7; BITX intraday drift was positive; crypto buying power exists). (b) Options — not approved on ****8334.
