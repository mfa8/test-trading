#!/usr/bin/env python3
# RULES_v3 §5 (v1.8): after the whole-share limit sell has FILLED, sell the fractional remainder by market order.
#   python3 exit_frac.py NIGHT YYYYMMDD SYM QTY [--dry]
# QTY = the exact remaining quantity from get_equity_positions (0 < QTY < 1, at most 6 decimals).
# Appends an INV-12 intent line to orders.jsonl and prints the ref_id. Regular hours only (fractional = market only).
import sys, json, uuid, datetime
a = [x for x in sys.argv[1:] if not x.startswith('--')]; dry = '--dry' in sys.argv
n, day, sym, q = a[0], a[1], a[2].upper(), a[3]
qf = float(q)
assert 0 < qf < 1, "QTY must be the fractional remainder (0 < QTY < 1); whole shares go through exit_ovn.py"
assert len(q.split('.')[-1]) <= 6 if '.' in q else True, "at most 6 decimals"
print(f"{sym} market sell {q} (fractional remainder, night {n})")
if dry: sys.exit()
d = {"t": datetime.datetime.now(datetime.timezone.utc).isoformat(), "coid": f"T3X-{day}-{n}-{sym}-XF", "ref_id": str(uuid.uuid4()), "sym": sym,
     "side": "sell", "qty": q, "type": "market", "tif": "gfd", "hours": "regular_hours",
     "rule": "RULES_v3 §5 v1.8 fractional remainder: market sell after the whole-share limit fill",
     "note": f"night {n} exit (fractional remainder)"}
open('/home/user/test-trading/trader/orders.jsonl', 'a').write(json.dumps(d) + "\n")
print(sym, q, d['ref_id'])
