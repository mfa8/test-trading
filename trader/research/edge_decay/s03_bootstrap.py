"""Step 3: circular moving-block bootstrap (block 5, 20,000 paths per series, seeded) at 0.86 invested.

Metrics
  streak4_27     P(>=4 consecutive losing nights somewhere in 27 nights)
  bad4_27        P(some 4-night window in 27 nights compounds to <= -9.0% of E)   (severity of the live streak)
  dd9_27         P(drawdown from running peak reaches >= 9% within the first 27 nights)
  pause60_hwm    from E=97.45, HWM=107.11 (DD -9.0%): P(E <= 0.80 x running HWM) within 60 sessions
  pause60_roll20 same start, §6 literal trigger: E <= 0.80 x rolling 20-session high (history seeded from equity.csv)
  pause60_fresh  from a new high (DD 0), P(E <= 0.80 x running HWM within 60) -- compare with RULES_v3 §6 '~30-45%'
  recover60      from E=97.45: P(E >= 107.11 again within 60 sessions)
  kill250_const  from E=97.45: P(E <= 50 within 250 sessions), constant 0.86 exposure (no PAUSE de-risking, no §3(f))
  kill250_rules  same but §6 PAUSE sizing modelled (1 NVDL share ~= $33 while paused, >=5 sessions, rolling-20 trigger)
Return series are per unit exposure, NVDA-earnings nights excluded (rules hold cash on those nights).
"""
import csv, json, os, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
REPO = "/home/user/test-trading/trader"
SEED = 20261016
NP = 20000
BLOCK = int(os.environ.get("BLOCK", "5"))  # sensitivity runs: BLOCK=1 / BLOCK=20
EXPO = 0.86
E_NOW, HWM = 97.45, 107.11
PAUSE_FRAC, KILL = 0.80, 50.0
NVDL_PX = 33.0  # ~1 NVDL share for PAUSE sizing

rows = list(csv.DictReader(open(os.path.join(OUT, "overnight.csv"))))
def col(key, start=None):
    return np.array([float(r[key]) for r in rows if r[key] != "" and r["earn"] == "0" and (start is None or r["date"] >= start)])

nvdl_clean = col("nvdl_clean")
nvdl_raw = col("nvdl_on")
proxy = col("proxy2x")
SERIES = {
    "NVDL_full_2022-12_to_2026-10": nvdl_clean,
    "NVDL_trailing250": nvdl_raw[-250:],
    "PROXY_2xNVDA_2015-2026": proxy,
    "PROXY_2015-2026_recentered_mu0.30": proxy - proxy.mean() + 0.0030,
    "PROXY_2015-2026_recentered_mu0": proxy - proxy.mean(),
}

# rolling-20 history seed: last 19 EOD equities from equity.csv (10/12 replaced by state HWM 107.11) + current E
eq = [(r["et"][:10], float(r["E_broker"])) for r in csv.DictReader(open(os.path.join(REPO, "equity.csv")))]
hist = [v for d, v in eq if d >= "2026-09-09"][-19:]
hist = [HWM if abs(v - 107.02) < 1e-9 else v for v in hist] + [E_NOW]
assert len(hist) == 20


def paths(r, H, rng):
    N = len(r)
    nb = math.ceil(H / BLOCK)
    starts = rng.integers(0, N, size=(NP, nb))
    idx = (starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % N
    return r[idx.reshape(NP, nb * BLOCK)[:, :H]]


def max_run_neg(x):
    neg = x < 0
    run = np.zeros(x.shape[0], int); best = np.zeros(x.shape[0], int)
    for k in range(x.shape[1]):
        run = np.where(neg[:, k], run + 1, 0)
        best = np.maximum(best, run)
    return best


def first27(r, rng):
    x = EXPO * paths(r, 27, rng)
    eqp = np.cumprod(1 + x, axis=1)
    peak = np.maximum.accumulate(np.concatenate([np.ones((NP, 1)), eqp], axis=1), axis=1)[:, 1:]
    dd = eqp / peak - 1
    lg = np.log1p(x)
    c4 = np.exp(np.lib.stride_tricks.sliding_window_view(lg, 4, axis=1).sum(-1)) - 1
    return dict(streak4_27=float((max_run_neg(x) >= 4).mean()),
                streak4_27_ending_at_27=float((x[:, -4:] < 0).all(1).mean()),
                bad4_27_le_m9pct=float((c4.min(1) <= -0.09).mean()),
                dd9_27=float((dd.min(1) <= -0.09).mean()),
                median_maxdd_27_pct=round(100 * float(np.median(dd.min(1))), 2))


def from_now(r, H, rng, rules=False, start_E=E_NOW, start_hwm=HWM, roll_hist=None):
    """Simulate H sessions. Returns dict of first-passage indicators."""
    rr = paths(r, H, rng)
    E = np.full(NP, start_E, float)
    hwm = np.full(NP, start_hwm, float)
    ring = np.tile(np.array(roll_hist if roll_hist is not None else [start_hwm] * 19 + [start_E], float), (NP, 1))
    hit_hwm = np.zeros(NP, bool); hit_roll = np.zeros(NP, bool); rec = np.zeros(NP, bool); dead = np.zeros(NP, bool)
    paused = np.zeros(NP, bool); pcount = np.zeros(NP, int)
    for k in range(H):
        expo = np.full(NP, EXPO)
        if rules:
            expo = np.where(paused, np.minimum(0.98, NVDL_PX / E), EXPO)
        E = np.where(dead, E, E * (1 + expo * rr[:, k]))
        hwm = np.maximum(hwm, E)
        ring[:, k % 20] = E  # overwrite oldest (ring seeded with 20 values; position k%20 is the oldest)
        rhigh = ring.max(1)
        hit_hwm |= E <= PAUSE_FRAC * hwm
        trig = E <= PAUSE_FRAC * rhigh
        hit_roll |= trig
        rec |= E >= HWM
        if rules:
            newp = (~paused) & trig
            pcount = np.where(paused, pcount + 1, 0)
            unp = paused & (pcount >= 5) & (~trig)
            paused = (paused | newp) & ~unp
            pcount = np.where(newp, 0, pcount)
        dead |= E <= KILL
    return dict(hit_hwm=float(hit_hwm.mean()), hit_roll=float(hit_roll.mean()), recover=float(rec.mean()),
                kill=float(dead.mean()), E_median=round(float(np.median(E)), 2),
                E_p05=round(float(np.percentile(E, 5)), 2), E_p95=round(float(np.percentile(E, 95)), 2))


res = dict(params=dict(seed=SEED, paths=NP, block=BLOCK, exposure=EXPO, E_now=E_NOW, HWM=HWM,
                       pause_level=round(PAUSE_FRAC * HWM, 2), kill=KILL, roll20_seed_hist=hist), series={})
for name, r in SERIES.items():
    rng = np.random.default_rng(SEED)
    out = dict(n_nights=len(r), mean_pct=round(100 * r.mean(), 4), sd_pct=round(100 * r.std(ddof=1), 3),
               win_pct=round(100 * (r > 0).mean(), 1))
    out.update(first27(r, rng))
    a = from_now(r, 60, rng, roll_hist=hist)
    out.update(pause60_hwm=a["hit_hwm"], pause60_roll20=a["hit_roll"], recover60=a["recover"],
               E60_median=a["E_median"], E60_p05=a["E_p05"])
    f = from_now(r, 60, rng, start_E=100.0, start_hwm=100.0)
    out.update(pause60_fresh=f["hit_hwm"], pause60_fresh_roll20=f["hit_roll"])
    k = from_now(r, 250, rng, roll_hist=hist)
    out.update(kill250_const=k["kill"], E250_median_const=k["E_median"], E250_p05_const=k["E_p05"])
    k2 = from_now(r, 250, rng, rules=True, roll_hist=hist)
    out.update(kill250_rules=k2["kill"], E250_median_rules=k2["E_median"])
    res["series"][name] = out
    print(name, json.dumps(out))

# Monte-Carlo standard error for a probability p with 20k paths: sqrt(p(1-p)/20000) <= 0.0035
res["mc_se_max"] = round(math.sqrt(0.25 / NP), 4)

# iid analytic sanity check for the streak: P(>=4 losses in a row in 27) with p_loss from NVDL full
def p_run(n, k, q):
    # DP over current run length
    dp = np.zeros(k); dp[0] = 1.0; hit = 0.0
    for _ in range(n):
        nd = np.zeros(k)
        nd[0] = dp.sum() * (1 - q)
        for j in range(k - 1):
            nd[j + 1] += dp[j] * q
        hit += dp[k - 1] * q
        dp = nd
    return hit
for name in ("NVDL_full_2022-12_to_2026-10", "PROXY_2xNVDA_2015-2026"):
    q = float((SERIES[name] < 0).mean())
    res["series"][name]["iid_streak4_27_analytic"] = round(p_run(27, 4, q), 4)

json.dump(res, open(os.path.join(OUT, "bootstrap.json" if BLOCK == 5 else f"bootstrap_block{BLOCK}.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
