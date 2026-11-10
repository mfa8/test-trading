"""Hand check of the L15 simulation (analyst A).

Part 1: a 30-night series with size 1.0 / pause size 0.5 whose every pause start and
        end was worked out by hand (derivation printed below); the expected flags and
        equity values are hard-coded here and compared with sim.simulate().
Part 2: a 24-night series with the real sizes (0.98 / 0.25) to check min(b, p).
Part 3: structural checks of the main NVDA run and an independent numpy recomputation
        of P0 and of the trend state.
Writes results_handtest.txt and the combined results.txt.
"""
import sys
import os
import math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np      # noqa: E402
import loader           # noqa: E402
import sim              # noqa: E402

OUT = []
FAIL = []


def P(*a):
    line = ' '.join(str(x) for x in a)
    OUT.append(line)
    print(line)


def check(label, ok):
    P('   [%s] %s' % ('ok' if ok else 'FAIL', label))
    if not ok:
        FAIL.append(label)


def rng_(a, b):
    return list(range(a, b + 1))


def close(a, b, tol=1e-12):
    return abs(a - b) <= tol * max(1.0, abs(b))


# ------------------------------------------------------------------ part 1
P('')
P('=' * 100)
P('11. HAND CHECK ON A TINY SERIES')
P('=' * 100)
P('Part 1: 30 nights, base size 1.0 on every night, pause size 0.5, window 20, threshold 0.80, minimum 5.')
N = 30
u = [0.0] * N
u[2] = -0.30
u[3] = +0.10
u[4] = +0.20
u[6] = -0.05
u[12] = -0.10
u[16] = +0.10
u[23] = -0.25
u[24] = +0.40
b = [1.0] * N
P('  unit returns u_t (zero unless listed): ' + ', '.join('u%d=%+.2f' % (t, v) for t, v in enumerate(u) if v != 0))
P('''  Derivation by hand (E_t = equity before night t; "trig" = 0.80 x max of the last 20 E):
   E0=E1=E2=1. Night 2 at size 1: -30%  -> E3 = 0.70 in every variant.
   t=3: trig 0.80, 0.70 <= 0.80 -> C true.  t=4: E4 = 0.70*1.05 = 0.735 (paused, half size) -> C true.
   t=5: E5 = 0.735*1.10 = 0.8085 > 0.80 -> C false.  t=6: C false.
   P1/P2 (still inside the 5 nights at t=6): E7 = 0.8085*0.975 = 0.7882875 -> C true at t=7 and onward.
   P3 (not paused at t=6, full size): E7 = 0.8085*0.95 = 0.768075 -> C true at t=7 and onward.
   The three 1.0 values (E0..E2) stay inside the 20-window up to t=21 (window E2..E21), so trig = 0.80 up to t=21.
   At t=22 the window is E3..E22, max 0.8085 (E5,E6), trig 0.6468 -> C false for every variant.
   P1 : paused 3..7 (minimum), stays paused 8..21 because C holds, normal at 22.  Episode (3, 19 nights).
        E13 = 0.7882875*0.95 = 0.748873125; E17 = *1.05 = 0.78631678125 (<= 0.80, still paused);
        E24 = *0.75 = 0.5897375859375 <= 0.6468 -> new pause 24..28 (C false from 25 on) -> episode (24, 5).
        E25 = *1.20 = 0.707685103125 = final equity.
   P2 reading A: paused 3..7; re-armed at t=5 (C false inside the pause); t=8 C true and armed -> second pause 8..12;
        normal from 13 (disarmed, C true 13..16); E13 = 0.748873125; night 16 at full size: E17 = *1.10 = 0.8237604375 > 0.80
        -> C false at 17 -> re-armed; E24 = *0.75 = 0.617820328125; window max now 0.8237604375, trig 0.65900835 -> pause 24..28.
        E25 = *1.20 = 0.74138439375 = final.  Starts 3, 8, 24.
   P2 reading B: paused 3..7; C false at t=5,6 is ignored (inside the pause); t=8 C true -> not re-armed -> normal 8..23.
        E13 = 0.7882875*0.90 = 0.70945875; E17 = *1.10 = 0.780404625 (<= 0.80, C true, still disarmed);
        t=22 C false -> re-armed; E24 = *0.75 = 0.58530346875 <= 0.6468 -> pause 24..28; E25 = *1.20 = 0.7023641625 = final.
        Starts 3, 24.
   P3 : paused exactly where C holds: 3,4 | 7..21 | 24.  E13 = 0.768075*0.95 = 0.72967125; E17 = *1.05 = 0.7661548125;
        E24 = *0.75 = 0.574616109375; E25 = *1.20 = 0.68953933125 = final (0.6895 > 0.6468 -> C false at 25).
   P0 : never paused. Final = 0.70*1.10*1.20*0.95*0.90*1.10*0.75*1.40 = 0.9124731.
   P2x10 (reading A): pause 3..12; re-armed at t=5; t=13: E13 = 0.748873125 <= 0.80, armed -> second pause 13..22;
        E17 = 0.78631678125; re-armed at t=22 (C false); E24 = 0.5897375859375 -> third pause from 24 (cut by the end of the series, 6 nights).''')

EXPECT = {
    'P0': dict(paused=[], episodes=[], final=0.9124731),
    'P1': dict(paused=rng_(3, 21) + rng_(24, 28), episodes=[(3, 19), (24, 5)], final=0.707685103125),
    'P2A': dict(paused=rng_(3, 12) + rng_(24, 28), episodes=[(3, 5), (8, 5), (24, 5)], final=0.74138439375),
    'P2B': dict(paused=rng_(3, 7) + rng_(24, 28), episodes=[(3, 5), (24, 5)], final=0.7023641625),
    'P3': dict(paused=[3, 4] + rng_(7, 21) + [24], episodes=[(3, 2), (7, 15), (24, 1)], final=0.68953933125),
    'P2x10': dict(paused=rng_(3, 22) + rng_(24, 29), episodes=[(3, 10), (13, 10), (24, 6)], final=0.707685103125),
}
EXPECT_E = {   # selected hand-computed equity values E_t
    'P1': {3: 0.70, 4: 0.735, 5: 0.8085, 7: 0.7882875, 13: 0.748873125, 17: 0.78631678125, 24: 0.5897375859375, 25: 0.707685103125},
    'P2A': {7: 0.7882875, 13: 0.748873125, 17: 0.8237604375, 24: 0.617820328125, 25: 0.74138439375},
    'P2B': {7: 0.7882875, 13: 0.70945875, 17: 0.780404625, 24: 0.58530346875, 25: 0.7023641625},
    'P3': {7: 0.768075, 13: 0.72967125, 17: 0.7661548125, 24: 0.574616109375, 25: 0.68953933125},
    'P0': {3: 0.70, 4: 0.77, 5: 0.924, 7: 0.8778, 13: 0.79002, 17: 0.869022, 24: 0.6517665, 25: 0.9124731},
}
RUNS = {
    'P0': sim.simulate(u, b, 'P0', p=0.5),
    'P1': sim.simulate(u, b, 'P1', p=0.5),
    'P2A': sim.simulate(u, b, 'P2', p=0.5, rearm_during_pause=True),
    'P2B': sim.simulate(u, b, 'P2', p=0.5, rearm_during_pause=False),
    'P3': sim.simulate(u, b, 'P3', p=0.5),
    'P2x10': sim.simulate(u, b, 'P2', p=0.5, n_len=10, rearm_during_pause=True),
}
P('')
P('  Trace from sim.simulate (E_t before the night; C = trigger condition; size used):')
for k in ['P1', 'P2A', 'P2B', 'P3']:
    r = RUNS[k]
    P('  %s' % k)
    P('    t   : ' + ' '.join('%5d' % t for t in range(N)))
    P('    E_t : ' + ' '.join('%5.3f' % r['E'][t] for t in range(N)))
    P('    C   : ' + ' '.join('%5s' % ('C' if r['cond'][t] else '.') for t in range(N)))
    P('    size: ' + ' '.join('%5.2f' % r['s'][t] for t in range(N)))
P('')
P('  Comparison with the hand-derived expectations:')
for k in ['P0', 'P1', 'P2A', 'P2B', 'P3', 'P2x10']:
    r = RUNS[k]
    got = [t for t in range(N) if r['paused'][t]]
    check('%-5s paused nights %s' % (k, got), got == EXPECT[k]['paused'])
    check('%-5s episodes (start, length) %s' % (k, r['episodes']), r['episodes'] == EXPECT[k]['episodes'])
    check('%-5s final equity %.12f (hand %.12f)' % (k, r['E'][N], EXPECT[k]['final']), close(r['E'][N], EXPECT[k]['final']))
    if k in EXPECT_E:
        ok = all(close(r['E'][t], v) for t, v in EXPECT_E[k].items())
        check('%-5s equity at t=%s matches hand values' % (k, sorted(EXPECT_E[k])), ok)
    szok = all(close(r['s'][t], 0.5 if r['paused'][t] else 1.0) for t in range(N))
    check('%-5s size is 0.5 on paused nights and 1.0 otherwise' % k, szok)

# ------------------------------------------------------------------ part 2
P('')
P('Part 2: 24 nights with the real sizes. b = 0.98, 0.98, then 0.25 on even nights and 0.98 on odd nights; u1 = -0.50, all other u = 0.')
P('  By hand: night 1 at 0.98 loses 49% -> E2 = 0.51 and equity never moves again. C holds from t=2 while E1 = 1 is in the window (t <= 20);')
P('  at t=21 the window is E2..E21 = 0.51 throughout, trig 0.408 -> C false. So P1 and P3 pause 2..20 (19 nights), P2 pauses 2..6.')
N2 = 24
u2 = [0.0] * N2
u2[1] = -0.5
b2 = [0.98, 0.98] + [0.25 if t % 2 == 0 else 0.98 for t in range(2, N2)]
for p in (0.10, 0.25, 0.50):
    for v, kw, exp in [('P1', {}, rng_(2, 20)), ('P2', {}, rng_(2, 6)), ('P2', dict(rearm_during_pause=False), rng_(2, 6)),
                       ('P3', {}, rng_(2, 20))]:
        r = sim.simulate(u2, b2, v, p=p, **kw)
        got = [t for t in range(N2) if r['paused'][t]]
        okp = got == exp
        oks = all(close(r['s'][t], min(b2[t], p) if r['paused'][t] else b2[t]) for t in range(N2))
        oke = close(r['E'][N2], 0.51)
        check('p=%.2f %s%s paused %d..%d, sizes = min(b,p) when paused else b, final E = 0.51'
              % (p, v, 'B' if kw else '', exp[0], exp[-1]), okp and oks and oke)
r = sim.simulate(u2, b2, 'P1', p=0.50)
P('    sizes P1 p=0.50, t=0..23: ' + ' '.join('%.2f' % x for x in r['s']))
r = sim.simulate(u2, b2, 'P2', p=0.10)
P('    sizes P2 p=0.10, t=0..23: ' + ' '.join('%.2f' % x for x in r['s']))

# ------------------------------------------------------------------ part 3
P('')
P('Part 3: structural checks on the real runs (all 11 names, trend on and off, p = 0.10 / 0.25 / 0.50)')
bars, lstats, log = loader.load_all([])
q = bars['QQQ']
qc = np.array([c for _, _, c in q])
# independent trend state with numpy: 200-session SMA including today
sma200 = np.convolve(qc, np.ones(200) / 200.0, mode='valid')      # index i-199 -> mean of closes i-199..i
up_np = {q[i][0]: bool(qc[i] >= sma200[i - 199]) for i in range(199, len(q))}
csum = np.concatenate([[0.0], np.cumsum(qc)])
up_py = {q[i][0]: bool(qc[i] >= (csum[i] - csum[i - 199]) / 199.0) for i in range(199, len(q))}
ndiff = sum(1 for d in up_np if up_np[d] != up_py[d])
check('trend state: "close >= mean of previous 199 closes" equals "close >= 200-session SMA incl. today" on all %d sessions (differences: %d)'
      % (len(up_np), ndiff), ndiff == 0)

viol = dict(p1_len=0, p1_start=0, p1_end=0, p1_ext=0, p2_len=0, p2_start=0, p2_rearmA=0, p2_rearmB=0, p3=0, size=0, eq=0, p0=0)
nruns = 0
for name in loader.NAMES:
    qidx = {d: i for i, (d, _, _) in enumerate(q)}
    x = [row for row in bars[name] if row[0] in qidx]
    d_in = []
    rr = []
    upf = []
    for j in range(len(x) - 1):
        if x[j][0] not in up_py:
            continue
        d_in.append(x[j][0])
        rr.append(x[j + 1][1] / x[j][2] - 1.0)
        upf.append(up_py[x[j][0]])
    uu = [2.0 * v - 0.0009 for v in rr]
    n = len(uu)
    for trend in ('on', 'off'):
        bb = [0.98 if (f or trend == 'off') else 0.25 for f in upf]
        # P0 with numpy
        r0 = sim.simulate(uu, bb, 'P0')
        lr_np = np.log1p(np.array(bb) * np.array(uu))
        if abs(lr_np.sum() - sum(r0['lr'])) > 1e-9:
            viol['p0'] += 1
        for p in (0.10, 0.25, 0.50):
            nruns += 1
            r1 = sim.simulate(uu, bb, 'P1', p=p)
            r2a = sim.simulate(uu, bb, 'P2', p=p, rearm_during_pause=True)
            r2b = sim.simulate(uu, bb, 'P2', p=p, rearm_during_pause=False)
            r3 = sim.simulate(uu, bb, 'P3', p=p)
            for r in (r1, r2a, r2b, r3):
                for t in range(n):
                    want = min(bb[t], p) if r['paused'][t] else bb[t]
                    if r['s'][t] != want:
                        viol['size'] += 1
                if abs(math.log(r['E'][n]) - sum(r['lr'])) > 1e-8:
                    viol['eq'] += 1
                # independent recomputation of C from the stored equity path (numpy rolling max over 20 values)
                Ea = np.array(r['E'][:n])
                pad = np.concatenate([np.full(19, -np.inf), Ea])
                Hroll = np.lib.stride_tricks.sliding_window_view(pad, 20).max(axis=1)
                c_np = Ea <= 0.80 * Hroll
                viol['cond'] = viol.get('cond', 0) + int((c_np != np.array(r['cond'])).sum())
                # equity path rebuilt from sizes and unit returns
                E_np = np.concatenate([[1.0], np.cumprod(1.0 + np.array(r['s']) * np.array(uu))])
                if np.max(np.abs(E_np / np.array(r['E']) - 1.0)) > 1e-9:
                    viol['eq'] += 1
            # P1: each episode >= 5 nights (unless cut by the sample end), starts on C with the previous night unpaused,
            #     the night after it has C false, and every night beyond the 5th has C true
            for st, L in r1['episodes']:
                if L < 5 and st + L < n:
                    viol['p1_len'] += 1
                if not r1['cond'][st] or (st > 0 and r1['paused'][st - 1]):
                    viol['p1_start'] += 1
                if st + L < n and (r1['cond'][st + L] or r1['paused'][st + L]):
                    viol['p1_end'] += 1
                if any(not r1['cond'][t] for t in range(st + 5, st + L)):
                    viol['p1_ext'] += 1
            # every unpaused P1 night has C false
            if any(r1['cond'][t] and not r1['paused'][t] for t in range(n)):
                viol['p1_start'] += 1
            for r, key, lo_off in ((r2a, 'p2_rearmA', 1), (r2b, 'p2_rearmB', 5)):
                eps = r['episodes']
                for i, (st, L) in enumerate(eps):
                    if L != 5 and st + L < n:
                        viol['p2_len'] += 1
                    if not r['cond'][st]:
                        viol['p2_start'] += 1
                    if i > 0:
                        pst = eps[i - 1][0]
                        # some night between the previous start and this start must have C false
                        if not any(not r['cond'][t] for t in range(pst + lo_off, st)):
                            viol[key] += 1
                paused = [False] * n
                for st, L in eps:
                    for t in range(st, min(n, st + L)):
                        paused[t] = True
                if paused != r['paused']:
                    viol['p2_len'] += 1
            if r3['paused'] != r3['cond']:
                viol['p3'] += 1
P('   %d (name, trend, p) cells checked' % nruns)
check('sizes: s = min(b, p) on paused nights and b otherwise, every run (violations %d)' % viol['size'], viol['size'] == 0)
check('equity: ln E_final = sum of ln(1+R) and E path = cumprod(1 + s*u) rebuilt with numpy, every run (violations %d)' % viol['eq'], viol['eq'] == 0)
check('trigger condition C recomputed from the equity path with a numpy rolling 20-value max: night-level mismatches %d' % viol.get('cond', -1),
      viol.get('cond', -1) == 0)
check('P0 total log return equals an independent numpy computation (violations %d)' % viol['p0'], viol['p0'] == 0)
check('P1 episodes: length >= 5 unless cut by the end of the sample (violations %d)' % viol['p1_len'], viol['p1_len'] == 0)
check('P1 episodes: start on a night with C true after an unpaused night; no unpaused night has C true (violations %d)' % viol['p1_start'], viol['p1_start'] == 0)
check('P1 episodes: the night after an episode has C false and is unpaused (violations %d)' % viol['p1_end'], viol['p1_end'] == 0)
check('P1 episodes: every night beyond the 5th has C true (violations %d)' % viol['p1_ext'], viol['p1_ext'] == 0)
check('P2/P2B episodes: exactly 5 nights, start on C true, paused flags = union of episodes (violations %d / %d)' % (viol['p2_len'], viol['p2_start']),
      viol['p2_len'] == 0 and viol['p2_start'] == 0)
check('P2 reading A: between two starts there is a night with C false after the first start (violations %d)' % viol['p2_rearmA'], viol['p2_rearmA'] == 0)
check('P2 reading B: between two starts there is a night with C false after the first pause ended (violations %d)' % viol['p2_rearmB'], viol['p2_rearmB'] == 0)
check('P3: paused flags identical to C (violations %d)' % viol['p3'], viol['p3'] == 0)

P('')
if FAIL:
    P('HAND CHECK RESULT: %d FAILURE(S): %s' % (len(FAIL), FAIL))
else:
    P('HAND CHECK RESULT: all checks passed.')

with open(os.path.join(HERE, 'results_handtest.txt'), 'w') as fh:
    fh.write('\n'.join(OUT) + '\n')
main_path = os.path.join(HERE, 'results_main.txt')
if os.path.exists(main_path):
    with open(main_path) as fh:
        main_txt = fh.read()
    with open(os.path.join(HERE, 'results.txt'), 'w') as fh:
        fh.write(main_txt + '\n'.join(OUT) + '\n')
sys.exit(1 if FAIL else 0)
