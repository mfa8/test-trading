"""Step 2: mean / sd / t of overnight returns over full, trailing-250, trailing-120 windows,
the RULES_v3 §3(f) edge-decay value (trailing-120 NVDL overnight mean, NVDA earnings nights excluded),
and the NVDL model path over the 27 live nights (2026-09-09 .. 2026-10-15 entries).
All returns in % per night per unit exposure.
"""
import csv, json, os, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
rows = list(csv.DictReader(open(os.path.join(OUT, "overnight.csv"))))
for r in rows:
    for k in ("nvda_on", "nvdl_on", "nvdl_clean", "proxy2x"):
        r[k] = float(r[k]) if r[k] != "" else None
    r["earn"] = int(r["earn"])


def stats(x):
    x = np.asarray(x, float) * 100
    n = len(x)
    m = x.mean(); sd = x.std(ddof=1)
    t = m / (sd / math.sqrt(n))
    return dict(n=n, mean=round(m, 4), sd=round(sd, 3), t=round(t, 2), win=round(100 * (x > 0).mean(), 1),
                worst=round(x.min(), 2), best=round(x.max(), 2),
                ci90=[round(m - 1.645 * sd / math.sqrt(n), 3), round(m + 1.645 * sd / math.sqrt(n), 3)])


def series(key, ex_earn=True, start=None, end=None):
    out = []
    for r in rows:
        if r[key] is None:
            continue
        if ex_earn and r["earn"]:
            continue
        if start and r["date"] < start:
            continue
        if end and r["date"] > end:
            continue
        out.append((r["date"], r[key]))
    return out


res = {}
for key, label in (("nvdl_on", "NVDL_raw"), ("nvdl_clean", "NVDL_clean"), ("proxy2x", "PROXY_2xNVDA_4bp")):
    for ex in (True, False):
        s = series(key, ex)
        v = [x for _, x in s]
        tag = f"{label}_{'exEarn' if ex else 'allNights'}"
        res[tag] = dict(span=[s[0][0], s[-1][0]],
                        full=stats(v), trailing250=stats(v[-250:]), trailing120=stats(v[-120:]),
                        trailing60=stats(v[-60:]))
# proxy on NVDL's own span (apples-to-apples with NVDL)
s = series("proxy2x", True, start="2022-12-13")
res["PROXY_2xNVDA_4bp_exEarn_NVDLspan"] = dict(span=[s[0][0], s[-1][0]], full=stats([x for _, x in s]))

# proxy by calendar year (regime context)
years = {}
for d, x in series("proxy2x", True):
    years.setdefault(d[:4], []).append(x)
res["PROXY_by_year_exEarn"] = {y: dict(n=len(v), mean=round(100 * np.mean(v), 3), sd=round(100 * np.std(v, ddof=1), 2),
                                       compound_pct=round(100 * (np.prod(1 + np.array(v)) - 1), 1))
                               for y, v in sorted(years.items())}

# §3(f) edge-decay: trailing-120 NVDL overnight mean ex NVDA-earnings nights.
# Variant A: last 120 non-earnings nights. Variant B: last 120 nights, earnings nights dropped (n<=120).
def w120(asof, key="nvdl_on"):
    ok = [r for r in rows if r[key] is not None and r["date"] <= asof]
    a = [r[key] for r in ok if not r["earn"]][-120:]
    b = [r[key] for r in ok[-120:] if not r["earn"]]
    return dict(asof_last_entry_night=asof, A_last120_nonearn=stats(a), B_last120_minus_earn=stats(b))

decay = {}
decay["now_through_night_2026-10-15"] = w120("2026-10-15")
decay["clean_now"] = w120("2026-10-15", "nvdl_clean")
decay["as_of_Mon_2026-10-12_check(nights<=10-09)"] = w120("2026-10-09")
# break-even: what single next-night return would push variant A to <= 0 (window drops oldest night)
nonearn = [r["nvdl_on"] for r in rows if r["nvdl_on"] is not None and not r["earn"]]
last119 = nonearn[-119:]
decay["breakeven_next_night_pct_to_flip_A"] = round(-100 * sum(last119), 2)
# history of trailing-120 (variant A) over the last 257 nights and over the whole NVDL life
ne = [(r["date"], r["nvdl_on"]) for r in rows if r["nvdl_on"] is not None and not r["earn"]]
roll = [(ne[i][0], 100 * np.mean([x for _, x in ne[i - 119:i + 1]])) for i in range(119, len(ne))]
last257 = roll[-257:]
decay["W120_min_last257"] = [last257[int(np.argmin([v for _, v in last257]))][0], round(min(v for _, v in last257), 3)]
decay["W120_min_life"] = [roll[int(np.argmin([v for _, v in roll]))][0], round(min(v for _, v in roll), 3)]
decay["W120_frac_nights_le0_life"] = round(float(np.mean([v <= 0 for _, v in roll])), 3)
decay["W120_last10"] = [(d, round(v, 3)) for d, v in roll[-10:]]
# proxy (2x NVDA) trailing-120 now, and how often <= 0 since 2015
pne = [(r["date"], r["proxy2x"]) for r in rows if not r["earn"]]
proll = [100 * np.mean([x for _, x in pne[i - 119:i + 1]]) for i in range(119, len(pne))]
decay["proxy_W120_now"] = round(proll[-1], 3)
decay["proxy_W120_frac_le0_since2015"] = round(float(np.mean([v <= 0 for v in proll])), 3)
res["edge_decay_3f"] = decay

# NVDL model path over the live window (entry dates 2026-09-09 .. 2026-10-15)
lw = [(r["date"], r["nvdl_on"]) for r in rows if "2026-09-09" <= r["date"] <= "2026-10-15"]
res["NVDL_model_over_live_27"] = dict(n=len(lw), stats=stats([x for _, x in lw]),
                                       compound_pct_unit=round(100 * (np.prod([1 + x for _, x in lw]) - 1), 2),
                                       compound_pct_at_0p86=round(100 * (np.prod([1 + 0.86 * x for _, x in lw]) - 1), 2),
                                       last5=[(d, round(100 * x, 2)) for d, x in lw[-5:]])
# How unusual is the NVDA-2x model's last 4 nights (10/12-10/15) relative to history? (4-night compounded)
v = np.array([r["nvdl_on"] for r in rows if r["nvdl_on"] is not None and not r["earn"]])
c4 = np.array([np.prod(1 + v[i:i + 4]) - 1 for i in range(len(v) - 3)])
last4 = np.prod(1 + np.array([x for _, x in lw[-4:]])) - 1
res["NVDL_4night_compound"] = dict(last4_pct=round(100 * last4, 2), pct_rank=round(100 * float(np.mean(c4 <= last4)), 1))

json.dump(res, open(os.path.join(OUT, "stats.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
