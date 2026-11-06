# T3X STATUS: Overnight Engine (started 2026-09-09)

**Mode:** FLAT_NO_DAY_LEG (as of 10:45 ET Fri 11/6).
- Night 42 closed at 09:31: NVDL 4, 22.7153 → 25.02, **+9.22**.
- Night 43 enters at 15:52 today, a weekend hold. The exit is 09:31:05 Mon 11/9.
- The day leg is SUSPENDED.

**Equity:** 103.58, all cash, after the 11/6 exit.
- Start 98.75. HWM 107.11 (10/12).
- PAUSE 85.69 through 11/6, then 84.65 on 11/9, 82.94 on 11/10 and 82.86 from 11/11 (`state.campaign.pause_schedule`).
- KILL 50.

**Campaign:** 42 nights closed, +1.48 (19 wins, 23 losses). Live NVDA-2x-only nights (N25–N42): 18, totalling −1.78.

**Options (v2.0 §12 FFB-L):** PENDING. Account 8334 has no options level. The human applies here (L3 preferred, L2 ok): https://applink.robinhood.com/upgrade_options?account_number=445788334
- The shadow quote log has run since 10/23. The plan is in `research/OPTIONS-PLAN-20261022.md`.
- From 11/9 the R4 shadow uses the Feb-19-2027 contracts. At E ≈ 100, the week-9 audit found no R4 pick on Feb-19.

**Thesis (v1.7):** NVDA at 2x earns its return overnight and loses it intraday.
- We hold NVDL (NVDX as filler) from close to open.
- Planning edge: +0.30% per night per unit invested.
- §3(f) trailing-120 NVDL check: +0.364%, t 1.40 (preview for 11/9) → the overnight leg stays on.
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
- 40 live NVDA-2x nights (18 so far, around mid-December).
- 2027-01-11 quarterly review: event-night hypotheses H1–H3. Live semis-peer nights are 0 for 7, −$23.
- down_session_skip: needs ≥ 120 nights at t ≥ 1.5. Logged nightly from 11/5; history is in `research/down_session_live_20261105.csv`.
- 09:29 pre-market exit: needs mean ≥ +10bp and t ≥ 2. After 12 days: +5.7bp, t 0.30.

**Schedule:** 5 crons, all live: t2x-analyst 07:45, t3x-exit-0926, t3x-entry-1548, and the t2x-wake-a/b hourly backstops. They are NEVER retired (human rule).

**T2X archive:** RULES.md is untouched. State is in `trader/archive`; see FINAL_REPORT.md.

**To stop me:** create `trader/HUMAN_STOP`, or say so in chat.
