# L5 main run: primary tables (trend-rule size), secondary (0.98 always), bootstrap, criteria inputs.
import sys, json
import numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/concentration')
from l5lib import *

B = load_long('2026-11-06')
print('symbols', sorted(B), '| QQQ', min(B['QQQ']), max(B['QQQ']), '| NVDA', min(B['NVDA']), max(B['NVDA']), '| TQQQ', min(B['TQQQ']), max(B['TQQQ']))
# calendar check
for s in ('NVDA', 'TQQQ'):
    a = set(d for d in B[s] if '2015-01-02' <= d <= '2026-11-06'); q = set(d for d in B['QQQ'] if '2015-01-02' <= d <= '2026-11-06')
    print('calendar', s, 'vs QQQ: only-in-%s' % s, sorted(a - q)[:5], 'only-in-QQQ', sorted(q - a)[:5], 'n', len(a), len(q))
rows = build_nights(B)
earn = earnings_dates()
dates = [r['d'] for r in rows]
N = len(rows)
legN = np.array([r['legN'] for r in rows]); legT = np.array([r['legT'] for r in rows])
up = np.array([r['up'] for r in rows]); isE = np.array([r['d'] in earn for r in rows])
print('nights', N, dates[0], '->', rows[0]['n'], '...', dates[-1], '->', rows[-1]['n'], '| UP nights', int(up.sum()), 'DOWN nights', int((~up).sum()), '| NVDA earnings nights', int(isE.sum()))
big = [(r['d'], round(100 * r['legN'], 1), round(100 * r['legT'], 1)) for r in rows if abs(r['legN']) > 0.45 or abs(r['legT']) > 0.45]
print('extreme (>45%) legs (data-break check):', big)
gaps = [(r['d'], r['n']) for r in rows if (np.datetime64(r['n']) - np.datetime64(r['d'])).astype(int) > 5]
print('nights spanning >5 calendar days:', gaps)

s_trend = np.where(up, 0.98, 0.25)
s_full = np.full(N, 0.98)
W = [('NVDL-only w=1', 1.0), ('split w=0.5', 0.5), ('TQQQ-only w=0', 0.0)]
PER = [('2015-2020', '2015', '2020'), ('2021-2026', '2021', '2026'), ('2015-2026', '2015', '2026')]
yr = np.array([d[:4] for d in dates])

def mask(a, b):
    return (yr >= a) & (yr <= b)

def run(label, s, legN_=legN, legT_=legT, ndraw=2000, tag=''):
    print('\n' + '=' * 110)
    print(label)
    print('=' * 110)
    allres = {}
    for pname, a, b in PER:
        m = mask(a, b)
        d_ = [d for d, k in zip(dates, m) if k]
        R = np.column_stack([account_returns(legN_[m], legT_[m], s[m], w) for _, w in W])
        st_ = [stats(R[:, j]) for j in range(3)]
        bo = bootstrap(R, d_, ndraw=ndraw, offset=True)
        bo0 = bootstrap(R, d_, ndraw=ndraw, offset=False)
        print('\n--- %s  nights %d (%s .. %s), years %d ---' % (pname, m.sum(), d_[0], d_[-1], len(set(x[:4] for x in d_))))
        print('%-18s %8s %8s %7s %9s %9s %7s %7s %8s | boot(random phase): P(KILL250) P(PAUSE250) eps/1000n  | boot(year-aligned): P(KILL250) P(PAUSE250)' % ('', 'g%/n', 'mean%', 'sd%', 'worst%', 'maxDD%', 'P-ngts', 'P-eps', 'x-mult'))
        for j, (wn, w) in enumerate(W):
            x = st_[j]
            print('%-18s %+8.4f %+8.4f %7.3f %+9.2f %+9.1f %7d %7d %8.2f |                     %7.4f   %7.4f   %7.2f   |                      %7.4f   %7.4f' % (
                wn, x['g'], x['mean'], x['sd'], x['worst'], x['maxdd'], x['pause_nights'], x['pause_eps'], x['mult'],
                (bo['minE_h'][:, j] <= 0.5).mean(), bo['pause_h'][:, j].mean(), bo['eps'][:, j].mean(),
                (bo0['minE_h'][:, j] <= 0.5).mean(), bo0['pause_h'][:, j].mean()))
        # other loss levels within 250 nights (random phase)
        print('   boot(random phase) P(min equity within 250 nights <= level): ' + ' | '.join(
            'level %.2f: ' % L + ' / '.join('%.4f' % (bo['minE_h'][:, j] <= L).mean() for j in range(3)) for L in (0.8, 0.7, 0.607, 0.5)))
        print('   boot(random phase) 5th pct of min equity in 250 nights: ' + ' / '.join('%.3f' % pct(bo['minE_h'][:, j], 5) for j in range(3))
              + ' | median end equity after 250 nights: ' + ' / '.join('%.3f' % pct(bo['endE_h'][:, j], 50) for j in range(3))
              + ' | 5th pct end equity: ' + ' / '.join('%.3f' % pct(bo['endE_h'][:, j], 5) for j in range(3)))
        # differences split - NVDL-only, year-block (year-aligned, K years) intervals
        print('   split minus NVDL-only (point; 90%% year-block interval [5th,95th]; share of draws < 0):')
        for key, lab, sample in (('g', 'growth g %/night', lambda j: st_[j]['g']), ('sd', 'sd %', lambda j: st_[j]['sd']),
                                 ('worst', 'worst night %', lambda j: st_[j]['worst']), ('maxdd', 'max drawdown %', lambda j: st_[j]['maxdd']),
                                 ('eps', 'PAUSE eps /1000 nights', lambda j: st_[j]['pause_eps'] * 1000.0 / m.sum())):
            dif = bo0[key][:, 1] - bo0[key][:, 0]
            print('      %-24s %+9.4f   [%+.4f, %+.4f]   P(diff<0)=%.3f   (random-phase interval [%+.4f, %+.4f])' % (
                lab, sample(1) - sample(0), pct(dif, 5), pct(dif, 95), (dif < 0).mean(),
                pct(bo[key][:, 1] - bo[key][:, 0], 5), pct(bo[key][:, 1] - bo[key][:, 0], 95)))
        dif = bo0['g'][:, 2] - bo0['g'][:, 0]
        print('      TQQQ-only minus NVDL-only growth: %+9.4f   [%+.4f, %+.4f]' % (st_[2]['g'] - st_[0]['g'], pct(dif, 5), pct(dif, 95)))
        allres[pname] = dict(stats={W[j][0]: st_[j] for j in range(3)},
                             kill250={W[j][0]: float((bo['minE_h'][:, j] <= 0.5).mean()) for j in range(3)},
                             kill250_aligned={W[j][0]: float((bo0['minE_h'][:, j] <= 0.5).mean()) for j in range(3)},
                             pause250={W[j][0]: float(bo['pause_h'][:, j].mean()) for j in range(3)},
                             pause250_aligned={W[j][0]: float(bo0['pause_h'][:, j].mean()) for j in range(3)},
                             eps1000={W[j][0]: float(bo['eps'][:, j].mean()) for j in range(3)},
                             dg_split=dict(point=st_[1]['g'] - st_[0]['g'], lo=pct(bo0['g'][:, 1] - bo0['g'][:, 0], 5), hi=pct(bo0['g'][:, 1] - bo0['g'][:, 0], 95)))
    return allres

res = {}
res['primary_trend'] = run('PRIMARY (pre-registered): size from the trend rule (0.98 UP / 0.25 DOWN), 9bp cost, synthetic 2x NVDA, real TQQQ, no earnings blackout', s_trend)
res['secondary_full'] = run('SECONDARY: size 0.98 always', s_full)
# Sensitivity E: live rule s3(d) - NVDA leg in cash on NVDA earnings nights (TQQQ part stays invested)
legN_E = np.where(isE, COST, legN)  # so that w*legN - w*cost nets ~0 for the NVDA part: handled below properly
def run_blackout(label, s):
    # NVDA part: on earnings nights neither return nor cost on that part
    print('\n' + '=' * 110); print(label); print('=' * 110)
    out = {}
    for pname, a, b in PER:
        m = mask(a, b); d_ = [d for d, k in zip(dates, m) if k]
        cols = []
        for _, w in W:
            partN = np.where(isE[m], 0.0, w * (legN[m] - COST))
            partT = (1 - w) * (legT[m] - COST)
            cols.append(s[m] * (partN + partT))
        R = np.column_stack(cols)
        st_ = [stats(R[:, j]) for j in range(3)]
        bo = bootstrap(R, d_, offset=True); bo0 = bootstrap(R, d_, offset=False)
        print('\n--- %s  nights %d ---' % (pname, m.sum()))
        print('%-18s %8s %8s %7s %9s %9s %7s %7s %8s | P(KILL250) P(PAUSE250) eps/1000n (random phase) | aligned P(KILL250) P(PAUSE250)' % ('', 'g%/n', 'mean%', 'sd%', 'worst%', 'maxDD%', 'P-ngts', 'P-eps', 'x-mult'))
        for j, (wn, w) in enumerate(W):
            x = st_[j]
            print('%-18s %+8.4f %+8.4f %7.3f %+9.2f %+9.1f %7d %7d %8.2f |  %7.4f   %7.4f   %7.2f |  %7.4f  %7.4f' % (
                wn, x['g'], x['mean'], x['sd'], x['worst'], x['maxdd'], x['pause_nights'], x['pause_eps'], x['mult'],
                (bo['minE_h'][:, j] <= 0.5).mean(), bo['pause_h'][:, j].mean(), bo['eps'][:, j].mean(),
                (bo0['minE_h'][:, j] <= 0.5).mean(), bo0['pause_h'][:, j].mean()))
        dif = bo0['g'][:, 1] - bo0['g'][:, 0]
        print('   split minus NVDL-only growth: %+9.4f  [%+.4f, %+.4f]' % (st_[1]['g'] - st_[0]['g'], pct(dif, 5), pct(dif, 95)))
        out[pname] = dict(stats={W[j][0]: st_[j] for j in range(3)},
                          kill250={W[j][0]: float((bo['minE_h'][:, j] <= 0.5).mean()) for j in range(3)},
                          pause250={W[j][0]: float(bo['pause_h'][:, j].mean()) for j in range(3)},
                          eps1000={W[j][0]: float(bo['eps'][:, j].mean()) for j in range(3)})
    return out
res['sens_blackout_trend'] = run_blackout('SENSITIVITY E (live rule s3(d)): NVDA part in cash on the 47 NVDA earnings nights; trend-rule size', s_trend)
res['sens_blackout_full'] = run_blackout('SENSITIVITY E2: NVDA part in cash on NVDA earnings nights; size 0.98 always', s_full)

json.dump(res, open(OUT + 'l5_results.json', 'w'), indent=1)
# nightly series for anyone re-deriving
with open(OUT + 'l5_nights.csv', 'w') as f:
    f.write('date,next,qqq_close,qqq_line,up,size,earn,legN_2xNVDA,legT_TQQQ,R_nvdl,R_split,R_tqqq\n')
    for i, r in enumerate(rows):
        f.write('%s,%s,%.4f,%.4f,%d,%.2f,%d,%.6f,%.6f,%.6f,%.6f,%.6f\n' % (r['d'], r['n'], r['qc'], r['line'], r['up'], s_trend[i], isE[i], legN[i], legT[i],
                account_returns(legN[i], legT[i], s_trend[i], 1.0), account_returns(legN[i], legT[i], s_trend[i], 0.5), account_returns(legN[i], legT[i], s_trend[i], 0.0)))
print('\nwrote', OUT + 'l5_results.json', OUT + 'l5_nights.csv')
