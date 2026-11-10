"""Analyst B loader for L15. Reads the raw broker day-bar JSON files only.

Rules applied (all counted in the returned report, nothing dropped silently):
  - bar skipped if flagged interpolated, or volume is zero/missing, or a price is
    missing / not positive;
  - duplicate dates (file-boundary overlap) de-duplicated, first kept, mismatch reported;
  - every NVDA date <= 2000-10-27 dropped (10x mis-scaled stretch);
  - every date > 2026-11-06 dropped (provisional bars).
"""
import json
import os

RAW = '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/rev'
FILES = ['d0a', 'd0b', 'd1', 'd2', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6']
END_DATE = '2026-11-06'
NVDA_LAST_BAD = '2000-10-27'


def load_all():
    bars = {}      # sym -> {date: (open, close)}
    rep = {}       # sym -> counters

    def counter(sym):
        return rep.setdefault(sym, dict(raw=0, interp=0, zero_vol=0, bad_price=0,
                                        dup=0, dup_mismatch=0, after_end=0,
                                        nvda_prebreak=0, kept=0, zero_vol_dates=[]))

    for f in FILES:
        with open(os.path.join(RAW, f + '.json')) as fh:
            j = json.load(fh)
        d = j['data'] if isinstance(j, dict) and 'data' in j else j
        for res in d['results']:
            sym = res['symbol']
            c = counter(sym)
            store = bars.setdefault(sym, {})
            for b in res['bars']:
                c['raw'] += 1
                ba = b['begins_at']
                assert ba[10:] == 'T00:00:00Z', ba
                date = ba[:10]
                if date > END_DATE:
                    c['after_end'] += 1
                    continue
                if sym == 'NVDA' and date <= NVDA_LAST_BAD:
                    c['nvda_prebreak'] += 1
                    continue
                if b.get('interpolated'):
                    c['interp'] += 1
                    continue
                vol = b.get('volume')
                if vol is None or float(vol) <= 0:
                    c['zero_vol'] += 1
                    c['zero_vol_dates'].append(date)
                    continue
                try:
                    o = float(b['open_price'])
                    cl = float(b['close_price'])
                except (TypeError, ValueError, KeyError):
                    c['bad_price'] += 1
                    continue
                if not (o > 0 and cl > 0):
                    c['bad_price'] += 1
                    continue
                if date in store:
                    c['dup'] += 1
                    if store[date] != (o, cl):
                        c['dup_mismatch'] += 1
                    continue
                store[date] = (o, cl)
    out = {}
    for sym, store in bars.items():
        dates = sorted(store)
        out[sym] = dict(dates=dates,
                        open=[store[x][0] for x in dates],
                        close=[store[x][1] for x in dates])
        rep[sym]['kept'] = len(dates)
        rep[sym]['first'] = dates[0] if dates else None
        rep[sym]['last'] = dates[-1] if dates else None
    return out, rep


def nvda_break_check():
    """Diagnostic only: show the raw NVDA bars around the 2000-10-27 break."""
    with open(os.path.join(RAW, 'd0a.json')) as fh:
        j = json.load(fh)
    d = j['data'] if 'data' in j else j
    rows = []
    for res in d['results']:
        if res['symbol'] != 'NVDA':
            continue
        for b in res['bars']:
            dt = b['begins_at'][:10]
            if '2000-10-24' <= dt <= '2000-11-01':
                rows.append((dt, b['open_price'], b['close_price'], b['volume']))
    return rows
