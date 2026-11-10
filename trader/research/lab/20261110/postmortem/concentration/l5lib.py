# L5 (LAB.md) - single-name risk: NVDL-only vs 50/50 NVDL+TQQQ vs TQQQ-only, overnight only.
# Read-only analysis. Loader + shared functions.
import json, math, csv
import numpy as np

BASE = '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/'
REV = BASE + 'rev/'
PM = BASE + 'pm/'
OUT = BASE + 'pm/concentration/'
EARN_CSV = '/home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv'
COST = 0.0009
SEED = 20261110


def loadbars(files, cutoff):
    """symbol -> {date: (open, close)}; drops interpolated / zero-volume bars and bars after cutoff."""
    out = {}
    for f in files:
        for x in json.load(open(f))['data']['results']:
            for b in x['bars']:
                if b.get('interpolated') or not b.get('volume'):
                    continue
                d = b['begins_at'][:10]
                if d > cutoff:
                    continue
                v = (float(b['open_price']), float(b['close_price']))
                prev = out.setdefault(x['symbol'], {}).get(d)
                if prev is not None and (abs(prev[0] - v[0]) > 1e-6 or abs(prev[1] - v[1]) > 1e-6):
                    print('  WARNING overlap mismatch', x['symbol'], d, prev, v, f)
                out[x['symbol']][d] = v
    return out


def load_long(cutoff='2026-11-06'):
    return loadbars([REV + 'd0b.json', REV + 'd1.json', REV + 'd2.json'], cutoff)


def load_pm():
    return loadbars([PM + 'day_0908_1110.json'], '2026-11-10')


def earnings_dates():
    return set(r['date'] for r in csv.DictReader(open(EARN_CSV)) if r['earn'] == '1')


def trend_states(qqq):
    """date -> (UP?, close, line) with line = mean of the previous 199 closes (RULES_v3 s13a)."""
    ds = sorted(qqq)
    c = np.array([qqq[d][1] for d in ds])
    cs = np.concatenate([[0.0], np.cumsum(c)])
    out = {}
    for i in range(199, len(ds)):
        line = (cs[i] - cs[i - 199]) / 199.0
        out[ds[i]] = (c[i] >= line, c[i], line)
    return out


def build_nights(B, first='2015-01-02', last_exit='2026-11-06'):
    """rows for consecutive common sessions t -> n of NVDA, TQQQ, QQQ."""
    ds = sorted(set(B['NVDA']) & set(B['TQQQ']) & set(B['QQQ']))
    T = trend_states(B['QQQ'])
    rows = []
    for i in range(len(ds) - 1):
        t, n = ds[i], ds[i + 1]
        if t < first or n > last_exit:
            continue
        legN = 2.0 * (B['NVDA'][n][0] / B['NVDA'][t][1] - 1.0)
        legT = B['TQQQ'][n][0] / B['TQQQ'][t][1] - 1.0
        qon = B['QQQ'][n][0] / B['QQQ'][t][1] - 1.0
        up, qc, line = T[t]
        rows.append(dict(d=t, n=n, legN=legN, legT=legT, qon=qon, up=bool(up), qc=qc, line=line,
                         nvda_on=B['NVDA'][n][0] / B['NVDA'][t][1] - 1.0))
    return rows


def account_returns(legN, legT, s, w, cost=COST):
    return s * (w * legN + (1.0 - w) * legT - cost)


def maxdd(R):
    E = np.cumprod(1.0 + R)
    E = np.concatenate([[1.0], E])
    pk = np.maximum.accumulate(E)
    return float((E / pk - 1.0).min())


def pause_flags(R):
    """flag[t] = equity after night t <= 0.80 x max(equity over the last 20 session points incl. today).
    Session points: the start (1.0) and the equity after each night."""
    E = np.concatenate([[1.0], np.cumprod(1.0 + R)])
    n = len(E)
    # rolling max over window of 20 ending at each index
    pad = np.concatenate([np.full(19, E[0]), E])
    from numpy.lib.stride_tricks import sliding_window_view
    hi = sliding_window_view(pad, 20).max(axis=1)
    fl = E <= 0.80 * hi
    return fl[1:], E  # per night


def pause_episodes(fl, gap=5):
    """episodes: a trigger night more than `gap` sessions after the previous trigger night starts a new one."""
    idx = np.flatnonzero(fl)
    if len(idx) == 0:
        return 0
    return int(1 + np.sum(np.diff(idx) > gap))


def stats(R):
    R = np.asarray(R, float)
    fl, E = pause_flags(R)
    return dict(n=int(len(R)), g=100 * float(np.mean(np.log1p(R))), mean=100 * float(R.mean()),
                sd=100 * float(R.std(ddof=1)), worst=100 * float(R.min()), best=100 * float(R.max()),
                maxdd=100 * maxdd(R), pause_nights=int(fl.sum()), pause_eps=pause_episodes(fl),
                mult=float(E[-1]))


def year_blocks(dates):
    yb = {}
    for i, d in enumerate(dates):
        yb.setdefault(d[:4], []).append(i)
    return {y: np.array(v) for y, v in yb.items()}


def bootstrap(Rmat, dates, ndraw=2000, seed=SEED, horizon=250, offset=True, kill_levels=(0.5,), blocklen=None):
    """Year-block bootstrap, paired across columns of Rmat (nights x variants).
    Each draw: K calendar-year blocks drawn with replacement (K = number of years in the sample),
    concatenated in drawn order. If offset, the path starts at a uniformly random night inside the first
    block (one extra block appended so the path keeps full length). Path statistics on the full path;
    KILL/PAUSE-within-horizon on the first `horizon` nights.
    blocklen: if given, use fixed-length circular blocks of that many nights instead of calendar years."""
    rng = np.random.default_rng(seed)
    nN, nV = Rmat.shape
    if blocklen is None:
        yb = year_blocks(dates)
        years = sorted(yb)
        K = len(years)
    res = dict(g=np.zeros((ndraw, nV)), sd=np.zeros((ndraw, nV)), worst=np.zeros((ndraw, nV)),
               maxdd=np.zeros((ndraw, nV)), eps=np.zeros((ndraw, nV)), pn=np.zeros((ndraw, nV)),
               pause_h=np.zeros((ndraw, nV), bool), minE_h=np.zeros((ndraw, nV)), n=np.zeros(ndraw, int),
               endE_h=np.zeros((ndraw, nV)))
    for k in range(ndraw):
        if blocklen is None:
            pick = rng.choice(len(years), K + (1 if offset else 0))
            idx = np.concatenate([yb[years[j]] for j in pick])
            if offset:
                u = int(rng.integers(0, len(yb[years[pick[0]]])))
                idx = idx[u:u + nN] if len(idx) - u >= nN else idx[u:]
        else:
            nb = int(math.ceil(nN / blocklen))
            starts = rng.integers(0, nN, nb)
            idx = np.concatenate([(s + np.arange(blocklen)) % nN for s in starts])[:nN]
        P = Rmat[idx]
        res['n'][k] = len(idx)
        res['g'][k] = 100 * np.log1p(P).mean(axis=0)
        res['sd'][k] = 100 * P.std(axis=0, ddof=1)
        res['worst'][k] = 100 * P.min(axis=0)
        for v in range(nV):
            fl, E = pause_flags(P[:, v])
            pk = np.maximum.accumulate(E)
            res['maxdd'][k, v] = 100 * (E / pk - 1).min()
            res['eps'][k, v] = pause_episodes(fl) * 1000.0 / len(idx)
            res['pn'][k, v] = fl.sum() * 1000.0 / len(idx)
            res['pause_h'][k, v] = fl[:horizon].any()
            res['minE_h'][k, v] = E[:horizon + 1].min()
            res['endE_h'][k, v] = E[min(horizon, len(E) - 1)]
    return res


def pct(a, q):
    return float(np.percentile(a, q))


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1])
