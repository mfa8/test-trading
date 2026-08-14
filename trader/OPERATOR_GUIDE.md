# T2X — operator guide (for the human, not the bot)

You have two documents:

- **`T2X_RULES.md`** — the operating manual. Paste it into the trading session as its standing instructions. It is long (≈15k words) on purpose: it is a spec the bot saves to disk and re-reads, not a pep talk. The 25-line mission card at the top is what it re-reads every wake after context compaction.
- **This guide** — how to install it, what to expect, how to intervene, and how to change the odds.

## The honest odds

Numbers below come from two Monte Carlo models the design agents built (a first-passage model of the $100 → $200 / kill $50 game, and a simulation of the manual's actual rule set over the 11 sessions Fri 8/14 → Fri 8/28), cross-checked by the quant red-teamer. They are estimates, not promises.

| Policy over ~10 sessions | P(touch $200) | P(touch $50) | Median finish | P(finish ≥ $150) |
|---|---|---|---|---|
| Buy & hold a normal stock (σ ≈ 2%/day) | ≈ 0% | ≈ 0% | $100 | ≈ 0% |
| Buy & hold TQQQ | ≈ 0% | ≈ 0% | $98 | ≈ 0% |
| Buy & hold SOXL (σ ≈ 11%/day, current regime), no skill | 1.3% | 7% | $90 | ≈ 5% |
| **This manual, zero edge per trade** | 0.5–1% | ≈ 0% | $94–96 | 4–5% |
| **This manual, semis keep trending like late July** | 4–5% | ≈ 0% | $107 | 17% |
| Generic "risk 8% of equity per trade, 1.5 trades/day", modest real edge | 12% | 6% | $103 | ≈ 20% |
| Hypothetical instrument with σ ≈ 22%/day (perps / options territory), no skill | 11% | 47% | $57 | 15% |

Read it this way: **on US stocks with 1× buying power, no rule set gives you a coin-flip at 2× in two weeks — the ceiling is single digits.** The venue caps daily volatility at roughly SOXL's (the most volatile liquid thing you can buy fractionally), and 2× in 10 sessions needs a +100% move. What the manual does is get close to that ceiling while keeping the probability of ever touching your $50 stop near zero, so the realistic distribution is "median roughly flat, 1-in-6 to 1-in-20 chance of a +50% fortnight, a few percent at 2×, almost no chance of −50%." Growth, when it comes, is lumpy: one to three +8–20% days, not a staircase.

I added one deliberate exception to the reviewers' caution — **Z-12, the event shot**: if the account is already ≥ $160 at 15:40 ET on NVDA earnings day (Wed 8/26), it goes all-in on NVDL (2× NVDA) or SOXL/SOXS through the print, because that is the one moment a single move can actually touch $200 while the worst case (≈ $105) stays nowhere near $50. It is worth roughly +1–2 points of P(2×). Toggle: `state.json → campaign.event_shot` (default `true`), threshold `event_shot_min_equity` (default 160; set 999 to disable, lower it if you would rather gamble gains than bank them).

### If you want materially better odds at 2× (the venue dial)

- **Same manual, longer runway.** Edit `campaign.END_DATE` to late September. With even a modest edge, P(2×) climbs into the 10–25% range because compounding gets time to work; the kill line stays protected.
- **Leverage venue.** Crypto perps at 3–5× or long options can put P(2× in 2 weeks) at 30–45% — with P(−50%) at 40–55%. That is a different manual (funding, liquidation math, 24/7 phases); say the word and I will produce it.
- **Don't** reach for penny-stock gappers: they have the variance but halt, gap and spread through any stop a 1-minute polling loop can run.

## Install checklist

1. **Broker.** Alpaca live account is what the manual's field names assume (it adapts to others at boot). Fund $100 and let the ACH **settle** first — a pending deposit makes it halt at boot by design. Enable fractional trading and extended hours; if the app asks you to acknowledge a leveraged/inverse-ETF disclosure, accept it now (the bot cannot click it).
2. **MCP.** Alpaca's MCP server with **live** keys. The bot needs tools for: account, positions, assets, clock/calendar, place / replace / cancel / list orders + get-order-by-client-id, snapshots / latest trade / latest quote / bars, account activities; news is optional. If any of "place order" or "quotes/bars" is missing it halts at boot and tells you.
3. **Session.** Give it a working directory it can write to (it creates `trader/`). First message: paste `T2X_RULES.md` in full, followed by one line: *"Save this verbatim as trader/RULES.md and begin WAKE-0 now."* The recurring wake prompt should be short and constant, e.g. *"T2X wake — follow trader/RULES.md §0: read trader/state.json first."* Do not add commentary to wake prompts; it treats extra text as data, but why tempt it.
4. **Cadence and cost.** One-minute wakes are what the manual is built for; its fast path makes off-hours wakes zero broker calls. Each wake still costs model tokens (a no-op wake is roughly 2–6k tokens; 1,440 wakes/day). If your scheduler allows it, run every minute 04:00–20:00 ET Mon–Fri and every 15 minutes otherwise. **Never point two sessions or two schedulers at the same account.**
5. **When to start.** Any evening or before 08:00 ET: boot's read-only discovery and the pre-market Analyst run before the open, the $1–3 order-type probes run 09:31–09:38 ET (≤ $0.10 cost), and the first real entry is possible from the 09:45 ET checkpoint. Started mid-session, it finishes probes and trades from the next checkpoint with the opening-range setup skipped that day.
6. **Paper dry-run (optional, one session recommended).** The manual halts if it detects a paper account ("this is supposed to be real money"). To allow a rehearsal, create `trader/HUMAN_GO` containing `GO`. When you switch to live keys, delete the whole `trader/` directory so it boots fresh.

## Controls while it runs

| You want to… | Do this |
|---|---|
| Stop everything now | Create the file `trader/HUMAN_STOP`. It cancels orders, sells at the next open-market wake (never a blind market order into a closed market), writes `FINAL_REPORT.md`, goes DONE. Then disable the scheduler. |
| See what it's doing | `trader/STATUS.md` (≤ 15 lines, always current), `trader/ALERT.md` (things that want you), `trader/report/DAY-YYYYMMDD.md` (end of day), `trader/BOOT_REPORT.md` (day 1), `trader/journal.log` (every action, one line each). |
| Un-stick a boot halt | Fix the condition it names (unsettled deposit, blocked flag, missing tool) — it re-probes every 30 min — or create `trader/HUMAN_GO` containing `GO`. |
| Give it a fact | Write it in `trader/HUMAN_NOTE` (e.g. `margin`, or `NVDA moved earnings to 8/27`). Read every pre-market. |
| Extend the deadline | Edit `trader/state.json → campaign.END_DATE` (YYYY-MM-DD) before 15:50 ET on the current end date. Default: Fri 2026-08-28, flatten 15:50. |
| Change the kill line | `campaign.kill` (default 50.0 = your −50%). Note it deliberately stops taking meaningful risk below ≈ $57 (PRESERVE) so a string of stop-outs cannot walk it into $50; $50 itself is the backstop for gaps and execution failures. |
| Turn the event shot off/on | `campaign.event_shot`, `campaign.event_shot_min_equity` (see above). |
| Withdraw/deposit mid-run | Fine — it detects transfers and measures the target on adjusted equity, but it will alert you that the experiment's accounting changed. |

## What a normal day looks like

- 08:00–09:30 ET: one Analyst pass writes `plan-YYYYMMDD.md` (levels, sizes, which setups are on, tonight's blocks). Nothing not in that file gets traded.
- 09:30–09:40: records the opening range; no orders (except re-arming the stop on a carried position at 09:31).
- 09:40–10:30: opening-range breakout may fire on a 5-minute close (SOXL/SOXS primary, TQQQ/SQQQ fallback), full notional, stop 3.6–6% below on SOXL (≈ 3.5–6% of equity at risk).
- 10:00–14:30: continuation setup checked only at :00/:30; otherwise it manages the stop and heartbeats every 15 min.
- 15:30: late-day momentum entry for an overnight carry may fire; 15:50: hold-or-flatten decision for anything open; nothing is sent 15:59–16:00:30.
- 16:10: end-of-day report. Overnight: near-silent unless holding.
- Expect 0–1 entries most days (cap 2/day, 7/week, 14/campaign), a 60-minute cooldown after a loss, and a day halt after 2 losses or −10%.

## Assumptions baked in on 2026-08-13 (it re-verifies, but you should know)

- The FINRA pattern-day-trader rule was replaced by the intraday-margin standard effective 2026-06-04 and Alpaca/Robinhood/Webull/IBKR/Fidelity/Schwab have migrated, so a $100 1× account has no 3-round-trips-per-week cap. The manual still detects and obeys legacy PDT or cash-account settlement if the broker shows either.
- Alpaca free data = IEX real-time (thin) + SIP delayed 15 min; fractional orders are day-only (stops expire 16:00 and are re-armed 09:31); Alpaca "limited margin" accounts under $2k reuse sale proceeds instantly.
- Calendar: no market holidays before Labor Day (Mon 9/7); opex Fri 8/21; FOMC minutes Wed 8/19 14:00; GDP/PCE Wed 8/26 08:30; NVDA earnings Wed 8/26 after close; Jackson Hole keynote Fri 8/28 ≈ 10:00. Regime snapshot: SPX at a record, VIX ≈ 14.5, semis extremely volatile (SOXL ATR ≈ 12%/day). If semis calm down (SOXL ATR < 7.5%) it falls back to TQQQ/SQQQ and tells you the 2× target is effectively out of reach.

## Provenance

Built 2026-08-13/14 by a 19-agent design tournament: six web-verified research briefs (rules, broker/MCP mechanics, instrument universe, documented intraday edges, the two-week catalyst calendar, lessons from live LLM-trading experiments), five competing designs (systematic index-leverage, catalyst hunter, barrier optimizer, agent-operations architect, relative-strength swing), three judges (prop risk manager, ORB-paper quant, LLM-ops engineer — the barrier optimizer won 7.2/10 and became the backbone), a synthesized draft, 92 red-team findings (5 fatal, 52 major — all fatal/major applied), a final edit, and my review pass (added Z-12, this guide). The full dossier is on the published page.
