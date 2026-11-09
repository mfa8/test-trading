#!/usr/bin/env python3
"""Post-hoc (hand-tagged) set: non-earnings NVDA gaps <= -4% whose cause was verified (web) as NVDA-specific
news, regardless of QQQ (NVDA is ~8-10% of QQQ and moves peers, so a pure QQQ filter drops real
company-specific nights such as the 2025-04-15 H20 charge). POST-HOC SELECTION -> descriptive only.
Uses panel.csv built by build.py; forward metrics defined exactly as in stats.py.
"""
import csv, json, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(1109)
P = [r for r in csv.DictReader(open(os.path.join(HERE, "panel.csv"))) if r["next"]]
oc = {r["date"]: float(r["nvda_oc"]) for r in csv.DictReader(open(os.path.join(HERE, "panel.csv")))}
dates = [r["date"] for r in P]; idx = {d: i for i, d in enumerate(dates)}
on = np.array([float(r["nvda_on"]) for r in P]); earn = np.array([int(r["earn"]) for r in P])
q = np.array([float(r["qqq_on"]) for r in P])
acct = np.where(earn == 1, 0.0, on)

TAGS = {  # night date (close) : (cause, source URL)
    "2017-02-22": ("Nomura/Instinet downgrade after hours 2/22 (BMO followed 2/23)", "https://www.cnbc.com/2017/02/23/nvidia-shares-drop-to-three-month-low-after-downgrade.html"),
    "2017-04-03": ("Pacific Crest downgrade to Underweight", "https://www.cnbc.com/2017/04/04/sell-chipmaker-nvidia-because-demand-going-from-bad-to-worse.html"),
    "2019-01-25": ("Q4 FY19 revenue pre-announcement cut (China/crypto), before 1/28 open", "https://www.bnnbloomberg.ca/nvidia-sinks-after-warning-on-revenue-especially-in-china-1.1204973"),
    "2022-08-05": ("Q2 FY23 revenue pre-announcement miss, before 8/8 open", "https://www.fool.com/investing/2022/08/08/why-nvidia-stock-slumped-on-monday/"),
    "2022-08-31": ("8-K: US licence requirement on A100/H100 exports to China", "https://www.cnbc.com/2022/08/31/nvidia-stock-falls-after-us-government-restricts-chip-sales-to-china.html"),
    "2023-10-16": ("US Commerce tightened AI-chip export rules to China (10/17 am)", "https://www.techspot.com/news/100689-us-export-restrictions-could-cost-nvidia-5-billion.html"),
    "2025-04-15": ("8-K: H20 China export licence, ~$5.5B charge (after close 4/15)", "https://www.rte.ie/news/business/2025/0416/1507904-nvidia-faces-5-5-billion-charge-as-us-restricts-sales"),
    "2025-11-24": ("The Information: Meta in talks to use Google TPUs", "https://finance.yahoo.com/news/nvidia-stock-falls-after-report-says-google-meta-in-talks-for-multibillion-dollar-ai-chip-deal-143725770.html"),
}
EXTRA = {
    "2016-12-28": ("follow-through gap the morning after Citron's 12/28 intraday short call (cause of the 12/29 gap itself UNVERIFIED)", "https://www.cnbc.com/2016/12/28/nvidia-shares-fall-sharply-after-short-seller-citron-research-tweets.html"),
    "2008-07-02": ("Q2 FY09 revenue warning + $150-200M faulty-chip charge (after close 7/2)", "https://fortune.com/2008/07/03/miss-by-chipmaker-nvidia-rattles-investors"),
}
CHINA_POLICY = ["2022-08-31", "2023-10-16", "2025-04-15"]


def fw(k):
    w = on[k + 1:k + 11][earn[k + 1:k + 11] == 0]
    return dict(night=dates[k], gap_open=P[k]["next"], nvda_on=on[k], qqq_on=q[k], oc0=oc[P[k]["next"]],
                on1=acct[k + 1], sum5=acct[k + 1:k + 6].sum(), sum10=acct[k + 1:k + 11].sum(),
                further5=float((w <= -0.05).any()), min10=float(w.min()))


pool = [k for k in range(len(P) - 11) if earn[k] == 0 and dates[k] >= "2015-01-01"]
U = {m: np.array([fw(k)[m] for k in pool]) for m in ("oc0", "on1", "sum5", "sum10", "further5")}


def summarize(ds, label):
    rows = [fw(idx[d]) for d in ds]
    out = {"label": label, "n": len(rows), "events": rows, "metrics": {}}
    for m in ("oc0", "on1", "sum5", "sum10", "further5"):
        e = np.array([r[m] for r in rows]); u = U[m]
        se = e.std(ddof=1) / math.sqrt(len(e)) if len(e) > 1 else float("nan")
        t = (e.mean() - u.mean()) / math.sqrt(se ** 2 + (u.std(ddof=1) / math.sqrt(len(u))) ** 2) if len(e) > 1 else float("nan")
        bs = rng.choice(e, size=(20000, len(e))).mean(axis=1)
        out["metrics"][m] = dict(mean=e.mean(), median=float(np.median(e)), sd=float(e.std(ddof=1)) if len(e) > 1 else None,
                                 neg=int((e < 0).sum()), boot95=(float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))),
                                 uncond_2015_2026=float(u.mean()), welch_t=t)
    return out


res = {
    "news_verified_2015_2026": summarize(sorted(TAGS), "verified NVDA-specific news, 2015-2026"),
    "news_verified_plus_extras": summarize(sorted(list(TAGS) + list(EXTRA)), "+ 2016-12-28 follow-through + 2008-07-02"),
    "china_us_policy": summarize(CHINA_POLICY, "US/China export-policy nights"),
    "tags": {**TAGS, **EXTRA},
}
json.dump(res, open(os.path.join(HERE, "out", "newsset.json"), "w"), indent=1, default=float)
for k in ("news_verified_2015_2026", "news_verified_plus_extras", "china_us_policy"):
    r = res[k]
    print(f"\n== {r['label']} n={r['n']}")
    for e in r["events"]:
        print(f"  {e['night']}->{e['gap_open']} gap {100*e['nvda_on']:+.2f} qqq {100*e['qqq_on']:+.2f} | oc0 {100*e['oc0']:+.2f} on1 {100*e['on1']:+.2f} s5 {100*e['sum5']:+.2f} s10 {100*e['sum10']:+.2f} f5 {e['further5']:.0f} min10 {100*e['min10']:+.2f}")
    for m, d in r["metrics"].items():
        print(f"  {m:8s} mean {100*d['mean']:+.2f} med {100*d['median']:+.2f} neg {d['neg']}/{r['n']} boot95 [{100*d['boot95'][0]:+.2f},{100*d['boot95'][1]:+.2f}] uncond {100*d['uncond_2015_2026']:+.2f} t {d['welch_t']:+.2f}")
