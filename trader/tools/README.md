# trader/tools — durable ops scripts (survive container resets)
All order scripts append an INV-12 intent line to trader/orders.jsonl and print the ref_id to use.
- `hb.py "<note>" HH:MM[et]` — loop sleep to a UTC time (or ET with the `et` suffix, DST-safe), capped at 480s per call.
- `bridge.py HH:MM:SS[et]` — exact-time sleep (UTC, or ET with `et`), refuses legs >= 500s. After 2026-11-01 (EST) always use the `et` form.
- `exit_ovn.py NIGHT YYYYMMDD SYM:QTY:BID ... [--reprice]` — §5 09:31 exit limits.
- `entry_v16.py nvdl NIGHT YYYYMMDD NVDL_ask NVDL_last E [--dry]` then `entry_v16.py nvdx NIGHT YYYYMMDD NVDX_ask NVDX_last E SPENT [--dry]` — §3 v1.6 NVDL-first sizing (entry_v15.py kept for history only).
- `trend.py add YYYY-MM-DD QQQ=.. NVDA=.. SMH=..` (07:45, prior session's official closes) and `trend.py state QQQ=<px> NVDA=<px> SMH=<px> --log` (15:50) — §13 market-trend state (v1.8, no orders). QQQ binds: UP -> f 0.98, DOWN -> f 0.25. Exit code 2 = no valid state: repair the cache, else size DOWN. `trend.py show` lists the cache; `trend.py init BARS.json ...` rebuilds it from day-bar files.
- `entry_v18.py core NIGHT YYYYMMDD NVDL_ask NVDL_last E up|down|pause [--dry]` then `entry_v18.py topup NIGHT YYYYMMDD E SPENT up|down|pause [--dry]` — after the core fill, or at once with SPENT 0 when `core` prints `x0` (one share costs more than the target, which happens on DOWN nights when NVDL is above 0.25×E; there is then no core order at all) — §3(c) v1.8 sizing: whole NVDL shares by limit, then one dollar-based market top-up (>= $2.00). Supersedes entry_v16.py from night 45.
- `exit_frac.py NIGHT YYYYMMDD SYM QTY [--dry]` — §5 v1.8: market sell of the fractional remainder, only after the whole-share limit sell (exit_ovn.py) has filled.
- `shadow_tza.py YYYY-MM-DD BARS.json` — §11 v1.7 TZA shadow log (no orders); feed it 1-minute TZA bars.
- `dayleg.py N YYYYMMDD TZA_ask TZA_last cash E [--dry]` / `daytp.py N YYYYMMDD ENTRY QTY` / `daysell.py N YYYYMMDD QTY BID [--reprice]` — §11 day leg.

## sleeve_r4.py (RULES_v3 §12(e), FFB-L options sleeve)
`python3 trader/tools/sleeve_r4.py E S EXPIRY K:bid:ask ...` applies R4 to the call quotes you pass. It prints the spread-mode pick ($10 wide, L0 = mid + 25% toward natural, cost <= B = min(0.2E, E-80), W/L0 >= 4, liquidity guard), the L2 single-call pick, and every candidate considered. Strike-to-instrument ids for the Jan-15-2027 expiry are in `trader/research/sleeve/nvda_calls_2027-01-15.json`. The same tool serves the shadow log and live orders.
