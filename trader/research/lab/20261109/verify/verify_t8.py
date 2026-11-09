"""Independent re-derivation of the t8 backtest (2x overnight, 200d trend sizing).
Run: python3 -I verify_t8.py
Reads JSON bars + earnings CSV only. Writes nothing outside stdout."""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/verify_t8')
import numpy as np
import pandas as pd
import vload

COST = 0.0009
LEV = 2.0
FLOOR = -0.95
PERIODS = [(2000, 2014), (2015, 2026), (2000, 2026)]
NAMES = ['NVDA', 'AMD', 'INTC', 'MU', 'AAPL', 'MSFT', 'AMZN', 'QCOM', 'TXN', 'AMAT', 'ORCL']
EARN_CSV = '/home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv'

raw = vload.load_raw()
PX = vload.build(raw)


# ---------------------------------------------------------------- core
def prep(df, L=200, brk_r=0.45, brk_io=0.6, quarantine=200, use_breaks=True):
    """Per-symbol frame: r (overnight t->t+1), sma (closes t-L+1..t), below, valid, brk."""
    c = df.c.values; o = df.o.values; n = len(df)
    r = np.full(n, np.nan); r[:-1] = o[1:] / c[:-1] - 1.0
    io = c / o - 1.0
    with np.errstate(invalid='ignore'):
        brk = (np.abs(r) > brk_r) | (np.abs(io) > brk_io)
    if not use_breaks:
        brk = np.zeros(n, bool)
    idx = np.arange(n)
    last = np.maximum.accumulate(np.where(brk, idx, -10**9))      # last break index <= t
    q = max(L, quarantine)
    sma = pd.Series(c).rolling(L, min_periods=L).mean().values      # inclusive of t, backward only
    valid = (idx >= L - 1) & ((idx - last) >= q) & np.isfinite(sma)
    below = np.where(valid, (c < sma).astype(float), np.nan)
    return pd.DataFrame(dict(c=c, r=r, sma=sma, below=below, valid=valid, brk=brk, io=io), index=df.index)


def nights(sym, mkt='QQQ', L_own=200, L_mkt=200, px=None, use_breaks=True, mkt_lag=0):
    """Joined frame of usable nights for sym with market state. mkt_lag=1 -> state from close(t-1)."""
    px = px or PX
    s = prep(px[sym], L_own, use_breaks=use_breaks)
    m = prep(px[mkt], L_mkt)
    mb = m.below
    if mkt_lag:
        mb = mb.shift(mkt_lag)          # shift on the market's own bar index (prior trading day)
    mb = mb.reindex(s.index, method='ffill')      # no-op unless market proxy lacks a bar (SPY 2004)
    d = pd.DataFrame(dict(r=s.r, own=s.below, mk=mb, brk=s.brk), index=s.index)
    d = d[np.isfinite(d.r) & d.own.notna() & d.mk.notna() & (~d.brk)]
    d['R'] = np.maximum(FLOOR, LEV * d.r)
    return d


def sizes(d, rule, dsz=0.25):
    o = d.own.values == 1; m = d.mk.values == 1
    if rule == 'full':
        b = np.zeros(len(d), bool)
    elif rule == 'own':
        b = o
    elif rule == 'mkt':
        b = m
    elif rule == 'both':
        b = o & m
    elif rule == 'either':
        b = o | m
    else:
        raise ValueError(rule)
    return np.where(b, dsz, 1.0)


def strat(d, rule, dsz=0.25, col='R', cost=COST):
    return sizes(d, rule, dsz) * (d[col].values - cost)


def g100(x):
    return 100.0 * np.mean(np.log1p(x)) if len(x) else np.nan


def maxdd(x):
    if not len(x):
        return np.nan
    eq = np.concatenate([[1.0], np.cumprod(1.0 + x)])
    return float(np.max(1.0 - eq / np.maximum.accumulate(eq)))


def psel(d, a, b):
    y = d.index.year
    return d[(y >= a) & (y <= b)]


RULES = ['full', 'own', 'mkt', 'both', 'either']


def rule_table(d, rules=RULES, periods=PERIODS, title='', col='R'):
    print(title)
    print(f"  {'period':<10}{'n':>6} " + ' '.join(f"{r+' g%':>10}{'DD':>5}" for r in rules))
    for a, b in periods:
        p = psel(d, a, b)
        cells = []
        for r in rules:
            x = strat(p, r, col=col)
            cells.append(f"{g100(x):>10.3f}{100*maxdd(x):>4.0f}%" if len(p) else f"{'-':>10}{'-':>5}")
        print(f"  {str(a)+'-'+str(b):<10}{len(p):>6} " + ' '.join(cells))


def hdr(s):
    print('\n' + '=' * 100 + '\n' + s + '\n' + '=' * 100)


# ---------------------------------------------------------------- data notes
hdr('DATA / STEP 3: break filter trips (|r|>0.45 or |c/o-1|>0.6), all symbols used')
for sym in ['QQQ', 'SPY', 'SMH'] + NAMES + ['NVDL', 'NVDX']:
    s = prep(PX[sym])
    t = s[s.brk]
    first_valid = s.index[s.valid.values][0].date() if s.valid.any() else None
    mx_r = s.r.abs().max(); mx_io = s.io.abs().max()
    print(f"  {sym:<5} bars={len(s):>5} {s.index[0].date()}..{s.index[-1].date()} first valid state {first_valid} "
          f"max|r|={mx_r:.3f} max|c/o-1|={mx_io:.3f} trips={len(t)}"
          + ''.join(f"  [{i.date()} r={row.r:+.3f} c/o-1={row.io:+.3f}]" for i, row in t.iterrows()))
for sym in ['NVDA', 'QQQ']:
    s = prep(PX[sym])
    top = s.r.abs().sort_values(ascending=False).head(6)
    print(f"  {sym} six largest |overnight|: " + ', '.join(f"{i.date()} {s.r[i]:+.3f}" for i in top.index))

# ---------------------------------------------------------------- steps 4-6 NVDA
hdr('STEPS 4-6: NVDA rule table (mean log growth %/night, max DD), spec-literal')
dN = nights('NVDA')
print(f"  NVDA usable nights {len(dN)}: {dN.index[0].date()} .. {dN.index[-1].date()}  "
      f"(own BELOW {int(dN.own.sum())}, QQQ BELOW {int(dN.mk.sum())})")
rule_table(dN, title='  NVDA')

hdr('STEP 7: NVDA 2x2 cells of R (gross, no cost): n, mean %, sd %, 100*mean ln(1+R)')
for a, b in PERIODS:
    p = psel(dN, a, b)
    print(f"  {a}-{b}")
    for own in (0, 1):
        for mk in (0, 1):
            c = p[(p.own == own) & (p.mk == mk)].R.values
            lab = f"own {'BELOW' if own else 'ABOVE'} / QQQ {'BELOW' if mk else 'ABOVE'}"
            if len(c) > 1:
                print(f"    {lab:<26} n={len(c):>5} mean={100*c.mean():>7.3f} sd={100*c.std(ddof=1):>6.3f} "
                      f"lg={g100(c):>7.3f}  min={100*c.min():>6.1f}")
            else:
                print(f"    {lab:<26} n={len(c):>5}")
    for mk in (0, 1):
        c = p[p.mk == mk].R.values
        print(f"    {'ALL own / QQQ ' + ('BELOW' if mk else 'ABOVE'):<26} n={len(c):>5} mean={100*c.mean():>7.3f} "
              f"sd={100*c.std(ddof=1):>6.3f} lg={g100(c):>7.3f}  min={100*c.min():>6.1f}")

# ---------------------------------------------------------------- step 8
hdr('STEP 8: rule tables for the other names + counts')
ALLD = {'NVDA': dN}
for sym in NAMES[1:]:
    ALLD[sym] = nights(sym)
for sym in NAMES:
    d = ALLD[sym]
    rule_table(d, title=f"  {sym}  ({len(d)} nights, {d.index[0].date()}..{d.index[-1].date()})")
print('\n  count of 11 names with rule > full on mean log growth')
print(f"  {'period':<10}{'mkt':>6}{'own':>6}{'both':>6}{'either':>8}   names where mkt<=full")
for a, b in PERIODS:
    cnt = {r: 0 for r in RULES[1:]}; losers = []
    for sym in NAMES:
        p = psel(ALLD[sym], a, b)
        f = g100(strat(p, 'full'))
        for r in RULES[1:]:
            if g100(strat(p, r)) > f:
                cnt[r] += 1
            elif r == 'mkt':
                losers.append(sym)
    print(f"  {str(a)+'-'+str(b):<10}{cnt['mkt']:>6}{cnt['own']:>6}{cnt['both']:>6}{cnt['either']:>8}   {','.join(losers)}")
print('\n  mkt - full (g %/night) per name')
print('  ' + f"{'period':<10}" + ''.join(f"{s:>8}" for s in NAMES) + f"{'median':>8}")
for a, b in PERIODS:
    v = [g100(strat(psel(ALLD[s], a, b), 'mkt')) - g100(strat(psel(ALLD[s], a, b), 'full')) for s in NAMES]
    print('  ' + f"{str(a)+'-'+str(b):<10}" + ''.join(f"{x:>8.3f}" for x in v) + f"{np.median(v):>8.3f}")

# ---------------------------------------------------------------- A
hdr('A: NVDA 2015-2026, earnings nights (earn=1) removed')
e = pd.read_csv(EARN_CSV)
earn_dates = pd.to_datetime(e.loc[e.earn == 1, 'date'])
p = psel(dN, 2015, 2026)
pe = p[~p.index.isin(earn_dates)]
print(f"  earnings nights in csv {len(earn_dates)}; in my 2015-26 sample {int(p.index.isin(earn_dates).sum())}; "
      f"of those QQQ-BELOW {int(p[p.index.isin(earn_dates)].mk.sum())}")
for lab, q in (('all nights', p), ('ex-earnings', pe), ('earnings only', p[p.index.isin(earn_dates)])):
    print(f"  {lab:<14} n={len(q):>5} " + ' '.join(
        f"{r}: g={g100(strat(q, r)):>7.3f} DD={100*maxdd(strat(q, r)):>3.0f}%" for r in ('full', 'own', 'mkt')))

# ---------------------------------------------------------------- B
hdr('B: real instruments NVDL / NVDX (actual close->next open, no multiplier), QQQ state')
qs = prep(PX['QQQ'])
nv = PX['NVDA']; nv_r = pd.Series(nv.o.shift(-1) / nv.c - 1, index=nv.index)
for sym in ('NVDL', 'NVDX'):
    df = PX[sym]
    nxt = pd.Series(df.index[1:], index=df.index[:-1])
    d = pd.DataFrame(dict(r=df.o.shift(-1) / df.c - 1), index=df.index).iloc[:-1]
    d['mk'] = qs.below.reindex(d.index); d['own'] = 0.0
    d['R'] = d.r                      # already leveraged
    d['nvda'] = nv_r.reindex(d.index)
    # keep only true one-session nights (next bar is next QQQ trading day)
    qnext = pd.Series(qs.index[1:], index=qs.index[:-1]).reindex(d.index)
    skip = (nxt.reindex(d.index) != qnext)
    print(f"  {sym}: {len(d)} nights {d.index[0].date()}..{d.index[-1].date()}, nights spanning a missing session: {int(skip.sum())} (dropped)")
    d = d[~skip.values & d.mk.notna()]
    # leverage actually delivered overnight, by calendar year
    lv = []
    for y, gdf in d.groupby(d.index.year):
        beta = np.polyfit(gdf.nvda.values, gdf.r.values, 1)[0]
        lv.append(f"{y}:{beta:.2f}")
    print(f"    OLS beta of {sym} overnight on NVDA overnight by year: " + ' '.join(lv))
    for mk in (0, 1):
        c = d[d.mk == mk].R.values
        s2 = np.maximum(FLOOR, 2 * d[d.mk == mk].nvda.values)
        print(f"    QQQ {'BELOW' if mk else 'ABOVE'}: n={len(c):>4} mean={100*c.mean():>7.3f}% sd={100*c.std(ddof=1):>6.3f}% "
              f"lg={g100(c):>7.3f}   | synthetic 2x NVDA same nights: mean={100*s2.mean():>7.3f}% lg={g100(s2):>7.3f}")
    xf = strat(d, 'full'); xm = strat(d, 'mkt')
    print(f"    rule table (cost 9bp): n={len(d)}  full g={g100(xf):.3f} DD={100*maxdd(xf):.0f}%   "
          f"mkt g={g100(xm):.3f} DD={100*maxdd(xm):.0f}%   diff={g100(xm)-g100(xf):+.3f}")
    # distinct BELOW episodes
    b = d.mk.values; ep = int(((b[1:] == 1) & (b[:-1] == 0)).sum() + (b[0] == 1))
    print(f"    QQQ-BELOW nights fall in {ep} separate episodes; by year: "
          + str(d[d.mk == 1].groupby(d[d.mk == 1].index.year).size().to_dict()))
    dd = np.log1p(xm) - np.log1p(xf)
    bel = d[d.mk == 1]
    se = dd.std(ddof=1) / np.sqrt(len(dd))
    print(f"    naive iid t-stat of (mkt-full) per night: {dd.mean()/se:.2f}")

# ---------------------------------------------------------------- C
hdr('C: look-ahead audit')
# (i) truncation test: state at t recomputed from data truncated at t must equal full-sample state
rng = np.random.default_rng(7)
bad = 0
for sym in ('QQQ', 'NVDA'):
    full = prep(PX[sym])
    vi = np.where(full.valid.values)[0]
    for t in rng.choice(vi, 300, replace=False):
        tr = prep(PX[sym].iloc[:t + 1])
        if tr.below.iloc[-1] != full.below.iloc[t] or abs(tr.sma.iloc[-1] - full.sma.iloc[t]) > 1e-12:
            bad += 1
        # explicit definition check
        c = PX[sym].c.values
        if abs(c[t - 199:t + 1].mean() - full.sma.iloc[t]) > 1e-9:
            bad += 1
print(f"  truncation/definition test on 600 random (symbol,t): mismatches = {bad}  (0 => state(t) uses closes <= t only)")
# break flag for night t uses open(t+1): only used to DROP night t and later nights, never to set state before t
d0 = nights('NVDA'); d1 = nights('NVDA', mkt_lag=1); dm = nights('NVDA', mkt_lag=-1)
common = d0.index.intersection(d1.index).intersection(dm.index)
flip = int((d0.mk.reindex(common) != d1.mk.reindex(common)).sum())
print(f"  nights where QQQ state(t) != state(t-1): {flip} of {len(common)}")
print(f"  {'period':<10}{'n':>6}{'full':>9}{'mkt(t)':>9}{'mkt(t-1)':>10}{'diff':>8}{'mkt(t+1) LOOKAHEAD':>20}")
for a, b in PERIODS:
    p0 = psel(d0.loc[common], a, b); p1 = psel(d1.loc[common], a, b); pm = psel(dm.loc[common], a, b)
    g0 = g100(strat(p0, 'mkt')); g1 = g100(strat(p1, 'mkt')); gm = g100(strat(pm, 'mkt'))
    print(f"  {str(a)+'-'+str(b):<10}{len(p0):>6}{g100(strat(p0,'full')):>9.3f}{g0:>9.3f}{g1:>10.3f}{g1-g0:>+8.3f}{gm:>20.3f}")

# ---------------------------------------------------------------- D
hdr('D: sensitivity of mkt rule on NVDA: cell = mkt g%/night (delta vs full); common sample across all configs')
cfg = {}
for proxy in ('QQQ', 'SPY'):
    for L in (100, 150, 200, 250):
        dd_ = nights('NVDA', mkt=proxy, L_mkt=L)
        cfg[(proxy, L)] = dd_[dd_.index.isin(dN.index)]
common_idx = dN.index
for v in cfg.values():
    common_idx = common_idx.intersection(v.index)
dNc = dN.loc[common_idx]
print(f"  common sample {len(common_idx)} nights ({common_idx[0].date()}..{common_idx[-1].date()}); "
      f"baseline sample has {len(dN)} (the {len(dN)-len(common_idx)} extra are Oct-2000 nights before SMA250 exists)")
print(f"  {'proxy':<5}{'SMA':>5}{'dsz':>6} " + ' '.join(f"{str(a)+'-'+str(b):>20}" for a, b in PERIODS) + '   nBELOW(00-26)')
fulls = [g100(strat(psel(dNc, a, b), 'full')) for a, b in PERIODS]
print(f"  {'full':<16} " + ' '.join(f"{f:>20.3f}" for f in fulls) + '   n=' + '/'.join(str(len(psel(dNc, a, b))) for a, b in PERIODS))
for proxy in ('QQQ', 'SPY'):
    for L in (100, 150, 200, 250):
        dd_ = cfg[(proxy, L)].loc[common_idx]
        for dsz in (0.0, 0.25, 0.5):
            cells = []
            for (a, b), f in zip(PERIODS, fulls):
                p = psel(dd_, a, b)
                g = g100(strat(p, 'mkt', dsz=dsz))
                cells.append(f"{g:>10.3f} ({g-f:+.3f})")
            print(f"  {proxy:<5}{L:>5}{dsz:>6.2f} " + ' '.join(f"{c:>20}" for c in cells) + f"   {int(dd_.mk.sum())}")

# constant-size benchmarks (is the gain timing or just de-levering?)
print('\n  constant-size benchmarks on NVDA (same nights): g%/night')
print(f"  {'period':<10}{'avg size mkt':>13}{'const=avg':>11}{'const .25':>11}{'const .5':>10}{'const .75':>11}{'full':>8}{'mkt':>8}{'best const f':>14}")
for a, b in PERIODS:
    p = psel(dN, a, b); x = p.R.values - COST
    sbar = sizes(p, 'mkt').mean()
    grid = np.linspace(0.05, 3, 60); gg = [g100(np.maximum(f * x, -0.999)) for f in grid]
    print(f"  {str(a)+'-'+str(b):<10}{sbar:>13.3f}{g100(sbar*x):>11.3f}{g100(.25*x):>11.3f}{g100(.5*x):>10.3f}{g100(.75*x):>11.3f}"
          f"{g100(x):>8.3f}{g100(strat(p,'mkt')):>8.3f}{grid[int(np.argmax(gg))]:>14.2f}")

# ---------------------------------------------------------------- E
hdr('E: NVDA sub-periods, full vs mkt')
SUB = [(2000, 2004), (2005, 2009), (2010, 2014), (2015, 2019), (2020, 2022), (2023, 2026)]
print(f"  {'period':<10}{'n':>6}{'nBELOW':>8}{'full g':>9}{'DD':>5}{'mkt g':>9}{'DD':>5}{'diff':>8}   mean R% ABOVE / BELOW   sd R% ABOVE / BELOW")
for a, b in SUB:
    p = psel(dN, a, b); xf = strat(p, 'full'); xm = strat(p, 'mkt')
    ab = p[p.mk == 0].R.values; be = p[p.mk == 1].R.values
    print(f"  {str(a)+'-'+str(b):<10}{len(p):>6}{int(p.mk.sum()):>8}{g100(xf):>9.3f}{100*maxdd(xf):>4.0f}%{g100(xm):>9.3f}{100*maxdd(xm):>4.0f}%"
          f"{g100(xm)-g100(xf):>+8.3f}   {100*ab.mean():>7.3f} / {100*be.mean() if len(be) else float('nan'):>7.3f}"
          f"      {100*ab.std(ddof=1):>6.3f} / {100*be.std(ddof=1) if len(be)>1 else float('nan'):>6.3f}")
print('  by calendar year (diff = mkt - full, g%/night; contribution = diff*n in log points)')
rows = []
for y in range(2000, 2027):
    p = psel(dN, y, y)
    if not len(p):
        continue
    xf = strat(p, 'full'); xm = strat(p, 'mkt')
    rows.append((y, len(p), int(p.mk.sum()), g100(xf), g100(xm), (np.log1p(xm) - np.log1p(xf)).sum()))
print('  ' + '  '.join(f"{y}:{nb}/{n} {c:+.2f}" for y, n, nb, gf, gm, c in rows))
print(f"  years mkt>full: {sum(1 for r in rows if r[5] > 1e-12)}, mkt<full: {sum(1 for r in rows if r[5] < -1e-12)}, "
      f"no BELOW nights: {sum(1 for r in rows if r[2] == 0)}")

# ---------------------------------------------------------------- F
hdr('F: uncertainty on (mkt - full) mean log growth per night, NVDA')
def boot(p, B=20000, block=20, seed=11):
    xf = strat(p, 'full'); xm = strat(p, 'mkt')
    d = np.log1p(xm) - np.log1p(xf); n = len(d)
    rng = np.random.default_rng(seed)
    # circular moving-block bootstrap
    nb = int(np.ceil(n / block)); out = np.empty(B)
    off = np.arange(block)
    for i in range(0, B, 500):
        st = rng.integers(0, n, size=(min(500, B - i), nb))
        ix = (st[:, :, None] + off[None, None, :]) % n
        out[i:i + st.shape[0]] = d[ix.reshape(st.shape[0], -1)[:, :n]].mean(axis=1)
    # year-block bootstrap (ratio estimator)
    yrs = p.index.year.values; uy = np.unique(yrs)
    sy = np.array([d[yrs == y].sum() for y in uy]); ny = np.array([(yrs == y).sum() for y in uy])
    pick = rng.integers(0, len(uy), size=(B, len(uy)))
    outy = sy[pick].sum(axis=1) / ny[pick].sum(axis=1)
    # Newey-West t
    m = d.mean(); u = d - m; lag = 20
    v = (u @ u) / n + 2 * sum((1 - k / (lag + 1)) * (u[k:] @ u[:-k]) / n for k in range(1, lag + 1))
    tnw = m / np.sqrt(v / n)
    return d, out, outy, tnw

for a, b in [(2000, 2026), (2000, 2014), (2015, 2026)]:
    p = psel(dN, a, b)
    d, out, outy, tnw = boot(p)
    _, out60, _, _ = boot(p, block=60, seed=12)
    print(f"  {a}-{b}: n={len(d)}, BELOW nights={int(p.mk.sum())}, point diff = {100*d.mean():+.4f} %/night, NW(20) t = {tnw:.2f}")
    for lab, o in (('20-night blocks', out), ('60-night blocks', out60), ('year blocks', outy)):
        lo, hi = np.percentile(100 * o, [5, 95])
        print(f"     {lab:<16} 90% CI [{lo:+.4f}, {hi:+.4f}]  P(mkt>full) = {np.mean(o > 0):.3f}")

# concentration: how much of the total gain comes from a few nights
p = psel(dN, 2000, 2026)
xf = strat(p, 'full'); xm = strat(p, 'mkt'); d = pd.Series(np.log1p(xm) - np.log1p(xf), index=p.index)
tot = d.sum()
top = d.sort_values(ascending=False).head(8)
print(f"\n  concentration 2000-2026: total gain = {tot:.3f} log points over {len(d)} nights ({100*d.mean():+.4f} %/night)")
for i, v in top.items():
    print(f"     {i.date()}  NVDA overnight {100*p.r[i]:+6.1f}%  contributes {v:+.3f} log pts ({100*v/tot:4.0f}% of total)")
for k in (1, 3, 5, 10):
    rest = d.drop(d.sort_values(ascending=False).head(k).index)
    print(f"     drop top {k:>2} nights: diff = {100*rest.sum()/len(d):+.4f} %/night  ({100*rest.sum()/tot:4.0f}% of total remains)")
bel = p[p.mk == 1]
print(f"     BELOW nights: sum of all positive contributions {d[d>0].sum():.3f}, all negative {d[d<0].sum():.3f}")
# same for each period, excluding nights with |r|>20% (single-stock blowups)
for a, b in PERIODS:
    q = psel(dN, a, b); q2 = q[q.r.abs() <= 0.20]
    print(f"     {a}-{b} excluding |NVDA overnight|>20% nights ({len(q)-len(q2)} dropped): full {g100(strat(q2,'full')):.3f}  "
          f"mkt {g100(strat(q2,'mkt')):.3f}  diff {g100(strat(q2,'mkt'))-g100(strat(q2,'full')):+.3f}")

# placebo: circularly shift the QQQ state vs NVDA nights
p = dN.copy(); obs = g100(strat(p, 'mkt')) - g100(strat(p, 'full'))
rng = np.random.default_rng(5); n = len(p); sh = []
for k in rng.integers(250, n - 250, size=3000):
    q = p.copy(); q['mk'] = np.roll(p.mk.values, k)
    sh.append(g100(strat(q, 'mkt')) - g100(strat(q, 'full')))
sh = np.array(sh)
print(f"\n  placebo (QQQ state circularly shifted by random >=250 nights, 3000 draws): observed diff {obs:+.4f}; "
      f"placebo mean {sh.mean():+.4f}, 5-95% [{np.percentile(sh,5):+.4f}, {np.percentile(sh,95):+.4f}], "
      f"P(placebo >= observed) = {np.mean(sh >= obs):.3f}")

# ---------------------------------------------------------------- G
hdr('G: state on last bar')
for sym in ('QQQ', 'NVDA', 'SMH'):
    s = prep(PX[sym]); i = s.index[-1]
    print(f"  {sym:<5} {i.date()} close={s.c[i]:.4f} sma200={s.sma[i]:.4f} dist={100*(s.c[i]/s.sma[i]-1):+.2f}%  "
          f"state={'BELOW' if s.below[i]==1 else 'ABOVE'}  valid={bool(s.valid[i])}")
    b = s.below.values; k = len(b) - 1
    while k > 0 and b[k - 1] == b[k]:
        k -= 1
    print(f"        in this state since close of {s.index[k].date()} ({len(b)-k} bars)")

# ---------------------------------------------------------------- extras: spec robustness
hdr('EXTRA 1: NVDA with the 2000 scale error repaired (pre-2000-10-30 bars /10) instead of quarantined')
px2 = dict(PX); n2 = PX['NVDA'].copy()
m = n2.index <= pd.Timestamp('2000-10-27')
n2.loc[m, ['o', 'h', 'l', 'c']] = n2.loc[m, ['o', 'h', 'l', 'c']] / 10.0
px2['NVDA'] = n2
dR = nights('NVDA', px=px2)
s2 = prep(n2)
print(f"  repaired series: break trips = {int(s2.brk.sum())}; usable nights {len(dR)}: {dR.index[0].date()}..{dR.index[-1].date()}")
rule_table(dR, title='  NVDA repaired')
extra = dR[~dR.index.isin(dN.index)]
print(f"  nights added by repair: {len(extra)} ({extra.index[0].date()}..{extra.index[-1].date()}), QQQ BELOW on {int(extra.mk.sum())}; "
      f"on them full g={g100(strat(extra,'full')):.3f}, mkt g={g100(strat(extra,'mkt')):.3f}, mean R={100*extra.R.mean():.3f}% sd={100*extra.R.std(ddof=1):.3f}%")
d_, out, outy, tnw = boot(dR)
lo, hi = np.percentile(100 * out, [5, 95]); loy, hiy = np.percentile(100 * outy, [5, 95])
print(f"  repaired 2000-2026 diff {100*d_.mean():+.4f}; 20-block 90% CI [{lo:+.4f},{hi:+.4f}] P={np.mean(out>0):.3f}; year-block [{loy:+.4f},{hiy:+.4f}] P={np.mean(outy>0):.3f}")

hdr('EXTRA 2: AAPL without the break quarantine (the 2000-09-28 trip is a real -47% night)')
dA = nights('AAPL', use_breaks=False)
print(f"  AAPL no-quarantine nights {len(dA)}: {dA.index[0].date()}..{dA.index[-1].date()} (spec-literal: {len(ALLD['AAPL'])} from {ALLD['AAPL'].index[0].date()})")
rule_table(dA, title='  AAPL no quarantine')

hdr('EXTRA 3: spec edge cases')
# AMZN night spanning the dropped zero-volume bar
dz = ALLD['AMZN']
print(f"  AMZN night 2008-10-28 -> next bar {PX['AMZN'].index[PX['AMZN'].index.get_loc(pd.Timestamp('2008-10-28'))+1].date()} "
      f"(spans dropped zero-volume session), r={100*dz.r.get(pd.Timestamp('2008-10-28'), np.nan):+.2f}%")
# floor usage
for sym in NAMES:
    d = ALLD[sym]
    k = int((LEV * d.r < FLOOR).sum())
    if k:
        print(f"  {sym}: floor -0.95 binds on {k} nights")
if not any(int((LEV * ALLD[s_].r < FLOOR).sum()) for s_ in NAMES):
    print('  floor -0.95 binds on no night in any spec-literal sample')
print(f"  worst R in sample: " + ', '.join(f"{s} {100*ALLD[s].R.min():.0f}%" for s in NAMES))

hdr('EXTRA 4: is "mkt > full" timing or just de-levering? per name: mkt vs constant size = avg mkt size; circular-shift placebo')
def placebo(p, K=1000, seed=3):
    obs = g100(strat(p, 'mkt')) - g100(strat(p, 'full'))
    rng = np.random.default_rng(seed); n = len(p); x = p.R.values - COST; mk = p.mk.values
    lf = np.log1p(x); ld = np.log1p(0.25 * x) - lf
    sh = np.array([100 * np.mean(np.roll(mk, k) * ld) for k in rng.integers(250, n - 250, size=K)])
    return obs, sh.mean(), float(np.mean(sh >= obs))
for a, b in PERIODS:
    print(f"  {a}-{b}")
    print(f"    {'name':<6}{'full':>8}{'mkt':>8}{'avgsz':>7}{'const':>8}{'mkt-full':>10}{'mkt-const':>10}{'placebo mean':>14}{'P(plc>=obs)':>13}")
    k1 = k2 = 0; v1 = []; v2 = []
    for sym in NAMES:
        p = psel(ALLD[sym], a, b); x = p.R.values - COST
        sb = sizes(p, 'mkt').mean(); gf = g100(x); gm = g100(strat(p, 'mkt')); gc = g100(sb * x)
        obs, pm, pp = placebo(p)
        k1 += gm > gf; k2 += gm > gc; v1.append(gm - gf); v2.append(gm - gc)
        print(f"    {sym:<6}{gf:>8.3f}{gm:>8.3f}{sb:>7.2f}{gc:>8.3f}{gm-gf:>+10.3f}{gm-gc:>+10.3f}{pm:>+14.3f}{pp:>13.3f}")
    print(f"    names mkt>full: {k1}/11 (median {np.median(v1):+.3f});  names mkt>const-avg-size: {k2}/11 (median {np.median(v2):+.3f})")
