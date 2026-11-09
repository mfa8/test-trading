"""Extra robustness checks; reuses objects from verify_t8 (imported silently)."""
import sys, io, contextlib, json
sys.path.insert(0, '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/verify_t8')
with contextlib.redirect_stdout(io.StringIO()):
    import verify_t8 as V
import numpy as np, pandas as pd
from math import log
g100, strat, psel, maxdd, PERIODS, COST = V.g100, V.strat, V.psel, V.maxdd, V.PERIODS, V.COST
dN = V.dN

print('X1. pure-python loop recomputation of NVDA full/mkt (independent of the vectorised path)')
def rawbars(sym):
    rows = {}
    for f in vl.FILES:
        j = json.load(open(vl.D + f + '.json'))
        for r in j['data']['results']:
            if r['symbol'] != sym: continue
            for b in r['bars']:
                if b.get('interpolated') or not b.get('volume'): continue
                d = b['begins_at'][:10]
                if d > '2026-11-06' or d in rows: continue
                rows[d] = (float(b['open_price']), float(b['close_price']))
    ds = sorted(rows)
    return ds, [rows[d][0] for d in ds], [rows[d][1] for d in ds]
import vload as vl
def states(ds, o, c):
    st = {}; last_brk = -10**9
    for t in range(len(ds)):
        r = o[t+1]/c[t]-1 if t+1 < len(ds) else None
        isb = (r is not None and abs(r) > 0.45) or abs(c[t]/o[t]-1) > 0.6
        if isb: last_brk = t
        if t >= 199 and t - last_brk >= 200:
            st[ds[t]] = (c[t] < sum(c[t-199:t+1])/200.0, r)
    return st
dsn, on, cn = rawbars('NVDA'); dsq, oq, cq = rawbars('QQQ')
sn = states(dsn, on, cn); sq = states(dsq, oq, cq)
for a, b in PERIODS:
    lf = lm = 0.0; n = 0; ef = em = 1.0; pf = pm = 1.0; ddf = ddm = 0.0; nb = 0
    for d in dsn:
        if d not in sn or d not in sq or sn[d][1] is None: continue
        y = int(d[:4])
        if y < a or y > b: continue
        R = max(-0.95, 2*sn[d][1]); x = R - 0.0009
        sz = 0.25 if sq[d][0] else 1.0; nb += sq[d][0]
        lf += log(1+x); lm += log(1+sz*x); n += 1
        ef *= 1+x; em *= 1+sz*x; pf = max(pf, ef); pm = max(pm, em)
        ddf = max(ddf, 1-ef/pf); ddm = max(ddm, 1-em/pm)
    print(f"   {a}-{b} n={n} nBELOW={nb} full g={100*lf/n:.3f} DD={100*ddf:.0f}%  mkt g={100*lm/n:.3f} DD={100*ddm:.0f}%"
          f"   | vectorised: full {g100(strat(psel(dN,a,b),'full')):.3f} mkt {g100(strat(psel(dN,a,b),'mkt')):.3f}")

print('\nX2. NVDA R (gross 2x) ABOVE vs BELOW QQQ: difference in means, Welch t, and decomposition of the mkt-full gain')
for a, b in PERIODS:
    p = psel(dN, a, b); A = p[p.mk == 0].R.values; B = p[p.mk == 1].R.values
    se = np.sqrt(A.var(ddof=1)/len(A) + B.var(ddof=1)/len(B))
    x = B - COST
    gain_per_below = np.mean(np.log1p(0.25*x) - np.log1p(x))
    cost_part = 0.75*COST                       # cost not paid on 75% of the position
    mean_part = -0.75*B.mean()                  # avoided (gross) mean return
    var_part = gain_per_below - cost_part - mean_part   # remainder = convexity / variance-drag
    fr = len(B)/len(p)
    print(f"   {a}-{b}: mean R ABOVE {100*A.mean():.3f}% BELOW {100*B.mean():.3f}%  diff {100*(A.mean()-B.mean()):.3f}  Welch t={((A.mean()-B.mean())/se):.2f} | "
          f"gain/BELOW night {100*gain_per_below:.3f} = cost saved {100*cost_part:.3f} + avoided mean {100*mean_part:+.3f} + variance-drag {100*var_part:.3f};"
          f" x frac BELOW {fr:.3f} = {100*gain_per_below*fr:.3f}")

print('\nX3. symmetric trimming (drop nights with |NVDA overnight| > X in BOTH states): mkt - full, g%/night')
print(f"   {'X':>5} " + ' '.join(f"{str(a)+'-'+str(b):>26}" for a, b in PERIODS))
for X in (1.0, 0.25, 0.20, 0.15, 0.10, 0.075, 0.05):
    cells = []
    for a, b in PERIODS:
        q = psel(dN, a, b); q2 = q[q.r.abs() <= X]
        cells.append(f"{g100(strat(q2,'mkt'))-g100(strat(q2,'full')):+.3f} (drop {len(q)-len(q2):>3}; B {int(q.mk.sum()-q2.mk.sum()):>2})")
    print(f"   {X:>5.3f} " + ' '.join(f"{c:>26}" for c in cells))
print('   winsorised instead of dropped (clip NVDA overnight to +/-X):')
for X in (0.20, 0.15, 0.10, 0.05):
    cells = []
    for a, b in PERIODS:
        q = psel(dN, a, b).copy(); q['R'] = np.maximum(-0.95, 2*q.r.clip(-X, X))
        cells.append(f"{g100(strat(q,'mkt'))-g100(strat(q,'full')):+.3f}")
    print(f"   {X:>5.3f} " + ' '.join(f"{c:>26}" for c in cells))

print('\nX4. earnings / pre-announcement flags in csv; NVDA 2015-26 excluding earn=1 OR preann set')
e = pd.read_csv(V.EARN_CSV)
print('   preann non-null rows:', e[e.preann.notna()][['date', 'next', 'earn', 'preann', 'nvda_on']].to_string(index=False).replace('\n', '\n   '))
ex = pd.to_datetime(e.loc[(e.earn == 1) | e.preann.notna(), 'date'])
p = psel(dN, 2015, 2026); q = p[~p.index.isin(ex)]
print(f"   ex earn+preann n={len(q)}: full {g100(strat(q,'full')):.3f} DD {100*maxdd(strat(q,'full')):.0f}%  own {g100(strat(q,'own')):.3f}  mkt {g100(strat(q,'mkt')):.3f} DD {100*maxdd(strat(q,'mkt')):.0f}%  diff {g100(strat(q,'mkt'))-g100(strat(q,'full')):+.3f}")
d_, out, outy, tnw = V.boot(q)
print(f"   ex-earnings(+preann) 2015-26 diff: 20-night block 90% CI [{np.percentile(100*out,5):+.4f},{np.percentile(100*out,95):+.4f}] P={np.mean(out>0):.3f}; "
      f"year-block [{np.percentile(100*outy,5):+.4f},{np.percentile(100*outy,95):+.4f}] P={np.mean(outy>0):.3f}")

print('\nX5. NVDL / NVDX: leverage actually delivered and shortfall vs synthetic 2x')
nv = V.PX['NVDA']; ncc = nv.c.pct_change(); non = (nv.o.shift(-1)/nv.c - 1)
for sym in ('NVDL', 'NVDX'):
    df = V.PX[sym]; cc = df.c.pct_change(); j = pd.DataFrame(dict(e=cc, n=ncc.reindex(df.index))).dropna()
    j = j[j.index.to_series().diff().dt.days <= 5]
    # quarterly close-to-close beta
    out = []
    for (y, qn), gdf in j.groupby([j.index.year, j.index.quarter]):
        if len(gdf) > 20:
            out.append(f"{y}Q{qn}:{np.polyfit(gdf.n.values, gdf.e.values, 1)[0]:.2f}")
    print(f"   {sym} close-to-close beta vs NVDA by quarter: " + ' '.join(out))
    on = (df.o.shift(-1)/df.c - 1)
    k = pd.DataFrame(dict(e=on, n=non.reindex(df.index))).dropna()
    k = k[k.index >= '2024-04-01']
    dlt = k.e - 2*k.n
    print(f"   {sym} since 2024-04: overnight actual minus 2x NVDA overnight: mean {100*dlt.mean():+.4f}%/night (se {100*dlt.std(ddof=1)/np.sqrt(len(dlt)):.4f}), n={len(k)};"
          f" log growth actual {g100(k.e.values):.3f} vs synthetic {g100(2*k.n.values):.3f}")
# NVDL restricted to the 2x era
qs = V.prep(V.PX['QQQ'])
for sym, start in (('NVDL', '2024-04-01'), ('NVDL', '2022-12-13'), ('NVDX', '2023-10-19')):
    df = V.PX[sym]
    d = pd.DataFrame(dict(r=df.o.shift(-1)/df.c - 1), index=df.index).iloc[:-1]
    gap = (df.index[1:] - df.index[:-1]).days
    d['mk'] = qs.below.reindex(d.index); d['own'] = 0.0; d['R'] = d.r
    qnext = pd.Series(qs.index[1:], index=qs.index[:-1]).reindex(d.index)
    d = d[(pd.Series(df.index[1:], index=df.index[:-1]) == qnext).values & (d.index >= start)]
    xf = strat(d, 'full'); xm = strat(d, 'mkt'); dd = np.log1p(xm) - np.log1p(xf)
    # block bootstrap 20 nights
    rng = np.random.default_rng(1); n = len(dd); nb = int(np.ceil(n/20)); st = rng.integers(0, n, size=(20000, nb))
    ix = (st[:, :, None] + np.arange(20)[None, None, :]) % n
    bs = dd[ix.reshape(20000, -1)[:, :n]].mean(axis=1)
    print(f"   {sym} from {start}: n={n} BELOW={int(d.mk.sum())} full {g100(xf):.3f} DD {100*maxdd(xf):.0f}% mkt {g100(xm):.3f} DD {100*maxdd(xm):.0f}% "
          f"diff {100*dd.mean():+.3f}; block-bootstrap 90% CI [{np.percentile(100*bs,5):+.3f},{np.percentile(100*bs,95):+.3f}] P(mkt>full)={np.mean(bs>0):.2f}")

print('\nX6. which rule is best per name, 2000-2026 (g%/night)')
for sym in V.NAMES:
    p = V.ALLD[sym]; v = {r: g100(strat(p, r)) for r in V.RULES}
    print(f"   {sym:<5} best={max(v, key=v.get):<7} " + ' '.join(f"{r}={x:.3f}" for r, x in v.items()))

print('\nX7. NVDA spec-literal vs excluding the 9 pre-break Oct-2000 nights vs repaired')
dC = dN[dN.index >= '2001-01-01']
for lab, d in (('spec-literal', dN), ('drop 9 pre-break nights', dC), ('repaired /10', V.dR)):
    print(f"   {lab:<24} " + ' | '.join(f"{a}-{b} n={len(psel(d,a,b))} full {g100(strat(psel(d,a,b),'full')):.3f} mkt {g100(strat(psel(d,a,b),'mkt')):.3f} "
          f"DD {100*maxdd(strat(psel(d,a,b),'full')):.0f}/{100*maxdd(strat(psel(d,a,b),'mkt')):.0f}%" for a, b in PERIODS))

print('\nX8. QQQ-BELOW episodes (NVDA sample): count, length distribution, and gain by episode')
p = dN; b = p.mk.values.astype(int); dd = np.log1p(strat(p, 'mkt')) - np.log1p(strat(p, 'full'))
eps = []; i = 0
while i < len(b):
    if b[i] == 1:
        j = i
        while j + 1 < len(b) and b[j+1] == 1: j += 1
        eps.append((p.index[i].date(), p.index[j].date(), j - i + 1, dd[i:j+1].sum())); i = j + 1
    else:
        i += 1
L = np.array([x[2] for x in eps]); G = np.array([x[3] for x in eps])
print(f"   {len(eps)} episodes; length median {np.median(L):.0f}, <=5 nights: {(L<=5).sum()}, >=60 nights: {(L>=60).sum()}")
print(f"   episodes with gain>0: {(G>0).sum()}, <0: {(G<0).sum()}; total gain {G.sum():.2f} log pts; "
      f"short (<=20 nights) episodes total {G[L<=20].sum():+.2f}; long (>20) total {G[L>20].sum():+.2f}")
for x in sorted(eps, key=lambda z: -z[3])[:5]: print(f"     best  {x[0]}..{x[1]} len {x[2]:>3} gain {x[3]:+.2f}")
for x in sorted(eps, key=lambda z: z[3])[:5]: print(f"     worst {x[0]}..{x[1]} len {x[2]:>3} gain {x[3]:+.2f}")
print('   last 2026 episodes:'); 
for x in eps[-4:]: print(f"     {x[0]}..{x[1]} len {x[2]:>3} gain {x[3]:+.3f}")
