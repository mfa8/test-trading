#!/usr/bin/env python3
"""Lab cycle 2026-11-14 (single-threaded, light). Research only; places no orders.
1. Extend the overnight series with the five nights 11/6->11/9 .. 11/12->11/13 (broker day bars, adjustment none).
2. RULES_v3 §3(f): trailing-120 NVDL overnight mean, NVDA earnings nights excluded (the Mon 11/16 check).
3. L12 preview: reduced size (0.25, 0.5) through NVDA earnings nights, 2x-NVDA proxy, against the pre-registered bar.
"""
import csv, math, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(HERE, '..', '..', 'edge_decay')
src = os.path.join(ED, 'overnight_thru_20261106.csv'); dst = os.path.join(ED, 'overnight_thru_20261113.csv')
rows = list(csv.DictReader(open(src))); cols = list(rows[0].keys())
bars = {  # date: (NVDL open, NVDL close, NVDA open, NVDA close), day bars read 2026-11-14
 '2026-11-06': (24.81, 23.71, 191.10, 186.64), '2026-11-09': (20.24, 21.64, 173.065, 178.67),
 '2026-11-10': (20.51, 19.28, 173.97, 168.89), '2026-11-11': (20.16, 20.40, 172.80, 173.73),
 '2026-11-12': (15.035, 18.57, 151.005, 166.19), '2026-11-13': (19.42, 17.83, 169.905, 162.85)}
ds = sorted(bars)
assert rows[-1]['next'] == '2026-11-06'
for a, b in zip(ds[:-1], ds[1:]):
    nl = bars[b][0] / bars[a][1] - 1; na = bars[b][2] / bars[a][3] - 1
    gap = 3 if a == '2026-11-06' else 1
    rows.append({'date': a, 'next': b, 'gapdays': str(gap), 'earn': '0', 'preann': '', 'nvda_on': '%.6f' % na,
                 'nvdl_on': '%.6f' % nl, 'nvdl_clean': '%.6f' % nl, 'proxy2x': '%.6f' % (2 * na - 0.0004)})
with open(dst, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

def t120(rs):
    x = [float(r['nvdl_clean']) * 100 for r in rs if r['earn'] == '0' and r['nvdl_clean'] != ''][-120:]
    m = sum(x) / len(x); sd = (sum((v - m) ** 2 for v in x) / (len(x) - 1)) ** 0.5
    return round(m, 3), round(sd, 3), round(m / (sd / math.sqrt(len(x))), 2), len(x)
old = t120(rows[:-5]); new = t120(rows)
first = [r['date'] for r in rows if r['earn'] == '0' and r['nvdl_clean'] != ''][-120]
out = {'f3_prev_check_reproduced': old, 'f3_now': new, 'f3_window_first_night': first,
       'five_nights_pct': [round(float(r['nvdl_clean']) * 100, 3) for r in rows[-5:]]}
# L12 preview
E = [(r['date'], float(r['proxy2x'])) for r in rows if r['earn'] == '1' and r['proxy2x'] != '']
out['l12_n'] = len(E); out['l12_span'] = [E[0][0], E[-1][0]]
rr = [x for _, x in E]
out['l12_raw'] = {'mean_pct': round(100 * sum(rr) / len(rr), 3), 'worst_pct': round(100 * min(rr), 2), 'best_pct': round(100 * max(rr), 2),
                  'wins': sum(1 for x in rr if x > 0)}
for s in (0.25, 0.5):
    g = [math.log(1 + s * x) for x in rr]; h = len(g) // 2
    g3 = sorted(g)[:-3]
    out['l12_s%s' % s] = {'mean_log_bp': round(1e4 * sum(g) / len(g), 1), 'first_half_bp': round(1e4 * sum(g[:h]) / h, 1),
                          'second_half_bp': round(1e4 * sum(g[h:]) / (len(g) - h), 1), 'ex_best3_bp': round(1e4 * sum(g3) / len(g3), 1),
                          'worst_night_cost_pct_of_E': round(-100 * s * min(rr), 2),
                          't': round((sum(g) / len(g)) / ((sum((v - sum(g) / len(g)) ** 2 for v in g) / (len(g) - 1)) ** 0.5 / math.sqrt(len(g))), 2)}
json.dump(out, open(os.path.join(HERE, 'cycle_result.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
