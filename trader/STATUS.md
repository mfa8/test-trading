# T3X STATUS — Overnight Engine (started 2026-09-09)
**Mode:** IN_POSITION_OVERNIGHT (T3X night 26, first v1.6 basket: NVDL 2 @34.1059 + NVDX 1 @19.1796 = 87.39 (85% E), entered 15:52 Wed 10/14; exit 09:31 Thu 10/15; day leg SUSPENDED (v1.7))
**Equity:** 103.13 at 15:52 ET 10/14 (cash 15.74, basket 87.39) · start 98.75 · HWM 107.11 · PAUSE 85.69 · KILL 50
thesis (v1.7): NVDA-2x earns overnight, loses intraday (257 nights: NVDL +0.38%/night ex-earnings, -0.24%/day intraday); hold NVDL/NVDX close->open; planning edge +0.30%/night/unit (honest, after review); inverse day leg SUSPENDED 10/15 (no long-sample edge, ~4x PAUSE risk); never inverse overnight
daily loop (v1.7): 09:26 wake -> sell 09:31 -> ALWAYS-ON scans (cash; day leg SUSPENDED since 10/15, shadow-logged only) -> buy 15:52 (NVDL first, NVDX filler) -> 16:02 EOD | Mon 07:45 analyst: §3(f) trailing-120 NVDL edge-decay check
blackouts: NVDL 2026-11-17 (NVDA); AMZU 2026-10-29 tentative (AMZN); MUU 2026-09-30 (MU)
schedule (5 crons, all live): t2x-analyst 07:45; t3x-exit-0926; t3x-entry-1548; t2x-wake-a/b hourly backstops — NEVER retired (human rule)
T2X archive: RULES.md untouched; state in trader/archive; FINAL_REPORT.md
to stop me: create trader/HUMAN_STOP or say so in chat
