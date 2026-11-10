# T3X STATUS: Overnight Engine (started 2026-09-09)

**Mode:** IN_POSITION_OVERNIGHT, **PAUSE in force** (as of 16:02 ET Tue 11/10).
- Night 44 closed at 09:31: NVDL 3, 21.5999 → 20.07, and NVDX 1, 12.11 → 11.27: **−5.43 (−7.06%)**. NVDA opened 3.5% lower after a hot inflation report and the continuing CEO-review story.
- **PAUSE triggered.** All cash after the exit was 82.31, under the 82.94 level (80% of the 20-session high). Nights 45–49 (11/10, 11/11, 11/12, 11/13, 11/16) are exactly 1 NVDL share with no top-up, whatever the trend state.
- Night 45 entered at 15:52: NVDL 1 @ 19.2553 (23% of equity). The exit is 09:31:05 Wed 11/11.
- Tue 11/17 is the NVDA earnings night: cash. From Wed 11/18 normal sizing returns only if equity is above 82.89; otherwise PAUSE continues.
- The day leg is SUSPENDED.

**Equity:** 82.41 at the 11/10 close (cash 63.05 + NVDL 1 marked 19.36; 82.40 at the bid).
- Start 98.75. HWM 107.11 (10/12).
- PAUSE level 82.89 from 11/11 to 12/4 (`state.campaign.pause_schedule`).
- KILL 50.

**Campaign:** 44 nights closed, −19.79 (19 wins, 25 losses). Live NVDA-2x-only nights (N25–N44): 20, totalling −23.05.

**Rules changed on 11/9 (v2.1, engine v1.8), on the human's instruction to review the plan and act autonomously:**
- New: the position size follows the market trend (RULES_v3 §13). In force from the night-45 entry on Tue 11/10. Night 44 is not resized.
- New: one symbol (NVDL) with a fractional top-up to the target, replacing the NVDX filler.
- New: a weekly research loop (§14, `LAB.md`, Saturdays 14:23 ET).
- Evidence and every rejected idea: `research/REVIEW-20261109.md`.
- The 11/9 question about holding only 2 NVDL until earnings is closed: on nights when QQQ is below its 200-day average the new rule holds about 1 share anyway.

**Options (v2.0 §12 FFB-L):** PENDING. Account 8334 has no options level. The human applies here (L3 preferred, L2 ok): https://applink.robinhood.com/upgrade_options?account_number=445788334&source=mcp
- The shadow quote log has run since 10/23. The plan is in `research/OPTIONS-PLAN-20261022.md`.
- From 11/9 the R4 shadow uses the Feb-19-2027 contracts. Under §12(c), E at bid was 87.72 at the 11/9 close, so B = min(17.54, 7.72) = 7.72 < 8 and the sleeve sleeps. It wakes once E at bid is ≥ 88.00.

**Thesis (v1.8):** NVDA at 2x earns its return overnight and loses it intraday.
- We hold NVDL from close to open.
- **Size follows the market trend (§13).** At 15:50 we compare QQQ with its 200-day average. At or above it we invest 98% of equity; below it, 25%. Nights below the line are about twice as volatile, and at 2x that volatility eats the compound return. An independent re-check on 11/9 reproduced the numbers and calls the rule insurance, not extra return: nearly all of its historical gain came from ten nights in long bear markets, and in most short dips it loses a little.
- Trend state on 11/9 (provisional closes): QQQ 678.77 against a line at 681.18, 0.35% below → DOWN. That close to the line the state can flip on any day; the 15:50 price on 11/10 decides night 45.
- At equity near $86: DOWN means about $21.50 of NVDL, which is one whole share if it fits under 25% of equity and otherwise a fractional position of just under one share; UP means 3 shares plus about $20 of fractional NVDL.
- Planning edge: +0.30% per night per unit invested.
- §3(f) trailing-120 NVDL check (11/9): +0.363%, t 1.40 → the overnight leg stays on. Next check 11/16.
- The inverse day leg has been SUSPENDED since 10/15. Never hold an inverse product overnight.

**Daily loop (v1.8):**
1. 07:45 analyst check. Add the prior session's official closes to the trend cache (`tools/trend.py add`). If the tool refuses a symbol, fix that symbol; QQQ is the one that matters.
2. 09:25 and 09:29 shadow quotes.
3. Sell at 09:31:05: whole shares by limit order, then any fractional remainder by market order.
4. Always-on 8-minute scans with hourly heartbeats.
5. Sleeve shadow at 10:30, 13:00 and 15:25.
6. 15:40 pre-entry check, journaled.
7. 15:50 trend state (`tools/trend.py state ... --log`; 12:50 on a half-day). Exit code 2 means no valid state: follow the printed repair, else size DOWN.
8. Buy at 15:52 (`tools/entry_v18.py`): whole NVDL shares by limit order, then one dollar-based top-up if at least $2 of the target is left. If one share costs more than the target (likely on a DOWN night), there is no limit order: the whole position is the dollar-based order, and the next morning's exit is a market sell of that fractional position.
9. 16:01:30 EOD. On DOWN nights the report shows what full size would have made.
10. 16:13 after-hours snapshot on tagged nights.

Mondays add the §3(f) edge-decay check. Fridays add the weekly report and audit. Saturdays at 14:23 ET the lab runs (§14): measure the week, test at most one idea, record the result in `LAB.md`. The lab places no orders.

**Blackouts:** NVDA earnings night 2026-11-17 (cash). No other blackouts. Half-days 11/27 and 12/24 have the entry at 12:52 ET.

**Pre-registered reviews (no behaviour change before them):**
- 40 live NVDA-2x nights (19 so far, around mid-December).
- 2027-01-11 quarterly review: event-night hypotheses H1–H3. Live semis-peer nights are 0 for 7, −$23.
- down_session_skip: needs ≥ 120 nights at t ≥ 1.5. Logged nightly from 11/5; history is in `research/down_session_live_20261105.csv`.
- 09:29 pre-market exit: needs mean ≥ +10bp and t ≥ 2. After 13 days: +20bp (sd 82bp), t 0.9. Not met.
- Trend sizing (§13): re-tested on long history at each quarterly review, first on 2027-01-11. It is not judged on live P&L alone. It reverts to always-full if the evidence turns out to be wrong, or if the updated test no longer shows it ahead for NVDA-2x and for at least 8 of 11 large technology names.
- The lab's backlog and the ledger of every test, passed or failed: `LAB.md`.

**Schedule:** 8 scheduled tasks, all live: t2x-analyst 07:45, t3x-exit-0926, t3x-entry-1548, the t2x-wake-a/b hourly backstops, two half-day wakes (11/27 and 12/24), and t3x-lab-weekly (Saturdays 14:23 ET, research only, added 11/9). They are NEVER retired (human rule).

**T2X archive:** RULES.md is untouched. State is in `trader/archive`; see FINAL_REPORT.md.

**To stop me:** create `trader/HUMAN_STOP`, or say so in chat.
