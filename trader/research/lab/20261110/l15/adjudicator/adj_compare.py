"""Adjudicator: (1) run own implementation; (2) compare item by item with analyst A's
results.json and analyst B's nvda_table.json; (3) run A's and B's simulation functions on
the adjudicator's night arrays under MATCHED P2 readings and compare night by night.
Writes nothing outside this directory (prints only)."""
import importlib.util
import json
import math
import sys
sys.dont_write_bytecode = True   # importing the analysts' modules must not write .pyc files into their directories
import numpy as np

import adj_core as K

BASE = '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/l15/'


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A = load_mod('a_sim', BASE + 'analyst_a/sim.py')
B = load_mod('b_sim', BASE + 'analyst_b/b_sim.py')

frames, rep = K.load_frames()
print('== LOADER (adjudicator) ==')
for s in ['QQQ'] + K.NAMES:
    print('  %-5s' % s, rep[s])
up, pm = K.trend_series(frames['QQQ'])
first_tr = up.dropna().index[0]
print('QQQ sessions', len(frames['QQQ']), 'first trend state', first_tr,
      '| last 4:', [(d, bool(v)) for d, v in up.dropna().iloc[-4:].items()],
      '| prev-199 mean on last 2:', [round(float(x), 2) for x in pm.iloc[-2:]])

NIGHTS = {s: K.nights(frames, s, up) for s in K.NAMES}
nv = NIGHTS['NVDA']
mk = K.masks(nv['dates'])
print('NVDA nights', len(nv['r']), nv['dates'][0], '..', nv['dates'][-1], 'last exit', nv['exit'][-1],
      '| H1', int(mk['H1'].sum()), 'H2', int(mk['H2'].sum()), '| UP nights', int(nv['up'].sum()))
big = [(s, NIGHTS[s]['dates'][i], float(NIGHTS[s]['r'][i])) for s in K.NAMES
       for i in np.where(np.abs(NIGHTS[s]['r']) > 0.45)[0]]
print('overnight moves beyond +/-45%:', big if big else 'none')
for s in K.NAMES:
    print('  %-5s nights %d first %s' % (s, len(NIGHTS[s]['r']), NIGHTS[s]['dates'][0]))


def base(nt, trend):
    return np.where(nt['up'], K.UP, K.DOWN) if trend == 'on' else np.full(len(nt['r']), K.UP)


VARS = [('P0', 'P0', 5, 'post'), ('P1', 'P1', 5, 'post'), ('P2post', 'P2', 5, 'post'),
        ('P2during', 'P2', 5, 'during'), ('P3', 'P3', 5, 'post'),
        ('P2x10post', 'P2', 10, 'post'), ('P2x10during', 'P2', 10, 'during')]

SIM = {}
for s in K.NAMES:
    for trend in ('on', 'off'):
        b = base(NIGHTS[s], trend)
        for p in (0.10, 0.25, 0.50):
            for lab, rule, N, rearm in VARS:
                SIM[(s, trend, p, lab)] = K.simulate(NIGHTS[s]['r'], b, rule, p, N, rearm)

# ---------------------------------------------------------------- night-by-night cross-run
print('\n== NIGHT-BY-NIGHT CROSS-RUN on the adjudicator night arrays (max |d lnR|, size mismatches) ==')
worstA = worstB = 0.0
mmA = mmB = 0
cells = 0
for s in K.NAMES:
    nt = NIGHTS[s]
    u = [2.0 * x - 0.0009 for x in nt['r']]
    for trend in ('on', 'off'):
        b = base(nt, trend)
        for p in (0.10, 0.25, 0.50):
            for lab, rule, N, rearm in VARS:
                mine = SIM[(s, trend, p, lab)]
                ra = A.simulate(u, list(b), rule, p=p, n_len=N, rearm_during_pause=(rearm == 'during'))
                rb = B.run_loop(nt['r'], b, rule, p, N, 'any' if rearm == 'during' else 'post')
                dA = float(np.max(np.abs(np.array(ra['lr']) - mine['lr'])))
                dB = float(np.max(np.abs(rb['lnR'] - mine['lr'])))
                worstA = max(worstA, dA)
                worstB = max(worstB, dB)
                mmA += int((np.array(ra['s']) != mine['size']).sum())
                mmB += int((rb['s'] != mine['size']).sum())
                mmA += int(list(ra['paused']) != list(mine['pz']))
                mmB += int(list(rb['paused']) != list(mine['pz']))
                mmA += int([e[0] for e in ra['episodes']] != [e[0] for e in mine['eps']])
                mmB += int(list(rb['starts']) != list(mine['starts']))
                cells += 1
print('cells compared: %d (11 names x 2 trend x 3 pause sizes x 7 variants)' % cells)
print('A vs adjudicator: max |d lnR| = %.3e, mismatches = %d' % (worstA, mmA))
print('B vs adjudicator: max |d lnR| = %.3e, mismatches = %d' % (worstB, mmB))

# ---------------------------------------------------------------- NVDA table, trend on, p 0.25
print('\n== NVDA, TREND ON, p=0.25: adjudicator vs A (results.json) vs B (nvda_table.json) ==')
ja = json.load(open(BASE + 'analyst_a/results.json'))
jb = json.load(open(BASE + 'analyst_b/nvda_table.json'))
PA = {'H1': '2000-10-30..2014-12-31', 'H2': '2015-01-02..2026-11-06', 'ALL': 'whole span'}
PB = {'H1': '2000-10-30..2014-12-31', 'H2': '2015-01-02..2026-11-06', 'ALL': 'whole span 2000-10-30..2026-11-06'}


def rowA(trend, per, var, p):
    for r in ja['nvda_on' if trend == 'on' else 'nvda_off']:
        if r['period'] == PA[per] and r['variant'] == var and (var == 'P0' or abs(r['pause_size'] - p) < 1e-9):
            return r
    return None


def rowB(trend, per, var, p):
    for r in jb:
        if r['trend_rule'] == trend and r['period'] == PB[per] and r['variant'] == var and (var == 'P0' or abs(r['pause_size'] - p) < 1e-9):
            return r
    return None


def show(trend, p):
    ndis = 0
    print('%-4s %-12s | %-34s | %-34s | %-34s | verdict' % ('per', 'variant', 'adjudicator g/dd/eps/paused', 'A g/dd/eps/paused', 'B g/dd/eps/paused'))
    for per in ('H1', 'H2', 'ALL'):
        m = mk[per]
        for lab, avar, bvar in [('P0', 'P0', 'P0'), ('P1', 'P1', 'P1'), ('P2post', 'P2B', 'P2'), ('P2during', 'P2', None),
                                ('P3', 'P3', 'P3'), ('P2x10post', 'P2Bx10', 'P2x10'), ('P2x10during', 'P2x10', None)]:
            st = K.pstats(SIM[('NVDA', trend, p, lab)], m)
            a = rowA(trend, per, avar, p)
            b = rowB(trend, per, bvar, p) if bvar else None
            fa = '%.4f %.2f %d %d' % (a['g_pct_per_night'], a['max_drawdown_pct'], a['episodes'], a['paused_nights']) if a else '-'
            fb = '%.4f %.2f %d %d' % (b['g_pct_per_night'], b['max_drawdown_pct'], b['episodes'], b['paused_nights']) if b else '(not in json)'
            ok = True
            for o in (a, b):
                if o:
                    ok &= abs(o['g_pct_per_night'] - st['g']) <= 0.0002 and abs(o['max_drawdown_pct'] - st['dd']) <= 0.01
                    ok &= o['episodes'] == st['eps'] and o['paused_nights'] == st['paused']
            ndis += (not ok)
            print('%-4s %-12s | %.4f %.2f %d %d  x%.5g med %s max %d | %-34s | %-34s | %s' % (
                per, lab, st['g'], st['dd'], st['eps'], st['paused'], st['mult'], st['med'], st['mx'], fa, fb,
                'same' if ok else 'DIFF'))
    return ndis


print('(A json label P2 = "during" reading, P2B = "post"; B json label P2 = "post")')
nd = show('on', 0.25)
print('rows differing from the adjudicator (matched reading): %d' % nd)
for trend, p in (('on', 0.10), ('on', 0.50), ('off', 0.10), ('off', 0.25), ('off', 0.50)):
    print('\n-- trend %s, p=%.2f --' % (trend, p))
    nd = show(trend, p)
    print('rows differing from the adjudicator (matched reading): %d' % nd)

# ---------------------------------------------------------------- as REPORTED (primary readings)
print('\n== AS REPORTED by each analyst (their primary P2 reading), NVDA trend on p=0.25: tolerance g 0.002, dd 0.5 ==')
for per in ('H1', 'H2', 'ALL'):
    for var in ('P0', 'P1', 'P2', 'P3', 'P2x10'):
        a = rowA('on', per, var, 0.25)
        b = rowB('on', per, var, 0.25)
        dg = a['g_pct_per_night'] - b['g_pct_per_night']
        ddd = a['max_drawdown_pct'] - b['max_drawdown_pct']
        print('%-4s %-6s A g %.4f dd %.2f eps %d pz %d | B g %.4f dd %.2f eps %d pz %d | dg %+.4f ddd %+.2f %s%s' % (
            per, var, a['g_pct_per_night'], a['max_drawdown_pct'], a['episodes'], a['paused_nights'],
            b['g_pct_per_night'], b['max_drawdown_pct'], b['episodes'], b['paused_nights'], dg, ddd,
            'within tol' if abs(dg) <= 0.002 and abs(ddd) <= 0.5 else 'OUTSIDE TOL',
            '' if (a['episodes'] == b['episodes'] and a['paused_nights'] == b['paused_nights']) else ' (episode counts differ)'))

# ---------------------------------------------------------------- P2 - P1 per name
print('\n== P2 - P1 in g (%/night), p=0.25, adjudicator. post = re-arm only after the pause; during = re-arm inside the pause ==')
for trend in ('on', 'off'):
    cnt = {('post', k): [0, 0, 0] for k in ('H1', 'H2', 'ALL')}
    cnt.update({('during', k): [0, 0, 0] for k in ('H1', 'H2', 'ALL')})
    print('trend %s' % trend)
    for s in K.NAMES:
        m = K.masks(NIGHTS[s]['dates'])
        line = '  %-5s' % s
        for rd in ('post', 'during'):
            d = SIM[(s, trend, 0.25, 'P2' + rd)]['lr'] - SIM[(s, trend, 0.25, 'P1')]['lr']
            for k in ('H1', 'H2', 'ALL'):
                v = 100.0 * d[m[k]].mean()
                cnt[(rd, k)][0 if v > 0 else (1 if v < 0 else 2)] += 1
                line += ' %+.4f' % v
            line += '  |'
        print(line, ' (post H1 H2 ALL | during H1 H2 ALL)')
    for rd in ('post', 'during'):
        print('  %-6s positive/negative/zero: H1 %s  H2 %s  ALL %s' % (rd, cnt[(rd, 'H1')], cnt[(rd, 'H2')], cnt[(rd, 'ALL')]))

# other pause sizes
print('\nwhole-span positive counts of 11 for P2-P1 at other pause sizes (post / during):')
for trend in ('on', 'off'):
    for p in (0.10, 0.25, 0.50):
        res = []
        for rd in ('post', 'during'):
            c = 0
            for s in K.NAMES:
                d = SIM[(s, trend, p, 'P2' + rd)]['lr'] - SIM[(s, trend, p, 'P1')]['lr']
                c += d.sum() > 0
            res.append(int(c))
        print('  trend %-3s p=%.2f: post %d, during %d' % (trend, p, res[0], res[1]))

# ---------------------------------------------------------------- event study
print('\n== EVENT STUDY (P1 starts, p=0.25; P0 cumulative log return over nights t..t+h-1) ==')
for trend in ('on', 'off'):
    pooled = {h: [] for h in (5, 10, 20, 40)}
    pooled_all = {h: [] for h in (5, 10, 20, 40)}
    for s in K.NAMES:
        p0 = SIM[(s, trend, 0.25, 'P0')]['lr']
        cs = np.concatenate(([0.0], np.cumsum(p0)))
        n = len(p0)
        st = SIM[(s, trend, 0.25, 'P1')]['starts']
        for h in (5, 10, 20, 40):
            allw = cs[h:] - cs[:-h]
            ev = [cs[t + h] - cs[t] for t in st if t + h <= n]
            pooled[h] += ev
            pooled_all[h] += list(allw)
            if s == 'NVDA':
                print('  trend %-3s NVDA  h=%2d: events %3d mean %+.4f median %+.4f | unconditional mean %+.4f' % (
                    trend, h, len(ev), np.mean(ev), np.median(ev), allw.mean()))
    for h in (5, 10, 20, 40):
        print('  trend %-3s POOLED h=%2d: events %3d mean %+.4f median %+.4f | unconditional mean %+.4f' % (
            trend, h, len(pooled[h]), np.mean(pooled[h]), np.median(pooled[h]), np.mean(pooled_all[h])))
