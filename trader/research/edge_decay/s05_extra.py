"""Step 5: p-values for the live-vs-plan z, paired live-vs-NVDL-model gap over the 27 live nights,
and NVDA overnight vs intraday split for the review week (entries 10/09..10/15)."""
import csv, json, os, math
import numpy as np
from scipy import stats as ss

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
live = json.load(open(os.path.join(OUT, "live.json")))
rows = {r["date"]: r for r in csv.DictReader(open(os.path.join(OUT, "overnight.csv")))}
res = {}
m, sd, n = live["per_unit"]["mean"], live["per_unit"]["sd"], live["n"]
for edge in (0.25, 0.30, 0.35):
    z = (m - edge) / (sd / math.sqrt(n))
    res[f"vs_{edge}"] = dict(z=round(z, 2), p_one_sided_t26=round(float(ss.t.cdf(z, n - 1)), 3))
res["vs_0"] = dict(t=round(m / (sd / math.sqrt(n)), 2), p_two_sided=round(float(2 * ss.t.cdf(-abs(m / (sd / math.sqrt(n))), n - 1)), 3))
res["live_mean_ci90_per_unit"] = [round(m - ss.t.ppf(0.95, n - 1) * sd / math.sqrt(n), 3), round(m + ss.t.ppf(0.95, n - 1) * sd / math.sqrt(n), 3)]

# paired: live per-unit return minus NVDL model overnight (close->open) on the same entry date
d = []
for x in live["nights"]:
    mod = 100 * float(rows[x["date"]]["nvdl_on"])
    d.append((x["date"], x["basket"], round(x["ret_unit"], 2), round(mod, 2), round(x["ret_unit"] - mod, 2)))
diff = np.array([e[4] for e in d])
res["live_minus_NVDLmodel"] = dict(mean=round(diff.mean(), 3), sd=round(diff.std(ddof=1), 3),
                                    t=round(diff.mean() / (diff.std(ddof=1) / math.sqrt(len(diff))), 2),
                                    nvda2x_only_nights=[e for e in d if e[0] >= "2026-10-13"])
res["per_night_live_vs_model"] = d

# review week: NVDA overnight vs intraday (entries 10/09 -> 10/15; open of 10/16 from 1-min bar)
bars = json.load(open(os.path.join(HERE, "data", "nvdl_nvda_day_2022.json")))
nv = {b["begins_at"][:10]: b for r in bars["data"]["results"] if r["symbol"] == "NVDA" for b in r["bars"]}
days = ["2026-10-09", "2026-10-12", "2026-10-13", "2026-10-14", "2026-10-15"]
on, intra = [], []
for i, t in enumerate(days):
    nxt_open = float(nv[days[i + 1]]["open_price"]) if i + 1 < len(days) else 216.53
    on.append(nxt_open / float(nv[t]["close_price"]) - 1)
    if i + 1 < len(days):
        intra.append(float(nv[days[i + 1]]["close_price"]) / float(nv[days[i + 1]]["open_price"]) - 1)
res["NVDA_week_overnight_pct"] = [round(100 * x, 2) for x in on[1:]]
res["NVDA_week_overnight_compound_pct(10/12..10/15 entries)"] = round(100 * (np.prod(1 + np.array(on[1:])) - 1), 2)
res["NVDA_week_intraday_pct(10/13..10/15)"] = [round(100 * x, 2) for x in intra[1:]]
res["NVDA_week_intraday_compound_pct"] = round(100 * (np.prod(1 + np.array(intra[1:])) - 1), 2)
json.dump(res, open(os.path.join(OUT, "extra.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "per_night_live_vs_model"}, indent=1))
