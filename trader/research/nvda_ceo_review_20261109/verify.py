#!/usr/bin/env python3
"""Independent re-derivation (verifier). Reads freshly pulled Robinhood day bars (v_*.json in this dir),
repo overnight CSV for 2015+ earnings flags, and (for pre-2015 only) the stream's heuristic flag list.
Writes nothing outside this directory."""
import json, os, csv, math, random, statistics as st
H = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/user/test-trading/trader/research/edge_decay/overnight_thru_20261106.csv"
FLAGS = os.path.join(H, "..", "earnings_flags.json")

bars = {"NVDA": {}, "QQQ": {}}
for fn in ("v_1999_2014.json", "v_2015_2026.json"):
    d = json.load(open(os.path.join(H, fn)))
    for x in d["data"]["results"]:
        for b in x["bars"]:
            if b.get("interpolated"):
                continue
            bars[x["symbol"]][b["begins_at"][:10]] = (float(b["open_price"]), float(b["close_price"]),
                                                     float(b["high_price"]), float(b["low_price"]), float(b["volume"]))
dates = sorted(set(bars["NVDA"]) & set(bars["QQQ"]))
N, Q = bars["NVDA"], bars["QQQ"]
print("sessions", len(dates), dates[0], dates[-1])

repo = {r["date"]: r for r in csv.DictReader(open(REPO))}
earn15 = {d for d, r in repo.items() if r["earn"] == "1"}
fl = json.load(open(FLAGS))
earnpre = set(fl["earn_heuristic_pre2015"])
assert set(fl["earn_list_2015plus"]) == earn15, "flag list mismatch"
EARN = earn15 | earnpre

# nights
rows = []
for i in range(len(dates) - 1):
    t, n = dates[i], dates[i + 1]
    on = N[n][0] / N[t][1] - 1
    qon = Q[n][0] / Q[t][1] - 1
    oc_next = N[n][1] / N[n][0] - 1  # gap-day open->close
    rows.append(dict(t=t, n=n, on=on, qon=qon, oc=oc_next, earn=(t in EARN)))
idx = {r["t"]: k for k, r in enumerate(rows)}

# repo cross-check
mx = 0; cnt = 0; big = 0
for r in rows:
    if r["t"] in repo and repo[r["t"]]["nvda_on"] != "":
        dlt = abs(r["on"] - float(repo[r["t"]]["nvda_on"]))
        mx = max(mx, dlt); cnt += 1; big += dlt > 1e-4
print(f"repo cross-check: {cnt} nights, max |diff| {mx*1e4:.2f}bp, >1bp: {big}")


def fwd(k):
    """metrics for night index k (event night)."""
    if k + 10 >= len(rows):
        return None
    r1 = rows[k + 1]
    on1 = r1["on"]
    s5 = sum(0 if rows[k + j]["earn"] else rows[k + j]["on"] for j in range(1, 6))
    s10 = sum(0 if rows[k + j]["earn"] else rows[k + j]["on"] for j in range(1, 11))
    fur = any((not rows[k + j]["earn"]) and rows[k + j]["on"] <= -0.05 for j in range(1, 11))
    return dict(oc=rows[k]["oc"], on1=on1, on1_earn=r1["earn"], s5=s5, s10=s10, fur=fur)


def welch(a, b):
    ma, mb = st.mean(a), st.mean(b)
    va = st.variance(a) if len(a) > 1 else float("nan")
    vb = st.variance(b)
    se = math.sqrt(va / len(a) + vb / len(b))
    return (ma - mb) / se


def boot(a, B=20000, seed=1):
    rnd = random.Random(seed)
    ms = sorted(st.mean(rnd.choices(a, k=len(a))) for _ in range(B))
    return ms[int(0.025 * B)], ms[int(0.975 * B)]


def wilson(x, n, z=1.96):
    p = x / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def binom_ge(x, n, p):
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(x, n + 1))


def run(lo, hi, label, qfilter=True, thr=-0.04):
    pool = [k for k, r in enumerate(rows) if lo <= r["t"] <= hi and not r["earn"]]
    poolm = [fwd(k) for k in pool]
    poolm = [m for m in poolm if m]
    ev = [k for k in pool if rows[k]["on"] <= thr and (not qfilter or rows[k]["qon"] >= -0.005)]
    em = [(rows[k]["t"], fwd(k)) for k in ev if fwd(k)]
    print(f"\n=== {label} {lo}..{hi} qfilter={qfilter}: pool {len(pool)} non-earn nights; events {len(ev)} (with fwd {len(em)})")
    if len(ev) <= 25:
        print("   dates:", [rows[k]["t"] for k in ev])
    out = {}
    for key in ("oc", "on1", "s5", "s10"):
        a = [m[key] for _, m in em]
        b = [m[key] for m in poolm]
        lo_, hi_ = boot(a)
        t = welch(a, b)
        pos = sum(1 for x in a if x > 0)
        print(f"  {key:4s} ev mean {st.mean(a)*100:+.2f}% med {st.median(a)*100:+.2f} pos {pos}/{len(a)} CI[{lo_*100:+.2f},{hi_*100:+.2f}]  uncond {st.mean(b)*100:+.3f}% sd {st.pstdev(b)*100:.2f} pos {sum(1 for x in b if x>0)/len(b)*100:.0f}%  welch t {t:+.2f}")
        out[key] = (st.mean(a), t)
    a = [abs(m["on1"]) for _, m in em]; b = [abs(m["on1"]) for m in poolm]
    print(f"  |on1| ev {st.mean(a)*100:.2f}% vs {st.mean(b)*100:.2f}% ratio {st.mean(a)/st.mean(b):.2f} t {welch(a,b):.2f}")
    for cut in (-0.03, -0.051):
        x = sum(1 for _, m in em if m["on1"] <= cut); n = len(em)
        p0 = sum(1 for m in poolm if m["on1"] <= cut) / len(poolm)
        print(f"  on1<={cut*100:.1f}%: {x}/{n} uncond {p0*100:.2f}% binom p(>=x) {binom_ge(x,n,p0):.4f} wilson {tuple(round(v*100,1) for v in wilson(x,n))}")
    x = sum(1 for _, m in em if m["fur"]); n = len(em)
    p0 = sum(1 for m in poolm if m["fur"]) / len(poolm)
    print(f"  further<=-5% in 10: {x}/{n} uncond {p0*100:.2f}% binom p {binom_ge(x,n,p0):.4f} wilson {tuple(round(v*100,1) for v in wilson(x,n))}")
    print("  on1 earn flags among events:", sum(1 for _, m in em if m["on1_earn"]))
    if len(em) <= 25:
        for d, m in em:
            print(f"    {d} gap {rows[idx[d]]['on']*100:+.2f} qqq {rows[idx[d]]['qon']*100:+.2f} oc {m['oc']*100:+.2f} on1 {m['on1']*100:+.2f} s5 {m['s5']*100:+.2f} s10 {m['s10']*100:+.2f} fur {int(m['fur'])}")
    return em, poolm


if __name__ == "__main__":
    for lo in ("2015-01-01", "2005-01-01", "1999-01-01"):
        run(lo, "2026-12-31", "IDIO")
        run(lo, "2026-12-31", "ALL", qfilter=False)
    # count non-earn 2015-2026 nights
    p15 = [r for r in rows if r["t"] >= "2015-01-01" and not r["earn"]]
    print("\nnon-earn nights 2015-2026:", len(p15), "first", rows[0]["t"])
