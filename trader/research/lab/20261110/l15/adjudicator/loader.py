"""Loader for L15 (analyst A). Written from scratch from the raw broker JSON.

Rules applied (from the task spec / README of 2026-11-09):
  - accept files with or without the outer "data" key
  - de-duplicate by date (file-boundary overlaps); when two files carry the same
    date keep the first one seen, and report any price disagreement
  - skip bars with zero / missing volume, or flagged interpolated
  - skip bars whose session is not 'reg' (none expected)
  - NVDA: drop every date <= 2000-10-27 (10x mis-scaled), start 2000-10-30
  - end the sample at 2026-11-06 (later bars are provisional)
"""
import json
import os

DATA_DIR = '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/rev/'
FILES = ['d0a', 'd0b', 'd1', 'd2', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6']
END_DATE = '2026-11-06'
NVDA_START = '2000-10-30'

NAMES = ['NVDA', 'AMD', 'INTC', 'MU', 'AAPL', 'MSFT', 'AMZN', 'QCOM', 'TXN', 'AMAT', 'ORCL']


def load_all(log=None):
    """Return {symbol: [(date, open, close), ...] sorted by date} and a list of log lines."""
    if log is None:
        log = []
    raw = {}      # sym -> date -> (open, close, volume, file)
    stats = {}    # sym -> counters
    for f in FILES:
        path = os.path.join(DATA_DIR, f + '.json')
        with open(path) as fh:
            j = json.load(fh)
        d = j.get('data', j)
        for res in d['results']:
            sym = res['symbol']
            st = stats.setdefault(sym, dict(total=0, dup=0, dup_mismatch=0, zero_vol=0,
                                            interp=0, nonreg=0, late=0, nvda_early=0,
                                            bad_price=0))
            book = raw.setdefault(sym, {})
            for b in res['bars']:
                st['total'] += 1
                date = b['begins_at'][:10]
                if date > END_DATE:
                    st['late'] += 1
                    continue
                if sym == 'NVDA' and date < NVDA_START:
                    st['nvda_early'] += 1
                    continue
                if b.get('interpolated'):
                    st['interp'] += 1
                    log.append('SKIP interpolated %s %s (file %s)' % (sym, date, f))
                    continue
                vol = b.get('volume')
                try:
                    volf = float(vol) if vol is not None else 0.0
                except (TypeError, ValueError):
                    volf = 0.0
                if volf <= 0:
                    st['zero_vol'] += 1
                    log.append('SKIP zero/missing volume %s %s (file %s)' % (sym, date, f))
                    continue
                if b.get('session', 'reg') != 'reg':
                    st['nonreg'] += 1
                    log.append('SKIP non-regular session %s %s (file %s)' % (sym, date, f))
                    continue
                try:
                    o = float(b['open_price'])
                    c = float(b['close_price'])
                except (TypeError, ValueError, KeyError):
                    st['bad_price'] += 1
                    log.append('SKIP unparsable price %s %s (file %s)' % (sym, date, f))
                    continue
                if not (o > 0 and c > 0):
                    st['bad_price'] += 1
                    log.append('SKIP non-positive price %s %s (file %s)' % (sym, date, f))
                    continue
                if date in book:
                    st['dup'] += 1
                    o0, c0, _, f0 = book[date]
                    if abs(o0 / o - 1) > 1e-6 or abs(c0 / c - 1) > 1e-6:
                        st['dup_mismatch'] += 1
                        log.append('DUP MISMATCH %s %s: %s o=%.6f c=%.6f vs %s o=%.6f c=%.6f (kept first)'
                                   % (sym, date, f0, o0, c0, f, o, c))
                    continue
                book[date] = (o, c, volf, f)
    out = {}
    for sym, book in raw.items():
        out[sym] = [(dt, book[dt][0], book[dt][1]) for dt in sorted(book)]
    return out, stats, log


if __name__ == '__main__':
    bars, stats, log = load_all()
    for sym in sorted(bars):
        b = bars[sym]
        print('%-5s n=%5d %s..%s  %s' % (sym, len(b), b[0][0], b[-1][0], stats[sym]))
    print('\n'.join(log))
