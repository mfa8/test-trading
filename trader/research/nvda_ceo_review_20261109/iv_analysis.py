#!/usr/bin/env python3
"""NVDA implied-vol read (read-only research, 2026-11-09 pre-open).

Inputs (all in this directory):
  data_quotes_fri1106close.json  - RH option quotes (all stamped Fri 11/6 16:00 ET close)
  data_opt_hist_daily.json       - RH daily option bars 10/19..11/06 (last-trade closes)
  nvda_daily_2y.json             - RH NVDA daily bars 2024-11-01..2026-11-06
  /home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv (read only)
Outputs: results.json (+ stdout)

Usage: python3 iv_analysis.py [quotes_json] [spot_for_quotes]
  Re-run after the 09:30 open with a fresh quotes file (same schema, live spot) to
  replace the Friday-close numbers with live ones.
"""
import json, math, sys, os
import numpy as np, pandas as pd
from scipy.stats import norm, t as tdist
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
QFILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'data_quotes_fri1106close.json')
q = json.load(open(QFILE))
S_Q = float(sys.argv[2]) if len(sys.argv) > 2 else q['spot_fri_close']  # spot synchronous with quotes
S_NOW = q['spot_premarket_1109_0801ET']['last']  # 177.05
R = 0.033  # ~implied by put-call parity on 12/18 180/185 (3.1-3.4%); effect is tiny

# Calendar days and trading days from Fri 2026-11-06 16:00 ET to each expiry 16:00 ET.
# NYSE open 11/11 (Veterans Day); closed 11/26 (Thanksgiving). Earnings 11/17 after close.
CAL = {'2026-11-09': 3, '2026-11-11': 5, '2026-11-13': 7, '2026-11-16': 10,
       '2026-11-18': 12, '2026-11-20': 14, '2026-12-18': 42}
TD = {'2026-11-09': 1, '2026-11-11': 3, '2026-11-13': 5, '2026-11-16': 6,
      '2026-11-18': 8, '2026-11-20': 10, '2026-12-18': 29}
EARN_IN = {e: e >= '2026-11-18' for e in CAL}
# Optional live re-run: argv[3] = valuation time ET 'YYYY-MM-DDTHH:MM' (e.g. 2026-11-09T09:50).
# Then T and trading days are measured from that moment (today's remaining session counted as a fraction
# of a day's intraday share, ~0.66; the overnight already elapsed). Default = Fri 11/6 16:00 ET close.
if len(sys.argv) > 3:
    from datetime import datetime
    import numpy as _np0
    val = datetime.fromisoformat(sys.argv[3])
    frac = min(max((datetime(val.year, val.month, val.day, 16) - val).total_seconds() / (6.5 * 3600), 0), 1)
    for e in list(CAL):
        exp_dt = datetime.fromisoformat(e + 'T16:00')
        CAL[e] = (exp_dt - val).total_seconds() / 86400
        nfull = int(_np0.busday_count(str(val.date() + __import__('datetime').timedelta(days=1)), str(exp_dt.date() + __import__('datetime').timedelta(days=1)), holidays=['2026-11-26']))
        TD[e] = nfull + 0.66 * frac
    CAL = {e: v for e, v in CAL.items() if v > 0}


def black(F, K, T, sig, df, cp):
    if sig <= 0 or T <= 0:
        return df * max(0.0, (F - K) if cp == 'call' else (K - F))
    v = sig * math.sqrt(T)
    d1 = (math.log(F / K) + 0.5 * v * v) / v
    d2 = d1 - v
    if cp == 'call':
        return df * (F * norm.cdf(d1) - K * norm.cdf(d2))
    return df * (K * norm.cdf(-d2) - F * norm.cdf(-d1))


def impvol(px, F, K, T, df, cp):
    intrinsic = df * max(0.0, (F - K) if cp == 'call' else (K - F))
    if px <= intrinsic + 1e-6:
        return float('nan')
    try:
        return brentq(lambda s: black(F, K, T, s, df, cp) - px, 1e-4, 6.0)
    except ValueError:
        return float('nan')


# ---------------------------------------------------------------- Friday surface
quotes = pd.DataFrame(q['quotes'])
quotes['mid'] = (quotes.bid + quotes.ask) / 2
surf = {}
for exp, g in quotes.groupby('exp'):
    if exp not in CAL:
        continue
    T = CAL[exp] / 365.0
    df = math.exp(-R * T)
    piv = g.pivot_table(index='K', columns='type', values='mid')
    # forward from put-call parity, median across strikes with both legs
    Fs = [(K + (row.call - row.put) / df) for K, row in piv.dropna().iterrows()]
    F = float(np.median(Fs))
    rows = []
    for K, row in piv.iterrows():
        ivc = impvol(row.get('call', np.nan), F, K, T, df, 'call') if not pd.isna(row.get('call', np.nan)) else np.nan
        ivp = impvol(row.get('put', np.nan), F, K, T, df, 'put') if not pd.isna(row.get('put', np.nan)) else np.nan
        # OTM-side IV is cleaner; average when both exist (parity-consistent F makes them close)
        ivs = [x for x in (ivc, ivp) if not np.isnan(x)]
        rows.append(dict(K=K, call_mid=row.get('call', np.nan), put_mid=row.get('put', np.nan),
                         iv_call=ivc, iv_put=ivp, iv=float(np.mean(ivs)) if ivs else np.nan,
                         straddle_mid=row.get('call', np.nan) + row.get('put', np.nan)))
    tab = pd.DataFrame(rows).sort_values('K')
    def iv_at(k):
        t2 = tab.dropna(subset=['iv'])
        return float(np.interp(k, t2.K, t2.iv))  # flat extrapolation outside listed strikes
    atm_iv = iv_at(F)
    straddle_atm = black(F, F, T, atm_iv, df, 'call') + black(F, F, T, atm_iv, df, 'put')
    V = atm_iv ** 2 * T  # total implied variance to expiry
    surf[exp] = dict(F=F, T_cal_days=CAL[exp], TD=TD[exp], earnings_inside=EARN_IN[exp],
                     atm_iv=atm_iv, total_var=V,
                     atm_straddle=straddle_atm, atm_straddle_pct=straddle_atm / S_Q,
                     sigma_per_TD=math.sqrt(V / TD[exp]),
                     sigma_daily_iv_over_sqrt252=atm_iv / math.sqrt(252),
                     iv_at_K177=iv_at(S_NOW), iv_at_K175=iv_at(175.0), iv_at_K180=iv_at(180.0),
                     iv_skew_177_minus_atm=iv_at(S_NOW) - atm_iv,
                     strikes=tab.round(4).to_dict('records'))

# ---------------------------------------------------------------- event split
V = {e: surf[e]['total_var'] for e in surf}
splits = {}
# Method A (task): 11/13 (5 TD, no earnings) vs 11/20 (10 TD incl. earnings day 11/18)
dA = V['2026-11-13'] / TD['2026-11-13']
EA = V['2026-11-20'] - (TD['2026-11-20'] - 1) * dA
splits['A_1113_vs_1120'] = dict(base_var_per_TD=dA, base_sigma_per_TD=math.sqrt(dA),
                               base_ann_vol_252=math.sqrt(dA * 252),
                               earn_day_var=EA, earn_day_sigma=math.sqrt(max(EA, 0)),
                               earn_share_of_1120_var=EA / V['2026-11-20'],
                               pre_earn_share_of_1120_var=(TD['2026-11-20'] - 1) * dA / V['2026-11-20'])
# Method B (cleaner, adjacent weeklies): 11/16 (6 TD) vs 11/18 (8 TD incl. earnings night)
dB = V['2026-11-16'] / TD['2026-11-16']
EB = V['2026-11-18'] - (TD['2026-11-18'] - 1) * dB
splits['B_1116_vs_1118'] = dict(base_var_per_TD=dB, base_sigma_per_TD=math.sqrt(dB),
                               base_ann_vol_252=math.sqrt(dB * 252),
                               earn_day_var=EB, earn_day_sigma=math.sqrt(max(EB, 0)),
                               earn_share_of_1118_var=EB / V['2026-11-18'],
                               earn_share_of_1120_var=EB / V['2026-11-20'],
                               implied_base_for_1120_other9=(V['2026-11-20'] - EB) / (TD['2026-11-20'] - 1))
# Method C: 11/20 minus earnings (from B) -> base for the 9 non-event days; 12/18 likewise
for e in ('2026-11-20', '2026-12-18'):
    nb = TD[e] - 1
    splits.setdefault('C_ex_earn_base', {})[e] = dict(
        base_sigma_per_TD=math.sqrt(max(V[e] - EB, 0) / nb),
        base_ann_vol_252=math.sqrt(max(V[e] - EB, 0) / nb * 252))
# premium split in dollars for the 11/20 ATM straddle
T20 = CAL['2026-11-20'] / 365
F20 = surf['2026-11-20']['F']
df20 = math.exp(-R * T20)
for key, Evar in (('A', EA), ('B', EB)):
    exvar = max(V['2026-11-20'] - Evar, 1e-9)
    s_ex = math.sqrt(exvar / T20)
    strad_ex = black(F20, F20, T20, s_ex, df20, 'call') + black(F20, F20, T20, s_ex, df20, 'put')
    splits[f'dollar_split_1120_straddle_{key}'] = dict(
        total=surf['2026-11-20']['atm_straddle'], ex_earnings_counterfactual=strad_ex,
        earnings_premium=surf['2026-11-20']['atm_straddle'] - strad_ex,
        earnings_premium_pct_of_straddle=1 - strad_ex / surf['2026-11-20']['atm_straddle'])

# ---------------------------------------------------------------- overnight share (history)
bars = pd.DataFrame(json.load(open(os.path.join(HERE, 'nvda_daily_2y.json')))['data']['results'][0]['bars'])
bars['date'] = bars.begins_at.str[:10]
for c in ('open_price', 'close_price'):
    bars[c] = bars[c].astype(float)
bars['prev_close'] = bars.close_price.shift(1)
bars['on'] = np.log(bars.open_price / bars.prev_close)
bars['id'] = np.log(bars.close_price / bars.open_price)
bars['cc'] = np.log(bars.close_price / bars.prev_close)
csv = pd.read_csv('/home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv')
earn_react = set(csv.loc[csv.earn == 1, 'next'])
b = bars.dropna(subset=['on'])
b = b[~b.date.isin(earn_react)]
def share(x):
    return dict(n=len(x), sd_on=x.on.std(), sd_id=x.id.std(), sd_cc=x.cc.std(),
                var_share_on_of_cc=x.on.var() / x.cc.var(),
                var_share_on_of_on_plus_id=x.on.var() / (x.on.var() + x.id.var()),
                corr_on_id=x.on.corr(x.id))
on_share = {'2y_ex_earn': share(b), '1y_ex_earn': share(b[b.date >= '2025-11-07']),
            'last60_ex_earn': share(b.tail(60)), 'last20': share(b.tail(20))}
# long-run from CSV (overnight only) + weekend factor
c = csv[csv.earn == 0].copy()
c['lon'] = np.log1p(c.nvda_on)
wk = {}
for lab, sub in (('2015_2026', c), ('last2y', c[c.date >= '2024-11-06'])):
    v1 = sub[sub.gapdays == 1].lon.var(); v3 = sub[sub.gapdays >= 3].lon.var()
    wk[lab] = dict(var_ratio_weekend_vs_weeknight=v3 / v1, sd_weeknight=math.sqrt(v1), sd_weekend=math.sqrt(v3),
                   n1=int((sub.gapdays == 1).sum()), n3=int((sub.gapdays >= 3).sum()))
# NVDL beta to NVDA overnight
cc2 = csv.dropna(subset=['nvdl_clean'])
cc2 = cc2[cc2.earn == 0]
beta_nvdl = float(np.polyfit(cc2.nvda_on, cc2.nvdl_clean, 1)[0])

# empirical tail of standardized overnight returns (2015-2026, ex earnings), trailing 20-night sd, lagged
c = c.reset_index(drop=True)
c['sd20'] = c.lon.rolling(20).std().shift(1)
c['z'] = c.lon / c.sd20
zz = c.z.dropna()
emp_tail = {f'P(z<=-{k})': float((zz <= -k).mean()) for k in (2, 2.5, 3, 4, 5)}
emp_tail['n'] = int(len(zz)); emp_tail['kurtosis_excess_raw_on'] = float(c.lon.kurt())
ZZ = np.sort(zz.values)
def emp_p(k):  # P(z <= -k) for standardized (trailing-20 realized sd, lagged) overnight log returns 2015-2026 ex earnings
    return float(np.searchsorted(ZZ, -k, side='right') / len(ZZ))
big_drops = csv[(csv.earn == 0) & (csv.nvda_on <= -0.05)][['date', 'next', 'gapdays', 'nvda_on']].to_dict('records')
for nu in (3, 4):
    s = math.sqrt((nu - 2) / nu)
    for k in (2, 3, 4, 5):
        emp_tail[f't{nu}_P(z<=-{k})'] = float(tdist.cdf(-k / s, nu))
for k in (2, 3, 4, 5):
    emp_tail[f'normal_P(z<=-{k})'] = float(norm.cdf(-k))
# raw frequencies of big NVDA overnight drops
raw_freq = {}
for lab, sub in (('2015_2026_ex_earn', csv[csv.earn == 0]), ('last2y_ex_earn', csv[(csv.earn == 0) & (csv.date >= '2024-11-06')])):
    raw_freq[lab] = dict(n=len(sub), le_m5=int((sub.nvda_on <= -0.05).sum()), le_m98=int((sub.nvda_on <= -0.098).sum()),
                         p_le_m5=float((sub.nvda_on <= -0.05).mean()), p_le_m98=float((sub.nvda_on <= -0.098).mean()),
                         worst=float(sub.nvda_on.min()))
recent = csv.tail(20)
realized = dict(on_sd_last10=float(np.log1p(csv.nvda_on.tail(10)).std()),
                on_sd_last20=float(np.log1p(csv.nvda_on.tail(20)).std()),
                cc_sd_last10=float(bars.cc.tail(10).std()), cc_sd_last20=float(bars.cc.tail(20).std()),
                cc_ann_last10=float(bars.cc.tail(10).std() * math.sqrt(252)),
                cc_ann_last20=float(bars.cc.tail(20).std() * math.sqrt(252)))

# ---------------------------------------------------------------- overnight translation
share_base = on_share['1y_ex_earn']['var_share_on_of_cc']
share_lo, share_hi = on_share['2y_ex_earn']['var_share_on_of_cc'], 0.60
wkf = wk['last2y']['var_ratio_weekend_vs_weeknight']
TH = {'-5%': math.log(0.95), '-9.8%': math.log(0.902)}

def probs(sig):
    out = {}
    for lab, x in TH.items():
        out[f'normal_{lab}'] = float(norm.cdf(x / sig))
        for nu in (3, 4):
            out[f't{nu}_{lab}'] = float(tdist.cdf(x / (sig * math.sqrt((nu - 2) / nu)), nu))
        out[f'empz_{lab}'] = emp_p(-x / sig)
    return out

def six_night(sig_wd):
    # nights: Mon-Tue, Tue-Wed, Wed-Thu, Thu-Fri, Fri-Mon(weekend), Mon-Tue(11/16-17). 11/17-18 = earnings night, excluded
    sigs = [sig_wd] * 5 + [sig_wd * math.sqrt(wkf)]
    cum = math.sqrt(sum(s * s for s in sigs))
    res = dict(per_night_sigma_weeknight=sig_wd, weekend_night_sigma=sigs[-1], cum_6night_sigma=cum,
               nvdl_per_night_sigma=2 * sig_wd, nvdl_cum_6night_sigma=2 * cum)
    for lab in TH:
        for model in ('normal', 't3', 't4', 'empz'):
            ps = [probs(s)[f'{model}_{lab}'] for s in sigs]
            res[f'P_any_of_6_{model}_{lab}'] = float(1 - np.prod([1 - p for p in ps]))
    res['per_night_probs_weeknight'] = probs(sig_wd)
    return res

scen = {}
d_fri = splits['A_1113_vs_1120']['base_var_per_TD']  # Friday pre-news, ex-earnings per-TD variance
d_fri_B = splits['B_1116_vs_1118']['base_var_per_TD']
# sticky-strike: Friday's IV at K=177 for the 11/13 weekly, per TD
iv177_13 = surf['2026-11-13']['iv_at_K177']
d_sticky = iv177_13 ** 2 * (CAL['2026-11-13'] / 365) / TD['2026-11-13']
cases = {
    'fri_close_atm_1113 (pre-news, measured)': d_fri,
    'fri_close_atm_1116 (pre-news, measured)': d_fri_B,
    'sticky_strike_K177_1113 (Friday surface re-centred on 177; measured skew, not a live price)': d_sticky,
}
base_ann = math.sqrt(d_fri * 252)
for bump in (0.10, 0.20, 0.30):
    cases[f'SCENARIO ATM +{int(bump*100)} vol pts vs Fri 11/13 (not measured)'] = (base_ann + bump) ** 2 / 252
for name, dvar in cases.items():
    sig_td = math.sqrt(dvar)
    row = dict(sigma_per_TD=sig_td, ann_vol_252=sig_td * math.sqrt(252))
    for sl, sh in (('share_1y', share_base), ('share_2y', share_lo), ('share_0.60_newsdriven', share_hi)):
        sig_on = sig_td * math.sqrt(sh)
        row[sl] = dict(share=sh, **six_night(sig_on))
    scen[name] = row

# realised-vol reference row (not implied)
for lab in ('on_sd_last10', 'on_sd_last20'):
    scen[f'REALIZED NVDA overnight sd {lab} (not implied)'] = dict(sigma_on=realized[lab], **six_night(realized[lab]))

# morning check: further drop needed from premarket to reach -9.8% vs Friday close at the 09:31 exit
need = math.log(0.902 * 186.64 / S_NOW)
morning = dict(premarket=S_NOW, level_minus9p8_vs_fri=0.902 * 186.64, further_log_drop_needed=need)
for f in (0.25, 0.5):
    for name in ('fri_close_atm_1113 (pre-news, measured)', 'sticky_strike_K177_1113 (Friday surface re-centred on 177; measured skew, not a live price)'):
        s_on = math.sqrt(cases[name] * share_base)
        s = s_on * math.sqrt(f)
        morning[f'{name[:20]}|frac{f}'] = dict(sigma=s, normal=float(norm.cdf(need / s)),
                                               t3=float(tdist.cdf(need / (s * math.sqrt(1 / 3)), 3)))

# ---------------------------------------------------------------- historical IV reference
h = json.load(open(os.path.join(HERE, 'data_opt_hist_daily.json')))
from datetime import date
def cal_between(d0, d1):
    return (date.fromisoformat(d1) - date.fromisoformat(d0)).days
import numpy as _np
hol = ['2026-11-26']
def td_between(d0, d1):
    days = _np.busday_count(d0, d1, holidays=hol)  # counts d0..d1-1 business days
    return int(days)  # sessions strictly after d0 up to and incl. d1 = busday_count(d0+1, d1+1)
hist = []
for i, d in enumerate(h['dates']):
    S = h['nvda_close'][i]
    row = dict(date=d, spot=S)
    for exp in ('2026-11-20', '2026-12-18'):
        T = cal_between(d, exp) / 365.0
        ntd = int(_np.busday_count(str(np.datetime64(d) + 1), str(np.datetime64(exp) + 1), holidays=hol))
        df = math.exp(-R * T); F = S / df
        ks, ivs = [], []
        for key, px in h[exp].items():
            K = float(key[:-1]); cp = 'call' if key[-1] == 'C' else 'put'
            if (cp == 'call' and K >= S) or (cp == 'put' and K <= S):  # OTM side only
                v = impvol(px[i], F, K, T, df, cp)
                if not np.isnan(v):
                    ks.append(K); ivs.append(v)
        o = np.argsort(ks); ks = np.array(ks)[o]; ivs = np.array(ivs)[o]
        extrap = bool(S < ks.min() or S > ks.max()) if len(ks) else True
        atm = float(np.interp(S, ks, ivs)) if len(ks) else float('nan')
        Vt = atm ** 2 * T
        base = math.sqrt(max(Vt - EB, 0) / (ntd - 1) * 252) if ntd > 1 else float('nan')
        row[exp] = dict(atm_iv=atm, extrapolated=extrap, TD=ntd, ex_earn_base_ann=base,
                        nearest_strikes=[float(k) for k in ks[np.argsort(abs(ks - S))[:2]]])
    hist.append(row)

now_strad = {}
for e in ('2026-11-11', '2026-11-13', '2026-11-16'):
    sig_td_k = math.sqrt(surf[e]['iv_at_K177'] ** 2 * CAL[e] / 365 / TD[e])
    nrem = TD[e] - share_base  # Monday's overnight portion already realised
    now_strad[e] = dict(sigma_per_TD_sticky=sig_td_k, approx_straddle_pct=math.sqrt(2 / math.pi) * sig_td_k * math.sqrt(nrem),
                        approx_straddle_usd=math.sqrt(2 / math.pi) * sig_td_k * math.sqrt(nrem) * S_NOW)
out = dict(now_straddle_sticky_strike_estimate=now_strad, big_drops_le_m5=big_drops, meta=dict(quotes_file=os.path.basename(QFILE), spot_for_quotes=S_Q, spot_now=S_NOW, r=R,
                     note='All option prices are Fri 11/6 16:00 ET closes (pre-news). Options had not traded since. '
                          'Sticky-strike and +vol rows are re-centrings/scenarios, not live market prices.'),
           surface={e: {k: v for k, v in s.items() if k != 'strikes'} for e, s in surf.items()},
           strikes={e: s['strikes'] for e, s in surf.items()},
           event_split=splits, overnight_share=on_share, weekend_factor=wk, nvdl_beta=beta_nvdl,
           empirical_tail=emp_tail, raw_big_drop_freq=raw_freq, realized=realized,
           overnight_scenarios=scen, morning_check=morning, hist_iv=hist)
json.dump(out, open(os.path.join(HERE, 'results.json'), 'w'), indent=1, default=float)

# ---------------------------------------------------------------- print
P = lambda x: f'{100*x:.2f}%'
print(f'spot used for quotes {S_Q}, premarket now {S_NOW}')
print('\nEXPIRY      F       ATM_IV  straddle  strad%S  TD  sig/TD  IV@177  IV@175  IV@180')
for e, s in surf.items():
    print(f"{e} {s['F']:.2f} {P(s['atm_iv']):>8} {s['atm_straddle']:8.2f} {P(s['atm_straddle_pct']):>8} {float(s['TD']):5.2f} {P(s['sigma_per_TD']):>7} {P(s['iv_at_K177']):>7} {P(s['iv_at_K175']):>7} {P(s['iv_at_K180']):>7}")
print('\nEVENT SPLIT'); print(json.dumps(splits, indent=1, default=float))
print('\nOVERNIGHT SHARE'); print(json.dumps(on_share, indent=1, default=float))
print('weekend factor', json.dumps(wk, default=float)); print('NVDL beta', beta_nvdl)
print('\nEMP TAIL', json.dumps(emp_tail, indent=1)); print('RAW FREQ', json.dumps(raw_freq, indent=1)); print('REALIZED', json.dumps(realized, indent=1))
print('\nSCENARIOS')
for k, v in scen.items():
    print('==', k)
    if 'share_1y' in v:
        print(f"   sigma/TD {P(v['sigma_per_TD'])} (ann {P(v['ann_vol_252'])})")
        for sl in ('share_1y', 'share_2y', 'share_0.60_newsdriven'):
            r_ = v[sl]; pn = r_['per_night_probs_weeknight']
            print(f"   {sl} ({r_['share']:.2f}): on-sig {P(r_['per_night_sigma_weeknight'])} wkend {P(r_['weekend_night_sigma'])} 6n {P(r_['cum_6night_sigma'])} | NVDL {P(r_['nvdl_per_night_sigma'])} 6n {P(r_['nvdl_cum_6night_sigma'])}")
            print(f"      1 night P<=-5%: N {P(pn['normal_-5%'])} t4 {P(pn['t4_-5%'])} t3 {P(pn['t3_-5%'])} | P<=-9.8%: N {P(pn['normal_-9.8%'])} t4 {P(pn['t4_-9.8%'])} t3 {P(pn['t3_-9.8%'])}")
            print(f"      any of 6  P<=-5%: N {P(r_['P_any_of_6_normal_-5%'])} t4 {P(r_['P_any_of_6_t4_-5%'])} t3 {P(r_['P_any_of_6_t3_-5%'])} | P<=-9.8%: N {P(r_['P_any_of_6_normal_-9.8%'])} t4 {P(r_['P_any_of_6_t4_-9.8%'])} t3 {P(r_['P_any_of_6_t3_-9.8%'])}")
            print(f"      empirical-z (2015-26 trailing-20 standardized): 1n -5% {P(pn['empz_-5%'])} -9.8% {P(pn['empz_-9.8%'])} | any6 -5% {P(r_['P_any_of_6_empz_-5%'])} -9.8% {P(r_['P_any_of_6_empz_-9.8%'])}")
    else:
        pn = v['per_night_probs_weeknight']
        print(f"   on-sig {P(v['per_night_sigma_weeknight'])} 6n {P(v['cum_6night_sigma'])} NVDL {P(v['nvdl_per_night_sigma'])} | 1n -5%: N {P(pn['normal_-5%'])} t3 {P(pn['t3_-5%'])} | -9.8%: N {P(pn['normal_-9.8%'])} t3 {P(pn['t3_-9.8%'])} | any6 -5% t3 {P(v['P_any_of_6_t3_-5%'])} -9.8% t3 {P(v['P_any_of_6_t3_-9.8%'])}")
print('\nNOW STRADDLE (sticky-strike, NOT live)', json.dumps(now_strad, indent=1))
print('\nBIG DROPS', json.dumps(big_drops))
print('\nMORNING', json.dumps(morning, indent=1, default=float))
print('\nHIST IV (ATM, OTM-side, last-trade closes)')
for r_ in hist:
    a = r_['2026-11-20']; b_ = r_['2026-12-18']
    print(f"{r_['date']} S={r_['spot']:.2f} 11/20 IV {P(a['atm_iv'])}{'*' if a['extrapolated'] else ''} base {P(a['ex_earn_base_ann'])} | 12/18 IV {P(b_['atm_iv'])}{'*' if b_['extrapolated'] else ''} base {P(b_['ex_earn_base_ann'])}")
