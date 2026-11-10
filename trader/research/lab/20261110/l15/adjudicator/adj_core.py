"""Adjudicator's own minimal implementation for L15 (third, independent of analysts A and B).

Loader: pandas. Trend: pandas shift/rolling. Simulation: explicit "night number inside the
pause" counter k (0 = not paused, k = 1..N the k-th mandatory night, k > N an extension night).
No code is shared with analyst_a/ or analyst_b/.
"""
import json
import math
import collections
import numpy as np
import pandas as pd

RAW = '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/rev'
FILES = ['d0a', 'd0b', 'd1', 'd2', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6']
NAMES = ['NVDA', 'AMD', 'INTC', 'MU', 'AAPL', 'MSFT', 'AMZN', 'QCOM', 'TXN', 'AMAT', 'ORCL']
END = '2026-11-06'
COST = 0.0009
UP, DOWN = 0.98, 0.25


def load_frames():
    parts = []
    for f in FILES:
        with open('%s/%s.json' % (RAW, f)) as fh:
            j = json.load(fh)
        d = j['data'] if 'data' in j else j
        for res in d['results']:
            df = pd.DataFrame(res['bars'])
            df['sym'] = res['symbol']
            df['file'] = f
            parts.append(df)
    a = pd.concat(parts, ignore_index=True)
    a['date'] = a['begins_at'].str.slice(0, 10)
    a['o'] = pd.to_numeric(a['open_price'], errors='coerce')
    a['c'] = pd.to_numeric(a['close_price'], errors='coerce')
    a['v'] = pd.to_numeric(a['volume'], errors='coerce')
    if 'interpolated' not in a:
        a['interpolated'] = None
    a['interp'] = a['interpolated'].fillna(False).astype(bool)
    rep = {}
    out = {}
    for sym, g in a.groupby('sym', sort=False):
        n0 = len(g)
        late = g['date'] > END
        early = (sym == 'NVDA') & (g['date'] <= '2000-10-27')
        bad = g['interp'] | ~(g['v'] > 0) | ~(g['o'] > 0) | ~(g['c'] > 0)
        k = g[~late & ~early & ~bad]
        ndup = int(k.duplicated('date').sum())
        # check duplicates carry the same prices
        dd = k[k.duplicated('date', keep=False)].groupby('date').agg(o=('o', 'nunique'), c=('c', 'nunique'))
        mism = int(((dd['o'] > 1) | (dd['c'] > 1)).sum()) if len(dd) else 0
        k = k.drop_duplicates('date', keep='first').sort_values('date')
        rep[sym] = dict(raw=n0, late=int(late.sum()), early=int((early & ~late).sum()),
                        bad=int((bad & ~late & ~early).sum()),
                        bad_dates=list(g.loc[bad & ~late & ~early, 'date'])[:5],
                        dup=ndup, dup_mismatch=mism, kept=len(k),
                        first=k['date'].iloc[0], last=k['date'].iloc[-1])
        out[sym] = k[['date', 'o', 'c']].set_index('date')
    return out, rep


def trend_series(q):
    """True/False per QQQ session once 199 prior closes exist, else NaN (object)."""
    prev_mean = q['c'].shift(1).rolling(199).mean()
    up = (q['c'] >= prev_mean).where(prev_mean.notna())
    return up, prev_mean


def nights(frames, sym, up, start=None):
    x = frames[sym]
    q = frames['QQQ']
    common = x.index.intersection(q.index)
    x = x.loc[sorted(common)]
    r = (x['o'].shift(-1) / x['c'] - 1.0).iloc[:-1]
    ex = pd.Series(x.index, index=x.index).shift(-1).iloc[:-1]
    t = up.reindex(r.index)
    keep = t.notna()
    if start:
        keep &= (r.index >= start)
    r, ex, t = r[keep], ex[keep], t[keep].astype(bool)
    return dict(dates=list(r.index), exit=list(ex.values), r=r.values.astype(float),
                up=t.values.astype(bool))


def simulate(r, b, rule, p=0.25, N=5, rearm='post', thr=0.80, win=20):
    """rule: 'P0', 'P1', 'P2', 'P3'.  rearm (P2): 'post' = the re-arm test happens only on
    nights that are not part of the pause; 'during' = any night after the start night."""
    n = len(r)
    E = 1.0
    last = collections.deque([1.0], maxlen=win)
    k = 0            # position inside a pause
    armed = True
    size = np.empty(n)
    lr = np.empty(n)
    pz = np.zeros(n, dtype=bool)
    C = np.zeros(n, dtype=bool)
    Ein = np.empty(n)
    starts = []
    for t in range(n):
        Ein[t] = E
        c = E <= thr * max(last)
        C[t] = c
        if rule == 'P0':
            paused = False
        elif rule == 'P3':
            paused = bool(c)
            if paused and (t == 0 or not pz[t - 1]):
                starts.append(t)
        elif rule == 'P1':
            if k == 0:
                if c:
                    k = 1
                    starts.append(t)
            else:
                k += 1
                if k > N and not c:
                    k = 0
            paused = k > 0
        elif rule == 'P2':
            if 1 <= k < N:               # still inside the fixed pause
                k += 1
                if rearm == 'during' and not c:
                    armed = True
            else:                         # not paused (k == 0) or pause just ran out (k == N)
                k = 0
                if not c:
                    armed = True
                elif armed:
                    k = 1
                    armed = False
                    starts.append(t)
            paused = k > 0
        else:
            raise ValueError(rule)
        pz[t] = paused
        s = min(b[t], p) if paused else b[t]
        size[t] = s
        R = s * (2.0 * r[t] - COST)
        lr[t] = math.log1p(R)
        E *= (1.0 + R)
        last.append(E)
    # episodes
    eps = []
    if rule == 'P2':
        eps = [(s0, min(N, n - s0)) for s0 in starts]
    elif rule in ('P1', 'P3'):
        for s0 in starts:
            e = s0
            while e < n and pz[e]:
                e += 1
            eps.append((s0, e - s0))
    return dict(size=size, lr=lr, pz=pz, C=C, Ein=Ein, starts=starts, eps=eps)


def maxdd(lr):
    path = np.concatenate(([0.0], np.cumsum(lr)))
    pk = np.maximum.accumulate(path)
    return 100.0 * (1.0 - math.exp((path - pk).min()))


def pstats(res, mask):
    lr = res['lr'][mask]
    idx = np.where(mask)[0]
    lo, hi = idx[0], idx[-1]
    eps = [(s0, L) for s0, L in res['eps'] if lo <= s0 <= hi]
    lens = [L for _, L in eps]
    return dict(n=len(lr), g=100.0 * lr.mean(), mult=math.exp(lr.sum()), dd=maxdd(lr),
                eps=len(eps), paused=int(res['pz'][mask].sum()),
                med=(float(np.median(lens)) if lens else float('nan')), mx=(max(lens) if lens else 0))


def masks(dates):
    d = np.array(dates)
    return {'H1': d <= '2014-12-31', 'H2': d >= '2015-01-02', 'ALL': np.ones(len(d), dtype=bool)}
