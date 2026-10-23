# trader/tools — durable ops scripts (survive container resets)
All order scripts append an INV-12 intent line to trader/orders.jsonl and print the ref_id to use.
- `hb.py "<note>" HH:MM[et]` — loop sleep to a UTC time (or ET with the `et` suffix, DST-safe), capped at 480s per call.
- `bridge.py HH:MM:SS[et]` — exact-time sleep (UTC, or ET with `et`), refuses legs >= 500s. After 2026-11-01 (EST) always use the `et` form.
- `exit_ovn.py NIGHT YYYYMMDD SYM:QTY:BID ... [--reprice]` — §5 09:31 exit limits.
- `entry_v16.py nvdl NIGHT YYYYMMDD NVDL_ask NVDL_last E [--dry]` then `entry_v16.py nvdx NIGHT YYYYMMDD NVDX_ask NVDX_last E SPENT [--dry]` — §3 v1.6 NVDL-first sizing (entry_v15.py kept for history only).
- `shadow_tza.py YYYY-MM-DD BARS.json` — §11 v1.7 TZA shadow log (no orders); feed it 1-minute TZA bars.
- `dayleg.py N YYYYMMDD TZA_ask TZA_last cash E [--dry]` / `daytp.py N YYYYMMDD ENTRY QTY` / `daysell.py N YYYYMMDD QTY BID [--reprice]` — §11 day leg.

## sleeve_r4.py (RULES_v3 §12(e), FFB-L options sleeve)
`python3 trader/tools/sleeve_r4.py E S EXPIRY K:bid:ask ...` applies R4 to the call quotes you pass. It prints the spread-mode pick ($10 wide, L0 = mid + 25% toward natural, cost <= B = min(0.2E, E-80), W/L0 >= 4, liquidity guard), the L2 single-call pick, and every candidate considered. Strike-to-instrument ids for the Jan-15-2027 expiry are in `trader/research/sleeve/nvda_calls_2027-01-15.json`. The same tool serves the shadow log and live orders.
