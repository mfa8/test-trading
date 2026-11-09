#!/usr/bin/env python3
# RULES_v3 §3(c) v1.8 sizing: one symbol (NVDL), target fraction f of E set by the §13 trend state.
#   up    -> f = 0.98      down -> f = 0.25      pause -> exactly 1 NVDL share, no top-up (§6 / §3(e))
# Two steps, both append an INV-12 intent line to orders.jsonl and print the ref_id to use:
#   python3 entry_v18.py core  NIGHT YYYYMMDD NVDL_ask NVDL_last E STATE [--dry]
#       a = largest whole number with a*lim <= f*E; §4 marketable LIMIT buy (lim = ask + max(0.02, 0.15%), <= last*1.004).
#   python3 entry_v18.py topup NIGHT YYYYMMDD E SPENT STATE [--dry]
#       After the core fill (SPENT = qty*avg; 0 if a was 0): ONE dollar-based NVDL MARKET buy, regular hours,
#       for floor_cent(f*E - SPENT), only if that is >= 2.00. Never under pause.
# Review the first live dollar-based order with review_equity_order before placing it (§13(c)).
import sys, math, json, uuid, datetime
F = {'up': 0.98, 'down': 0.25}
MIN_TOPUP = 2.00
SYM = 'NVDL'
ORD = '/home/user/test-trading/trader/orders.jsonl'
a = [x for x in sys.argv[1:] if not x.startswith('--')]; dry = '--dry' in sys.argv
mode, n, day = a[0], a[1], a[2]
now = datetime.datetime.now(datetime.timezone.utc).isoformat()

def log(d):
    open(ORD, 'a').write(json.dumps(d) + "\n")

if mode == 'core':
    ask, last, E = map(float, a[3:6]); state = a[6].lower()
    assert state in ('up', 'down', 'pause'), 'STATE must be up|down|pause'
    lim = math.ceil((ask + max(0.02, 0.0015 * ask)) * 100) / 100
    assert lim <= last * 1.004, f"limit {lim} > last*1.004 {last*1.004:.4f}"
    if state == 'pause':
        q = 1 if lim <= 0.98 * E else 0; target = lim
    else:
        target = F[state] * E; q = int(target // lim)
    rest = 0.0 if state == 'pause' else math.floor((target - q * lim) * 100) / 100
    print(f"{SYM} state {state}  target {target:.2f} ({(target/E*100):.1f}% of E {E:.2f})  lim {lim:.2f} x{q} = {q*lim:.2f}"
          f"  -> planned top-up {rest:.2f}" + ("" if rest >= MIN_TOPUP else " (below 2.00: none)"))
    if dry or q == 0: sys.exit()
    d = {"t": now, "coid": f"T3X-{day}-{n}-{SYM}-E", "ref_id": str(uuid.uuid4()), "sym": SYM, "side": "buy", "qty": q, "type": "limit",
         "limit": lim, "tif": "gfd", "hours": "regular_hours",
         "rule": f"RULES_v3 §3(c) v1.8 target f={'1 share (PAUSE)' if state=='pause' else F[state]} (§13 trend {state}) + §4 entry 15:52 marketable limit",
         "note": f"night {n} entry (core, whole shares)"}
    log(d); print(SYM, q, lim, d['ref_id'])
elif mode == 'topup':
    E, spent = float(a[3]), float(a[4]); state = a[5].lower()
    assert state in ('up', 'down', 'pause'), 'STATE must be up|down|pause'
    if state == 'pause': print("pause: no top-up"); sys.exit()
    amt = math.floor((F[state] * E - spent) * 100 + 1e-9) / 100
    print(f"{SYM} top-up: target {F[state]*E:.2f} - spent {spent:.2f} = {amt:.2f}" + ("" if amt >= MIN_TOPUP else "  (below 2.00: none)"))
    if dry or amt < MIN_TOPUP: sys.exit()
    assert spent + amt <= 0.98 * E + 1e-9, "top-up would exceed 0.98*E"
    d = {"t": now, "coid": f"T3X-{day}-{n}-{SYM}-EF", "ref_id": str(uuid.uuid4()), "sym": SYM, "side": "buy", "dollar_amount": amt, "type": "market",
         "tif": "gfd", "hours": "regular_hours",
         "rule": f"RULES_v3 §3(c) v1.8 fractional top-up to f={F[state]} (§13 trend {state}); dollar-based market order, regular hours",
         "note": f"night {n} entry (fractional top-up)"}
    log(d); print(SYM, 'dollar_amount', f"{amt:.2f}", d['ref_id'])
else:
    sys.exit('mode must be core|topup')
