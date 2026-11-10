#!/usr/bin/env python3
# RULES_v3 §13 market-trend filter (engine v1.8). No orders; reads/writes only the closes cache, closed.json and the log.
#
#   python3 trend.py init BARS.json [BARS2.json ...]
#       (Re)build the cache from day-bar files saved from get_equity_historicals
#       ({"data":{"results":[{"symbol","bars":[{"begins_at","close_price","volume",...}]}]}}).
#       Give the bars of ALL symbols: init replaces the whole cache.
#   python3 trend.py add YYYY-MM-DD QQQ=656.10 NVDA=186.64 SMH=463.96 [--force]
#       Append official closes for one COMPLETED session (07:45 analyst, from get_equity_quotes "close").
#       The date is refused (nothing saved, exit 1) if it is a weekend, an NYSE holiday, a declared closure, or
#       today (ET) or later. A symbol is refused (the others are still saved, exit 1) if it is not yet in the cache,
#       if the date already has a different value, or if the close is more than 25% from the previous cached close.
#       --force overrides those checks. It never overrides a malformed date or a value that is not a positive number.
#   python3 trend.py del YYYY-MM-DD [SYM ...]
#       Remove one date (for all symbols, or only those named). For a mistyped or non-session entry.
#   python3 trend.py closed YYYY-MM-DD [--remove]
#       Declare ONE unscheduled full-day NYSE closure (a weekday that is not in HOLIDAYS and has no official close).
#       Stored in closed.json next to the cache and honoured by state, add and show from then on.
#       Refused if the date is a weekend/holiday, in the future, or already has a cached close.
#   python3 trend.py state QQQ=678.10 [NVDA=178.50 SMH=487.00] [--date YYYY-MM-DD] [--closed YYYY-MM-DD[,..]] [--log]
#       State before the entry (15:50 ET; 12:50 ET on a half-day). For each symbol: flip level = mean of the 199
#       official closes BEFORE --date (default today, ET). price >= flip -> UP, price < flip -> DOWN. This is the
#       same test as "price vs its 200-day simple average including today's price". QQQ is the binding symbol;
#       NVDA and SMH are shadows: a problem with a shadow never changes the QQQ result or the exit code.
#       --log writes the rows to research/trend/log.csv (one row per date and symbol). A re-run on the same day within
#       20 minutes replaces that date's rows; later runs and runs with a past --date leave the log unchanged.
#   python3 trend.py show
#       Last three cached closes per symbol, the cache size, declared closures and any missing or non-session date.
#
# Exit code of `state`: 0 = a VALID QQQ state was computed. 2 = no valid state -> §13(a): repair the cache as the
# message says and re-run; if that is not possible before the entry, size DOWN. A state is valid only if the cache
# holds at least 199 closes before the date, its last close is the previous NYSE session, no session is missing
# inside the 199-close window and every date in the window is an NYSE session. Any crash in `state` also exits 2.
import sys, json, os, re, math, datetime

def _today_fallback(): return (datetime.datetime.utcnow() - datetime.timedelta(hours=5)).date().isoformat()
try:
    from zoneinfo import ZoneInfo
    _TZ = ZoneInfo('America/New_York')          # raises here, not later, if the time-zone database is missing
    def today_et(): return datetime.datetime.now(_TZ).date().isoformat()
except Exception:
    today_et = _today_fallback

_DEFAULT_BASE = '/home/user/test-trading/trader/research/trend'
BASE = os.environ.get('TREND_BASE') or _DEFAULT_BASE
CACHE = os.path.join(BASE, 'closes.json')
CLOSED = os.path.join(BASE, 'closed.json')      # unscheduled full-day closures declared with `trend.py closed`
LOG = os.path.join(BASE, 'log.csv')
LOG_HEADER = "date,utc,sym,price,flip,dist_pct,state,valid,f"
N = 200              # SMA length; the flip level uses the N-1 prior closes
BINDING = 'QQQ'
F_UP, F_DOWN = 0.98, 0.25
MAX_JUMP = 0.25      # `add` refuses a close more than 25% from the previous cached close unless --force
# NYSE full-day closures (nyse.com/markets/hours-calendars). Early-close days are sessions and are not listed.
HOLIDAYS = {
    '2025-01-01', '2025-01-09', '2025-01-20', '2025-02-17', '2025-04-18', '2025-05-26', '2025-06-19', '2025-07-04',
    '2025-09-01', '2025-11-27', '2025-12-25',
    '2026-01-01', '2026-01-19', '2026-02-16', '2026-04-03', '2026-05-25', '2026-06-19', '2026-07-03',
    '2026-09-07', '2026-11-26', '2026-12-25',
    '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26', '2027-05-31', '2027-06-18', '2027-07-05',
    '2027-09-06', '2027-11-25', '2027-12-24',
    '2028-01-17', '2028-02-21', '2028-04-14', '2028-05-29', '2028-06-19', '2028-07-04', '2028-09-04',
    '2028-11-23', '2028-12-25',
}
HOLIDAYS_THROUGH = '2028-12-31'
HOLIDAYS_FROM = '2025-01-01'     # the table does not reach further back; earlier dates are not calendar-checked
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
WHEN = "before the entry (15:50 ET; 12:50 ET on a half-day)"

def load():
    return json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def _atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, 'w') as fh: fh.write(text)
    os.replace(tmp, path)

def save(c):
    _atomic_write(CACHE, json.dumps({s: dict(sorted(v.items())) for s, v in sorted(c.items())}, indent=0, sort_keys=True))

def load_closed():
    """Declared closures. A missing or unreadable file means none (state then fails safe with STALE/HOLE)."""
    if not os.path.exists(CLOSED): return ()
    try:
        x = json.load(open(CLOSED))
        if not isinstance(x, list): raise ValueError('not a list')
        return tuple(sorted({d for d in x if isinstance(d, str) and DATE_RE.match(d)}))
    except Exception as e:
        print(f"NOTE: {CLOSED} is unreadable ({type(e).__name__}); declared closures are ignored -> trend.py closed YYYY-MM-DD"); return ()

def parse_date(d):
    if not DATE_RE.match(d): raise ValueError(f"date must be YYYY-MM-DD, got {d!r}")
    return datetime.date.fromisoformat(d)

def is_session(d, closed=()):
    return parse_date(d).weekday() < 5 and d not in HOLIDAYS and d not in closed

def prev_session(d, closed=()):
    x = parse_date(d) - datetime.timedelta(days=1)
    while not is_session(x.isoformat(), closed): x -= datetime.timedelta(days=1)
    return x.isoformat()

def missing_sessions(dates, closed=()):
    """Sessions strictly between consecutive cached dates that are not in the list."""
    out = []
    for a, b in zip(dates, dates[1:]):
        x = parse_date(a) + datetime.timedelta(days=1)
        while x.isoformat() < b:
            if x.isoformat() >= HOLIDAYS_FROM and is_session(x.isoformat(), closed): out.append(x.isoformat())
            x += datetime.timedelta(days=1)
    return out

def non_sessions(dates, closed=()):
    """Cached dates that are not NYSE sessions (weekend, holiday or declared closure)."""
    return [d for d in dates if d >= HOLIDAYS_FROM and not is_session(d, closed)]

def split_args(args, flags=(), valued=()):
    """Return (positional, options). Unknown --flags are an error, so a mistyped flag cannot be dropped silently."""
    pos, opt, i = [], {}, 0
    while i < len(args):
        a = args[i]
        if a.startswith('--'):
            k, eq, v = a.partition('=')
            if k in flags and not eq: opt[k] = True
            elif k in valued:
                if not eq:
                    i += 1
                    if i >= len(args): raise ValueError(f"{k} needs a value")
                    v = args[i]
                opt[k] = v
            else: raise ValueError(f"unknown option {a!r}")
        else: pos.append(a)
        i += 1
    return pos, opt

def one_price(k, v):
    x = float(v)
    if not (math.isfinite(x) and x > 0): raise ValueError(f"{k}: price must be a positive finite number, got {v!r}")
    return x

def kv(args, lenient=()):
    """SYM=price pairs. A bad value raises, except for symbols in `lenient`, which map to the error text instead."""
    out = {}
    for a in args:
        k, eq, v = a.partition('='); k = k.upper()
        soft = lenient == '*' and k and k != BINDING        # a shadow (state) or any symbol (add): record the error, keep going
        if not eq or not k:
            if soft: out[k] = f"expected {k}=price, got {a!r}"; continue
            raise ValueError(f"expected SYM=price, got {a!r}")
        if k in out:
            if soft: out[k] = f"{k} given twice"; continue
            raise ValueError(f"{k} given twice")
        try: out[k] = one_price(k, v)
        except ValueError as e:
            if soft: out[k] = f"{k}: not a positive number: {v!r}"
            else: raise
    return out

def table_warning(day):
    left = (parse_date(HOLIDAYS_THROUGH) - parse_date(day)).days
    if 0 <= left <= 60: print(f"WARNING: the NYSE holiday table in trend.py ends {HOLIDAYS_THROUGH} ({left} days left); extend HOLIDAYS before then")

def cmd_init(files):
    c = {}; skipped = set()
    for f in files:
        j = json.load(open(f)); res = j['data']['results'] if 'data' in j else j['results']
        for x in res:
            for b in x['bars']:
                if b.get('interpolated') or not b.get('volume'): continue
                if b['begins_at'][:10] >= today_et(): skipped.add(b['begins_at'][:10]); continue     # today's bar is not an official close yet
                c.setdefault(x['symbol'], {})[b['begins_at'][:10]] = round(float(b['close_price']), 4)
    old = load(); lost = sorted(set(old) - set(c))
    if lost: print(f"NOTHING SAVED: init would drop {', '.join(lost)} from the cache; give the bar files of ALL symbols"); sys.exit(1)
    save(c)
    if skipped: print(f"skipped unfinished bar(s) dated {', '.join(sorted(skipped))} (today or later); add the official close tomorrow at 07:45")
    for s, v in sorted(c.items()):
        ds = sorted(v); print(f"{s}: {len(ds)} closes {ds[0]} .. {ds[-1]} (last {v[ds[-1]]})")

def cmd_add(args):
    try:
        pos, opt = split_args(args, flags=('--force',))
        if not pos: raise ValueError('usage: add YYYY-MM-DD SYM=close [SYM=close ...] [--force]')
        day = pos[0]; parse_date(day); force = opt.get('--force', False)
        new = {}; serr = {}
        for a in pos[1:]:                       # a bad value refuses that symbol only; a token that names no symbol refuses the line
            k, eq, v = a.partition('='); k = k.upper()
            if not eq or not k: raise ValueError(f"expected SYM=close, got {a!r}")
            if k in new or k in serr: raise ValueError(f"{k} given twice")
            try: new[k] = one_price(k, v)
            except ValueError: serr[k] = f"{k}: close must be a positive number, got {v!r}"
        if not new and not serr: raise ValueError('no SYM=close pairs')
    except ValueError as e:
        print(f"NOTHING SAVED: {e}"); sys.exit(1)
    c = load(); closed = load_closed(); derr = []
    if not force:
        if parse_date(day).weekday() >= 5: derr.append(f"{day} is a weekend; use the date of the session the closes belong to (the previous session is {prev_session(day, closed)})")
        elif day in HOLIDAYS: derr.append(f"{day} is an NYSE holiday; use the date of the session the closes belong to (the previous session is {prev_session(day, closed)})")
        elif day in closed: derr.append(f"{day} was declared a full-day market closure (undo: trend.py closed {day} --remove)")
        if day >= today_et(): derr.append(f"{day} is today (ET) or later; closes are added the next morning at 07:45 (--force for an end-of-day add of today's official close)")
        for s, px in new.items():
            if c and s not in c: serr[s] = f"{s} is not in the cache (known: {', '.join(sorted(c))})"; continue
            v = c.get(s, {})
            if day in v and abs(v[day] - round(px, 4)) > 1e-9: serr[s] = f"{s} {day} is already {v[day]}; refusing to replace it with {px} (to correct a typo: trend.py del {day} {s}, then add again)"; continue
            before = [d for d in sorted(v) if d < day]
            if before and abs(px / v[before[-1]] - 1) > MAX_JUMP:
                serr[s] = (f"{s} {px} is {100 * (px / v[before[-1]] - 1):+.1f}% from the previous cached close {v[before[-1]]} ({before[-1]}). "
                           f"If this is a typo, fix it. If {s} had a stock split, do NOT force: rebuild the cache with init from split-adjusted day bars of ALL symbols")
    if derr:
        print("NOTHING SAVED:"); [print("  - " + e) for e in derr]; sys.exit(1)
    saved = []
    for s, px in new.items():
        if s in serr: continue
        old = c.setdefault(s, {}).get(day)
        c[s][day] = round(px, 4); saved.append(s)
        print(f"{s} {day} = {px:.4f}" + (f" (replaced {old})" if old is not None and abs(old - px) > 1e-9 else '') + f"  [{len(c[s])} closes]")
    if saved: save(c)
    for s in sorted(c):
        ds = sorted(c[s]); miss = missing_sessions(ds[-(N + 5):], closed)
        if miss: print(f"WARNING {s}: missing session(s) {', '.join(miss)} -> trend.py add <date> {s}=<official close>; ONLY for a date on which NYSE was closed all day: trend.py closed <date>")
    lasts = {s: max(c[s]) for s in c if c[s]}
    if len(set(lasts.values())) > 1: print("WARNING: symbols end on different dates: " + ", ".join(f"{s} {d}" for s, d in sorted(lasts.items())))
    table_warning(day)
    if serr:
        print("NOT SAVED (" + (f"saved: {', '.join(saved)}" if saved else "nothing saved") + "):"); [print("  - " + e) for e in serr.values()]
        print("Re-run for the refused symbol(s) after checking; --force only if the value is really intended.")
        sys.exit(1)

def cmd_del(args):
    try:
        pos, opt = split_args(args)
        if not pos: raise ValueError('usage: del YYYY-MM-DD [SYM ...]')
        day = pos[0]; parse_date(day); syms = [s.upper() for s in pos[1:]]
    except ValueError as e:
        print(f"NOTHING CHANGED: {e}"); sys.exit(1)
    c = load(); hit = []
    for s in sorted(c):
        if (not syms or s in syms) and day in c[s]:
            hit.append(f"{s} {day} = {c[s].pop(day)}")
    unknown = [s for s in syms if s not in c]
    if unknown: print(f"NOTHING CHANGED: {', '.join(unknown)} not in the cache"); sys.exit(1)
    if not hit: print(f"NOTHING CHANGED: no cached close on {day}"); sys.exit(1)
    save(c); print("removed: " + "; ".join(hit))

def state_one(c, s, p, day, closed):
    """Return dict(sym, price, flip, dist, state, valid, problems)."""
    if isinstance(p, str):
        return {"sym": s, "price": None, "flip": None, "dist": None, "state": None, "valid": False, "problems": [p]}
    prior = sorted(d for d in c.get(s, {}) if DATE_RE.match(d) and d < day)
    problems = []
    if len(prior) < N - 1:
        return {"sym": s, "price": p, "flip": None, "dist": None, "state": None, "valid": False,
                "problems": [f"only {len(prior)} closes before {day} (need {N - 1})"]}
    if day > HOLIDAYS_THROUGH: problems.append(f"the holiday table ends {HOLIDAYS_THROUGH}; extend HOLIDAYS in trend.py")
    want = prev_session(day, closed)
    last = prior[-(N - 1):]
    bad = non_sessions(last, closed)
    if bad: problems.append(f"NON-SESSION: cached date(s) {', '.join(bad[:6])} are not NYSE sessions -> trend.py del <date>")
    if prior[-1] != want and prior[-1] not in bad:
        problems.append(f"STALE: last cached close is {prior[-1]}, the previous session is {want} -> trend.py add {want} {s}=<official close>; "
                        f"ONLY if NYSE was closed all day on {want} (no official close exists): trend.py closed {want}")
    miss = missing_sessions(last, closed)
    if miss: problems.append(f"HOLE: {len(miss)} session(s) missing inside the window: {', '.join(miss[:6])} -> trend.py add <date> {s}=<official close>; "
                             f"ONLY for a date on which NYSE was closed all day: trend.py closed <date>")
    vals = [c[s][d] for d in last]
    if not all(isinstance(v, (int, float)) and math.isfinite(v) and v > 0 for v in vals): problems.append("BAD VALUE: a cached close in the window is not a positive number")
    flip = math.fsum(vals) / (N - 1)
    st = 'UP' if p >= flip - 1e-9 else 'DOWN'       # P == L is UP (§13(a)); the tolerance absorbs float summation error
    return {"sym": s, "price": p, "flip": flip, "dist": 100 * (p / flip - 1), "state": st, "valid": not problems, "problems": problems}

def write_log(day, rows, f):
    # The log is the record of the read that sized the order. A re-run replaces a date's rows only on that day and only
    # within 20 minutes of the first valid QQQ row (a duplicate wake or a repair); later runs leave the log alone.
    nowu = datetime.datetime.now(datetime.timezone.utc)
    if day != today_et():
        print(f"WARNING: --log ignored because --date {day} is not today (ET); the log keeps what was written on the day"); return
    keep = []
    if os.path.exists(LOG):
        lines = open(LOG, errors='replace').read().splitlines()
        syms = {r['sym'] for r in rows}
        for ln in lines[1:]:
            parts = ln.split(',')
            if len(parts) >= 8 and parts[0] == day and parts[2] == BINDING and parts[7] == '1':
                try: age = (nowu - datetime.datetime.strptime(parts[1], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)).total_seconds()
                except ValueError: age = 0
                if age > 1200:
                    print(f"WARNING: log not changed: it already holds a valid {BINDING} row for {day} written at {parts[1]} (the read that sized the order)"); return
        for ln in lines[1:]:
            parts = ln.split(',')
            if len(parts) >= 3 and parts[0] == day and parts[2] in syms: continue      # a re-run replaces that date's rows
            keep.append(ln if len(parts) >= 9 else ln + ',,')                           # pad rows written before the valid,f columns existed
    t = nowu.strftime('%Y-%m-%dT%H:%M:%SZ')
    for r in rows:
        pr = '' if r['price'] is None else f"{r['price']:.4f}"
        fl = '' if r['flip'] is None else f"{r['flip']:.4f}"; di = '' if r['dist'] is None else f"{r['dist']:.3f}"
        ff = f"{f:.2f}" if r['sym'] == BINDING else ''
        keep.append(f"{day},{t},{r['sym']},{pr},{fl},{di},{r['state'] or ''},{1 if r['valid'] else 0},{ff}")
    _atomic_write(LOG, LOG_HEADER + "\n" + "\n".join(keep) + "\n")

def cmd_state(args):
    pos, opt = split_args(args, flags=('--log',), valued=('--date', '--closed'))
    day = opt.get('--date') or today_et(); parse_date(day)
    closed = tuple(x for x in (opt.get('--closed') or '').split(',') if x)
    for x in closed: parse_date(x)
    stored = load_closed(); closed = tuple(sorted(set(closed) | set(stored)))
    if stored: print(f"NOTE: declared full-day market closure(s): {', '.join(stored)} (closed.json)")
    px = kv(pos, lenient='*'); c = load()
    if BINDING not in px: raise ValueError(f'{BINDING}=price is required')
    if not is_session(day, closed): print(f"NOTE: {day} is not an NYSE session")
    rows = [state_one(c, BINDING, px[BINDING], day, closed)]
    for s in [k for k in px if k != BINDING]:
        try: rows.append(state_one(c, s, px[s], day, closed))
        except Exception as e:      # a shadow problem never changes the QQQ result or the exit code
            rows.append({"sym": s, "price": None, "flip": None, "dist": None, "state": None, "valid": False, "problems": [f"{type(e).__name__}: {e}"]})
    for r in rows:
        if r['flip'] is None:
            print(f"{r['sym']}: CANNOT COMPUTE: {r['problems'][0]}"); continue
        sma = (r['flip'] * (N - 1) + r['price']) / N
        print(f"{r['sym']}: price {r['price']:.3f}  flip {r['flip']:.3f}  SMA200 {sma:.3f}  dist {r['dist']:+.2f}%  -> {r['state']}"
              + ('' if r['valid'] else "   INVALID: " + '; '.join(r['problems'])))
    b = rows[0]; rc = 0 if b['valid'] else 2
    f = (F_UP if b['state'] == 'UP' else F_DOWN) if rc == 0 else F_DOWN
    if rc == 0:
        print(f"BINDING {BINDING} {b['state']} -> target fraction f = {f:.2f}  (PAUSE / §3(f) cash / earnings blackout override this)")
        print(json.dumps({"date": day, "qqq": b['price'], "flip": round(b['flip'], 3), "dist_pct": round(b['dist'], 2), "state": b['state'], "f": f, "valid": True,
                          "shadow": {r['sym']: {"px": r['price'], "flip": round(r['flip'], 3), "dist_pct": round(r['dist'], 2), "state": r['state'], "valid": r['valid']}
                                     for r in rows[1:] if r['flip'] is not None}}))
    else:
        print(f"BINDING {BINDING}: NO VALID STATE (exit code 2) -> repair the cache as shown above and re-run; if that is not possible {WHEN}, size DOWN (f = {F_DOWN:.2f})")
    table_warning(day)
    if opt.get('--log'):
        try: write_log(day, rows, f)
        except Exception as e: print(f"WARNING: log not written ({type(e).__name__}: {e}); the state above stands")
    sys.exit(rc)

def cmd_closed(args):
    try:
        pos, opt = split_args(args, flags=('--remove',))
        if len(pos) != 1: raise ValueError('usage: closed YYYY-MM-DD [--remove]')
        day = pos[0]; parse_date(day); days = set(load_closed())
        if opt.get('--remove'): days.discard(day)
        else:
            if not is_session(day): raise ValueError(f"{day} is a weekend or already an NYSE holiday")
            if day > today_et(): raise ValueError(f"{day} is in the future; declare a closure on or after the day")
            have = sorted(s for s, v in load().items() if day in v)
            if have: raise ValueError(f"{day} has a cached close for {', '.join(have)}, so it was a session (if those closes were added by mistake: trend.py del {day}, then closed {day})")
            days.add(day)
    except ValueError as e:
        print(f"NOTHING SAVED: {e}"); sys.exit(1)
    _atomic_write(CLOSED, json.dumps(sorted(days)))
    print("declared full-day market closures (beyond HOLIDAYS): " + (', '.join(sorted(days)) or 'none'))

def cmd_show():
    c = load(); closed = load_closed()
    if closed: print(f"declared full-day market closure(s): {', '.join(closed)}")
    for s, v in sorted(c.items()):
        ds = sorted(d for d in v if DATE_RE.match(d)); miss = missing_sessions(ds, closed); bad = non_sessions(ds, closed)
        odd = sorted(d for d in v if not DATE_RE.match(d))
        print(f"{s}: {len(v)} closes; last: " + ", ".join(f"{d} {v[d]}" for d in ds[-3:]) + (f"   MISSING: {', '.join(miss)}" if miss else '')
              + (f"   NON-SESSION: {', '.join(bad)}" if bad else '') + (f"   MALFORMED KEYS: {', '.join(odd)}" if odd else ''))

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] not in ('init', 'add', 'del', 'state', 'show', 'closed'):
        print(open(__file__).read().split('import sys')[0]); sys.exit(1)
    if BASE != _DEFAULT_BASE: print(f"NOTE: TREND_BASE override active: {BASE}")
    if a[0] == 'init': cmd_init(a[1:])
    elif a[0] == 'add': cmd_add(a[1:])
    elif a[0] == 'del': cmd_del(a[1:])
    elif a[0] == 'show': cmd_show()
    elif a[0] == 'closed': cmd_closed(a[1:])
    else:
        try:
            cmd_state(a[1:])
        except SystemExit:
            raise
        except Exception as e:      # any failure to compute is "no valid state" (§13(a))
            print(f"BINDING {BINDING}: NO VALID STATE (exit code 2): {type(e).__name__}: {e} -> if not repaired {WHEN}, size DOWN (f = {F_DOWN:.2f})")
            sys.exit(2)
