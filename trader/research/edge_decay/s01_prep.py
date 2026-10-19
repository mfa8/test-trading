"""Week-6 drawdown-consistency study, step 1: build overnight return series.

Overnight return for date t = open(t+1)/close(t) - 1 (entry close t, exit next open),
labelled by the entry date t (same convention as state.json night_returns).

Inputs (read-only):
  data/nvdl_nvda_day_2022.json   get_equity_historicals NVDL,NVDA day from 2022-12-01 (split-adjusted)
  data/nvda_day_2015_2022.json   get_equity_historicals NVDA day 2015-01-01..2022-12-01
  data/open_20261016.json        10/16 opens from first 1-min bar
  /home/user/test-trading/trader/research/daily_1y_20261012.json  (cross-check only)
Outputs:
  out/overnight.csv   date, nvda_on, nvdl_on, nvdl_on_clean, proxy2x, earn, flags
  out/prep_summary.json
"""
import json, csv, os, statistics as st
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
REPO_RESEARCH = "/home/user/test-trading/trader/research"

# NVDA report dates (after the close) -> the overnight hold that starts at that close is the earnings night.
# 2025-11-19, 2026-02-25, 2026-05-20, 2026-08-26 are confirmed in research/VERIFY-V15 + IDLE-CAPITAL docs;
# 2023-05-24 confirmed via get_earnings_calendar (NVDA, pm, verified). Others: public record, cross-checked
# below against next-day volume spikes and gaps.
EARN = """2015-02-11 2015-05-07 2015-08-06 2015-11-05
2016-02-17 2016-05-12 2016-08-11 2016-11-10
2017-02-09 2017-05-09 2017-08-10 2017-11-09
2018-02-08 2018-05-10 2018-08-16 2018-11-15
2019-02-14 2019-05-16 2019-08-15 2019-11-14
2020-02-13 2020-05-21 2020-08-19 2020-11-18
2021-02-24 2021-05-26 2021-08-18 2021-11-17
2022-02-16 2022-05-25 2022-08-24 2022-11-16
2023-02-22 2023-05-24 2023-08-23 2023-11-21
2024-02-21 2024-05-22 2024-08-28 2024-11-20
2025-02-26 2025-05-28 2025-08-27 2025-11-19
2026-02-25 2026-05-20 2026-08-26""".split()
EARN = set(EARN)
# Pre-market pre-announcements (not scheduled earnings; kept in the sample, flagged only)
PROXY_DRAG = 0.0004  # NVDL - 2x NVDA overnight, ex-earn: 2024 -4.7bp mean, 2025 -1.6, 2026 -2.4 (see s01 output)
PREANN = {"2019-01-25": "NVDA pre-announced Q4 miss before 01-28 open", "2022-08-05": "NVDA pre-announced Q2 miss before 08-08 open"}


def load_bars(path):
    d = json.load(open(path))
    out = {}
    for r in d["data"]["results"]:
        rows = {}
        for b in r["bars"]:
            if b.get("interpolated"):
                continue
            dt = b["begins_at"][:10]
            rows[dt] = dict(o=float(b["open_price"]), c=float(b["close_price"]), v=float(b["volume"]))
        out[r["symbol"]] = rows
    return out


a = load_bars(os.path.join(DATA, "nvda_day_2015_2022.json"))
b = load_bars(os.path.join(DATA, "nvdl_nvda_day_2022.json"))
nvda = dict(a["NVDA"]); nvda.update(b["NVDA"])
nvdl = dict(b["NVDL"])
op16 = json.load(open(os.path.join(DATA, "open_20261016.json")))
nvda["2026-10-16"] = dict(o=op16["NVDA"], c=float("nan"), v=float("nan"))
nvdl["2026-10-16"] = dict(o=op16["NVDL"], c=float("nan"), v=float("nan"))

# overlap consistency check on 2022-12-01 (both files contain it)
chk_overlap = (a["NVDA"].get("2022-12-01"), b["NVDA"].get("2022-12-01"))

dates = sorted(nvda)
rows = []
for i in range(len(dates) - 1):
    t, t1 = dates[i], dates[i + 1]
    r_a = nvda[t1]["o"] / nvda[t]["c"] - 1
    r_l = None
    if t in nvdl and t1 in nvdl:
        r_l = nvdl[t1]["o"] / nvdl[t]["c"] - 1
    gapdays = (date.fromisoformat(t1) - date.fromisoformat(t)).days
    rows.append(dict(date=t, next=t1, nvda_on=r_a, nvdl_on=r_l, gapdays=gapdays,
                     earn=int(t in EARN), preann=PREANN.get(t, "")))

# --- earnings cross-check: next-day volume ratio vs trailing 20-day median, and |gap| rank in quarter window
vol = [nvda[d]["v"] for d in dates]
idx = {d: i for i, d in enumerate(dates)}
earn_check = []
for e in sorted(EARN):
    if e not in idx:
        earn_check.append(dict(date=e, status="NOT A TRADING DAY IN DATA"))
        continue
    i = idx[e]
    if i + 1 >= len(dates) or i < 21:
        earn_check.append(dict(date=e, status="edge"))
        continue
    med = st.median(vol[i - 20:i])
    vr = vol[i + 1] / med
    # in a +-10 trading-day window, which day has the max next-day volume ratio?
    best, bestd = 0, None
    for j in range(max(21, i - 10), min(len(dates) - 1, i + 11)):
        m2 = st.median(vol[j - 20:j])
        r = vol[j + 1] / m2
        if r > best:
            best, bestd = r, dates[j]
    gap = nvda[dates[i + 1]]["o"] / nvda[e]["c"] - 1
    earn_check.append(dict(date=e, next_day_vol_ratio=round(vr, 2), nvda_gap_pct=round(100 * gap, 2),
                           window_max_vol_day=bestd, agrees=(bestd == e)))
mism = [x for x in earn_check if x.get("agrees") is False]

# --- NVDL vs 2x NVDA overnight: drag estimate and outlier flags (distributions / bad prints)
pairs = [r for r in rows if r["nvdl_on"] is not None]
diffs = [r["nvdl_on"] - 2 * r["nvda_on"] for r in pairs if not r["earn"]]
drag_mean = st.mean(diffs)
drag_median = st.median(diffs)
flags = []
for r in pairs:
    d = r["nvdl_on"] - 2 * r["nvda_on"]
    r["nvdl_minus_2x"] = d
    if abs(d) > 0.01:
        flags.append(dict(date=r["date"], next=r["next"], nvdl=round(100 * r["nvdl_on"], 3),
                          two_x_nvda=round(200 * r["nvda_on"], 3), diff=round(100 * d, 3), earn=r["earn"]))

# Clean NVDL series: on flagged nights (|NVDL - 2x NVDA| > 1%) replace NVDL by 2x NVDA + median drag
# (stand-in for "distribution added back / first-trade open"); unflagged nights unchanged.
for r in rows:
    r["proxy2x"] = 2 * r["nvda_on"] - PROXY_DRAG  # 2x NVDA overnight minus fixed 4bp/night drag (prior-review convention)
    if r["nvdl_on"] is None:
        r["nvdl_clean"] = None
    elif abs(r["nvdl_on"] - 2 * r["nvda_on"]) > 0.01:
        r["nvdl_clean"] = 2 * r["nvda_on"] + drag_median
    else:
        r["nvdl_clean"] = r["nvdl_on"]

# cross-check against the saved research file (NVDL 2025-10-01..2026-10-09)
sv = load_bars(os.path.join(REPO_RESEARCH, "daily_1y_20261012.json"))["NVDL"]
mx = 0
for d0, v in sv.items():
    if d0 in nvdl:
        mx = max(mx, abs(v["c"] - nvdl[d0]["c"]), abs(v["o"] - nvdl[d0]["o"]))

with open(os.path.join(OUT, "overnight.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "next", "gapdays", "earn", "preann", "nvda_on", "nvdl_on", "nvdl_clean", "proxy2x"])
    for r in rows:
        w.writerow([r["date"], r["next"], r["gapdays"], r["earn"], r["preann"], f"{r['nvda_on']:.6f}",
                    "" if r["nvdl_on"] is None else f"{r['nvdl_on']:.6f}",
                    "" if r["nvdl_clean"] is None else f"{r['nvdl_clean']:.6f}", f"{r['proxy2x']:.6f}"])

summ = dict(
    nvda_first=dates[0], nvda_last_close=dates[-2], n_nvda_nights=len(rows),
    nvdl_first=min(nvdl), n_nvdl_nights=len(pairs),
    overlap_2022_12_01_identical=chk_overlap[0] == chk_overlap[1],
    max_abs_price_diff_vs_saved_research_file=round(mx, 6),
    earnings_nights_in_nvda_sample=sum(r["earn"] for r in rows),
    earnings_nights_in_nvdl_sample=sum(r["earn"] for r in pairs),
    earnings_crosscheck_mismatches=mism,
    earnings_crosscheck=earn_check,
    nvdl_minus_2x_nvda_overnight_ex_earn_bp=dict(mean=round(1e4 * drag_mean, 2), median=round(1e4 * drag_median, 2)),
    nvdl_flagged_nights_gt_1pct=flags,
    last_night=rows[-1],
)
json.dump(summ, open(os.path.join(OUT, "prep_summary.json"), "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in summ.items() if k != "earnings_crosscheck"}, indent=1, default=str))
