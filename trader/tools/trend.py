#!/usr/bin/env python3
# RULES_v3 §13 market-trend filter (engine v1.8). No orders; reads/writes only the closes cache and the log.
#
#   python3 trend.py init BARS.json [BARS2.json ...]
#       (Re)build the cache from day-bar files saved from get_equity_historicals
#       ({"data":{"results":[{"symbol","bars":[{"begins_at","close_price","volume",...}]}]}}).
#   python3 trend.py add YYYY-MM-DD QQQ=656.10 NVDA=186.64 SMH=463.96
#       Append official closes for one session (07:45 analyst, from get_equity_quotes "close").
#   python3 trend.py state QQQ=678.10 [NVDA=178.50 SMH=487.00] [--date YYYY-MM-DD] [--log]
#       State at 15:50 ET. For each symbol: flip level = mean of the 199 official closes BEFORE --date
#       (default today, ET). price >= flip -> UP, price < flip -> DOWN. This is the same test as
#       "price vs its 200-day simple average including today's price". QQQ is the binding symbol;
#       NVDA and SMH are shadows. --log appends the rows to research/trend/log.csv.
#   python3 trend.py show
#       Last three cached closes per symbol and the cache size.
#
# Exit code: 0 = QQQ state computed; 2 = cannot compute (cache short or stale) -> §13(a): repair, else size DOWN.
import sys, json, os, datetime
try:
    from zoneinfo import ZoneInfo
    def today_et(): return datetime.datetime.now(ZoneInfo('America/New_York')).date().isoformat()
except Exception:
    def today_et(): return (datetime.datetime.utcnow() - datetime.timedelta(hours=5)).date().isoformat()

BASE = '/home/user/test-trading/trader/research/trend'
CACHE = os.path.join(BASE, 'closes.json')
LOG = os.path.join(BASE, 'log.csv')
N = 200              # SMA length; the flip level uses the N-1 prior closes
BINDING = 'QQQ'
F_UP, F_DOWN = 0.98, 0.25

def load():
    return json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def save(c):
    os.makedirs(BASE, exist_ok=True)
    json.dump({s: dict(sorted(v.items())) for s, v in sorted(c.items())}, open(CACHE, 'w'), indent=0, sort_keys=True)

def kv(args):
    out = {}
    for a in args:
        if a.startswith('--') or '=' not in a: continue
        k, v = a.split('=', 1); out[k.upper()] = float(v)
    return out

def prev_weekday(d):
    d = datetime.date.fromisoformat(d) - datetime.timedelta(days=1)
    while d.weekday() >= 5: d -= datetime.timedelta(days=1)
    return d.isoformat()

def cmd_init(files):
    c = {}
    for f in files:
        j = json.load(open(f)); res = j['data']['results'] if 'data' in j else j['results']
        for x in res:
            for b in x['bars']:
                if b.get('interpolated') or not b.get('volume'): continue
                c.setdefault(x['symbol'], {})[b['begins_at'][:10]] = round(float(b['close_price']), 4)
    save(c)
    for s, v in sorted(c.items()):
        ds = sorted(v); print(f"{s}: {len(ds)} closes {ds[0]} .. {ds[-1]} (last {v[ds[-1]]})")

def cmd_add(args):
    day = args[0]; datetime.date.fromisoformat(day)
    c = load(); new = kv(args[1:])
    assert new, 'no SYM=close pairs'
    for s, px in new.items():
        old = c.setdefault(s, {}).get(day)
        c[s][day] = round(px, 4)
        print(f"{s} {day} = {px:.4f}" + (f" (replaced {old})" if old is not None and abs(old - px) > 1e-9 else '') + f"  [{len(c[s])} closes]")
    save(c)

def cmd_state(args):
    day = today_et()
    if '--date' in args: day = args[args.index('--date') + 1]
    px = kv([a for a in args if a != day]); c = load(); rows = []; rc = 0
    assert BINDING in px, f'{BINDING}=price is required'
    for s in [BINDING] + [k for k in px if k != BINDING]:
        prior = sorted(d for d in c.get(s, {}) if d < day)
        problems = []
        if len(prior) < N - 1: problems.append(f"only {len(prior)} prior closes (< {N-1})")
        elif prior[-1] != prev_weekday(day):
            gap = (datetime.date.fromisoformat(day) - datetime.date.fromisoformat(prior[-1])).days
            problems.append(f"last cached close {prior[-1]} is not the previous weekday {prev_weekday(day)} ({gap}d gap; ok only if holidays)")
        if len(prior) < N - 1:
            print(f"{s}: CANNOT COMPUTE: {problems[0]}")
            if s == BINDING: rc = 2
            continue
        last = prior[-(N - 1):]; flip = sum(c[s][d] for d in last) / (N - 1)
        p = px[s]; sma = (flip * (N - 1) + p) / N; st = 'UP' if p >= flip else 'DOWN'
        dist = 100 * (p / flip - 1)
        stale = any('gap' in q for q in problems) and (datetime.date.fromisoformat(day) - datetime.date.fromisoformat(prior[-1])).days > 4
        print(f"{s}: price {p:.3f}  flip {flip:.3f}  SMA200 {sma:.3f}  dist {dist:+.2f}%  -> {st}" + (f"   WARNING: {'; '.join(problems)}" if problems else ''))
        if s == BINDING and stale: rc = 2
        rows.append((day, s, p, flip, dist, st))
    if rc == 0:
        b = [r for r in rows if r[1] == BINDING][0]
        f = F_UP if b[5] == 'UP' else F_DOWN
        print(f"BINDING {BINDING} {b[5]} -> target fraction f = {f:.2f}  (PAUSE / §3(f) cash / earnings blackout override this)")
        print(json.dumps({"date": day, "qqq": b[2], "flip": round(b[3], 3), "dist_pct": round(b[4], 2), "state": b[5], "f": f,
                          "shadow": {r[1]: {"px": r[2], "flip": round(r[3], 3), "dist_pct": round(r[4], 2), "state": r[5]} for r in rows if r[1] != BINDING}}))
    else:
        print(f"BINDING {BINDING}: NO VALID STATE -> repair the cache (trend.py init/add); if not possible by 15:50, size DOWN (f = {F_DOWN:.2f})")
    if '--log' in args and rows:
        new = not os.path.exists(LOG)
        with open(LOG, 'a') as fh:
            if new: fh.write("date,utc,sym,price,flip,dist_pct,state\n")
            t = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            for d, s, p, fl, di, stt in rows: fh.write(f"{d},{t},{s},{p:.4f},{fl:.4f},{di:.3f},{stt}\n")
    sys.exit(rc)

def cmd_show():
    c = load()
    for s, v in sorted(c.items()):
        ds = sorted(v); print(f"{s}: {len(ds)} closes; last: " + ", ".join(f"{d} {v[d]}" for d in ds[-3:]))

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__ or open(__file__).read().split('import')[0]); sys.exit(1)
    if a[0] == 'init': cmd_init(a[1:])
    elif a[0] == 'add': cmd_add(a[1:])
    elif a[0] == 'state': cmd_state(a[1:])
    elif a[0] == 'show': cmd_show()
    else: sys.exit('unknown command')
