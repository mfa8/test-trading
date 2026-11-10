#!/usr/bin/env python3
# RULES_v3 §3(c) v1.8 sizing: one symbol (NVDL), target fraction f of E set by the §13 trend state.
#   up    -> f = 0.98      down -> f = 0.25      pause -> exactly 1 NVDL share, no top-up (§6 / §3(e))
# Each step appends ONE INV-12 intent line to orders.jsonl and prints the ref_id to use:
#   python3 entry_v18.py core    NIGHT YYYYMMDD NVDL_ask NVDL_last E STATE [--dry] [--again]
#       a = largest whole number with a*lim <= f*E; §4 marketable LIMIT buy (lim = ask + max(0.02, 0.15%), <= last*1.004).
#       If it prints x0 there is NO core order: go straight to topup with SPENT 0 (§3(c)).
#   python3 entry_v18.py reprice NIGHT YYYYMMDD NVDL_ask NVDL_last E STATE [--dry] [--again]
#       §4, core unfilled at 15:55 (12:55 on a half-day): CANCEL the first order, confirm 0 open orders, then this
#       (lim = ask + 0.3%, <= last*1.0055: the same room for the ask above the last trade as the first order has).
#       The quantity is recomputed at the new limit and can be one share smaller. If shares of the first order
#       already filled (a partial fill), do not use this mode: size the remainder by hand and journal it.
#   python3 entry_v18.py topup   NIGHT YYYYMMDD E SPENT STATE [--dry] [--again]
#       After the core fill (SPENT = qty*avg), or at once with SPENT 0 when core printed x0: ONE dollar-based NVDL
#       MARKET buy, regular hours, for floor_cent(f*E - SPENT), only if that is >= 2.00. Never under pause,
#       never after 15:58, never if a core order was cancelled unfilled.
# Hard stops (nothing written, exit 1): an unknown --flag, a malformed or negative number, E <= 50 (KILL, §6),
# a limit above the cap. Log checks (a second intent of the same kind for the night, a top-up that does not match
# the night's core intent) also stop the tool, print what is stored and say when --again is the right answer;
# --again overrides every log check and nothing else. With --dry the log checks only print a note.
# Review the first live dollar-based order with review_equity_order before placing it (§13(h)).
import sys, os, math, json, uuid, datetime
F = {'up': 0.98, 'down': 0.25}
MIN_TOPUP = 2.00
KILL = 50.0
SYM = 'NVDL'
_DEFAULT_ORD = '/home/user/test-trading/trader/orders.jsonl'
ORD = os.environ.get('T3X_ORDERS') or _DEFAULT_ORD
ME = f"python3 {os.path.abspath(__file__)}"
FLAGS = {'--dry', '--again'}

def die(msg):
    print("NOTHING WRITTEN: " + msg); sys.exit(1)

bad = [x for x in sys.argv[1:] if x.startswith('--') and x not in FLAGS]
if bad: die(f"unknown option {bad[0]!r} (known: --dry, --again)")
a = [x for x in sys.argv[1:] if not x.startswith('--')]; dry = '--dry' in sys.argv; again = '--again' in sys.argv
if len(a) < 3 or a[0] not in ('core', 'reprice', 'topup'): die("mode must be core|reprice|topup; see the header for the arguments")
mode, n, day = a[0], a[1], a[2]
if not (n.isdigit() and len(day) == 8 and day.isdigit()): die("NIGHT must be a number and the date YYYYMMDD")
n = str(int(n))
if ORD != _DEFAULT_ORD: print(f"NOTE: T3X_ORDERS override active: intent log is {ORD}")
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
DRY = ' --dry' if dry else ''

def num(x, name):
    try: v = float(x)
    except ValueError: die(f"{name} must be a number, got {x!r}")
    if not (math.isfinite(v) and v >= 0): die(f"{name} must be a finite number >= 0, got {x!r}")
    return v

def state_of(x):
    s = x.lower()
    if s not in ('up', 'down', 'pause'): die(f"STATE must be up|down|pause, got {x!r}")
    return s

def intents(kind):
    """Earlier intent lines for this night and kind (coid suffix). Damaged lines are skipped."""
    coid = f"T3X-{day}-{n}-{SYM}-{kind}"; out = []
    if os.path.exists(ORD):
        with open(ORD, errors='replace') as fh:
            for ln in fh:
                try: d = json.loads(ln)
                except Exception: continue
                if isinstance(d, dict) and d.get('coid') == coid: out.append(d)
    return out

def show(d):
    what = f"dollar_amount {d.get('dollar_amount')}" if 'dollar_amount' in d else f"qty {d.get('qty')} limit {d.get('limit')}"
    return f"[{d.get('coid')}: {what}, ref_id {d.get('ref_id')}, written {str(d.get('t'))[:19]}Z]"

OVERRODE = []
def check(msg):
    """A log check failed: note under --dry, pass under --again, stop otherwise."""
    if again: OVERRODE.append(1)
    if dry: print(("REHEARSAL NOTE (a real run would continue because of --again): " if again else "REHEARSAL NOTE (a real run would stop here): ") + msg); return
    if again: print("--again: overriding: " + msg); return
    die(msg)

def state_in(d):
    """The sizing state recorded in an intent line (own field, or the rule text of lines written by older versions)."""
    if d.get('state') in ('up', 'down', 'pause'): return d['state']
    r = str(d.get('rule', ''))
    if 'PAUSE' in r: return 'pause'
    for s in ('up', 'down'):
        if f"trend {s})" in r: return s
    return None

def log(d):
    lead = ''
    if os.path.exists(ORD) and os.path.getsize(ORD) > 0:
        with open(ORD, 'rb') as fh:
            fh.seek(-1, 2)
            if fh.read(1) != b'\n': lead = '\n'
    with open(ORD, 'a') as fh: fh.write(lead + json.dumps(d) + "\n")

def floor_cent(x): return math.floor(x * 100 + 1e-7) / 100

def cost(d):
    try: return float(d['qty']) * float(d['limit'])
    except Exception: return None

if mode in ('core', 'reprice'):
    if len(a) != 7: die(f"{mode} needs: NIGHT YYYYMMDD NVDL_ask NVDL_last E STATE")
    ask, last, E = num(a[3], 'ask'), num(a[4], 'last'), num(a[5], 'E'); state = state_of(a[6])
    if ask <= 0 or last <= 0: die("ask and last must be > 0")
    if E <= KILL: die(f"E {E:.2f} <= {KILL:.0f}: KILL (§6). No entry.")
    rp = mode == 'reprice'
    raw = ask * 1.003 if rp else ask + max(0.02, 0.0015 * ask)
    lim = math.ceil(round(raw * 100, 6)) / 100
    capf = 1.0055 if rp else 1.004
    if lim > last * capf + 1e-9:
        die(f"limit {lim:.2f} is above last*{capf} = {last * capf:.4f} ({'re-price bound, §4' if rp else '§4 cap'}). "
            "The quote is stale or the spread is wide: take a fresh quote and run again. "
            + ("If it still fails at the cut-off (15:58; 12:58 on a half-day): leave the first order cancelled and stay in cash (§4)." if rp else
               "If it still fails at 15:57 (12:57 on a half-day): skip the entry (§4)."))
    if state == 'pause':
        q = 1 if lim <= 0.98 * E + 1e-9 else 0; target = lim; rest = 0.0
    else:
        target = F[state] * E; q = int((target + 1e-7) // lim); rest = floor_cent(target - q * lim)
    print(f"{SYM} state {state}  target {target:.4f} ({(target / E * 100):.1f}% of E {E:.2f})  lim {lim:.2f} x{q} = {q * lim:.2f}"
          + ("" if state == 'pause' else f"  -> top-up after the fill about {rest:.2f}" + ("" if rest >= MIN_TOPUP else " (below 2.00: none)")))
    prior = intents('E') + intents('E2')
    if q == 0:
        if state == 'pause' or rest < MIN_TOPUP:
            print("NO ORDER: size is 0 (pause with one share above 0.98*E, or a target under 2.00). Stay in cash tonight.")
        elif rp and prior:
            print("NO ORDER: at the re-price limit one share costs more than the target, and the first core order was cancelled unfilled: "
                  "NO top-up (§3(c)). Stay in cash tonight.")
        elif rp:
            print("NO ORDER at the re-price limit, and no core intent exists for this night: use core, not reprice.")
        elif prior:
            print(f"NO CORE ORDER at this quote, but a core intent exists for night {n}: {show(prior[-1])}.\n"
                  f"  - If that order is live or filled: do nothing here; the top-up comes after its fill.\n"
                  f"  - If it was cancelled unfilled at 15:58: no top-up tonight (§3(c)).\n"
                  f"  - ONLY if it never reached the broker or the broker rejected it: {ME} topup {n} {day} {E:.2f} 0 {state} --again{DRY}")
        else:
            print(f"NO CORE ORDER: one share at the limit costs more than the target. §3(c): place the top-up at once -> "
                  f"{ME} topup {n} {day} {E:.2f} 0 {state}{DRY}   (review_equity_order first on first live use, §13(h); never after 15:58)")
        sys.exit()
    kind = 'E2' if rp else 'E'
    if rp and not intents('E'): die("reprice without a core intent for this night; use core")
    same = intents(kind)
    if same: check(f"an intent of this kind already exists for night {n}: {show(same[-1])}. If that order is live or filled, do nothing. "
                   "If it never reached the broker, send it with THAT ref_id. Only if the broker rejected it (a new order is needed): run again with --again.")
    ef = intents('EF')
    if ef: check(f"a top-up intent already exists for night {n}: {show(ef[-1])}. If that top-up was SENT there is no core order tonight (§3(c)). "
                 "Only if it was never sent (for example written in a rehearsal) or was rejected: run again with --again, and never send that top-up.")
    if again and not OVERRODE: print("note: --again given, but there was nothing to override")
    if dry: sys.exit()
    d = {"t": now, "coid": f"T3X-{day}-{n}-{SYM}-{kind}", "ref_id": str(uuid.uuid4()), "sym": SYM, "side": "buy", "qty": q, "type": "limit",
         "limit": lim, "tif": "gfd", "hours": "regular_hours", "state": state,
         "rule": f"RULES_v3 §3(c) v1.8 target f={'1 share (PAUSE)' if state == 'pause' else F[state]} (§13 trend {state}) + §4 "
                 + ("re-price 15:55 ask+0.3%" if rp else "entry 15:52 marketable limit"),
         "note": f"night {n} entry (core, whole shares{', re-price' if rp else ''})"}
    if OVERRODE: d["again"] = True
    log(d); print(SYM, q, f"{lim:.2f}", d['ref_id'])
else:
    if len(a) != 6: die("topup needs: NIGHT YYYYMMDD E SPENT STATE")
    E, spent = num(a[3], 'E'), num(a[4], 'SPENT'); state = state_of(a[5])
    if E <= KILL: die(f"E {E:.2f} <= {KILL:.0f}: KILL (§6). No entry.")
    if state == 'pause': print("pause: no top-up"); sys.exit()
    amt = floor_cent(F[state] * E - spent)
    print(f"{SYM} top-up: target {F[state] * E:.4f} - spent {spent:.2f} = {amt:.2f}" + ("" if amt >= MIN_TOPUP else "  (below 2.00: none)"))
    if amt < MIN_TOPUP: sys.exit()
    if spent + amt > 0.98 * E + 1e-9: die("top-up would exceed 0.98*E")
    core = intents('E') + intents('E2')
    cs = state_in(core[-1]) if core else None
    if cs and cs != state:
        check(f"the core intent of night {n} was sized for state '{cs}' ({show(core[-1])}) but this top-up says '{state}'. "
              + ("A PAUSE night has NO top-up (§3(e)). " if cs == 'pause' else "Use the state of the 15:50 read that sized the core order. ")
              + "Only if the core intent itself recorded the wrong state: run again with --again.")
    if core and spent == 0:
        check(f"a core intent exists for night {n}: {show(core[-1])}, but SPENT is 0. After a fill SPENT is qty*avg. "
              "If that order was cancelled unfilled there is NO top-up (§3(c)). Only if it never reached the broker or was rejected, "
              "and core now prints x0: run again with --again.")
    if not core and spent > 0:
        check(f"SPENT {spent:.2f} > 0 but no core intent exists for night {n} on {day}. Check NIGHT and the date against the core run "
              "(a --dry core writes no intent). Only if the core order was logged by hand or under another id: run again with --again.")
    costs = [c for c in map(cost, core) if c is not None]
    if costs and spent > max(costs) + 1e-9:
        check(f"SPENT {spent:.2f} is more than any core order of night {n} could cost (max {max(costs):.2f}). Check qty*avg. "
              "Only if shares were bought outside these intents (a hand-sized remainder after a partial fill): run again with --again.")
    ef = intents('EF')
    if ef: check(f"a top-up intent already exists for night {n}: {show(ef[-1])} (ONE top-up per night, §3(c)). If it never reached the broker, "
                 "send it with THAT ref_id. Only if the broker rejected it: run again with --again.")
    if again and not OVERRODE: print("note: --again given, but there was nothing to override")
    if dry: sys.exit()
    d = {"t": now, "coid": f"T3X-{day}-{n}-{SYM}-EF", "ref_id": str(uuid.uuid4()), "sym": SYM, "side": "buy", "dollar_amount": amt, "type": "market",
         "tif": "gfd", "hours": "regular_hours", "state": state,
         "rule": f"RULES_v3 §3(c) v1.8 fractional top-up to f={F[state]} (§13 trend {state}); dollar-based market order, regular hours",
         "note": f"night {n} entry (fractional top-up)"}
    if OVERRODE: d["again"] = True
    log(d); print(SYM, 'dollar_amount', f"{amt:.2f}", d['ref_id'])
