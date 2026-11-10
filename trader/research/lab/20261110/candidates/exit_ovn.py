# usage: python3 exit_ovn.py NIGHT YYYYMMDD SYM:QTY:BID [SYM:QTY:BID ...] [--reprice] [--dry]
# RULES_v3 §5: 09:31:05 marketable limit sell at bid - max(0.02, 0.15%); --reprice -> bid*(1-0.003)
# QTY may be the broker's quantity string (e.g. 3.000000 or 3.997642): the WHOLE-share part is sold here by limit
# order; the tool prints the exit_frac.py command for any fractional remainder (to run after this order has filled).
# A position under 1 share has no whole-share order: use exit_frac.py only.
# An exit is never refused for a log reason: a re-run writes a new intent line with a fresh ref_id.
import sys, os, math, json, uuid, datetime
from decimal import Decimal, InvalidOperation
_DEFAULT_ORD = '/home/user/test-trading/trader/orders.jsonl'
ORD = os.environ.get('T3X_ORDERS') or _DEFAULT_ORD
FRAC = f"python3 {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exit_frac.py')}"
def die(m): print("NOTHING WRITTEN: " + m); sys.exit(1)
bad = [x for x in sys.argv[1:] if x.startswith('--') and x not in ('--reprice', '--dry', '--again')]
if bad: die(f"unknown option {bad[0]!r} (known: --reprice, --dry)")
if '--again' in sys.argv: print("note: --again is not needed here; every run of exit_ovn.py writes a new intent")
pos = [x for x in sys.argv[1:] if not x.startswith('--')]; rp = '--reprice' in sys.argv; dry = '--dry' in sys.argv
if len(pos) < 3: die("usage: exit_ovn.py NIGHT YYYYMMDD SYM:QTY:BID [SYM:QTY:BID ...] [--reprice] [--dry]")
n, day = pos[0], pos[1]
if not (n.isdigit() and len(day) == 8 and day.isdigit()): die("NIGHT must be a number and the date YYYYMMDD")
n = str(int(n))
if ORD != _DEFAULT_ORD: print(f"NOTE: T3X_ORDERS override active: intent log is {ORD}")
legs = []
for a in pos[2:]:
    p = a.split(':')
    if len(p) != 3: die(f"leg must be SYM:QTY:BID, got {a!r}")
    try: q = Decimal(p[1]); b = float(p[2])
    except (InvalidOperation, ValueError): die(f"bad number in {a!r}")
    if p[0].isalpha() and q.is_finite() and q == 0:
        print(f"{p[0].upper()}: quantity 0, nothing to sell, skipped"); continue
    if not (p[0].isalpha() and q.is_finite() and q > 0 and math.isfinite(b) and b > 0): die(f"SYM must be letters, QTY and BID must be > 0 in {a!r}")
    l = math.floor(round((b * (1 - 0.003) if rp else b - max(0.02, 0.0015 * b)) * 100, 6)) / 100
    if l <= 0: die(f"the limit for {a!r} would be {l:.2f}; check the bid")
    whole = int(q); frac = q - whole
    legs.append((p[0].upper(), whole, frac, b, l))
if len({x[0] for x in legs}) != len(legs): die("a symbol appears twice")
t = datetime.datetime.now(datetime.timezone.utc).isoformat()
for sym, whole, frac, b, l in legs:
    fq = format(frac.normalize(), 'f') if frac else ''
    fine = (not frac) or -frac.normalize().as_tuple().exponent <= 6
    hint = (f"{FRAC} {n} {day} {sym} {fq}{' --dry' if dry else ''}" if fine else
            f"re-read get_equity_positions and pass the remaining quantity (at most 6 decimals, rounded DOWN if the broker shows more) to {FRAC} {n} {day} {sym} <QTY>")
    if whole == 0:
        print(f"{sym}: position under 1 share -> no limit order; run: {hint}"); continue
    d = {"t": t, "coid": f"T3X-{day}-{n}-{sym}-X{'2' if rp else ''}", "ref_id": str(uuid.uuid4()), "sym": sym, "side": "sell", "qty": whole, "type": "limit",
         "limit": l, "tif": "gfd", "hours": "regular_hours",
         "rule": "RULES_v3 §5 exit 09:31 " + ("re-price bid-0.3%" if rp else "marketable limit bid-max(0.02,0.15%)"), "note": f"night {n} exit"}
    if not dry:
        lead = ''
        if os.path.exists(ORD) and os.path.getsize(ORD) > 0:
            with open(ORD, 'rb') as fh:
                fh.seek(-1, 2)
                if fh.read(1) != b'\n': lead = '\n'
        with open(ORD, 'a') as fh: fh.write(lead + json.dumps(d) + "\n")
    print(sym, whole, f"{l:.2f}", '(dry)' if dry else d['ref_id'])
    if frac: print(f"{sym}: after this order has FILLED, sell the remainder: {hint}")
