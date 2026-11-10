#!/usr/bin/env python3
# RULES_v3 §5 (v1.8): sell the fractional remainder by ONE market order, regular hours, after the whole-share
# limit sell has FILLED (or as the only exit order when the position is under 1 share).
#   python3 exit_frac.py NIGHT YYYYMMDD SYM QTY [--dry] [--again]
# QTY = the remaining quantity exactly as get_equity_positions reports it (trailing zeros are fine): 0 < QTY < 1,
# at most 6 significant decimals. Appends an INV-12 intent line to orders.jsonl and prints the quantity and ref_id.
# A second intent for the same night and symbol stops the tool and prints the first one; --again writes a new one
# (use it when the broker rejected the first order, or when the quantity must change, e.g. dust left after a fill).
import sys, os, json, uuid, datetime
from decimal import Decimal, InvalidOperation
_DEFAULT_ORD = '/home/user/test-trading/trader/orders.jsonl'
ORD = os.environ.get('T3X_ORDERS') or _DEFAULT_ORD
def die(m): print("NOTHING WRITTEN: " + m); sys.exit(1)
bad = [x for x in sys.argv[1:] if x.startswith('--') and x not in ('--dry', '--again')]
if bad: die(f"unknown option {bad[0]!r} (known: --dry, --again)")
a = [x for x in sys.argv[1:] if not x.startswith('--')]; dry = '--dry' in sys.argv; again = '--again' in sys.argv
if len(a) != 4: die("usage: exit_frac.py NIGHT YYYYMMDD SYM QTY [--dry] [--again]")
n, day, sym = a[0], a[1], a[2].upper()
if not (n.isdigit() and len(day) == 8 and day.isdigit()): die("NIGHT must be a number and the date YYYYMMDD")
n = str(int(n))
if not sym.isalpha(): die(f"SYM must be letters, got {a[2]!r}")
if ORD != _DEFAULT_ORD: print(f"NOTE: T3X_ORDERS override active: intent log is {ORD}")
try: q = Decimal(a[3])
except InvalidOperation: die(f"QTY must be a number, got {a[3]!r}")
if not q.is_finite(): die("QTY must be finite")
if q == 0: die("QTY is 0: nothing to sell")
if not (0 < q < 1): die(f"QTY {a[3]} is not a fractional remainder (0 < QTY < 1). Whole shares go through exit_ovn.py, which prints the remainder command.")
q = q.normalize()
if -q.as_tuple().exponent > 6: die(f"QTY {a[3]} has more than 6 decimals. Fractional orders take at most 6: re-read get_equity_positions; "
                                   "if the broker itself reports more, round DOWN to 6 decimals. A remainder below 0.000001 cannot be sold by a "
                                   "share order: leave it and note it in the journal")
qs = format(q, 'f'); coid = f"T3X-{day}-{n}-{sym}-XF"
prev = None
if os.path.exists(ORD):
    with open(ORD, errors='replace') as fh:
        for ln in fh:
            try: p = json.loads(ln)
            except Exception: continue
            if isinstance(p, dict) and p.get('coid') == coid: prev = p
if prev:
    msg = (f"an intent {coid} already exists (qty {prev.get('qty')}, ref_id {prev.get('ref_id')}, written {str(prev.get('t'))[:19]}Z). "
           "If that order is live or filled and nothing is left, do nothing. If it never reached the broker, send it with THAT ref_id. "
           "If the broker rejected it, or shares are still held and the quantity must change: run again with --again.")
    if dry: print(("REHEARSAL NOTE (a real run would continue because of --again): " if again else "REHEARSAL NOTE (a real run would stop here): ") + msg)
    elif again: print("--again: overriding: " + msg)
    else: die(msg)
if again and not prev: print("note: --again given, but no earlier intent exists for this night and symbol")
print(f"{sym} market sell {qs} (fractional remainder, night {n})")
if dry: sys.exit()
d = {"t": datetime.datetime.now(datetime.timezone.utc).isoformat(), "coid": coid, "ref_id": str(uuid.uuid4()), "sym": sym,
     "side": "sell", "qty": qs, "type": "market", "tif": "gfd", "hours": "regular_hours",
     "rule": "RULES_v3 §5 v1.8 fractional remainder: market sell after the whole-share limit fill", "note": f"night {n} exit (fractional remainder)"}
if again and prev: d["again"] = True
lead = ''
if os.path.exists(ORD) and os.path.getsize(ORD) > 0:
    with open(ORD, 'rb') as fh:
        fh.seek(-1, 2)
        if fh.read(1) != b'\n': lead = '\n'
with open(ORD, 'a') as fh: fh.write(lead + json.dumps(d) + "\n")
print(sym, qs, d['ref_id'])
