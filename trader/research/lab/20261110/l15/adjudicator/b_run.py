"""Analyst B main run for LAB item L15 (PAUSE exit condition). Read-only on the data.
Writes results.txt and nvda_table.json next to this script.
Run:  python3 -I b_run.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np          # noqa: E402
import b_loader as L        # noqa: E402
import b_sim as S           # noqa: E402

SEED = 20261110
NDRAW = 2000
NAMES = ['NVDA', 'AMD', 'INTC', 'MU', 'AAPL', 'MSFT', 'AMZN', 'QCOM', 'TXN', 'AMAT', 'ORCL']
PSIZES = [0.10, 0.25, 0.50]
H1_END = '2014-12-31'
PERIODS = ['2000-10-30..2014-12-31', '2015-01-02..2026-11-06', 'whole span 2000-10-30..2026-11-06']
PKEY = ['H1', 'H2', 'ALL']
HORIZ = [5, 10, 20, 40]

out_lines = []


def P(*a):
    line = ' '.join(str(x) for x in a)
    out_lines.append(line)
    print(line)


# ------------------------------------------------------------------ data
data, rep = L.load_all()
P('=' * 100)
P('L15 PAUSE exit condition - analyst B - independent loader and simulation')
P('bootstrap seed', SEED, 'draws', NDRAW, '| cost 9bp per unit size | threshold 0.80 | window 20 | min pause 5')
P('=' * 100)
P('\n## 0. READINGS TAKEN (where the specification left a choice)')
for ln_ in [
    'R1 P2 re-arm: the rule is disarmed when a pause starts and the re-arm test (C false) is made only on nights after',
    '   the 5 paused nights ("post", primary). Other reading ("any"): a night with C false during the pause also re-arms.',
    '   Both are run; section 8 shows the effect.',
    'R2 A night belongs to the period / calendar year of its entry date (the close). Exit-date labelling moves one night',
    '   (2014-12-31 -> 2015-01-02) into the second half; shown in section 8.',
    'R3 Each name starts on its first night with a trend state: NVDA 2000-10-30, the other ten 2000-10-16. Starting all',
    '   eleven on 2000-10-30 is shown in section 8.',
    'R4 One continuous simulation per name; the two halves are slices (state carried over). A fresh second-half run is',
    '   shown in section 8.',
    'R5 Trend-off table: b=0.98 on the same nights as the trend-on table.',
    'R6 P0 in the event study is the unpaused strategy of the same table (trend rule on: 0.98 or 0.25; off: 0.98).',
    '   The window is the pause-start night plus the next n-1 nights.',
    'R7 Bootstrap: years resampled with replacement (as many as the period has), statistic = pooled mean over the drawn',
    '   years of the realised per-night difference in ln(1+R). Paths are not re-simulated. 5th/95th percentiles.',
    'R8 Episodes are counted in the period where they start (full length kept); paused nights by their own date.',
    '   Drawdown is measured inside the period, starting from the equity at the period start.',
    'R9 Episode = one pause start and the paused nights that follow it. For P3, a maximal run of C nights.',
    'R10 Criterion 3 is read as: P2-P1 positive (the direction that would justify the change) for >= 8 of 11 names;',
    '   the count with either sign is printed as well.',
    'R11 No earnings blackout, no KILL, no whole-share rounding, no 1-share floor: only the two rules in the brief.']:
    P(' ', ln_)
P('\n## 1. DATA REPORT')
P('raw NVDA bars around the break (date, open, close, volume):')
for row in L.nvda_break_check():
    P('   ', row)
P('%-5s %6s %6s %7s %8s %8s %4s %7s %9s %6s  %s .. %s' % ('sym', 'raw', 'interp', 'zerovol', 'badprice', 'afterEnd',
                                                         'dup', 'dupMism', 'nvdaPre', 'kept', 'first', 'last'))
for sym in ['QQQ'] + NAMES:
    c = rep[sym]
    P('%-5s %6d %6d %7d %8d %8d %4d %7d %9d %6d  %s .. %s' % (sym, c['raw'], c['interp'], c['zero_vol'], c['bad_price'],
                                                             c['after_end'], c['dup'], c['dup_mismatch'],
                                                             c['nvda_prebreak'], c['kept'], c['first'], c['last']))
    if c['zero_vol_dates']:
        P('      zero-volume dates skipped:', c['zero_vol_dates'])

# QQQ trend state on QQQ's own sessions
q = data['QQQ']
qd = q['dates']
qc = np.array(q['close'])
csum = np.concatenate(([0.0], np.cumsum(qc)))
trend_up = {}
for i in range(199, len(qd)):
    m = (csum[i] - csum[i - 199]) / 199.0          # mean of the 199 closes before session i
    trend_up[qd[i]] = bool(qc[i] >= m)
first_trend = qd[199]
P('QQQ sessions kept: %d, first trend state on %s (needs 199 prior closes); share of sessions at or above the mean: %.3f'
  % (len(qd), first_trend, np.mean(list(trend_up.values()))))
P('QQQ trend state on the last sessions:', [(d_, 'UP' if trend_up[d_] else 'DOWN') for d_ in qd[-3:]])
# brute-force check of the rolling mean on a few indices
for i in (199, 1234, len(qd) - 1):
    assert abs(np.mean(qc[i - 199:i]) - (csum[i] - csum[i - 199]) / 199.0) < 1e-9


def build(sym, start_date=None):
    """Night arrays for one underlying on the calendar common to it and QQQ."""
    x = data[sym]
    qset = set(qd)
    xs = set(x['dates'])
    missing_in_q = [d_ for d_ in x['dates'] if d_ not in qset]
    missing_in_x = [d_ for d_ in qd if d_ not in xs and x['dates'][0] <= d_ <= x['dates'][-1]]
    keep = [i for i, d_ in enumerate(x['dates']) if d_ in qset]
    dts = [x['dates'][i] for i in keep]
    op = np.array([x['open'][i] for i in keep])
    cl = np.array([x['close'][i] for i in keep])
    nd, r, bt = [], [], []
    ex = []
    for i in range(len(dts) - 1):
        d0 = dts[i]
        if d0 not in trend_up:
            continue
        if start_date is not None and d0 < start_date:
            continue
        nd.append(d0)
        ex.append(dts[i + 1])
        r.append(op[i + 1] / cl[i] - 1.0)
        bt.append(0.98 if trend_up[d0] else 0.25)
    return dict(dates=np.array(nd), exit_dates=np.array(ex), r=np.array(r), b_on=np.array(bt),
                b_off=np.full(len(r), 0.98), years=np.array([int(d_[:4]) for d_ in nd]),
                missing_in_q=missing_in_q, missing_in_x=missing_in_x)


N = {s_: build(s_) for s_ in NAMES}
P('\nnights per name (labelled by the date of the close; last night is the close of %s -> open of %s):'
  % (N['NVDA']['dates'][-1], N['NVDA']['exit_dates'][-1]))
P('%-5s %7s %-11s %-11s %8s %8s %9s %9s %9s  calendar mismatches vs QQQ' % (
    'sym', 'nights', 'first', 'last', 'H1', 'H2', 'mean r%', 'min r%', 'max r%'))
flagged = []
for s_ in NAMES:
    n_ = N[s_]
    h1 = int((n_['dates'] <= H1_END).sum())
    P('%-5s %7d %-11s %-11s %8d %8d %9.4f %9.2f %9.2f  notInQQQ=%d notInX=%d' % (
        s_, len(n_['r']), n_['dates'][0], n_['dates'][-1], h1, len(n_['r']) - h1,
        100 * n_['r'].mean(), 100 * n_['r'].min(), 100 * n_['r'].max(),
        len(n_['missing_in_q']), len(n_['missing_in_x'])))
    for i in np.where(np.abs(n_['r']) > 0.45)[0]:
        flagged.append((s_, n_['dates'][i], n_['exit_dates'][i], float(n_['r'][i])))
P('\nSANITY FILTER (overnight move beyond +/-45% in the underlying):',
  'NONE flagged' if not flagged else flagged)
P('largest absolute overnight moves per name (date of close, r%):')
for s_ in NAMES:
    n_ = N[s_]
    o = np.argsort(-np.abs(n_['r']))[:3]
    P('   %-5s' % s_, ['%s %+.1f%%' % (n_['dates'][i], 100 * n_['r'][i]) for i in o])
# gaps between consecutive sessions longer than 5 calendar days
import datetime as _dt
gaps = []
for i in range(len(N['NVDA']['dates'])):
    a = _dt.date.fromisoformat(N['NVDA']['dates'][i]); b_ = _dt.date.fromisoformat(N['NVDA']['exit_dates'][i])
    if (b_ - a).days > 5:
        gaps.append((N['NVDA']['dates'][i], N['NVDA']['exit_dates'][i]))
P('NVDA nights spanning more than 5 calendar days:', gaps)


# ------------------------------------------------------------------ simulate
def variants():
    v = [('P0', 'P0', 0.25, 5, 'post')]
    for p in PSIZES:
        v.append(('P1', 'P1', p, 5, 'post'))
        v.append(('P2', 'P2', p, 5, 'post'))
        v.append(('P3', 'P3', p, 5, 'post'))
        v.append(('P2x10', 'P2', p, 10, 'post'))
        v.append(('P2any', 'P2', p, 5, 'any'))
        v.append(('P2x10any', 'P2', p, 10, 'any'))
    return v


def simulate_name(n_, trend):
    b = n_['b_on'] if trend == 'on' else n_['b_off']
    res = {}
    for label, var, p, nfix, rearm in variants():
        rr = S.run_loop(n_['r'], b, var, p, nfix, rearm)
        rr['eps'] = S.episodes_from(rr)
        rr['chk'] = S.verify(n_['r'], b, rr, var, p, nfix, rearm)
        res[(label, p)] = rr
    return res


SIM = {}
worst = dict(max_lnR_diff=0.0, flag_mismatch=0, C_mismatch=0, size_mismatch=0, starts_bad=0)
vec_report = []
for trend in ('on', 'off'):
    for s_ in NAMES:
        n_ = N[s_]
        b = n_['b_on'] if trend == 'on' else n_['b_off']
        res = simulate_name(n_, trend)
        SIM[(trend, s_)] = res
        for k, rr in res.items():
            c = rr['chk']
            worst['max_lnR_diff'] = max(worst['max_lnR_diff'], c['max_lnR_diff'])
            worst['flag_mismatch'] += c['flag_mismatch']
            worst['C_mismatch'] += c['C_mismatch']
            worst['size_mismatch'] += c['size_mismatch']
            worst['starts_bad'] += 0 if c['starts_equal'] else 1
        # vectorised P0
        v0 = S.vec_P0(n_['r'], b)
        d0 = float(np.max(np.abs(v0['lnR'] - res[('P0', 0.25)]['lnR'])))
        # vectorised P3 (fixed point) at each pause size
        d3 = []
        for p in PSIZES:
            v3 = S.vec_P3(n_['r'], b, p)
            l3 = res[('P3', p)]
            d3.append((p, float(np.max(np.abs(v3['lnR'] - l3['lnR']))), int((v3['s'] != l3['s']).sum()),
                       float(abs(v3['lnR'].sum() - l3['lnR'].sum())), v3['iters']))
        vec_report.append((trend, s_, d0, d3))

P('\n## 2. CROSS-CHECKS (loop vs vectorised)')
P('P0: vectorised log1p(b*(2r-9bp)); P3: vectorised fixed-point iteration (array ops only).')
P('%-4s %-5s %12s | per pause size: (p, max|dlnR|, size mismatches, |d sum lnR|, passes)' % ('trnd', 'sym', 'P0 max|dlnR|'))
for trend, s_, d0, d3 in vec_report:
    P('%-4s %-5s %12.2e | %s' % (trend, s_, d0, '  '.join('(%.2f, %.1e, %d, %.1e, %d)' % x for x in d3)))
P('All variants (P0,P1,P2,P3,P2x10 and the alternative P2 reading), all names, both trend modes: re-derived')
P('from the loop sizes with cumprod + rolling max + an independently coded flag scan:', worst)


# ------------------------------------------------------------------ statistics helpers
def pmask(n_, pk, by='entry'):
    d_ = n_['dates'] if by == 'entry' else n_['exit_dates']
    if pk == 'H1':
        return d_ <= H1_END if by == 'entry' else d_ <= '2015-01-01'
    if pk == 'H2':
        return d_ > H1_END if by == 'entry' else d_ > '2015-01-01'
    return np.ones(len(d_), dtype=bool)


def stats(n_, rr, pk, b, by='entry'):
    m = pmask(n_, pk, by)
    ln = rr['lnR'][m]
    eps = [(t0, ln_) for (t0, ln_) in rr['eps'] if m[t0]]
    lens = [e[1] for e in eps]
    return dict(n=int(m.sum()), g=100 * ln.mean(), mult=float(np.exp(ln.sum())),
                dd=S.max_drawdown(1.0, ln), eps=len(eps), pn=int(rr['paused'][m].sum()),
                eff=int(((rr['s'] < b - 1e-12) & m).sum()),
                med=(float(np.median(lens)) if lens else float('nan')),
                mx=(int(max(lens)) if lens else 0))


def gdiff(n_, ra, rb, pk, by='entry'):
    """100 * mean(lnR_a - lnR_b) with year-block bootstrap 90% interval."""
    m = pmask(n_, pk, by)
    d_ = 100 * (ra['lnR'][m] - rb['lnR'][m])
    lo, hi, ppos = S.boot_ci(d_, n_['years'][m], SEED, NDRAW)
    return float(d_.mean()), lo, hi, ppos


TABLE_ORDER = [('P0', 0.25)] + [(v, p) for p in PSIZES for v in ('P1', 'P2', 'P3', 'P2x10')]
nvda_json = []


def table_for(sym, trend, to_json=False):
    n_ = N[sym]
    b = n_['b_on'] if trend == 'on' else n_['b_off']
    res = SIM[(trend, sym)]
    for pk, pname in zip(PKEY, PERIODS):
        P('\n  %s | trend rule %s | %s' % (sym, trend.upper(), pname))
        P('  %-6s %5s %6s %9s %14s %8s %4s %7s %7s %6s %4s' % (
            'var', 'p', 'nights', 'g %/night', 'terminal x', 'maxDD %', 'eps', 'paused', 'reduced', 'medLen', 'max'))
        for (v, p) in TABLE_ORDER:
            st = stats(n_, res[(v, p)], pk, b)
            P('  %-6s %5s %6d %9.4f %14.4g %8.2f %4d %7d %7d %6s %4d' % (
                v, '-' if v == 'P0' else '%.2f' % p, st['n'], st['g'], st['mult'], st['dd'], st['eps'], st['pn'],
                st['eff'], ('%.1f' % st['med']) if st['eps'] else '-', st['mx']))
            if to_json:
                row = dict(trend_rule=trend, period=pname, variant=v, pause_size=p,
                           g_pct_per_night=round(st['g'], 4), max_drawdown_pct=round(st['dd'], 2),
                           episodes=st['eps'], paused_nights=st['pn'],
                           median_len=(round(st['med'], 1) if st['eps'] else 0.0), max_len=st['mx'],
                           terminal_multiple=float('%.5g' % st['mult']), nights=st['n'], reduced_nights=st['eff'])
                nvda_json.append(row)
        P('  differences in g (%/night) [90% year-block bootstrap interval] {share of draws > 0}:')
        for p in PSIZES:
            parts = []
            for (a, b_) in (('P1', 'P0'), ('P2', 'P0'), ('P3', 'P0'), ('P2', 'P1'), ('P2x10', 'P1')):
                ra = res[(a, p)]
                rb = res[(b_, 0.25)] if b_ == 'P0' else res[(b_, p)]
                dm, lo, hi, pp = gdiff(n_, ra, rb, pk)
                parts.append('%s-%s %+.4f [%+.4f,%+.4f] {%.2f}' % (a, b_, dm, lo, hi, pp))
            P('   p=%.2f  ' % p + ' | '.join(parts))


P('\n## 3. NVDA TABLES')
P('columns: g = 100*mean ln(1+R); terminal x = product of (1+R) inside the period; maxDD = worst peak-to-trough')
P('fall of E inside the period; eps = pause episodes that START in the period; paused = nights in the paused')
P('state; reduced = paused nights on which the size was actually cut (s < b); medLen/max = episode length.')
P('The simulation is ONE continuous run from the first night; the halves are slices of it.')
for trend in ('on', 'off'):
    table_for('NVDA', trend, to_json=True)

# ------------------------------------------------------------------ NVDA episodes under P1
for trend in ('on', 'off'):
    n_ = N['NVDA']
    res = SIM[(trend, 'NVDA')]
    b = n_['b_on'] if trend == 'on' else n_['b_off']
    r1, r0, r2 = res[('P1', 0.25)], res[('P0', 0.25)], res[('P2', 0.25)]
    P('\n## 4. NVDA pause episodes under P1 (p=0.25), trend rule %s' % trend.upper())
    P('cum log return (%) over the nights of the P1 episode, each variant on its own equity path.')
    P('up = nights in the episode with base size 0.98; ext = P1 paused nights beyond the first 5;')
    P('P2pz = nights of the episode on which P2 was itself paused.')
    P('  %-3s %-11s %-11s %4s %3s %4s %5s %9s %9s %9s %9s' % ('#', 'start', 'last night', 'len', 'up', 'ext', 'P2pz',
                                                             'P0 %', 'P1 %', 'P2 %', 'P2-P1 %'))
    tot = np.zeros(3)
    for k, (t0, ln_) in enumerate(r1['eps']):
        sl = slice(t0, t0 + ln_)
        c0, c1, c2 = (100 * r0['lnR'][sl].sum(), 100 * r1['lnR'][sl].sum(), 100 * r2['lnR'][sl].sum())
        tot += (c0, c1, c2)
        P('  %-3d %-11s %-11s %4d %3d %4d %5d %+9.2f %+9.2f %+9.2f %+9.2f' % (
            k + 1, n_['dates'][t0], n_['dates'][t0 + ln_ - 1], ln_, int((b[sl] > 0.5).sum()), max(0, ln_ - 5),
            int(r2['paused'][sl].sum()), c0, c1, c2, c2 - c1))
    P('  sum over episodes: P0 %+.2f  P1 %+.2f  P2 %+.2f  (P2-P1 %+.2f) ; whole-span sum of lnR: P1 %.2f  P2 %.2f  diff %+.2f'
      % (tot[0], tot[1], tot[2], tot[2] - tot[1], 100 * r1['lnR'].sum(), 100 * r2['lnR'].sum(),
         100 * (r2['lnR'].sum() - r1['lnR'].sum())))
    P('  P2 (p=0.25) pause starts:', [n_['dates'][t0] for (t0, _) in r2['eps']])


# ------------------------------------------------------------------ event study
def event_study(trend, names, p=0.25):
    rows = {}
    for h in HORIZ:
        ev, unc_all, own = [], [], []
        for s_ in names:
            n_ = N[s_]
            ln0 = SIM[(trend, s_)][('P0', 0.25)]['lnR']
            cs = np.concatenate(([0.0], np.cumsum(ln0)))
            nn = len(ln0)
            win = cs[h:] - cs[:-h] if nn >= h else np.array([])      # window starting at t, t=0..nn-h
            unc_all.append(win)
            for (t0, _) in SIM[(trend, s_)][('P1', p)]['eps']:
                if t0 + h <= nn:
                    ev.append(win[t0])
                    own.append(win.mean())
        ev = np.array(ev)
        ua = np.concatenate(unc_all)
        rows[h] = dict(n=len(ev), mean=100 * ev.mean() if len(ev) else float('nan'),
                       med=100 * np.median(ev) if len(ev) else float('nan'),
                       se=100 * ev.std(ddof=1) / np.sqrt(len(ev)) if len(ev) > 1 else float('nan'),
                       pos=float((ev > 0).mean()) if len(ev) else float('nan'),
                       unc=100 * ua.mean(), unc_med=100 * np.median(ua), own=100 * np.mean(own) if own else float('nan'))
    return rows


P('\n## 5. EVENT STUDY: P0 cumulative log return (%) over the next n nights from each P1 pause start')
P('(window = the night the pause starts and the n-1 after it; events whose window runs past the sample end are')
P('left out of that horizon; "uncond" = mean over every possible start night; "own-name uncond" = each event')
P('compared with its own name\'s unconditional mean; se = sd/sqrt(n), events are not independent.)')
ES = {}
for trend in ('on', 'off'):
    for lab, names in (('NVDA', ['NVDA']), ('POOLED 11 names', NAMES), ('10 names ex NVDA', NAMES[1:])):
        rows = event_study(trend, names)
        ES[(trend, lab)] = rows
        P('  trend %s | %s | P1 p=0.25' % (trend.upper(), lab))
        P('   %4s %6s %9s %9s %7s %6s %9s %9s %12s %10s' % ('n', 'events', 'mean %', 'median %', 'se', '%pos',
                                                         'uncond %', 'unc med %', 'own-name unc', 'mean-unc'))
        for h in HORIZ:
            x = rows[h]
            P('   %4d %6d %+9.2f %+9.2f %7.2f %6.2f %+9.2f %+9.2f %+12.2f %+10.2f' % (
                h, x['n'], x['mean'], x['med'], x['se'], x['pos'], x['unc'], x['unc_med'], x['own'],
                x['mean'] - x['own']))

# extension nights: the only nights on which P1 and P2 can differ in a path-free sense
P('\n## 6. EXTENSION NIGHTS (P1 paused beyond the first 5 nights of an episode), p=0.25')
P('unit = 2r-9bp, the return of one unit of size, in % per night. "bite" = extension nights with base size 0.98')
P('(with p=0.25 the extension changes nothing when the trend rule already has the size at 0.25).')
EXT = {}
for trend in ('on', 'off'):
    for lab, names in (('NVDA', ['NVDA']), ('POOLED 11 names', NAMES)):
        u_ext, u_all, u_first5, nb, n_ep, ext_per_ep = [], [], [], 0, 0, []
        for s_ in names:
            n_ = N[s_]
            b = n_['b_on'] if trend == 'on' else n_['b_off']
            unit = 100 * (2 * n_['r'] - S.COST)
            u_all.append(unit[b > 0.5])
            for (t0, ln_) in SIM[(trend, s_)][('P1', 0.25)]['eps']:
                n_ep += 1
                idx = np.arange(t0 + 5, t0 + ln_)
                bite = idx[b[idx] > 0.5] if len(idx) else idx
                ext_per_ep.append(len(bite))
                u_ext.append(unit[bite])
                f5 = np.arange(t0, min(t0 + 5, t0 + ln_))
                u_first5.append(unit[f5[b[f5] > 0.5]])
        u_ext = np.concatenate(u_ext) if u_ext else np.array([])
        u_all = np.concatenate(u_all)
        u_first5 = np.concatenate(u_first5)
        EXT[(trend, lab)] = dict(n_ep=n_ep, n_ext=len(u_ext), mean_ext=float(u_ext.mean()) if len(u_ext) else float('nan'),
                                 mean_all=float(u_all.mean()), ext_per_ep=float(np.mean(ext_per_ep)),
                                 med_ext=float(np.median(ext_per_ep)), max_ext=int(max(ext_per_ep)))
        P('  trend %-3s | %-16s | episodes %3d | biting extension nights %4d (mean %.1f, median %.0f, max %d per episode)'
          % (trend.upper(), lab, n_ep, len(u_ext), np.mean(ext_per_ep), np.median(ext_per_ep), max(ext_per_ep)))
        if len(u_ext) > 1:
            P('      mean unit return on them %+.3f%% (se %.3f, median %+.3f, %%pos %.2f) | first-5 pause nights with base 0.98: n=%d mean %+.3f%% | all base-0.98 nights: %+.3f%%'
              % (u_ext.mean(), u_ext.std(ddof=1) / np.sqrt(len(u_ext)), np.median(u_ext), (u_ext > 0).mean(),
                 len(u_first5), u_first5.mean() if len(u_first5) else float('nan'), u_all.mean()))

# ------------------------------------------------------------------ 11 names
P('\n## 7. THE 11 NAMES: P2 - P1 in g (%/night), [90% year-block bootstrap]')
NAMECOUNT = {}
for trend in ('on', 'off'):
    for p in PSIZES:
        P('  trend %s | pause size %.2f' % (trend.upper(), p))
        P('  %-5s | %-34s | %-34s | %-34s | P1 eps, P2 eps | maxDD P1/P2 (ALL)' % ('sym', 'H1', 'H2', 'ALL'))
        cnt = {pk: [0, 0, 0] for pk in PKEY}
        for s_ in NAMES:
            n_ = N[s_]
            b = n_['b_on'] if trend == 'on' else n_['b_off']
            res = SIM[(trend, s_)]
            cells = []
            for pk in PKEY:
                dm, lo, hi, pp = gdiff(n_, res[('P2', p)], res[('P1', p)], pk)
                cnt[pk][0 if dm > 0 else (1 if dm < 0 else 2)] += 1
                cells.append('%+.4f [%+.4f,%+.4f] %s' % (dm, lo, hi, '+' if dm > 0 else ('-' if dm < 0 else '0')))
            s1 = stats(n_, res[('P1', p)], 'ALL', b)
            s2 = stats(n_, res[('P2', p)], 'ALL', b)
            P('  %-5s | %-34s | %-34s | %-34s | %3d %3d | %.1f / %.1f' % (s_, cells[0], cells[1], cells[2],
                                                                        s1['eps'], s2['eps'], s1['dd'], s2['dd']))
        P('  count positive / negative / zero:  H1 %s  H2 %s  ALL %s' % tuple(str(cnt[pk]) for pk in PKEY))
        NAMECOUNT[(trend, p)] = cnt
    # P0 comparisons, for context only
    P('  trend %s | context only (dropping PAUSE is not on the table): g of P0, P1, P2, P3 (p=0.25), whole span' % trend.upper())
    for s_ in NAMES:
        n_ = N[s_]
        b = n_['b_on'] if trend == 'on' else n_['b_off']
        res = SIM[(trend, s_)]
        gs = [stats(n_, res[k], 'ALL', b) for k in (('P0', 0.25), ('P1', 0.25), ('P2', 0.25), ('P3', 0.25))]
        P('   %-5s g: P0 %+.4f P1 %+.4f P2 %+.4f P3 %+.4f | maxDD: P0 %.1f P1 %.1f P2 %.1f P3 %.1f' % (
            (s_,) + tuple(x['g'] for x in gs) + tuple(x['dd'] for x in gs)))

# ------------------------------------------------------------------ criteria
P('\n## 8. PRE-REGISTERED CRITERIA (primary: trend rule ON, pause size 0.25, P2 re-arm reading "post")')


def criteria(trend, p, p2label='P2', by='entry', sims=None, nights=None):
    sims = sims or SIM
    nights = nights or N
    n_ = nights['NVDA']
    b = n_['b_on'] if trend == 'on' else n_['b_off']
    res = sims[(trend, 'NVDA')]
    out = {}
    for pk in ('H1', 'H2'):
        s1 = stats(n_, res[('P1', p)], pk, b, by)
        s2 = stats(n_, res[(p2label, p)], pk, b, by)
        out[pk] = (s1['g'], s2['g'], s1['dd'], s2['dd'])
    c1 = all(out[pk][1] >= out[pk][0] for pk in ('H1', 'H2'))
    c2 = all(out[pk][3] - out[pk][2] <= 5.0 for pk in ('H1', 'H2'))
    pos = neg = zero = 0
    for s_ in NAMES:
        nn = nights[s_]
        rs = sims[(trend, s_)]
        dm = float((rs[(p2label, p)]['lnR'] - rs[('P1', p)]['lnR']).mean())
        if dm > 0:
            pos += 1
        elif dm < 0:
            neg += 1
        else:
            zero += 1
    c3 = pos >= 8
    return dict(halves=out, c1=c1, c2=c2, pos=pos, neg=neg, zero=zero, c3=c3, change=(c1 and c2 and c3))


def show_crit(tag, cr):
    h = cr['halves']
    P('  %-44s | H1 g P1 %.4f P2 %.4f (%+.4f) dd P1 %.2f P2 %.2f (%+.2f) | H2 g P1 %.4f P2 %.4f (%+.4f) dd P1 %.2f P2 %.2f (%+.2f)'
      % (tag, h['H1'][0], h['H1'][1], h['H1'][1] - h['H1'][0], h['H1'][2], h['H1'][3], h['H1'][3] - h['H1'][2],
         h['H2'][0], h['H2'][1], h['H2'][1] - h['H2'][0], h['H2'][2], h['H2'][3], h['H2'][3] - h['H2'][2]))
    P('  %-44s |   (1) %s  (2) %s  (3) %d of 11 positive, %d negative, %d zero -> %s  => %s'
      % ('', 'PASS' if cr['c1'] else 'FAIL', 'PASS' if cr['c2'] else 'FAIL', cr['pos'], cr['neg'], cr['zero'],
         'PASS' if cr['c3'] else 'FAIL', 'CHANGE TO P2' if cr['change'] else 'KEEP AS WRITTEN'))


CR = criteria('on', 0.25)
show_crit('PRIMARY trend on, p=0.25', CR)
P('\n  sensitivities (not the pre-registered test; they show how fragile the outcome is):')
for trend in ('on', 'off'):
    for p in PSIZES:
        if (trend, p) == ('on', 0.25):
            continue
        show_crit('trend %s, p=%.2f' % (trend, p), criteria(trend, p))
for trend in ('on', 'off'):
    show_crit('P2 re-arm "any" reading, trend %s, p=0.25' % trend, criteria(trend, 0.25, 'P2any'))
show_crit('halves labelled by exit date, trend on', criteria('on', 0.25, by='exit'))
show_crit('P2x10 in place of P2, trend on, p=0.25', criteria('on', 0.25, 'P2x10'))

# sensitivity: all names started at 2000-10-30
N2 = {s_: build(s_, '2000-10-30') for s_ in NAMES}
SIM2 = {}
for trend in ('on', 'off'):
    for s_ in NAMES:
        n_ = N2[s_]
        b = n_['b_on'] if trend == 'on' else n_['b_off']
        SIM2[(trend, s_)] = {}
        for label, var, p, nfix, rearm in (('P1', 'P1', 0.25, 5, 'post'), ('P2', 'P2', 0.25, 5, 'post')):
            rr = S.run_loop(n_['r'], b, var, p, nfix, rearm)
            rr['eps'] = S.episodes_from(rr)
            SIM2[(trend, s_)][(label, p)] = rr
show_crit('all names started 2000-10-30, trend on', criteria('on', 0.25, sims=SIM2, nights=N2))

# sensitivity: second half run as a fresh simulation from 2015-01-02
P('\n  NVDA second half as a FRESH run from 2015-01-02 (E=1, empty window) instead of a slice:')
for trend in ('on', 'off'):
    nf = build('NVDA', '2015-01-02')
    b = nf['b_on'] if trend == 'on' else nf['b_off']
    f1 = S.run_loop(nf['r'], b, 'P1', 0.25)
    f2 = S.run_loop(nf['r'], b, 'P2', 0.25)
    P('   trend %-3s: g P1 %.4f P2 %.4f (%+.4f) | maxDD P1 %.2f P2 %.2f (%+.2f)' % (
        trend, 100 * f1['lnR'].mean(), 100 * f2['lnR'].mean(), 100 * (f2['lnR'].mean() - f1['lnR'].mean()),
        S.max_drawdown(1, f1['lnR']), S.max_drawdown(1, f2['lnR']),
        S.max_drawdown(1, f2['lnR']) - S.max_drawdown(1, f1['lnR'])))

# reading sensitivity for P2 itself: 'post' vs 'any'
P('\n  P2 re-arm reading, NVDA p=0.25: g and maxDD under "post" (primary) and "any"')
for trend in ('on', 'off'):
    n_ = N['NVDA']
    b = n_['b_on'] if trend == 'on' else n_['b_off']
    for pk in PKEY:
        a = stats(n_, SIM[(trend, 'NVDA')][('P2', 0.25)], pk, b)
        c = stats(n_, SIM[(trend, 'NVDA')][('P2any', 0.25)], pk, b)
        P('   trend %-3s %-3s: post g %.4f dd %.2f eps %d paused %d | any g %.4f dd %.2f eps %d paused %d | d g %+.5f'
          % (trend, pk, a['g'], a['dd'], a['eps'], a['pn'], c['g'], c['dd'], c['eps'], c['pn'], c['g'] - a['g']))
P('  P2 re-arm reading, per name, whole span, trend on, p=0.25: P2-P1 under post / any')
for s_ in NAMES:
    rs = SIM[('on', s_)]
    P('   %-5s %+.4f / %+.4f' % (s_, 100 * (rs[('P2', 0.25)]['lnR'] - rs[('P1', 0.25)]['lnR']).mean(),
                                 100 * (rs[('P2any', 0.25)]['lnR'] - rs[('P1', 0.25)]['lnR']).mean()))

# ------------------------------------------------------------------ dollars
P('\n## 9. DOLLARS AT STAKE at $82 of equity')
E0 = 82.0
n_ = N['NVDA']
unit = 2 * n_['r'] - S.COST
m2 = n_['dates'] > H1_END
up = n_['b_on'] > 0.5
P('  size gap on a night where P1 is still paused and P2 is back to normal: 0.98 - 0.25 = 0.73 of equity = $%.2f'
  % (0.73 * E0))
P('  (zero if QQQ is below its mean: the trend rule then has the size at 0.25 either way)')
mus = [('NVDA all nights 2000-2026', unit.mean()), ('NVDA all nights 2015-2026', unit[m2].mean()),
       ('NVDA trend-UP nights 2000-2026', unit[up].mean()), ('NVDA trend-UP nights 2015-2026', unit[up & m2].mean()),
       ('NVDA biting extension nights (trend on)', EXT[('on', 'NVDA')]['mean_ext'] / 100),
       ('pooled 11 names biting extension nights (trend on)', EXT[('on', 'POOLED 11 names')]['mean_ext'] / 100)]
for lab, mu in mus:
    P('  %-52s mean unit return %+.3f%%/night -> $%+.3f per extension night, $%+.2f over 16 nights (a 21-session month less the 5 common nights)'
      % (lab, 100 * mu, 0.73 * E0 * mu, 16 * 0.73 * E0 * mu))
sd_unit = unit[up].std(ddof=1)
P('  one-night sd of the gap P&L on trend-UP nights: $%.2f ; over 16 nights about $%.2f' % (
    0.73 * E0 * sd_unit, 0.73 * E0 * sd_unit * 4))
for trend in ('on', 'off'):
    res = SIM[(trend, 'NVDA')]
    for pk in PKEY:
        m = pmask(n_, pk)
        dg = (res[('P2', 0.25)]['lnR'][m] - res[('P1', 0.25)]['lnR'][m]).mean()
        P('  simulated long-run average, trend %-3s %-3s: P2-P1 = %+.4f%%/night = $%+.3f per 21-session month at $82'
          % (trend, pk, 100 * dg, E0 * 21 * dg))
ee = EXT[('on', 'NVDA')]
P('  expected per episode = biting extension nights per episode (mean %.2f) x $ per night: $%.2f at the all-night NVDA mean, $%.2f at the 2015-26 trend-UP mean, $%.2f at the mean actually seen on NVDA extension nights'
  % (ee['ext_per_ep'], ee['ext_per_ep'] * 0.73 * E0 * unit.mean(), ee['ext_per_ep'] * 0.73 * E0 * unit[up & m2].mean(),
     ee['ext_per_ep'] * 0.73 * E0 * ee['mean_ext'] / 100))
P('  longest run of biting extension nights in one NVDA episode: %d -> at most $%.2f..$%.2f in one episode at those means'
  % (ee['max_ext'], ee['max_ext'] * 0.73 * E0 * unit.mean(), ee['max_ext'] * 0.73 * E0 * unit[up & m2].mean()))
P('  QQQ trend state at the last completed sessions in the data: %s  (DOWN => base size 0.25 => P1 and P2 hold the same size, gap $0)'
  % [(d_, 'UP' if trend_up[d_] else 'DOWN') for d_ in qd[-3:]])
P('  history of the extension under P1 (trend on, p=0.25), NVDA: %d episodes, %.1f biting extension nights per episode on average (median %.0f, max %d)'
  % (EXT[('on', 'NVDA')]['n_ep'], EXT[('on', 'NVDA')]['ext_per_ep'], EXT[('on', 'NVDA')]['med_ext'],
     EXT[('on', 'NVDA')]['max_ext']))

# ------------------------------------------------------------------ other names tables (compact)
P('\n## 10. PER-NAME TABLES (p=0.25 rows only printed for brevity: P0, P1, P2, P3, P2x10)')
for trend in ('on', 'off'):
    for s_ in NAMES[1:]:
        n_ = N[s_]
        b = n_['b_on'] if trend == 'on' else n_['b_off']
        res = SIM[(trend, s_)]
        for pk, pname in zip(PKEY, PERIODS):
            for (v, p) in (('P0', 0.25), ('P1', 0.25), ('P2', 0.25), ('P3', 0.25), ('P2x10', 0.25)):
                st = stats(n_, res[(v, p)], pk, b)
                P('  %-5s %-3s %-3s %-6s n=%5d g=%+.4f mult=%-11.4g dd=%6.2f eps=%3d paused=%4d reduced=%4d med=%s max=%d' % (
                    s_, trend, pk, v, st['n'], st['g'], st['mult'], st['dd'], st['eps'], st['pn'], st['eff'],
                    ('%.1f' % st['med']) if st['eps'] else '-', st['mx']))

with open(os.path.join(HERE, 'results.txt'), 'w') as fh:
    fh.write('\n'.join(out_lines) + '\n')
with open(os.path.join(HERE, 'nvda_table.json'), 'w') as fh:
    json.dump(nvda_json, fh, indent=0)
summary = dict(criteria=dict(c1=CR['c1'], c2=CR['c2'], pos=CR['pos'], neg=CR['neg'], zero=CR['zero'],
                             change=CR['change'], halves=CR['halves']))
with open(os.path.join(HERE, 'summary.json'), 'w') as fh:
    json.dump(summary, fh, indent=1)
print('\nwrote', os.path.join(HERE, 'results.txt'))
