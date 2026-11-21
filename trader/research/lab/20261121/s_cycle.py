#!/usr/bin/env python3
"""Lab cycle 2026-11-21 (single-threaded, measurement only). Research only; places no orders.
1. Extend the overnight series with the five nights 11/13->11/16 .. 11/19->11/20 (broker day bars, adjustment none, read 2026-11-21).
   The night 11/17->11/18 is the NVDA earnings night (earn=1), excluded from the §3(f) mean.
2. RULES_v3 §3(f): trailing-120 NVDL overnight mean, NVDA earnings nights excluded (the Mon 11/23 check).
"""
import csv, math, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(HERE, '..', '..', 'edge_decay')
src = os.path.join(ED, 'overnight_thru_20261113.csv'); dst = os.path.join(ED, 'overnight_thru_20261120.csv')
rows = list(csv.DictReader(open(src))); cols = list(rows[0].keys())
bars = {  # date: (NVDL open, NVDL close, NVDA open, NVDA close)
 '2026-11-13': (19.42, 17.83, 169.905, 162.85), '2026-11-16': (16.97, 16.35, 159.015, 156.14),
 '2026-11-17': (16.515, 16.22, 156.895, 155.46), '2026-11-18': (16.965, 15.24, 159.19, 150.96),
 '2026-11-19': (15.645, 14.25, 152.915, 145.98), '2026-11-20': (13.74, 10.33, 143.52, 125.53)}
EARN = {'2026-11-17'}
ds = sorted(bars)
assert rows[-1]['next'] == '2026-11-13' and rows[-1]['date'] == '2026-11-12'
n0 = len(rows)
for a, b in zip(ds[:-1], ds[1:]):
    nl = bars[b][0] / bars[a][1] - 1; na = bars[b][2] / bars[a][3] - 1
    gap = 3 if a == '2026-11-13' else 1
    rows.append({'date': a, 'next': b, 'gapdays': str(gap), 'earn': '1' if a in EARN else '0', 'preann': '', 'nvda_on': '%.6f' % na,
                 'nvdl_on': '%.6f' % nl, 'nvdl_clean': '%.6f' % nl, 'proxy2x': '%.6f' % (2 * na - 0.0004)})
with open(dst, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

def t120(rs):
    x = [float(r['nvdl_clean']) * 100 for r in rs if r['earn'] == '0' and r['nvdl_clean'] != ''][-120:]
    m = sum(x) / len(x); sd = (sum((v - m) ** 2 for v in x) / (len(x) - 1)) ** 0.5
    return round(m, 3), round(sd, 3), round(m / (sd / math.sqrt(len(x))), 2), len(x)
old = t120(rows[:n0]); new = t120(rows)
elig = [r for r in rows if r['earn'] == '0' and r['nvdl_clean'] != '']
win = elig[-120:]
pos = sum(1 for r in win if float(r['nvdl_clean']) > 0)
worst5 = sorted(((round(float(r['nvdl_clean']) * 100, 2), r['date']) for r in win))[:5]
ex5 = [float(r['nvdl_clean']) * 100 for r in win]; ex5 = sorted(ex5)[5:]
out = {'f3_prev_check_reproduced': old, 'f3_now': new, 'f3_window_first_night': win[0]['date'], 'f3_window_last_night': win[-1]['date'],
       'five_nights_pct': [(r['date'], r['earn'], round(float(r['nvdl_clean']) * 100, 3), round(float(r['nvda_on']) * 100, 3)) for r in rows[n0:]],
       'window_positive_nights': pos, 'window_worst5': worst5, 'window_mean_ex_worst5_pct': round(sum(ex5) / len(ex5), 3),
       'nvda_week': {'overnight_sum_pct': round(100 * sum(float(r['nvda_on']) for r in rows[n0:]), 2),
                     'intraday_pct': [(d, round(100 * (bars[d][3] / bars[d][2] - 1), 2)) for d in ds[1:]]}}
json.dump(out, open(os.path.join(HERE, 'cycle_result.json'), 'w'), indent=1)
print(json.dumps(out))
