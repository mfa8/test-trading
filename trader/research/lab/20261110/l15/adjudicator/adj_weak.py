"""Adjudicator: weaknesses of the test (concentration, sensitivity) and the dollar figures.
Uses only adj_core (own implementation). Prints; writes nothing."""
import math
import numpy as np
import adj_core as K

frames, rep = K.load_frames()
up, pm = K.trend_series(frames['QQQ'])
NIGHTS = {s: K.nights(frames, s, up) for s in K.NAMES}
nv = NIGHTS['NVDA']
dates = np.array(nv['dates'])
years = np.array([int(d[:4]) for d in dates])
mk = K.masks(nv['dates'])
b_on = np.where(nv['up'], K.UP, K.DOWN)
b_off = np.full(len(nv['r']), K.UP)
unit = 2.0 * nv['r'] - K.COST

P0 = K.simulate(nv['r'], b_on, 'P0')
P1 = K.simulate(nv['r'], b_on, 'P1', 0.25)
P2 = {rd: K.simulate(nv['r'], b_on, 'P2', 0.25, 5, rd) for rd in ('post', 'during')}

print('== 1. NVDA trend on p=0.25: P1 episodes ==')
print('start       len ext upExt  P0      P1      P2post  P2during  (cum log return over the P1 episode nights, own paths)')
tot = np.zeros(4)
n_ext_eps = 0
upext_total = 0
for s0, L in P1['eps']:
    sl = slice(s0, s0 + L)
    ext = max(0, L - 5)
    upext = int(nv['up'][s0 + 5:s0 + L].sum())
    upext_total += upext
    n_ext_eps += upext > 0
    v = [P0['lr'][sl].sum(), P1['lr'][sl].sum(), P2['post']['lr'][sl].sum(), P2['during']['lr'][sl].sum()]
    tot += v
    print('%s %3d %3d %4d  %+.4f %+.4f %+.4f %+.4f' % (dates[s0], L, ext, upext, *v))
print('episodes %d | exactly 5 nights: %d | longer than 5: %d | with at least one UP-trend extension night: %d | UP-trend extension nights: %d'
      % (len(P1['eps']), sum(1 for _, L in P1['eps'] if L == 5), sum(1 for _, L in P1['eps'] if L > 5), n_ext_eps, upext_total))
print('sums P0 %+.4f P1 %+.4f P2post %+.4f P2during %+.4f' % tuple(tot))

print('\n== 2. P2 - P1: nights that differ, per-year totals, leave-one-year-out ==')
for rd in ('post', 'during'):
    d = P2[rd]['lr'] - P1['lr']
    print('reading %-6s: nights with a different return %d of %d | total log diff H1 %+.4f H2 %+.4f ALL %+.4f | g diff H1 %+.4f H2 %+.4f ALL %+.4f'
          % (rd, int((d != 0).sum()), len(d), d[mk['H1']].sum(), d[mk['H2']].sum(), d.sum(),
             100 * d[mk['H1']].mean(), 100 * d[mk['H2']].mean(), 100 * d.mean()))
    ys = [(y, d[years == y].sum()) for y in np.unique(years) if abs(d[years == y].sum()) > 1e-12]
    print('   per-year totals (non-zero only):', ', '.join('%d %+.4f' % t for t in ys))
    for half, lo, hi in (('H1', 2000, 2014), ('H2', 2015, 2026)):
        base = d[mk[half]].sum()
        flips = []
        for y, v in ys:
            if lo <= y <= hi and (base - v) * base < 0:
                flips.append('%d (half total %+.4f -> %+.4f)' % (y, base, base - v))
        print('   %s total %+.4f; years whose removal flips the sign of the half: %s' % (half, base, flips if flips else 'none'))
    # 2-largest absolute contributions share
    a = sorted(ys, key=lambda t: -abs(t[1]))
    print('   largest absolute year contributions:', a[:4])

print('\n== 3. year-block bootstrap of P2 - P1 (own code; seeds 20261110 and 7) ==')


def boot(dv, yv, seed, ndraw=2000):
    uy = np.unique(yv)
    sums = np.array([dv[yv == y].sum() for y in uy])
    cnt = np.array([(yv == y).sum() for y in uy], float)
    rng = np.random.default_rng(seed)
    out = np.empty(ndraw)
    for i in range(ndraw):
        pick = rng.integers(0, len(uy), len(uy))
        out[i] = 100 * sums[pick].sum() / cnt[pick].sum()
    return np.percentile(out, 5), np.percentile(out, 95), (out > 0).mean()


for rd in ('post', 'during'):
    d = P2[rd]['lr'] - P1['lr']
    for half in ('H1', 'H2', 'ALL'):
        m = mk[half]
        for seed in (20261110, 7):
            lo, hi, pp = boot(d[m], years[m], seed)
            print('  %-6s %-3s seed %-8d: %+.4f [%+.4f, %+.4f] share of draws > 0 %.2f' % (rd, half, seed, 100 * d[m].mean(), lo, hi, pp))

print('\n== 4. sensitivity of NVDA P2 - P1 (g, %/night; H1 / H2 / ALL), post | during ==')


def cell(bv, p, thr=0.80, win=20, N=5):
    out = []
    p1 = K.simulate(nv['r'], bv, 'P1', p, N, 'post', thr, win)
    for rd in ('post', 'during'):
        p2 = K.simulate(nv['r'], bv, 'P2', p, N, rd, thr, win)
        d = p2['lr'] - p1['lr']
        out.append('%+.4f / %+.4f / %+.4f' % (100 * d[mk['H1']].mean(), 100 * d[mk['H2']].mean(), 100 * d.mean()))
    return '  |  '.join(out) + '   (P1 episodes %d)' % len(p1['eps'])


for trend, bv in (('on', b_on), ('off', b_off)):
    for p in (0.10, 0.25, 0.50):
        print('  trend %-3s p=%.2f: %s' % (trend, p, cell(bv, p)))
print('  -- not pre-registered, fragility probes only (trend on, p=0.25) --')
for thr in (0.78, 0.79, 0.80, 0.81, 0.82):
    print('  threshold %.2f: %s' % (thr, cell(b_on, 0.25, thr=thr)))
for win in (15, 20, 25):
    print('  window %d: %s' % (win, cell(b_on, 0.25, win=win)))
for cost in (0.0, 0.0009, 0.0020):
    K.COST = cost
    print('  cost %.1fbp: %s' % (cost * 1e4, cell(b_on, 0.25)))
K.COST = 0.0009
# pause size as a share-like ratio: 0.20, 0.30
for p in (0.20, 0.30):
    print('  pause size %.2f: %s' % (p, cell(b_on, p)))

print('\n== 5. the nights that separate P1 from P2: P1 extension nights with base size 0.98 ==')
ext_idx = []
for s0, L in P1['eps']:
    for t in range(s0 + 5, s0 + L):
        if nv['up'][t]:
            ext_idx.append(t)
ext_idx = np.array(ext_idx)
ue = unit[ext_idx]
print('NVDA: %d UP-trend extension nights; mean unit return %+.4f%% (sd %.3f%%, s.e. %.3f%%), share positive %.2f'
      % (len(ue), 100 * ue.mean(), 100 * ue.std(ddof=1), 100 * ue.std(ddof=1) / math.sqrt(len(ue)), (ue > 0).mean()))
print('NVDA unit return (2r - 9bp): all nights mean %+.4f%% sd %.3f%% | UP-trend nights mean %+.4f%% sd %.3f%% | UP-trend 2015-26 mean %+.4f%% sd %.3f%% | DOWN nights mean %+.4f%%'
      % (100 * unit.mean(), 100 * unit.std(ddof=1), 100 * unit[nv['up']].mean(), 100 * unit[nv['up']].std(ddof=1),
         100 * unit[nv['up'] & mk['H2']].mean(), 100 * unit[nv['up'] & mk['H2']].std(ddof=1), 100 * unit[~nv['up']].mean()))
print('per-episode count of UP-trend extension nights:', [int(nv['up'][s0 + 5:s0 + L].sum()) for s0, L in P1['eps']])
# pooled
pool = []
for s in K.NAMES:
    nt = NIGHTS[s]
    bb = np.where(nt['up'], K.UP, K.DOWN)
    p1 = K.simulate(nt['r'], bb, 'P1', 0.25)
    uu = 2.0 * nt['r'] - K.COST
    for s0, L in p1['eps']:
        for t in range(s0 + 5, s0 + L):
            if nt['up'][t]:
                pool.append(uu[t])
pool = np.array(pool)
print('pooled 11 names: %d UP-trend extension nights, mean unit return %+.4f%% (s.e. %.3f%%)'
      % (len(pool), 100 * pool.mean(), 100 * pool.std(ddof=1) / math.sqrt(len(pool))))

print('\n== 6. dollars at 82 dollars of equity ==')
Eq = 82.0
gap = (0.98 - 0.25) * Eq
print('extra exposure of P2 over P1 on an UP-trend extension night: 0.73 x %.0f = $%.2f; on the first 5 nights and on every DOWN-trend night: $0' % (Eq, gap))
for lab, mu in (('NVDA all nights', unit.mean()), ('NVDA UP-trend nights', unit[nv['up']].mean()),
                ('NVDA 64 extension nights', ue.mean()), ('pooled extension nights', pool.mean())):
    print('  expected $ per such night at the %-26s mean (%+.3f%%): %+.3f ; x14 nights (longest extension) %+.2f ; x16 (21-session month minus 5) %+.2f'
          % (lab, 100 * mu, gap * mu, 14 * gap * mu, 16 * gap * mu))
print('  one-night s.d. of the gap P&L: all-night sd $%.2f, UP-night sd $%.2f, extension-night sd $%.2f'
      % (gap * unit.std(ddof=1), gap * unit[nv['up']].std(ddof=1), gap * ue.std(ddof=1)))
for rd in ('post', 'during'):
    d = P2[rd]['lr'] - P1['lr']
    for half in ('H1', 'H2', 'ALL'):
        print('  long-run simulated average, reading %-6s %-3s: %+.4f %%/night x $82 x 21 nights = $%+.3f per month'
              % (rd, half, 100 * d[mk[half]].mean(), d[mk[half]].mean() * Eq * 21))
    lo, hi, _ = boot(d, years, 20261110)
    print('     whole-span 90%% interval in $ per month: %+.3f .. %+.3f ; per P1 episode (24): $%+.2f' % (lo / 100 * Eq * 21, hi / 100 * Eq * 21, d.sum() * Eq / len(P1['eps'])))
print('QQQ trend state at the end of the sample:', [(d_, bool(v)) for d_, v in up.dropna().iloc[-3:].items()])

print('\n== 7. criteria on the pre-registered cell (NVDA, trend on, p=0.25) ==')
for rd in ('post', 'during'):
    res = {}
    for half in ('H1', 'H2'):
        s1 = K.pstats(P1, mk[half])
        s2 = K.pstats(P2[rd], mk[half])
        res[half] = (s1['g'], s2['g'], s1['dd'], s2['dd'])
        print('  %-6s %s: P1 g %.6f, P2 g %.6f, diff %+.6f | P1 dd %.4f, P2 dd %.4f, diff %+.4f points'
              % (rd, half, s1['g'], s2['g'], s2['g'] - s1['g'], s1['dd'], s2['dd'], s2['dd'] - s1['dd']))
    c1 = all(res[h][1] >= res[h][0] for h in res)
    c2 = all(res[h][3] - res[h][2] <= 5.0 for h in res)
    pos = neg = 0
    for s in K.NAMES:
        nt = NIGHTS[s]
        bb = np.where(nt['up'], K.UP, K.DOWN)
        dd_ = K.simulate(nt['r'], bb, 'P2', 0.25, 5, rd)['lr'].sum() - K.simulate(nt['r'], bb, 'P1', 0.25)['lr'].sum()
        pos += dd_ > 0
        neg += dd_ < 0
    print('  %-6s: c1 %s, c2 %s, names positive %d negative %d -> largest same-sign group %d' % (rd, c1, c2, pos, neg, max(pos, neg)))
