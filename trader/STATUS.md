# T3X STATUS — Overnight Engine (started 2026-09-09)
**Mode:** IN_POSITION_OVERNIGHT (night 32: NVDL 3 @31.2899, entered 15:52 Thu 10/22; exit 09:31:05 Fri 10/23; day leg SUSPENDED)
**Equity:** 97.30 at 16:01 ET 10/22 (cash 3.40 + NVDL3 93.90; -9.2% from HWM) · start 98.75 · HWM 107.11 · PAUSE 85.69 · KILL 50
**Options (v2.0 §12 FFB-L):** PENDING — 8334 has no options level; human to apply (L3 preferred, L2 ok): https://applink.robinhood.com/upgrade_options?account_number=445788334 . Shadow quote log from 10/23. Plan: research/OPTIONS-PLAN-20261022.md
thesis (v1.7): NVDA-2x earns overnight, loses intraday (NVDL ex-earnings overnight: +0.29%/night since Dec-2022, t 2.7; trailing 120 +0.33, t 1.4 — weekly audit 10/16); hold NVDL/NVDX close->open; planning edge +0.30%/night/unit; inverse day leg SUSPENDED 10/15 (no long-sample edge, ~4x PAUSE risk); never inverse overnight
daily loop (v1.7): 09:26 wake -> sell 09:31 -> ALWAYS-ON scans (cash; day leg SUSPENDED since 10/15, shadow-logged only) -> buy 15:52 (NVDL first, NVDX filler) -> 16:02 EOD | Mon 07:45 analyst: §3(f) trailing-120 NVDL edge-decay check
blackouts: NVDA earnings night 2026-11-17 (cash; date per Robinhood, recheck when NVIDIA publishes its call notice). No other blackouts (single NVDA-2x core). Half-days 11/27, 12/24: entry 12:52 ET (one-off wakes set). Crons in ET (DST-safe).
schedule (5 crons, all live): t2x-analyst 07:45; t3x-exit-0926; t3x-entry-1548; t2x-wake-a/b hourly backstops — NEVER retired (human rule)
T2X archive: RULES.md untouched; state in trader/archive; FINAL_REPORT.md
to stop me: create trader/HUMAN_STOP or say so in chat
