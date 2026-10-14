# trader/tools — durable ops scripts (survive container resets)
All order scripts append an INV-12 intent line to trader/orders.jsonl and print the ref_id to use.
- `hb.py "<note>" HH:MM` — loop sleep to a UTC time, capped at 480s per call.
- `bridge.py HH:MM:SS` — exact-time sleep (UTC), refuses legs >= 500s.
- `exit_ovn.py NIGHT YYYYMMDD SYM:QTY:BID ... [--reprice]` — §5 09:31 exit limits.
- `entry_v15.py NIGHT YYYYMMDD NVDL_ask NVDL_last NVDX_ask NVDX_last E [--dry]` — §3 v1.5 sizing + §4 limits.
- `dayleg.py N YYYYMMDD TZA_ask TZA_last cash E [--dry]` / `daytp.py N YYYYMMDD ENTRY QTY` / `daysell.py N YYYYMMDD QTY BID [--reprice]` — §11 day leg.
