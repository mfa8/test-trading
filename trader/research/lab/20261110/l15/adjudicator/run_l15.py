"""L15 main run (analyst A): PAUSE exit condition, P0/P1/P2/P3 comparison.

Usage: python3 -I run_l15.py   -> writes results_main.txt and results.json next to this file.
"""
import sys
import os
import json
import math
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np      # noqa: E402
import loader           # noqa: E402
import sim              # noqa: E402

SEED = 20261110
NBOOT = 2000
UP_SIZE = 0.98
DOWN_SIZE = 0.25
TREND_N = 199
H1_END = '2014-12-31'
H2_START = '2015-01-02'
PERIODS = ['H1', 'H2', 'ALL']
PLABEL = {'H1': '2000-10-30..2014-12-31', 'H2': '2015-01-02..2026-11-06', 'ALL': 'whole span'}
PSIZES = [0.10, 0.25, 0.50]
SANITY = 0.45

OUT = []


def P(*a):
    line = ' '.join(str(x) for x in a)
    OUT.append(line)
    print(line)


# ----------------------------------------------------------------------------
# data preparation
# ----------------------------------------------------------------------------
def qqq_trend(bars):
    """date -> True (UP) / False (DOWN), defined once 199 prior closes exist."""
    q = bars['QQQ']
    closes = [c for _, _, c in q]
    up = {}
    csum = [0.0]
    for c in closes:
        csum.append(csum[-1] + c)
    for i in range(TREND_N, len(q)):
        m = (csum[i] - csum[i - TREND_N]) / TREND_N      # mean of closes i-199 .. i-1
        up[q[i][0]] = closes[i] >= m
    return up


def build_nights(name, bars, up, start_date=None, drop_gap=False):
    """Nights for one underlying. Returns dict of parallel lists."""
    qidx = {d: i for i, (d, _, _) in enumerate(bars['QQQ'])}
    x = [row for row in bars[name] if row[0] in qidx]
    not_in_q = [row[0] for row in bars[name] if row[0] not in qidx]
    d_in, d_out, r, upf, gap = [], [], [], [], []
    for j in range(len(x) - 1):
        d, o, c = x[j]
        d2, o2, c2 = x[j + 1]
        if d not in up:
            continue
        if start_date and d < start_date:
            continue
        g = (qidx[d2] - qidx[d]) != 1
        rr = o2 / c - 1.0
        if g and drop_gap:
            rr = 0.0      # alternative reading: flat in cash across a missing bar
            # (unit return then = -cost; set below to exactly zero)
        d_in.append(d)
        d_out.append(d2)
        r.append(rr)
        upf.append(up[d])
        gap.append(g)
    u = [sim.unit_return(v) for v in r]
    if drop_gap:
        u = [0.0 if g else v for v, g in zip(u, gap)]
    return dict(name=name, d_in=d_in, d_out=d_out, r=r, u=u, up=upf, gap=gap,
                not_in_q=not_in_q)


def period_bounds(d_in):
    """index ranges [lo, hi) of nights by entry date."""
    n = len(d_in)
    split = next((i for i, d in enumerate(d_in) if d >= H2_START), n)
    return {'H1': (0, split), 'H2': (split, n), 'ALL': (0, n)}


# ----------------------------------------------------------------------------
# statistics
# ----------------------------------------------------------------------------
def pstats(res, b, lo, hi):
    lr = res['lr'][lo:hi]
    n = len(lr)
    g = 100.0 * sum(lr) / n
    mult = math.exp(sum(lr))
    dd = 100.0 * sim.max_drawdown(res['E'][lo:hi + 1])
    eps = [(st, L) for st, L in res['episodes'] if lo <= st < hi]
    lens = [L for _, L in eps]
    paused_n = sum(1 for t in range(lo, hi) if res['paused'][t])
    eff_n = sum(1 for t in range(lo, hi) if res['paused'][t] and res['s'][t] < b[t])
    return dict(n=n, g=g, mult=mult, dd=dd, episodes=len(eps), paused=paused_n, eff=eff_n,
                med=(statistics.median(lens) if lens else float('nan')),
                mx=(max(lens) if lens else 0))


def dd_carried(res, lo, hi):
    """Drawdown inside [lo,hi] measured against the running peak since the start."""
    E = res['E']
    peak = max(E[:lo + 1])
    worst = 0.0
    for t in range(lo, hi + 1):
        if E[t] > peak:
            peak = E[t]
        worst = max(worst, 1.0 - E[t] / peak)
    return 100.0 * worst


def year_boot(diff, years, lo, hi, seed=SEED, nboot=NBOOT):
    """Block bootstrap by calendar year of mean(diff) over nights lo..hi-1.
    Returns (point estimate in % per night, 5th pct, 95th pct, share of draws > 0)."""
    d = np.asarray(diff[lo:hi], dtype=float)
    y = np.asarray(years[lo:hi])
    uy = np.unique(y)
    sums = np.array([d[y == k].sum() for k in uy])
    cnts = np.array([(y == k).sum() for k in uy], dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(uy), size=(nboot, len(uy)))
    stat = 100.0 * sums[idx].sum(axis=1) / cnts[idx].sum(axis=1)
    point = 100.0 * d.mean()
    return point, float(np.percentile(stat, 5)), float(np.percentile(stat, 95)), float((stat > 0).mean())


def run_all_variants(u, b):
    """All simulations for one (underlying, trend setting)."""
    R = {}
    R['P0'] = sim.simulate(u, b, 'P0')
    for p in PSIZES:
        R[('P1', p)] = sim.simulate(u, b, 'P1', p=p)
        R[('P2', p)] = sim.simulate(u, b, 'P2', p=p, rearm_during_pause=True)
        R[('P2B', p)] = sim.simulate(u, b, 'P2', p=p, rearm_during_pause=False)
        R[('P3', p)] = sim.simulate(u, b, 'P3', p=p)
        R[('P2x10', p)] = sim.simulate(u, b, 'P2', p=p, n_len=10, rearm_during_pause=True)
        R[('P2Bx10', p)] = sim.simulate(u, b, 'P2', p=p, n_len=10, rearm_during_pause=False)
    return R


def vkey(v, p):
    return 'P0' if v == 'P0' else (v, p)


# ----------------------------------------------------------------------------
def main():
    log = []
    bars, lstats, log = loader.load_all(log)
    up = qqq_trend(bars)
    results = {}       # for results.json

    P('=' * 100)
    P('L15  PAUSE exit condition: as written (P1) vs fixed 5 sessions (P2)   -- analyst A')
    P('=' * 100)
    P('Scripts: %s/{loader.py, sim.py, run_l15.py, hand_test.py}' % HERE)
    P('Bootstrap: block by calendar year of the entry date, %d draws, numpy default_rng seed %d' % (NBOOT, SEED))
    P('           (the generator is re-seeded for every comparison, so all comparisons in a period use the same year draws)')
    P('')
    P('READINGS TAKEN (ambiguities in the specification)')
    readings = [
        'R1 Night t is dated by its ENTRY session (close of t). H1 = entry dates up to 2014-12-31 (the last H1 night exits at the 2015-01-02 open); H2 = entry dates 2015-01-02..2026-11-05 (last exit: the 2026-11-06 open, the last non-provisional bar).',
        'R2 One continuous simulation 2000->2026 per name; the period figures are cut out of it (pause state and the 20-session window carry across 2015-01-02). Alternative (restart E=1, fresh state on 2015-01-02) is shown in section 8.',
        'R3 P2 re-arming, reading A (primary): after a pause starts the rule is disarmed and re-arms on the first later night on which C is false, even if that night is still inside the 5-night pause. Reading B (re-arming is only looked at on nights after the 5 have run out) is reported next to it everywhere it matters (label P2B).',
        'R4 Trend: UP if QQQ close_t >= mean of the 199 closes before t (identical to close >= 200-session SMA including today). First night with a trend state: QQQ session 200 = %s.' % sorted(up)[0],
        'R5 Each name starts at E=1 on its first night with a trend state. For NVDA that is 2000-10-30 (bars before are dropped). For the other ten it is %s, so their first period holds 10 nights before 2000-10-30. Alternative (all names start 2000-10-30) in section 8.' % sorted(up)[0],
        'R6 Trend-off table uses the same nights as the trend-on table (b = 0.98 on every night).',
        'R7 H_t uses the E values available (fewer than 20 during the first 19 nights), E_0 = 1 included.',
        'R8 Worst drawdown of a period = worst peak-to-trough with both peak and trough inside the period. Alternative (peak carried in from before the period) in section 8.',
        'R9 A pause episode belongs to the period in which it starts; its full length is counted. Paused nights are counted in the period of the night.',
        'R10 Event study horizon h = nights t .. t+h-1, where t is the night on which the P1 pause starts (the first paused night). Events too close to the end of the sample for a horizon are left out of that horizon (counts shown).',
        'R11 A skipped bar (zero volume) removes that session for that name: the night then runs from the previous close to the next available open (one case: AMZN 2008-10-29). Alternative (flat that night) in section 8.',
        'R12 "Paused night" = a night on which the pause is in force, whether or not it changes the size. "eff" = paused nights on which the size was actually cut (b_t > p). With the trend rule on and p >= 0.25, a pause changes nothing on DOWN nights.',
    ]
    for r_ in readings:
        P('  ' + r_)
    results['readings'] = readings

    # ---------------- data notes ----------------
    P('')
    P('1. DATA')
    data_notes = []
    for sym in ['QQQ'] + loader.NAMES:
        st = lstats[sym]
        b_ = bars[sym]
        P('  %-5s kept %5d bars %s..%s | raw %d, after 2026-11-06 dropped %d, NVDA<=2000-10-27 dropped %d, duplicates %d (price mismatch %d), zero-volume %d, interpolated %d'
          % (sym, len(b_), b_[0][0], b_[-1][0], st['total'], st['late'], st['nvda_early'], st['dup'],
             st['dup_mismatch'], st['zero_vol'], st['interp']))
    for line in log:
        if any(line.find(' %s ' % s) >= 0 for s in ['QQQ'] + loader.NAMES):
            P('   ' + line)
            data_notes.append(line)
    series = {}
    for name in loader.NAMES:
        series[name] = build_nights(name, bars, up)
    P('')
    P('  Nights per name (entry dates):')
    for name in loader.NAMES:
        s_ = series[name]
        pb = period_bounds(s_['d_in'])
        nup = sum(1 for v in s_['up'] if v)
        P('   %-5s %5d nights %s..%s (last exit %s) | H1 %d, H2 %d | trend UP on %d (%.1f%%) | gap nights %s | dates not in QQQ calendar: %s'
          % (name, len(s_['u']), s_['d_in'][0], s_['d_in'][-1], s_['d_out'][-1],
             pb['H1'][1] - pb['H1'][0], pb['H2'][1] - pb['H2'][0], nup, 100.0 * nup / len(s_['u']),
             [(a, b_) for a, b_, g in zip(s_['d_in'], s_['d_out'], s_['gap']) if g], s_['not_in_q']))
    P('')
    P('  Sanity filter: overnight moves beyond +/-45% in the underlying (reported, NOT dropped):')
    flagged = []
    for name in loader.NAMES:
        s_ = series[name]
        for d, d2, r_ in zip(s_['d_in'], s_['d_out'], s_['r']):
            if abs(r_) > SANITY:
                flagged.append((name, d, d2, r_))
    if flagged:
        for f in flagged:
            P('   FLAG %-5s %s -> %s  r = %+.2f%%' % (f[0], f[1], f[2], 100 * f[3]))
    else:
        P('   none in any of the 11 names')
    data_notes.append('overnight moves beyond +/-45%%: %d' % len(flagged))
    P('  Largest overnight moves per name (for information):')
    for name in loader.NAMES:
        s_ = series[name]
        ix = sorted(range(len(s_['r'])), key=lambda i: s_['r'][i])
        lo3 = ', '.join('%s %+.1f%%' % (s_['d_in'][i], 100 * s_['r'][i]) for i in ix[:2])
        hi3 = ', '.join('%s %+.1f%%' % (s_['d_in'][i], 100 * s_['r'][i]) for i in ix[-2:][::-1])
        P('   %-5s worst: %s | best: %s' % (name, lo3, hi3))
    qd = sorted(up)
    P('  QQQ trend state on the last five sessions: ' + ', '.join('%s %s' % (d, 'UP' if up[d] else 'DOWN') for d in qd[-5:]))
    results['data_notes'] = data_notes
    results['flagged'] = flagged

    # ---------------- simulations ----------------
    SIMS = {}   # (name, trend) -> dict of results
    BASE = {}
    for name in loader.NAMES:
        s_ = series[name]
        for trend in ('on', 'off'):
            if trend == 'on':
                b = [UP_SIZE if v else DOWN_SIZE for v in s_['up']]
            else:
                b = [UP_SIZE] * len(s_['u'])
            BASE[(name, trend)] = b
            SIMS[(name, trend)] = run_all_variants(s_['u'], b)

    def table(name, trend, title):
        s_ = series[name]
        pb = period_bounds(s_['d_in'])
        b = BASE[(name, trend)]
        Rr = SIMS[(name, trend)]
        P('')
        P(title)
        P('  %-22s %-7s %5s %6s %9s %14s %7s %5s %6s %5s %5s %4s'
          % ('period', 'variant', 'p', 'nights', 'g %/night', 'terminal x', 'maxDD%', 'epis', 'paused', 'eff', 'med', 'max'))
        rows = []
        for per in PERIODS:
            lo, hi = pb[per]
            order = [('P0', None)]
            for v in ['P1', 'P2', 'P2B', 'P3', 'P2x10', 'P2Bx10']:
                for p in PSIZES:
                    order.append((v, p))
            for v, p in order:
                st = pstats(Rr[vkey(v, p)], b, lo, hi)
                P('  %-22s %-7s %5s %6d %+9.4f %14.4g %7.2f %5d %6d %5d %5s %4d'
                  % (PLABEL[per], v, ('-' if p is None else '%.2f' % p), st['n'], st['g'], st['mult'], st['dd'],
                     st['episodes'], st['paused'], st['eff'],
                     ('-' if st['episodes'] == 0 else '%g' % st['med']), st['mx']))
                rows.append(dict(name=name, trend_rule=trend, period=PLABEL[per], variant=v,
                                 pause_size=(0.0 if p is None else p), nights=st['n'],
                                 g_pct_per_night=st['g'], terminal_multiple=st['mult'],
                                 max_drawdown_pct=st['dd'], episodes=st['episodes'],
                                 paused_nights=st['paused'], effective_paused_nights=st['eff'],
                                 median_len=(None if st['episodes'] == 0 else st['med']), max_len=st['mx']))
            P('')
        return rows

    P('')
    P('2. NVDA, TREND RULE ON (main case). g = 100*mean ln(1+R). maxDD within the period. epis/med/max = pause episodes, median and maximum length in nights.')
    P('   P2 = reading A, P2B = reading B (see R3). P2x10/P2Bx10 = 10-night fixed pause.')
    results['nvda_on'] = table('NVDA', 'on', '   NVDA trend ON')
    P('3. NVDA, TREND RULE OFF (b = 0.98 every night; the pre-2026-11-10 engine)')
    results['nvda_off'] = table('NVDA', 'off', '   NVDA trend OFF')

    # ---------------- differences with bootstrap ----------------
    def diffs(name, trend, plist, show=True):
        s_ = series[name]
        pb = period_bounds(s_['d_in'])
        years = [int(d[:4]) for d in s_['d_in']]
        Rr = SIMS[(name, trend)]
        out = []
        for p in plist:
            comps = [('P1-P0', ('P1', p), 'P0'), ('P2-P0', ('P2', p), 'P0'), ('P3-P0', ('P3', p), 'P0'),
                     ('P2-P1', ('P2', p), ('P1', p)), ('P2B-P1', ('P2B', p), ('P1', p)),
                     ('P2x10-P1', ('P2x10', p), ('P1', p)), ('P3-P1', ('P3', p), ('P1', p))]
            for lab, a, b_ in comps:
                d = [x - y for x, y in zip(Rr[a]['lr'], Rr[b_]['lr'])]
                for per in PERIODS:
                    lo, hi = pb[per]
                    pt, q5, q95, fpos = year_boot(d, years, lo, hi)
                    tot = sum(d[lo:hi])
                    out.append(dict(name=name, trend_rule=trend, pause_size=p, comparison=lab, period=PLABEL[per],
                                    diff_g=pt, lo90=q5, hi90=q95, share_pos=fpos, total_log=tot,
                                    nights_differ=sum(1 for v in d[lo:hi] if v != 0.0)))
                    if show:
                        P('  p=%.2f %-9s %-22s  dg = %+8.4f %%/night  90%% [%+8.4f, %+8.4f]  boot share>0 %.2f | total log diff %+7.3f | nights with different return %d'
                          % (p, lab, PLABEL[per], pt, q5, q95, fpos, tot, out[-1]['nights_differ']))
            if show:
                P('')
        return out

    P('4. NVDA DIFFERENCES IN g (percent per night), 90% year-block bootstrap intervals')
    P('  -- trend ON --')
    results['nvda_diff_on'] = diffs('NVDA', 'on', PSIZES)
    P('  -- trend OFF --')
    results['nvda_diff_off'] = diffs('NVDA', 'off', PSIZES)

    # ---------------- NVDA episode list ----------------
    def episode_list(name, trend, p=0.25):
        s_ = series[name]
        Rr = SIMS[(name, trend)]
        b = BASE[(name, trend)]
        r0, r1, r2, r2b = Rr['P0'], Rr[('P1', p)], Rr[('P2', p)], Rr[('P2B', p)]
        P('  %-10s %-10s %4s %5s %9s %9s %9s %9s %9s'
          % ('start', 'last night', 'len', 'UPn', 'P0 cum', 'P1 cum', 'P2 cum', 'P2B cum', 'P2-P1'))
        rows = []
        tot = [0.0, 0.0, 0.0, 0.0]
        for st, L in r1['episodes']:
            c0 = sum(r0['lr'][st:st + L])
            c1 = sum(r1['lr'][st:st + L])
            c2 = sum(r2['lr'][st:st + L])
            c2b = sum(r2b['lr'][st:st + L])
            upn = sum(1 for t in range(st, st + L) if b[t] > DOWN_SIZE)
            tot = [tot[0] + c0, tot[1] + c1, tot[2] + c2, tot[3] + c2b]
            P('  %-10s %-10s %4d %5d %+9.4f %+9.4f %+9.4f %+9.4f %+9.4f'
              % (s_['d_in'][st], s_['d_in'][st + L - 1], L, upn, c0, c1, c2, c2b, c2 - c1))
            rows.append(dict(start=s_['d_in'][st], last=s_['d_in'][st + L - 1], length=L, up_nights=upn,
                             p0=c0, p1=c1, p2=c2, p2b=c2b))
        P('  %-10s %-10s %4d %5s %+9.4f %+9.4f %+9.4f %+9.4f %+9.4f'
          % ('TOTAL', '', sum(L for _, L in r1['episodes']), '', tot[0], tot[1], tot[2], tot[3], tot[2] - tot[1]))
        return rows

    P('5. NVDA PAUSE EPISODES UNDER P1 (p = 0.25): start = entry date of the first paused night, len = nights under P1,')
    P('   UPn = nights in the episode with base size 0.98; cum = sum of ln(1+R) over the episode\'s nights on each variant\'s own path.')
    P('  -- trend ON --')
    results['nvda_episodes_on'] = episode_list('NVDA', 'on')
    P('')
    P('  -- trend OFF --')
    results['nvda_episodes_off'] = episode_list('NVDA', 'off')

    # ---------------- extension nights ----------------
    P('')
    P('5b. WHERE P1 AND P2 CAN DIFFER: P1 "extension" nights (night 6 onward of a P1 episode), p = 0.25')
    P('   ext = all extension nights; extUP = those with base size 0.98 (only there does P1 hold less than normal size).')
    P('   mean u = mean unit return 2r-9bp on extUP nights; dlog = sum over extUP nights of ln(1+0.98u) - ln(1+0.25u).')
    ext_rows = []
    for trend in ('on', 'off'):
        P('  -- trend %s --' % trend.upper())
        P('  %-6s %5s %5s %6s %10s %8s %9s' % ('name', 'epis', 'ext', 'extUP', 'mean u %', 'pos %', 'dlog'))
        pool_u = []
        for name in loader.NAMES:
            s_ = series[name]
            b = BASE[(name, trend)]
            r1 = SIMS[(name, trend)][('P1', 0.25)]
            ext = []
            for st, L in r1['episodes']:
                ext += list(range(st + 5, st + L))
            extup = [t for t in ext if b[t] > DOWN_SIZE]
            us = [s_['u'][t] for t in extup]
            pool_u += us
            dl = sum(math.log1p(0.98 * v) - math.log1p(0.25 * v) for v in us)
            P('  %-6s %5d %5d %6d %10s %8s %+9.4f'
              % (name, len(r1['episodes']), len(ext), len(extup),
                 ('%+.4f' % (100 * sum(us) / len(us))) if us else '-',
                 ('%.1f' % (100.0 * sum(1 for v in us if v > 0) / len(us))) if us else '-', dl))
            ext_rows.append(dict(name=name, trend_rule=trend, episodes=len(r1['episodes']), ext=len(ext),
                                 ext_up=len(extup), mean_u_pct=(100 * sum(us) / len(us)) if us else None, dlog=dl))
        if pool_u:
            P('  %-6s %5s %5s %6d %+10.4f %8.1f' % ('POOLED', '', '', len(pool_u), 100 * sum(pool_u) / len(pool_u),
                                                 100.0 * sum(1 for v in pool_u if v > 0) / len(pool_u)))
        # unconditional mean u for comparison
        for name in ['NVDA']:
            s_ = series[name]
            allu = s_['u']
            upu = [v for v, f in zip(s_['u'], s_['up']) if f]
            P('  for comparison NVDA mean u: all nights %+.4f%%, UP-trend nights %+.4f%%, DOWN-trend nights %+.4f%%'
              % (100 * sum(allu) / len(allu), 100 * sum(upu) / len(upu),
                 100 * (sum(allu) - sum(upu)) / (len(allu) - len(upu))))
    results['extension'] = ext_rows

    # ---------------- event study ----------------
    HZ = [5, 10, 20, 40]

    def event_study(ev_trend, ret_trend, title):
        """Events: P1 (p=0.25) pause starts under ev_trend. Returns: P0 under ret_trend."""
        P('')
        P(title)
        P('  %-7s %3s %6s %10s %10s %10s %10s %24s %8s'
          % ('set', 'h', 'events', 'cond mean', 'cond med', 'uncond mn', 'uncond md', 'mean diff 90% boot', 'share>0'))
        out = []
        pooled = {h: dict(ev=[], evy=[], un=[], uny=[]) for h in HZ}
        for name in loader.NAMES:
            s_ = series[name]
            lr0 = SIMS[(name, ret_trend)]['P0']['lr']
            starts = [st for st, _ in SIMS[(name, ev_trend)][('P1', 0.25)]['episodes']]
            n = len(lr0)
            cs = [0.0]
            for v in lr0:
                cs.append(cs[-1] + v)
            years = [int(d[:4]) for d in s_['d_in']]
            for h in HZ:
                cum = [cs[t + h] - cs[t] for t in range(0, n - h + 1)]
                ev = [cum[t] for t in starts if t <= n - h]
                evy = [years[t] for t in starts if t <= n - h]
                pooled[h]['ev'] += ev
                pooled[h]['evy'] += evy
                pooled[h]['un'] += cum
                pooled[h]['uny'] += years[:n - h + 1]
                if name == 'NVDA':
                    row = es_row('NVDA', h, ev, evy, cum, years[:n - h + 1])
                    out.append(row)
        for h in HZ:
            out.append(es_row('POOL11', h, pooled[h]['ev'], pooled[h]['evy'], pooled[h]['un'], pooled[h]['uny']))
        return out

    def es_row(label, h, ev, evy, un, uny):
        ev_a = np.asarray(ev, dtype=float)
        un_a = np.asarray(un, dtype=float)
        evy_a = np.asarray(evy)
        uny_a = np.asarray(uny)
        uy = np.unique(uny_a)
        es = np.array([ev_a[evy_a == k].sum() for k in uy])
        ec = np.array([(evy_a == k).sum() for k in uy], dtype=float)
        us_ = np.array([un_a[uny_a == k].sum() for k in uy])
        uc = np.array([(uny_a == k).sum() for k in uy], dtype=float)
        rng = np.random.default_rng(SEED)
        idx = rng.integers(0, len(uy), size=(NBOOT, len(uy)))
        ecs = ec[idx].sum(axis=1)
        ok = ecs > 0
        dd_ = es[idx].sum(axis=1)[ok] / ecs[ok] - us_[idx].sum(axis=1)[ok] / uc[idx].sum(axis=1)[ok]
        cm = float(ev_a.mean()) if len(ev_a) else float('nan')
        cmed = float(np.median(ev_a)) if len(ev_a) else float('nan')
        um = float(un_a.mean())
        umed = float(np.median(un_a))
        q5, q95 = (float(np.percentile(dd_, 5)), float(np.percentile(dd_, 95))) if len(dd_) else (float('nan'),) * 2
        sp = float((dd_ > 0).mean()) if len(dd_) else float('nan')
        P('  %-7s %3d %6d %+10.4f %+10.4f %+10.4f %+10.4f   %+8.4f [%+7.4f,%+7.4f] %8.2f'
          % (label, h, len(ev_a), cm, cmed, um, umed, cm - um, q5, q95, sp))
        return dict(set=label, h=h, events=len(ev), cond_mean=cm, cond_median=cmed, uncond_mean=um,
                    uncond_median=umed, diff=cm - um, lo90=q5, hi90=q95, share_pos=sp,
                    distinct_event_years=int(len(np.unique(evy_a))) if len(evy_a) else 0)

    P('')
    P('6. EVENT STUDY: P0 cumulative log return over the next h nights after each P1 pause start (p = 0.25), vs all h-night windows.')
    P('   "mean diff" = conditional mean - unconditional mean, with a 90% year-block bootstrap interval (events and windows grouped by start year).')
    results['event_on'] = event_study('on', 'on', '  6a. PRIMARY: trend ON. Events = P1 starts under the trend rule; returns = P0 under the trend rule (0.98 / 0.25).')
    results['event_off'] = event_study('off', 'off', '  6b. SECONDARY: trend OFF. Events = P1 starts with b = 0.98 always; returns = always-0.98 strategy.')
    results['event_mixed'] = event_study('on', 'off', '  6c. SUPPLEMENT: events as in 6a (trend ON), returns of the always-0.98 strategy (true full size).')
    # distinct dates
    for trend in ('on', 'off'):
        alld = []
        for name in loader.NAMES:
            s_ = series[name]
            alld += [s_['d_in'][st] for st, _ in SIMS[(name, trend)][('P1', 0.25)]['episodes']]
        yrs = sorted(set(d[:4] for d in alld))
        P('  trend %s: %d pooled P1 starts on %d distinct dates in %d distinct years; per year: %s'
          % (trend, len(alld), len(set(alld)), len(yrs),
             ', '.join('%s:%d' % (y, sum(1 for d in alld if d[:4] == y)) for y in yrs)))

    # ---------------- 11 names ----------------
    def names_table(trend, p, v2='P2', show=True):
        rows = []
        if show:
            P('  %-6s | %-34s | %-34s | %-34s | %4s %4s' % ('name', PLABEL['H1'], PLABEL['H2'], PLABEL['ALL'], 'P1ep', 'P2ep'))
        cnt = {per: [0, 0, 0] for per in PERIODS}
        for name in loader.NAMES:
            s_ = series[name]
            pb = period_bounds(s_['d_in'])
            years = [int(d[:4]) for d in s_['d_in']]
            Rr = SIMS[(name, trend)]
            d = [x - y for x, y in zip(Rr[(v2, p)]['lr'], Rr[('P1', p)]['lr'])]
            cells = []
            row = dict(name=name, trend_rule=trend, pause_size=p, variant=v2)
            for per in PERIODS:
                lo, hi = pb[per]
                pt, q5, q95, fpos = year_boot(d, years, lo, hi)
                sgn = '+' if pt > 0 else ('-' if pt < 0 else '0')
                cnt[per][0 if pt > 0 else (1 if pt < 0 else 2)] += 1
                cells.append('%s %+8.4f [%+7.4f,%+7.4f]' % (sgn, pt, q5, q95))
                row[per] = pt
                row[per + '_lo'] = q5
                row[per + '_hi'] = q95
            row['p1_episodes'] = len(Rr[('P1', p)]['episodes'])
            row['p2_episodes'] = len(Rr[(v2, p)]['episodes'])
            rows.append(row)
            if show:
                P('  %-6s | %-34s | %-34s | %-34s | %4d %4d' % (name, cells[0], cells[1], cells[2],
                                                              row['p1_episodes'], row['p2_episodes']))
        summ = {per: dict(pos=cnt[per][0], neg=cnt[per][1], zero=cnt[per][2]) for per in PERIODS}
        P('  %s-P1, trend %s, p=%.2f: positive/negative/zero of 11 -> H1 %d/%d/%d, H2 %d/%d/%d, whole %d/%d/%d'
          % (v2, trend, p, cnt['H1'][0], cnt['H1'][1], cnt['H1'][2], cnt['H2'][0], cnt['H2'][1], cnt['H2'][2],
             cnt['ALL'][0], cnt['ALL'][1], cnt['ALL'][2]))
        return rows, summ

    P('')
    P('7. ELEVEN NAMES: P2 - P1 in g (percent per night), sign, 90% year-block interval')
    P('  7a. trend ON, p = 0.25 (the pre-registered comparison)')
    rows_on, summ_on = names_table('on', 0.25)
    results['names_on_025'] = rows_on
    results['names_on_025_summary'] = summ_on
    P('')
    P('  7b. trend OFF, p = 0.25')
    rows_off, summ_off = names_table('off', 0.25)
    results['names_off_025'] = rows_off
    results['names_off_025_summary'] = summ_off
    P('')
    P('  7c. sign counts for the other cells (no per-name lines)')
    results['names_other'] = {}
    for trend in ('on', 'off'):
        for p in PSIZES:
            for v2 in ('P2', 'P2B', 'P2x10', 'P3'):
                if trend in ('on', 'off') and p == 0.25 and v2 == 'P2':
                    continue
                _, sm = names_table(trend, p, v2, show=False)
                results['names_other']['%s|%.2f|%s' % (trend, p, v2)] = sm
    P('')
    P('  7d. per name, whole span, trend ON p=0.25: g of P0, P1, P2, P2B, P3 and worst drawdown of P1 and P2')
    P('  %-6s %9s %9s %9s %9s %9s %8s %8s %8s' % ('name', 'g P0', 'g P1', 'g P2', 'g P2B', 'g P3', 'DD P0', 'DD P1', 'DD P2'))
    names_levels = []
    for name in loader.NAMES:
        s_ = series[name]
        n = len(s_['u'])
        Rr = SIMS[(name, 'on')]
        b = BASE[(name, 'on')]
        st = {k: pstats(Rr[vkey(k, 0.25)], b, 0, n) for k in ['P0', 'P1', 'P2', 'P2B', 'P3']}
        P('  %-6s %+9.4f %+9.4f %+9.4f %+9.4f %+9.4f %8.2f %8.2f %8.2f'
          % (name, st['P0']['g'], st['P1']['g'], st['P2']['g'], st['P2B']['g'], st['P3']['g'],
             st['P0']['dd'], st['P1']['dd'], st['P2']['dd']))
        names_levels.append(dict(name=name, g={k: st[k]['g'] for k in st}, dd={k: st[k]['dd'] for k in st}))
    results['names_levels_on'] = names_levels

    # ---------------- sensitivities ----------------
    P('')
    P('8. SENSITIVITY TO THE READINGS (NVDA unless stated; trend ON, p = 0.25)')
    sens = {}
    s_ = series['NVDA']
    pb = period_bounds(s_['d_in'])
    Rr = SIMS[('NVDA', 'on')]
    b = BASE[('NVDA', 'on')]
    # 8a P2 reading A vs B
    P('  8a. P2 re-arming reading A vs B (R3): g per period')
    for per in PERIODS:
        lo, hi = pb[per]
        a_ = pstats(Rr[('P2', 0.25)], b, lo, hi)
        b2 = pstats(Rr[('P2B', 0.25)], b, lo, hi)
        p1 = pstats(Rr[('P1', 0.25)], b, lo, hi)
        P('     %-22s g P1 %+.4f | P2(A) %+.4f (P2-P1 %+.4f, DD %.2f) | P2(B) %+.4f (P2B-P1 %+.4f, DD %.2f) | DD P1 %.2f'
          % (PLABEL[per], p1['g'], a_['g'], a_['g'] - p1['g'], a_['dd'], b2['g'], b2['g'] - p1['g'], b2['dd'], p1['dd']))
        sens['rearm_%s' % per] = dict(p1=p1['g'], p2a=a_['g'], p2b=b2['g'], dd1=p1['dd'], dd2a=a_['dd'], dd2b=b2['dd'])
    # 8b restart at 2015
    P('  8b. Restart E = 1 with fresh pause state on 2015-01-02 (R2), second half only')
    lo, hi = pb['H2']
    u2 = s_['u'][lo:hi]
    b2_ = b[lo:hi]
    rs = {k: sim.simulate(u2, b2_, v, p=0.25, rearm_during_pause=ra)
          for k, v, ra in [('P0', 'P0', True), ('P1', 'P1', True), ('P2', 'P2', True), ('P2B', 'P2', False), ('P3', 'P3', True)]}
    for k in ['P0', 'P1', 'P2', 'P2B', 'P3']:
        a_ = pstats(rs[k], b2_, 0, hi - lo)
        c_ = pstats(Rr[vkey(k, 0.25)], b, lo, hi)
        P('     %-4s restart: g %+.4f DD %.2f epis %d paused %d | continuous: g %+.4f DD %.2f epis %d paused %d'
          % (k, a_['g'], a_['dd'], a_['episodes'], a_['paused'], c_['g'], c_['dd'], c_['episodes'], c_['paused']))
        sens['restart_%s' % k] = dict(restart_g=a_['g'], cont_g=c_['g'], restart_dd=a_['dd'], cont_dd=c_['dd'])
    # 8c drawdown with carried peak
    P('  8c. Worst drawdown with the peak carried in from before the period (R8)')
    for per in PERIODS:
        lo, hi = pb[per]
        P('     %-22s ' % PLABEL[per] + ' | '.join('%s within %.2f carried %.2f'
                                                 % (k, pstats(Rr[vkey(k, 0.25)], b, lo, hi)['dd'], dd_carried(Rr[vkey(k, 0.25)], lo, hi))
                                                 for k in ['P0', 'P1', 'P2', 'P2B', 'P3']))
        sens['ddcarried_%s' % per] = {k: dd_carried(Rr[vkey(k, 0.25)], lo, hi) for k in ['P0', 'P1', 'P2', 'P2B', 'P3']}
    # 8d other names started 2000-10-30; AMZN flat on gap night
    P('  8d. Ten other names started on 2000-10-30 instead of %s (R5): whole-span P2-P1 (trend ON, p=0.25)' % sorted(up)[0])
    cnt = [0, 0, 0]
    cntb = [0, 0, 0]
    for name in loader.NAMES:
        sa = build_nights(name, bars, up, start_date='2000-10-30')
        ba = [UP_SIZE if v else DOWN_SIZE for v in sa['up']]
        r1 = sim.simulate(sa['u'], ba, 'P1', p=0.25)
        r2 = sim.simulate(sa['u'], ba, 'P2', p=0.25)
        r2b = sim.simulate(sa['u'], ba, 'P2', p=0.25, rearm_during_pause=False)
        n = len(sa['u'])
        dg = 100 * (sum(r2['lr']) - sum(r1['lr'])) / n
        dgb = 100 * (sum(r2b['lr']) - sum(r1['lr'])) / n
        base = next(r for r in rows_on if r['name'] == name)['ALL']
        cnt[0 if dg > 0 else (1 if dg < 0 else 2)] += 1
        cntb[0 if dgb > 0 else (1 if dgb < 0 else 2)] += 1
        P('     %-5s P2-P1 %+.4f (default start %+.4f) | P2B-P1 %+.4f' % (name, dg, base, dgb))
    P('     positive/negative/zero: P2 %d/%d/%d, P2B %d/%d/%d' % (cnt[0], cnt[1], cnt[2], cntb[0], cntb[1], cntb[2]))
    sens['start1030_counts'] = dict(p2=cnt, p2b=cntb)
    P('  8e. AMZN with the night across its skipped bar (2008-10-28 -> 2008-10-30) held flat instead (R11)')
    sa = build_nights('AMZN', bars, up, drop_gap=True)
    ba = [UP_SIZE if v else DOWN_SIZE for v in sa['up']]
    r1 = sim.simulate(sa['u'], ba, 'P1', p=0.25)
    r2 = sim.simulate(sa['u'], ba, 'P2', p=0.25)
    n = len(sa['u'])
    P('     AMZN whole-span P2-P1 %+.4f (default %+.4f)' % (100 * (sum(r2['lr']) - sum(r1['lr'])) / n,
                                                           next(r for r in rows_on if r['name'] == 'AMZN')['ALL']))
    # 8f flagged moves removed
    if flagged:
        P('  8f. Flagged >45%% moves set to zero return: see list in section 1 (%d nights)' % len(flagged))
    else:
        P('  8f. No overnight move beyond +/-45% exists, so the sanity filter changes nothing.')
    # 8g event study, other horizon reading (nights t+1 .. t+h)
    P('  8g. Event study with the horizon starting the night AFTER the pause start (nights t+1..t+h) (R10), trend ON, p=0.25')
    P('     %-7s %3s %6s %10s %10s %10s' % ('set', 'h', 'events', 'cond mean', 'cond med', 'uncond mn'))
    sens['event_alt'] = []
    pooled = {h: dict(ev=[], un=[]) for h in HZ}
    for name in loader.NAMES:
        lr0 = SIMS[(name, 'on')]['P0']['lr']
        starts = [st for st, _ in SIMS[(name, 'on')][('P1', 0.25)]['episodes']]
        n = len(lr0)
        cs = [0.0]
        for v in lr0:
            cs.append(cs[-1] + v)
        for h in HZ:
            ev = [cs[t + 1 + h] - cs[t + 1] for t in starts if t + 1 + h <= n]
            un = [cs[t + h] - cs[t] for t in range(0, n - h + 1)]
            pooled[h]['ev'] += ev
            pooled[h]['un'] += un
            if name == 'NVDA':
                P('     %-7s %3d %6d %+10.4f %+10.4f %+10.4f' % ('NVDA', h, len(ev), sum(ev) / len(ev), statistics.median(ev), sum(un) / len(un)))
                sens['event_alt'].append(dict(set='NVDA', h=h, events=len(ev), cond_mean=sum(ev) / len(ev),
                                              cond_median=statistics.median(ev), uncond_mean=sum(un) / len(un)))
    for h in HZ:
        ev, un = pooled[h]['ev'], pooled[h]['un']
        P('     %-7s %3d %6d %+10.4f %+10.4f %+10.4f' % ('POOL11', h, len(ev), sum(ev) / len(ev), statistics.median(ev), sum(un) / len(un)))
        sens['event_alt'].append(dict(set='POOL11', h=h, events=len(ev), cond_mean=sum(ev) / len(ev),
                                      cond_median=statistics.median(ev), uncond_mean=sum(un) / len(un)))
    # 8h periods by exit date
    P('  8h. Nights assigned to periods by EXIT date instead of entry date (R1): NVDA, trend ON, p=0.25')
    split_exit = next(i for i, d in enumerate(s_['d_out']) if d >= H2_START)
    for lab, (lo, hi) in [('H1 (exit <= 2014-12-31)', (0, split_exit)), ('H2 (exit >= 2015-01-02)', (split_exit, len(s_['u'])))]:
        g1 = pstats(Rr[('P1', 0.25)], b, lo, hi)
        g2 = pstats(Rr[('P2', 0.25)], b, lo, hi)
        g2b = pstats(Rr[('P2B', 0.25)], b, lo, hi)
        P('     %-26s nights %d | g P1 %+.4f P2 %+.4f (diff %+.4f) P2B %+.4f (diff %+.4f) | DD P1 %.2f P2 %.2f'
          % (lab, g1['n'], g1['g'], g2['g'], g2['g'] - g1['g'], g2b['g'], g2b['g'] - g1['g'], g1['dd'], g2['dd']))
    sens['split_exit_moves_nights'] = pb['H1'][1] - split_exit
    # 8i pauses inside the first 19 nights (window not yet full, R7)
    early = {}
    for name in loader.NAMES:
        for trend in ('on', 'off'):
            for key, rr_ in SIMS[(name, trend)].items():
                if key == 'P0':
                    continue
                e_ = [st for st, _ in rr_['episodes'] if st < 19]
                if e_:
                    early.setdefault((name, trend), []).append((key[0], key[1], series[name]['d_in'][e_[0]]))
    P('  8i. Pause episodes that start inside the first 19 nights, when the 20-session window is not yet full (R7)')
    if not early:
        P('     none in any run')
    for (name, trend), lst in sorted(early.items()):
        P('     %-5s trend %-3s: %d of 18 paused variants affected, earliest start %s' % (name, trend, len(lst), min(x[2] for x in lst)))
    if any(tr == 'on' for (_, tr) in early):
        P('     NOTE: a trend-ON run is affected (see above).')
    else:
        P('     No trend-ON run is affected, so R7 cannot change the pre-registered criteria (trend ON, p = 0.25).')
    P('     Alternative reading (no trigger until 20 equity values exist): whole-span P2-P1, p = 0.25')
    sens['early_alt'] = []
    for trend in ('on', 'off'):
        cnt_alt = [0, 0, 0]
        cnt_def = [0, 0, 0]
        parts = []
        for name in loader.NAMES:
            sn = series[name]
            bn = BASE[(name, trend)]
            r1a = sim.simulate(sn['u'], bn, 'P1', p=0.25, min_obs=20)
            r2a = sim.simulate(sn['u'], bn, 'P2', p=0.25, min_obs=20)
            n_ = len(sn['u'])
            dalt = 100 * (sum(r2a['lr']) - sum(r1a['lr'])) / n_
            ddef = 100 * (sum(SIMS[(name, trend)][('P2', 0.25)]['lr']) - sum(SIMS[(name, trend)][('P1', 0.25)]['lr'])) / n_
            cnt_alt[0 if dalt > 0 else (1 if dalt < 0 else 2)] += 1
            cnt_def[0 if ddef > 0 else (1 if ddef < 0 else 2)] += 1
            if abs(dalt - ddef) > 1e-12:
                parts.append('%s %+.4f (default %+.4f)' % (name, dalt, ddef))
            sens['early_alt'].append(dict(name=name, trend_rule=trend, alt=dalt, default=ddef))
        P('     trend %-3s: names whose P2-P1 changes: %s | positive/negative/zero %d/%d/%d (default %d/%d/%d)'
          % (trend, '; '.join(parts) if parts else 'none', cnt_alt[0], cnt_alt[1], cnt_alt[2], cnt_def[0], cnt_def[1], cnt_def[2]))
    sens['early_starts'] = {'%s|%s' % k: v for k, v in early.items()}
    # 8j concentration: P2-P1 by calendar year, NVDA
    P('  8j. Concentration: NVDA P2-P1 total log difference by calendar year (trend ON, p=0.25; years with no difference omitted)')
    years_n = [int(d[:4]) for d in s_['d_in']]
    conc = {}
    for lab, key in [('P2(A)-P1', 'P2'), ('P2(B)-P1', 'P2B')]:
        d = [x - y for x, y in zip(Rr[(key, 0.25)]['lr'], Rr[('P1', 0.25)]['lr'])]
        byy = {}
        for y, v in zip(years_n, d):
            byy[y] = byy.get(y, 0.0) + v
        nz = {y: v for y, v in byy.items() if abs(v) > 1e-12}
        P('     %-9s ' % lab + ', '.join('%d %+.4f' % (y, nz[y]) for y in sorted(nz)))
        h1 = {y: v for y, v in nz.items() if y <= 2014}
        h2 = {y: v for y, v in nz.items() if y >= 2015}
        for hl, hh in (('H1', h1), ('H2', h2)):
            tot = sum(hh.values())
            if hh:
                ybig = max(hh, key=lambda k: abs(hh[k]))
                P('       %s total %+.4f; largest single year %d (%+.4f); total without that year %+.4f'
                  % (hl, tot, ybig, hh[ybig], tot - hh[ybig]))
                conc['%s_%s' % (key, hl)] = dict(total=tot, big_year=ybig, big=hh[ybig], without=tot - hh[ybig])
    sens['concentration'] = conc
    results['sensitivity'] = sens

    # ---------------- criteria ----------------
    P('')
    P('9. PRE-REGISTERED CRITERIA (LAB.md L15), trend ON, p = 0.25')
    crit = {}
    for lab, key in [('reading A (primary)', 'P2'), ('reading B', 'P2B')]:
        g1 = {per: pstats(Rr[('P1', 0.25)], b, *pb[per]) for per in PERIODS}
        g2 = {per: pstats(Rr[(key, 0.25)], b, *pb[per]) for per in PERIODS}
        c1 = (g2['H1']['g'] >= g1['H1']['g']) and (g2['H2']['g'] >= g1['H2']['g'])
        c2 = (g2['H1']['dd'] - g1['H1']['dd'] <= 5.0) and (g2['H2']['dd'] - g1['H2']['dd'] <= 5.0)
        pos = neg = zero = 0
        for name in loader.NAMES:
            Rn = SIMS[(name, 'on')]
            dsum = sum(Rn[(key, 0.25)]['lr']) - sum(Rn[('P1', 0.25)]['lr'])
            if dsum > 0:
                pos += 1
            elif dsum < 0:
                neg += 1
            else:
                zero += 1
        c3 = pos >= 8
        outcome = 'change_to_P2' if (c1 and c2 and c3) else 'keep_as_written'
        P('  %s:' % lab)
        P('    (1) P2 g not lower than P1 in both halves: H1 %+.4f vs %+.4f (diff %+.4f), H2 %+.4f vs %+.4f (diff %+.4f) -> %s'
          % (g2['H1']['g'], g1['H1']['g'], g2['H1']['g'] - g1['H1']['g'],
             g2['H2']['g'], g1['H2']['g'], g2['H2']['g'] - g1['H2']['g'], 'PASS' if c1 else 'FAIL'))
        P('    (2) P2 worst drawdown no more than 5 points deeper in either half: H1 %.2f vs %.2f (%+.2f), H2 %.2f vs %.2f (%+.2f) -> %s'
          % (g2['H1']['dd'], g1['H1']['dd'], g2['H1']['dd'] - g1['H1']['dd'],
             g2['H2']['dd'], g1['H2']['dd'], g2['H2']['dd'] - g1['H2']['dd'], 'PASS' if c2 else 'FAIL'))
        P('    (3) sign of P2-P1 (whole span) across 11 names: %d positive, %d negative, %d exactly zero -> largest same-sign count %d, positive count %d -> %s'
          % (pos, neg, zero, max(pos, neg), pos, 'PASS' if c3 else 'FAIL'))
        P('    OUTCOME: %s' % outcome)
        crit[key] = dict(c1=c1, c2=c2, c3=c3, pos=pos, neg=neg, zero=zero, outcome=outcome,
                         h1_diff=g2['H1']['g'] - g1['H1']['g'], h2_diff=g2['H2']['g'] - g1['H2']['g'],
                         h1_dd=(g1['H1']['dd'], g2['H1']['dd']), h2_dd=(g1['H2']['dd'], g2['H2']['dd']))
    results['criteria'] = crit

    # ---------------- dollars ----------------
    P('')
    P('10. MONEY AT STAKE AT E = $82')
    EQ = 82.0
    NPM = 21.0
    allu = s_['u']
    upu = [v for v, f in zip(s_['u'], s_['up']) if f]
    lo2, hi2 = pb['H2']
    upu2 = [v for v, f in zip(s_['u'][lo2:hi2], s_['up'][lo2:hi2]) if f]
    r1 = Rr[('P1', 0.25)]
    ext = []
    for st, L in r1['episodes']:
        ext += list(range(st + 5, st + L))
    extup = [t for t in ext if b[t] > DOWN_SIZE]
    extu = [s_['u'][t] for t in extup]
    dsz = UP_SIZE - DOWN_SIZE
    P('  P1 and P2 hold the same size during the first 5 sessions of a pause and on every DOWN-trend night (both 0.25).')
    P('  They differ only on extension nights (session 6 onward, equity still at or below the trigger) when the trend is UP:')
    P('  P1 holds 0.25 of equity, P2 holds 0.98, a difference of %.2f of equity = $%.2f of 2x exposure.' % (dsz, dsz * EQ))
    dol = {}
    for lab, us in [('NVDA all nights 2000-2026', allu), ('NVDA UP-trend nights 2000-2026', upu),
                    ('NVDA UP-trend nights 2015-2026', upu2), ('NVDA P1 extension nights with trend UP (n=%d)' % len(extu), extu)]:
        if not us:
            continue
        m = sum(us) / len(us)
        sd = statistics.pstdev(us) if len(us) > 1 else float('nan')
        se = sd / math.sqrt(len(us)) if len(us) > 1 else float('nan')
        P('   mean unit return %-48s %+.4f%% a night (s.e. %.4f%%) -> $%+.3f a night, $%+.2f per 21-night month of UP-trend extension'
          % (lab + ':', 100 * m, 100 * se, EQ * dsz * m, EQ * dsz * m * NPM))
        dol[lab] = dict(mean_u=m, per_night=EQ * dsz * m, per_month=EQ * dsz * m * NPM, n=len(us))
    nall = len(allu)
    tot = sum(Rr[('P2', 0.25)]['lr']) - sum(r1['lr'])
    totb = sum(Rr[('P2B', 0.25)]['lr']) - sum(r1['lr'])
    P('  Realised in the 2000-2026 simulation (NVDA, trend ON, p=0.25): P2-P1 = %+.4f log points in total over %d nights (%.1f years), reading B %+.4f.'
      % (tot, nall, nall / 252.0, totb))
    P('   as a long-run average over all months, pause or not: $%+.4f a month at $82 (reading B $%+.4f)'
      % (EQ * tot / nall * NPM, EQ * totb / nall * NPM))
    P('   P1 episodes %d; extension nights %d, of which trend UP %d (%.2f per episode).'
      % (len(r1['episodes']), len(ext), len(extup), len(extup) / max(1, len(r1['episodes']))))
    lens = [L for _, L in r1['episodes']]
    P('   per episode at $82: %+.4f log points / %d episodes = %+.5f -> $%+.3f per pause episode (reading B $%+.3f)'
      % (tot, len(lens), tot / len(lens), EQ * tot / len(lens), EQ * totb / len(lens)))
    dol['sim_total_log'] = tot
    dol['sim_total_log_B'] = totb
    dol['per_month_longrun'] = EQ * tot / nall * NPM
    dol['per_episode'] = EQ * tot / len(lens)
    dol['per_episode_B'] = EQ * totb / len(lens)
    dol['episodes'] = len(lens)
    dol['ext'] = len(ext)
    dol['extup'] = len(extup)
    # pooled across names: extension nights UP
    pool = []
    for name in loader.NAMES:
        sn = series[name]
        bn = BASE[(name, 'on')]
        rn = SIMS[(name, 'on')][('P1', 0.25)]
        for st, L in rn['episodes']:
            pool += [sn['u'][t] for t in range(st + 5, st + L) if bn[t] > DOWN_SIZE]
    if pool:
        m = sum(pool) / len(pool)
        se = statistics.pstdev(pool) / math.sqrt(len(pool))
        P('   pooled 11 names, P1 extension nights with trend UP (n=%d): mean unit return %+.4f%% (naive s.e. %.4f%%) -> $%+.3f a night, $%+.2f per 21 such nights'
          % (len(pool), 100 * m, 100 * se, EQ * dsz * m, EQ * dsz * m * NPM))
        dol['pooled_ext_up'] = dict(mean_u=m, n=len(pool), per_night=EQ * dsz * m, per_month=EQ * dsz * m * NPM)
    qd = sorted(up)
    P('  Trend state at the last completed close in the sample (%s): %s. On a DOWN night the two variants are identical and the difference is $0.'
      % (qd[-1], 'UP' if up[qd[-1]] else 'DOWN'))
    dol['last_trend'] = (qd[-1], bool(up[qd[-1]]))
    sd_u = statistics.pstdev(allu)
    P('  Noise: the s.d. of the NVDA unit return is %.2f%% a night, so the $%.2f size gap moves by about $%.2f (1 s.d.) on a single night,'
      % (100 * sd_u, dsz * EQ, dsz * EQ * sd_u))
    P('   against an expected difference of $0.10-$0.17 a night. Over a full extension (at most 14 nights) the 1-s.d. band is about $%.2f.'
      % (dsz * EQ * sd_u * math.sqrt(14)))
    dol['sd_u'] = sd_u
    dol['sd_night_dollars'] = dsz * EQ * sd_u
    years_n = [int(d[:4]) for d in s_['d_in']]
    for lab, key in [('reading A', 'P2'), ('reading B', 'P2B')]:
        d = [x - y for x, y in zip(Rr[(key, 0.25)]['lr'], r1['lr'])]
        pt, q5, q95, _ = year_boot(d, years_n, 0, nall)
        P('  Whole-span P2-P1 (%s) = %+.4f %%/night, 90%% interval [%+.4f, %+.4f] -> $%+.3f a month at $82, interval [$%+.3f, $%+.3f]'
          % (lab, pt, q5, q95, EQ * NPM * pt / 100, EQ * NPM * q5 / 100, EQ * NPM * q95 / 100))
        dol['longrun_ci_%s' % key] = (EQ * NPM * pt / 100, EQ * NPM * q5 / 100, EQ * NPM * q95 / 100)
    results['dollars'] = dol

    P('')
    P('VARIANTS TRIED (adoption bar): 19 simulated variants per name and trend setting = P0 + {P1, P2 reading A, P2 reading B, P3,')
    P(' P2x10 reading A, P2x10 reading B} x 3 pause sizes; run for 11 names x 2 trend settings (418 simulations). The pre-registered')
    P(' decision uses one comparison only: P2 vs P1, pause size 0.25, trend rule ON (NVDA halves; 11-name sign count).')

    with open(os.path.join(HERE, 'results_main.txt'), 'w') as fh:
        fh.write('\n'.join(OUT) + '\n')
    with open(os.path.join(HERE, 'results.json'), 'w') as fh:
        json.dump(results, fh, indent=1, default=str)


if __name__ == '__main__':
    main()
