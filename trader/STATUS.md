# T3X STATUS — Overnight Engine (started 2026-09-09)
**Mode:** IN_POSITION_OVERNIGHT (night 31: NVDL 2 @34.1999 + NVDX 1 @19.2199, entered 15:52 Wed 10/21; exit 09:31:05 Thu 10/22; day leg SUSPENDED)
**Equity:** 101.19 at 16:01 ET 10/21 (cash 13.21 + basket 87.98; -5.5% from HWM) · start 98.75 · HWM 107.11 · PAUSE 85.69 · KILL 50
thesis (v1.7): NVDA-2x earns overnight, loses intraday (NVDL ex-earnings overnight: +0.29%/night since Dec-2022, t 2.7; trailing 120 +0.33, t 1.4 — weekly audit 10/16); hold NVDL/NVDX close->open; planning edge +0.30%/night/unit; inverse day leg SUSPENDED 10/15 (no long-sample edge, ~4x PAUSE risk); never inverse overnight
daily loop (v1.7): 09:26 wake -> sell 09:31 -> ALWAYS-ON scans (cash; day leg SUSPENDED since 10/15, shadow-logged only) -> buy 15:52 (NVDL first, NVDX filler) -> 16:02 EOD | Mon 07:45 analyst: §3(f) trailing-120 NVDL edge-decay check
blackouts: NVDA earnings night 2026-11-17 (cash; date per Robinhood, recheck when NVIDIA publishes its call notice). No other blackouts (single NVDA-2x core). Half-days 11/27, 12/24: entry 12:52 ET (one-off wakes set). Crons in ET (DST-safe).
schedule (5 crons, all live): t2x-analyst 07:45; t3x-exit-0926; t3x-entry-1548; t2x-wake-a/b hourly backstops — NEVER retired (human rule)
T2X archive: RULES.md untouched; state in trader/archive; FINAL_REPORT.md
to stop me: create trader/HUMAN_STOP or say so in chat
