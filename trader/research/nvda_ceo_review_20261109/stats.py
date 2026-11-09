#!/usr/bin/env python3
"""NVDA idiosyncratic overnight gap-downs: what happens next?

Night k = close(t_k) -> open(t_k+1).  Event night k: earn==0, nvda_on <= GAP, (idio: qqq_on >= QMIN).
Forward metrics for event night k (all NVDA 1x, split-adjusted RH daily bars):
  oc0    : open->close of the gap day t_k+1 (the day the gap opens)
  on1    : next overnight = night k+1 (close t_k+1 -> open t_k+2)   [the 15:52->09:31 hold the account would take
           on the gap day]; if night k+1 is an NVDA earnings night it is set to 0 (account in cash) -- flagged
  sum5 / sum10 : sum of nights k+1..k+5 / k+1..k+10 (earnings nights zeroed)
  further5 : 1 if any non-earnings night in k+1..k+10 has nvda_on <= -5%
Unconditional = same metric computed from every non-earnings night k in the same sample.
Tests: Welch t (event vs unconditional), bootstrap 95% CI of event mean and of difference,
random-date Monte Carlo p (n nights drawn from the unconditional pool), vol-matched baseline (trailing 60-night
sd of non-earnings nvda_on, quintiles), binomial/Wilson for further5; plus episode de-duplication (events within
10 nights of an earlier event dropped).
"""
import csv, json, math, os, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261109)

P = list(csv.DictReader(open(os.path.join(HERE, "panel.csv"))))
P = [r for r in P if r["next"]]  # nights with a known next open (through 2026-11-05 -> 11-06)
for r in P:
    for k in ("nvda_on", "qqq_on", "nvda_oc", "qqq_oc"):
        r[k] = float(r[k])
    r["earn"] = int(r["earn"]); r["near_heur"] = int(r["near_heur"])
# intraday return of the day the gap opens (= day 'next'); map date->oc
oc_by_date = {r["date"]: r["nvda_oc"] for r in csv.DictReader(open(os.path.join(HERE, "panel.csv")))}
oc_by_date = {k: float(v) for k, v in oc_by_date.items()}
n_all = len(P)
on = np.array([r["nvda_on"] for r in P]); q = np.array([r["qqq_on"] for r in P])
earn = np.array([r["earn"] for r in P]); near = np.array([r["near_heur"] for r in P])
dates = [r["date"] for r in P]; nxt = [r["next"] for r in P]
on_acct = np.where(earn == 1, 0.0, on)  # account in cash on earnings nights

# trailing 60-night sd of non-earnings overnight returns (known at close t_k, i.e. uses nights < k)
tvol = np.full(n_all, np.nan)
buf = []
for k in range(n_all):
    if len(buf) >= 40:
        tvol[k] = np.std(buf[-60:], ddof=1)
    if earn[k] == 0:
        buf.append(on[k])


def fwd(k):
    """forward metrics for night k (requires k+10 < n_all for 10-night metrics)."""
    d = {}
    d["oc0"] = oc_by_date.get(nxt[k], np.nan)  # gap-day open->close
    d["on1"] = on_acct[k + 1] if k + 1 < n_all else np.nan
    d["on1_is_earn"] = int(earn[k + 1]) if k + 1 < n_all else 0
    d["sum5"] = on_acct[k + 1:k + 6].sum() if k + 5 < n_all else np.nan
    d["sum10"] = on_acct[k + 1:k + 11].sum() if k + 10 < n_all else np.nan
    if k + 10 < n_all:
        w = on[k + 1:k + 11][earn[k + 1:k + 11] == 0]
        d["further5"] = float((w <= -0.05).any())
        d["further4"] = float((w <= -0.04).any())
        d["min10"] = float(w.min()) if len(w) else np.nan
    else:
        d["further5"] = d["further4"] = d["min10"] = np.nan
    d["on1_le_m3"] = float(d["on1"] <= -0.03) if not np.isnan(d["on1"]) else np.nan
    d["on1_le_m5"] = float(d["on1"] <= -0.05) if not np.isnan(d["on1"]) else np.nan
    d["on1_le_m51"] = float(d["on1"] <= -0.051) if not np.isnan(d["on1"]) else np.nan
    d["on1_pos"] = float(d["on1"] > 0) if not np.isnan(d["on1"]) else np.nan
    d["abs_on1"] = abs(d["on1"]) if not np.isnan(d["on1"]) else np.nan
    return d


F = [fwd(k) for k in range(n_all)]
METRICS = ["oc0", "on1", "sum5", "sum10", "further5", "further4", "on1_le_m3", "on1_le_m5", "on1_le_m51",
           "on1_pos", "abs_on1", "min10"]
FM = {m: np.array([f[m] for f in F], dtype=float) for m in METRICS}

# vol quintile per night (within sample computed later)


def wilson(x, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = x / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def binom_two_sided(x, n, p0):
    from math import comb
    pr = [comb(n, i) * p0 ** i * (1 - p0) ** (n - i) for i in range(n + 1)]
    return min(1.0, sum(v for v in pr if v <= pr[x] * (1 + 1e-9)))


def analyse(ev_idx, pool_idx, label, B=10000):
    res = {"label": label, "n_events": len(ev_idx), "n_pool": len(pool_idx), "metrics": {}}
    pool_idx = np.array(pool_idx); ev_idx = np.array(ev_idx)
    # vol quintiles over the pool
    pv = tvol[pool_idx]
    okv = ~np.isnan(pv)
    qs = np.quantile(pv[okv], [0.2, 0.4, 0.6, 0.8])
    def vq(k):
        return int(np.searchsorted(qs, tvol[k])) if not np.isnan(tvol[k]) else -1
    pool_q = np.array([vq(k) for k in pool_idx])
    ev_q = np.array([vq(k) for k in ev_idx])
    res["event_vol_quintiles"] = {int(i): int((ev_q == i).sum()) for i in range(-1, 5)}
    for m in METRICS:
        e = FM[m][ev_idx]; e = e[~np.isnan(e)]
        u_all = FM[m][pool_idx]; u_mask = ~np.isnan(u_all); u = u_all[u_mask]
        if len(e) == 0:
            continue
        me, mu = e.mean(), u.mean()
        se_e = e.std(ddof=1) / math.sqrt(len(e)) if len(e) > 1 else np.nan
        se_u = u.std(ddof=1) / math.sqrt(len(u))
        welch = (me - mu) / math.sqrt(se_e ** 2 + se_u ** 2) if len(e) > 1 else np.nan
        bs = rng.choice(e, size=(B, len(e)), replace=True).mean(axis=1)
        ci = (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))
        # random-date MC: n draws from pool (without replacement)
        draws = np.array([rng.choice(u, size=len(e), replace=False).mean() for _ in range(B)])
        p_mc = float((np.abs(draws - mu) >= abs(me - mu) - 1e-15).mean())
        p_lo = float((draws <= me + 1e-15).mean())  # one-sided: event mean this low or lower by chance
        # vol-matched baseline: for each event draw from same trailing-vol quintile
        pool_by_q = {i: FM[m][pool_idx[(pool_q == i)]] for i in range(5)}
        pool_by_q = {i: v[~np.isnan(v)] for i, v in pool_by_q.items()}
        evq = np.array([vq(k) for k in ev_idx[~np.isnan(FM[m][ev_idx])]])
        valid = evq >= 0
        if valid.sum() > 0:
            base_vm = float(np.mean([pool_by_q[i].mean() for i in evq[valid]]))
            vm_draws = np.zeros(B)
            for i in evq[valid]:
                vm_draws += rng.choice(pool_by_q[i], size=B, replace=True)
            vm_draws /= valid.sum()
            e_valid = e[valid] if len(e) == len(evq) else e
            p_vm = float((np.abs(vm_draws - base_vm) >= abs(e_valid.mean() - base_vm) - 1e-15).mean())
        else:
            base_vm, p_vm = np.nan, np.nan
        d = dict(n=int(len(e)), mean=float(me), median=float(np.median(e)), sd=float(e.std(ddof=1)) if len(e) > 1 else None,
                 min=float(e.min()), max=float(e.max()), hit_pos=float((e > 0).mean()),
                 boot95_mean=ci, uncond_n=int(len(u)), uncond_mean=float(mu), uncond_median=float(np.median(u)),
                 uncond_sd=float(u.std(ddof=1)), diff=float(me - mu), welch_t=float(welch),
                 boot95_diff=(ci[0] - mu, ci[1] - mu), p_randomdate_2s=p_mc, p_randomdate_low_1s=p_lo,
                 volmatched_baseline=base_vm, p_volmatched_2s=p_vm)
        if m in ("further5", "further4", "on1_le_m3", "on1_le_m5", "on1_le_m51", "on1_pos"):
            x = int(e.sum()); n = len(e)
            d["count"] = x; d["wilson95"] = wilson(x, n)
            d["binom_p_vs_uncond"] = binom_two_sided(x, n, mu)
            d["binom_p_vs_volmatched"] = binom_two_sided(x, n, base_vm) if not np.isnan(base_vm) else None
        res["metrics"][m] = d
    return res


def episodes(ev_idx, gap=10):
    out, last = [], -10 ** 9
    for k in sorted(ev_idx):
        if k - last > gap:
            out.append(k)
            last = k
    return out


SAMPLES = {
    "2015_2026_exact": lambda k: dates[k] >= "2015-01-01",
    "2005_2026_heur": lambda k: dates[k] >= "2005-01-01",
    "2005_2026_heur_conservative": lambda k: dates[k] >= "2005-01-01" and near[k] == 0,
    "1999_2026_heur": lambda k: True,
    "2020_2026_recent": lambda k: dates[k] >= "2020-01-01",
}
# event definitions: (gap threshold, qqq floor or None, exclude preann?)
DEFS = {
    "IDIO_le4_qqq_ge_m05": (-0.04, -0.005, False),
    "IDIO_le4_qqq_ge_m05_noPreann": (-0.04, -0.005, True),
    "IDIO_le5_qqq_ge_m05": (-0.05, -0.005, False),
    "ALL_le4": (-0.04, None, False),
    "ALL_le4_noPreann": (-0.04, None, True),
    "ALL_le5": (-0.05, None, False),
    # robustness: NVDA is ~8-10% of QQQ, so its own gap drags QQQ; relative-gap definition
    "REL_le4_minus_qqq_le4": (-0.04, "rel", False),
}

results = {}
event_tables = {}
for sname, sfun in SAMPLES.items():
    pool = [k for k in range(n_all - 1) if sfun(k) and earn[k] == 0]
    for dname, (g, qmin, nopre) in DEFS.items():
        if qmin == "rel":
            ev = [k for k in pool if on[k] <= g and on[k] - q[k] <= -0.04]
        else:
            ev = [k for k in pool if on[k] <= g and (qmin is None or q[k] >= qmin) and (not nopre or not P[k]["preann"])]
        key = f"{sname}|{dname}"
        results[key] = analyse(ev, pool, key)
        ep = episodes(ev)
        results[key + "|episodes"] = analyse(ep, pool, key + "|episodes")
        event_tables[key] = ev

# ---- event tables for the main definitions ----
def write_events(key, fn):
    ev = event_tables[key]
    with open(os.path.join(OUT, fn), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["night_date", "gap_open_date", "gapdays", "nvda_on", "qqq_on", "rel_on", "nvda_close", "trail60_sd",
                    "oc0_gapday", "on1_next", "on1_is_earn", "sum5", "sum10", "further5", "min10", "near_heur", "preann",
                    "episode_first"])
        ep = set(episodes(ev))
        from datetime import date
        for k in ev:
            f_ = F[k]
            gd = (date.fromisoformat(nxt[k]) - date.fromisoformat(dates[k])).days
            w.writerow([dates[k], nxt[k], gd, f"{on[k]:.5f}", f"{q[k]:.5f}", f"{on[k]-q[k]:.5f}", P[k]["nvda_c"],
                        f"{tvol[k]:.4f}", f"{f_['oc0']:.5f}", f"{f_['on1']:.5f}", f_["on1_is_earn"],
                        f"{f_['sum5']:.5f}", f"{f_['sum10']:.5f}", f_["further5"], f"{f_['min10']:.5f}",
                        near[k], P[k]["preann"], int(k in ep)])

write_events("1999_2026_heur|IDIO_le4_qqq_ge_m05", "events_idio_le4_1999_2026.csv")
write_events("1999_2026_heur|ALL_le4", "events_all_le4_1999_2026.csv")
write_events("2015_2026_exact|IDIO_le4_qqq_ge_m05", "events_idio_le4_2015_2026.csv")
write_events("2015_2026_exact|ALL_le4", "events_all_le4_2015_2026.csv")
write_events("1999_2026_heur|REL_le4_minus_qqq_le4", "events_rel_le4_1999_2026.csv")

json.dump(results, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=float)

# ---- compact summary ----
lines = []
def pct(x):
    return "nan" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{100*x:+.2f}"
for key, r in results.items():
    lines.append(f"\n=== {key}  n_events={r['n_events']} pool={r['n_pool']} volQ={r['event_vol_quintiles']}")
    for m in ("oc0", "on1", "sum5", "sum10", "further5", "on1_le_m5", "abs_on1"):
        if m not in r["metrics"]:
            continue
        d = r["metrics"][m]
        if m in ("further5", "on1_le_m5"):
            lines.append(f"  {m:9s} n={d['n']:3d} rate={d['mean']:.3f} ({d['count']}/{d['n']}) wilson=[{d['wilson95'][0]:.3f},{d['wilson95'][1]:.3f}] "
                         f"uncond={d['uncond_mean']:.3f} volmatched={d['volmatched_baseline']:.3f} binom_p={d['binom_p_vs_uncond']:.3f} "
                         f"binom_p_vm={d['binom_p_vs_volmatched']:.3f}")
        else:
            lines.append(f"  {m:9s} n={d['n']:3d} mean={pct(d['mean'])} med={pct(d['median'])} sd={pct(d['sd'])} boot95=[{pct(d['boot95_mean'][0])},{pct(d['boot95_mean'][1])}] "
                         f"uncond={pct(d['uncond_mean'])} (sd {pct(d['uncond_sd'])}) diff={pct(d['diff'])} t={d['welch_t']:+.2f} "
                         f"p_rand={d['p_randomdate_2s']:.3f} vm_base={pct(d['volmatched_baseline'])} p_vm={d['p_volmatched_2s']:.3f} win={d['hit_pos']:.2f}")
open(os.path.join(OUT, "summary.txt"), "w").write("\n".join(lines))
print("\n".join(lines))
