"""Analyst B: hand-checkable traces and side checks for L15. Writes checks.txt.
Run: python3 -I b_checks.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np      # noqa: E402
import b_loader as L    # noqa: E402
import b_sim as S       # noqa: E402

lines = []


def P(*a):
    s = ' '.join(str(x) for x in a)
    lines.append(s)
    print(s)


data, rep = L.load_all()
q = data['QQQ']
qd, qc = q['dates'], np.array(q['close'])
up = {}
mean199 = {}
for i in range(199, len(qd)):
    m = float(np.mean(qc[i - 199:i]))          # brute force, not the cumsum used in b_run
    mean199[qd[i]] = m
    up[qd[i]] = qc[i] >= m

P('QQQ close vs mean of the previous 199 closes, last 8 sessions:')
for i in range(len(qd) - 8, len(qd)):
    P('  %s close %.2f mean199 %.2f ratio %.4f %s' % (qd[i], qc[i], mean199[qd[i]], qc[i] / mean199[qd[i]],
                                                     'UP' if up[qd[i]] else 'DOWN'))
cc = qc[1:] / qc[:-1] - 1
o = np.argsort(-np.abs(cc))[:5]
P('QQQ largest close-to-close moves:', [(qd[i + 1], round(100 * float(cc[i]), 1)) for i in o])
P('QQQ first closes:', [(qd[i], qc[i]) for i in range(3)], '... 2000-03-17..22:',
  [(d_, c_) for d_, c_ in zip(qd, qc) if '2000-03-16' <= d_ <= '2000-03-22'])


def nights(sym, start=None):
    x = data[sym]
    dts = x['dates']
    op, cl = np.array(x['open']), np.array(x['close'])
    nd, r, b = [], [], []
    for i in range(len(dts) - 1):
        d0 = dts[i]
        if d0 not in up or (start and d0 < start):
            continue
        assert dts[i] in up
        nd.append(d0)
        r.append(op[i + 1] / cl[i] - 1)
        b.append(0.98 if up[d0] else 0.25)
    return np.array(nd), np.array(r), np.array(b)


def trace(sym, d_from, d_to, trend='on', p=0.25):
    nd, r, b = nights(sym)
    if trend == 'off':
        b = np.full(len(r), 0.98)
    r1 = S.run_loop(r, b, 'P1', p)
    r2 = S.run_loop(r, b, 'P2', p)
    r0 = S.run_loop(r, b, 'P0', p)
    P('\nTRACE %s trend %s p=%.2f  %s..%s' % (sym, trend, p, d_from, d_to))
    P('  %-10s %7s %4s | %10s %10s %6s %2s %2s %5s | %10s %6s %2s %2s %5s | %8s' % (
        'date', 'r %', 'b', 'P1 E_in', 'P1 H20', 'E/H', 'C', 'pz', 's', 'P2 E_in', 'E/H', 'C', 'pz', 's', 'P0 lnR%'))
    for t in range(len(nd)):
        if d_from <= nd[t] <= d_to:
            H1 = max(r1['E_in'][max(0, t - 19):t + 1])
            H2 = max(r2['E_in'][max(0, t - 19):t + 1])
            P('  %-10s %+7.2f %4.2f | %10.3f %10.3f %6.3f %2d %2d %5.2f | %10.3f %6.3f %2d %2d %5.2f | %+8.2f' % (
                nd[t], 100 * r[t], b[t], r1['E_in'][t], H1, r1['E_in'][t] / H1, r1['C'][t], r1['paused'][t], r1['s'][t],
                r2['E_in'][t], r2['E_in'][t] / H2, r2['C'][t], r2['paused'][t], r2['s'][t], 100 * r0['lnR'][t]))


trace('NVDA', '2019-05-01', '2019-06-12')
trace('NVDA', '2025-01-22', '2025-02-28')
trace('NVDA', '2020-02-20', '2020-04-03')

# where the worst drawdowns sit
nd, r, b = nights('NVDA')
for var in ('P0', 'P1', 'P2'):
    rr = S.run_loop(r, b, var, 0.25)
    for lab, m in (('H1', nd <= '2014-12-31'), ('H2', nd > '2014-12-31')):
        ln = rr['lnR'][m]
        dts = nd[m]
        path = np.concatenate(([0.0], np.cumsum(ln)))
        peak = np.maximum.accumulate(path)
        j = int(np.argmin(path - peak))
        i = int(np.argmax(path[:j + 1]))
        P('NVDA trend on %s %s: worst drawdown %.2f%% from before night %s to after night %s' % (
            var, lab, 100 * (1 - np.exp(path[j] - path[i])), dts[min(i, len(dts) - 1)], dts[j - 1]))

# ORCL first half: why P2 - P1 is exactly zero
nd, r, b = nights('ORCL')
r1 = S.run_loop(r, b, 'P1', 0.25)
r2 = S.run_loop(r, b, 'P2', 0.25)
m = nd <= '2014-12-31'
P('\nORCL H1: nights with different size P1 vs P2: %d ; P1 episodes starting in H1: %s' % (
    int((r1['s'][m] != r2['s'][m]).sum()),
    [(nd[t0], ln_, int((b[t0:t0 + ln_] > 0.5).sum())) for (t0, ln_) in S.episodes_from(r1) if m[t0]]))

# AMZN zero-volume bar
with open(os.path.join(L.RAW, 'x4.json')) as fh:
    j = json.load(fh)
for res in j.get('data', j)['results']:
    if res['symbol'] == 'AMZN':
        P('\nAMZN raw bars around 2008-10-29:',
          [(x['begins_at'][:10], x['open_price'], x['close_price'], x['volume']) for x in res['bars']
           if '2008-10-27' <= x['begins_at'][:10] <= '2008-10-31'])

# sensitivity: neutralise the possibly bad AMD print of 2002-10-16 (+39.5% overnight)
nd, r, b = nights('AMD')
for lab, rr_ in (('as is', r), ('2002-10-16 night set to 0', np.where(nd == '2002-10-16', 0.0, r))):
    a1 = S.run_loop(rr_, b, 'P1', 0.25)
    a2 = S.run_loop(rr_, b, 'P2', 0.25)
    P('AMD trend on p=0.25 %-28s P2-P1 g whole span %+.4f' % (lab, 100 * (a2['lnR'] - a1['lnR']).mean()))

# brute-force re-implementation of P1 and P2 with a completely different structure
# (recursive description: decide each night from the full history of C and paused flags)
def brute(r, b, variant, p=0.25, nfix=5):
    n = len(r)
    E = [1.0]
    C, pz, st = [], [], []
    for t in range(n):
        H = max(E[max(0, t - 19):t + 1])
        c = E[t] <= 0.8 * H
        C.append(c)
        if variant == 'P1':
            # paused iff (a) a start within the last nfix-1 nights, or (b) previous night paused and c,
            # or (c) c and previous night not paused (new start)
            recent = any(s_ > t - nfix for s_ in st)
            prev = pz[t - 1] if t else False
            if recent:
                z = True
            elif prev and c:
                z = True
            elif (not prev) and c:
                z = True
                st.append(t)
            else:
                z = False
        else:   # P2, primary reading
            recent = any(s_ > t - nfix for s_ in st)
            if recent:
                z = True
            else:
                last = st[-1] if st else None
                if last is None:
                    armed = True
                else:
                    # armed iff some night after the pause (>= last+nfix) and before t had C false
                    armed = any(not C[k] for k in range(last + nfix, t + 1))
                z = bool(armed and c)
                if z:
                    st.append(t)
        pz.append(z)
        s = min(b[t], p) if z else b[t]
        E.append(E[t] * (1 + s * (2 * r[t] - 0.0009)))
    return np.array(pz), st, np.array(E)


tot = 0
for sym in ['NVDA', 'AMD', 'INTC', 'MU', 'AAPL', 'MSFT', 'AMZN', 'QCOM', 'TXN', 'AMAT', 'ORCL']:
    nd, r, b = nights(sym)
    for trend in ('on', 'off'):
        bb = b if trend == 'on' else np.full(len(r), 0.98)
        for var in ('P1', 'P2'):
            for p in (0.10, 0.25, 0.50):
                a = S.run_loop(r, bb, var, p)
                z, st, E = brute(r, bb, var, p)
                tot += int((z != a['paused']).sum()) + (0 if st == list(a['starts']) else 1)
                assert abs(E[-1] / a['E_out'][-1] - 1) < 1e-9
P('\nbrute-force re-implementation of P1 and P2 (different code structure), 11 names x 2 trend modes x 3 pause sizes:',
  'total flag/start mismatches =', tot)

with open(os.path.join(HERE, 'checks.txt'), 'w') as fh:
    fh.write('\n'.join(lines) + '\n')
