#!/usr/bin/env python3
"""Build a daily NVDA/QQQ panel with overnight returns and earnings flags.

Inputs (read-only):
  data/rh_day_1999_2014.json, data/rh_day_2015_2026.json  -- Robinhood get_equity_historicals,
      interval=day, adjustment=split, bounds=regular, symbols NVDA,QQQ (pulled 2026-11-09 ~08:00 ET)
  /home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv  -- repo nights
      (earn flag = exact NVDA earnings nights 2015-2026; preann flag)
Output:
  panel.csv : one row per trading day t (non-interpolated bars only)
     date, nvda_o,h,l,c,v, qqq_o,c, next = next trading date,
     nvda_on = open(t+1)/close(t)-1, qqq_on likewise, nvda_oc = close(t)/open(t)-1 (intraday of day t),
     earn = 1 if night t->t+1 is an NVDA earnings night, earn_src (list|heuristic|''),
     near_heur = 1 if pre-2015 and within +-3 sessions of a heuristic earnings date, preann text
"""
import json, os, statistics as st, csv
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_CSV = "/home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv"

bars = {"NVDA": {}, "QQQ": {}}
for fn in ("rh_day_1999_2014.json", "rh_day_2015_2026.json"):
    d = json.load(open(os.path.join(HERE, "data", fn)))
    for x in d["data"]["results"]:
        for b in x["bars"]:
            if b.get("interpolated"):
                continue
            bars[x["symbol"]][b["begins_at"][:10]] = dict(
                o=float(b["open_price"]), h=float(b["high_price"]), l=float(b["low_price"]),
                c=float(b["close_price"]), v=float(b["volume"]))
dates = sorted(set(bars["NVDA"]) & set(bars["QQQ"]))
miss = sorted(set(bars["NVDA"]) ^ set(bars["QQQ"]))
print("sessions", len(dates), dates[0], dates[-1], "symbol-mismatch dates:", miss[:10])
idx = {d: i for i, d in enumerate(dates)}
N = bars["NVDA"]

# ---- repo nights (exact earnings flags 2015+) ----
repo = {}
with open(REPO_CSV) as f:
    for r in csv.DictReader(f):
        repo[r["date"]] = r
EARN_LIST = {d for d, r in repo.items() if r["earn"] == "1"}
PREANN = {d: r["preann"] for d, r in repo.items() if r["preann"]}


# ---- heuristic earnings dates pre-2015 (same method as week9/q1: max next-day volume ratio
#      vs median of prior 20 sessions, within Feb(>=3)/May/Aug/Nov) ----
def volratio(i):
    if i < 21 or i + 1 >= len(dates):
        return None
    m = st.median(N[dates[j]]["v"] for j in range(i - 20, i))
    return N[dates[i + 1]]["v"] / m


def heuristic(years):
    out = {}
    for y in years:
        for m in (2, 5, 8, 11):
            sc = []
            for d in dates:
                if int(d[:4]) == y and int(d[5:7]) == m and int(d[8:10]) >= 3:
                    i = idx[d]
                    vr = volratio(i)
                    if vr is None:
                        continue
                    gap = abs(N[dates[i + 1]]["o"] / N[d]["c"] - 1)
                    sc.append((vr, gap, d))
            if sc:
                out[(y, m)] = max(sc)
    return out


hv = heuristic(range(2015, 2027))
known = {(int(e[:4]), int(e[5:7])): e for e in EARN_LIST}
hit = sum(1 for k, v in hv.items() if k in known and v[2] == known[k])
tot = sum(1 for k in hv if k in known)
print(f"heuristic validation 2015-2026: {hit}/{tot} exact")
hpre = heuristic(range(1999, 2015))
EARN_H = {v[2] for v in hpre.values()}
prior = json.load(open("/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/week9/q1/earnings_dates.json"))
pl = set(prior["earn_heuristic_pre2015"])
mine05 = {d for d in EARN_H if d >= "2005"}
print("pre-2015 heuristic vs week9/q1 list (2005-2014): same=", len(mine05 & pl), "only mine=", sorted(mine05 - pl), "only prior=", sorted(pl - mine05))
heur_idx = sorted(idx[d] for d in EARN_H)

rows = []
for i, d in enumerate(dates[:-1]):
    n = dates[i + 1]
    a, b = N[d], N[n]
    q, qn = bars["QQQ"][d], bars["QQQ"][n]
    if d >= "2015-01-01":
        earn = 1 if d in EARN_LIST else 0
        src = "list" if earn else ""
        near = 0
    else:
        earn = 1 if d in EARN_H else 0
        src = "heuristic" if earn else ""
        near = 1 if any(abs(i - j) <= 3 for j in heur_idx) else 0
    rows.append(dict(date=d, next=n, nvda_o=a["o"], nvda_h=a["h"], nvda_l=a["l"], nvda_c=a["c"], nvda_v=a["v"],
                     qqq_o=q["o"], qqq_c=q["c"],
                     nvda_on=b["o"] / a["c"] - 1, qqq_on=qn["o"] / q["c"] - 1,
                     nvda_oc=a["c"] / a["o"] - 1, qqq_oc=q["c"] / q["o"] - 1,
                     earn=earn, earn_src=src, near_heur=near, preann=PREANN.get(d, "")))
# last day (2026-11-06): no next open yet; keep intraday only
d = dates[-1]
rows.append(dict(date=d, next="", nvda_o=N[d]["o"], nvda_h=N[d]["h"], nvda_l=N[d]["l"], nvda_c=N[d]["c"], nvda_v=N[d]["v"],
                 qqq_o=bars["QQQ"][d]["o"], qqq_c=bars["QQQ"][d]["c"], nvda_on="", qqq_on="",
                 nvda_oc=N[d]["c"] / N[d]["o"] - 1, qqq_oc=bars["QQQ"][d]["c"] / bars["QQQ"][d]["o"] - 1,
                 earn=0, earn_src="", near_heur=0, preann=""))

# ---- cross-check vs repo nvda_on and earn flags ----
diffs = []
for r in rows:
    if r["date"] in repo and r["nvda_on"] != "":
        diffs.append((abs(r["nvda_on"] - float(repo[r["date"]]["nvda_on"])), r["date"]))
        assert r["next"] == repo[r["date"]]["next"], (r["date"], r["next"], repo[r["date"]]["next"])
diffs.sort(reverse=True)
print("repo cross-check: nights", len(diffs), "max |diff| bp", round(diffs[0][0] * 1e4, 2), diffs[0][1],
      "n>1bp", sum(1 for x in diffs if x[0] > 1e-4))
missing_repo = [d for d in repo if d not in idx]
print("repo nights missing from panel:", missing_repo[:5])

with open(os.path.join(HERE, "panel.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
json.dump(dict(earn_list_2015plus=sorted(EARN_LIST), earn_heuristic_pre2015=sorted(EARN_H),
               heuristic_validation_2015_2026=f"{hit}/{tot}", preann=PREANN),
          open(os.path.join(HERE, "earnings_flags.json"), "w"), indent=1)
print("wrote panel.csv rows", len(rows))
