# T3X STATUS: Overnight Engine (started 2026-09-09)

**Mode:** IN_POSITION_OVERNIGHT (as of 16:01 ET Mon 11/9).
- Night 43 closed at 09:31: NVDL 4, 23.7899 → 19.8301, **−15.84**. NVDA-specific weekend news: the board opened a review of CEO Huang.
- Night 44 entered at 15:52: NVDL 3 @ 21.5999 + NVDX 1 @ 12.11 (87.7% of E). The exit is 09:31:05 Tue 11/10.
- The day leg is SUSPENDED.

**Equity:** 87.78 at the 11/9 close (cash 10.83 + positions marked 76.95; 87.72 at the bids).
- Start 98.75. HWM 107.11 (10/12).
- PAUSE 84.65 on 11/9, 82.94 on 11/10 and 82.89 from 11/11 (`state.campaign.pause_schedule`). An NVDA overnight of about −3.1% tonight would reach PAUSE.
- KILL 50.

**Campaign:** 43 nights closed, −14.36 (19 wins, 24 losses). Live NVDA-2x-only nights (N25–N43): 19, totalling −17.62.

**Open question for the human (11/9):** should we hold only 2 NVDL per night until the 11/17 earnings night while the CEO review is open? Default: no change. See `research/NVDA-CEO-REVIEW-20261109.md` and DAY-20261109.

**Options (v2.0 §12 FFB-L):** PENDING. Account 8334 has no options level. The human applies here (L3 preferred, L2 ok): https://applink.robinhood.com/upgrade_options?account_number=445788334
- The shadow quote log has run since 10/23. The plan is in `research/OPTIONS-PLAN-20261022.md`.
- From 11/9 the R4 shadow uses the Feb-19-2027 contracts. Under §12(c), E at bid was 87.72 at the 11/9 close, so B = min(17.54, 7.72) = 7.72 < 8 and the sleeve sleeps. It wakes once E at bid is ≥ 88.00.

**Thesis (v1.7):** NVDA at 2x earns its return overnight and loses it intraday.
- We hold NVDL (NVDX as filler) from close to open.
- Planning edge: +0.30% per night per unit invested.
- §3(f) trailing-120 NVDL check (11/9): +0.363%, t 1.40 → the overnight leg stays on. Next check 11/16.
- The inverse day leg has been SUSPENDED since 10/15. Never hold an inverse product overnight.

**Daily loop (v1.7):**
1. 07:45 analyst check.
2. 09:25 and 09:29 shadow quotes (NVDL and NVDX).
3. Sell at 09:31:05.
4. Always-on 8-minute scans with hourly heartbeats.
5. Sleeve shadow at 10:30, 13:00 and 15:25.
6. 15:40 pre-entry check, journaled.
7. Buy at 15:52 (NVDL first, NVDX filler).
8. 16:01:30 EOD.
9. 16:13 after-hours snapshot on tagged nights.

Mondays add the §3(f) edge-decay check. Fridays add the weekly report and audit.

**Blackouts:** NVDA earnings night 2026-11-17 (cash). No other blackouts. Half-days 11/27 and 12/24 have the entry at 12:52 ET.

**Pre-registered reviews (no behaviour change before them):**
- 40 live NVDA-2x nights (19 so far, around mid-December).
- 2027-01-11 quarterly review: event-night hypotheses H1–H3. Live semis-peer nights are 0 for 7, −$23.
- down_session_skip: needs ≥ 120 nights at t ≥ 1.5. Logged nightly from 11/5; history is in `research/down_session_live_20261105.csv`.
- 09:29 pre-market exit: needs mean ≥ +10bp and t ≥ 2. After 13 days: +20bp (sd 82bp), t 0.9. Not met.

**Schedule:** 5 crons, all live: t2x-analyst 07:45, t3x-exit-0926, t3x-entry-1548, and the t2x-wake-a/b hourly backstops. They are NEVER retired (human rule).

**T2X archive:** RULES.md is untouched. State is in `trader/archive`; see FINAL_REPORT.md.

**To stop me:** create `trader/HUMAN_STOP`, or say so in chat.
