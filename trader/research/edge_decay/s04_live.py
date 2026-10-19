"""Step 4: live 27-night record vs the planning edge (+0.25..0.35%/night gross per unit exposure).
Reads (read-only): trader/state.json, trader/trades.csv, trader/equity.csv.
Per night: pnl (from fills: sum (exit-entry)*qty), invested (sum entry*qty), E_entry (equity.csv 16:02 EOD on entry date).
"""
import csv, json, os, math
import numpy as np

REPO = "/home/user/test-trading/trader"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
state = json.load(open(os.path.join(REPO, "state.json")))
nr = state["campaign"]["night_returns"]

eq = {}
for r in csv.DictReader(open(os.path.join(REPO, "equity.csv"))):
    eq[r["et"][:10]] = float(r["E_broker"])

tr = {}
for line in csv.reader(open(os.path.join(REPO, "trades.csv"))):
    if not line or not line[0].startswith("T3X-N"):
        continue
    nid, d, sym = line[0], line[1], line[2]
    px_in, qty, px_out = float(line[8]), int(line[9]), float(line[13])
    t = tr.setdefault(d, dict(id=nid, legs=[], pnl=0.0, inv=0.0))
    t["legs"].append(f"{sym}x{qty}")
    t["pnl"] += (px_out - px_in) * qty
    t["inv"] += px_in * qty

nights = []
for n in nr:
    d = n["date"]
    t = tr.get(d)
    E = eq.get(d)
    nights.append(dict(date=d, basket=n["basket"], pnl_state=n["pnl"], pct_state=n["pct"],
                       pnl_fills=round(t["pnl"], 3) if t else None, invested=round(t["inv"], 2) if t else None,
                       E_entry=E,
                       ret_E=100 * t["pnl"] / E if (t and E) else None,
                       ret_unit=100 * t["pnl"] / t["inv"] if t else None,
                       expo=t["inv"] / E if (t and E) else None,
                       nvda2x_only=n["basket"].startswith("NVDX") or n["basket"].startswith("NVDL x2 + NVDX")))


def st(x):
    x = np.asarray(x, float); n = len(x); m = x.mean(); sd = x.std(ddof=1) if n > 1 else float("nan")
    return dict(n=n, mean=round(m, 4), sd=round(sd, 3), t_vs0=round(m / (sd / math.sqrt(n)), 2) if n > 1 else None,
                win=round(100 * (x > 0).mean(), 1))


ru = [x["ret_unit"] for x in nights]
rE = [x["ret_E"] for x in nights]
ex = [x["expo"] for x in nights]
res = dict(n=len(nights),
           sum_pnl_fills=round(sum(x["pnl_fills"] for x in nights), 2),
           sum_pnl_state=round(sum(x["pnl_state"] for x in nights), 2),
           mean_exposure=round(float(np.mean(ex)), 3), exposure_range=[round(min(ex), 3), round(max(ex), 3)],
           per_unit=st(ru), on_E=st(rE),
           compound_on_E_pct=round(100 * (np.prod(1 + np.array(rE) / 100) - 1), 2),
           nvda2x_only_nights=[(x["date"], round(x["ret_unit"], 2)) for x in nights if x["nvda2x_only"]],
           last4=[(x["date"], x["basket"], x["pnl_fills"], round(x["ret_E"], 2), round(x["ret_unit"], 2)) for x in nights[-4:]])

# z-scores vs planning edge (per unit exposure). SE from (a) live sd, (b) model sd = NVDL trailing-250 ex-earn sd 2.661
SD_MODEL = 2.661
z = {}
m = res["per_unit"]["mean"]; sd = res["per_unit"]["sd"]; n = res["n"]
for edge in (0.25, 0.30, 0.35, 0.0):
    z[f"edge_{edge}"] = dict(z_live_sd=round((m - edge) / (sd / math.sqrt(n)), 2),
                             z_model_sd=round((m - edge) / (SD_MODEL / math.sqrt(n)), 2))
# same on-E basis: planning edge x actual mean exposure
mE = res["on_E"]["mean"]; sdE = res["on_E"]["sd"]
for edge in (0.25, 0.30, 0.35):
    e = edge * res["mean_exposure"]
    z[f"onE_edge_{edge}x{res['mean_exposure']}"] = dict(edge_on_E=round(e, 3), z_live_sd=round((mE - e) / (sdE / math.sqrt(n)), 2))
res["z"] = z
# power: nights needed to tell +0.30 from 0 at t=2 with sd 2.66
res["nights_needed_t2_for_0.30_edge"] = round((2 * SD_MODEL / 0.30) ** 2)
res["SE_of_27_night_mean_model_sd"] = round(SD_MODEL / math.sqrt(27), 3)
res["nights"] = [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in x.items()} for x in nights]

# live equity path / drawdown from equity.csv EOD + current
path = [(d, v) for d, v in sorted(eq.items()) if d >= "2026-09-09"] + [("2026-10-16 09:31", state["account"]["equity"])]
pk = -1; mdd = 0
for d, v in path:
    pk = max(pk, v); mdd = min(mdd, v / pk - 1)
res["eod_path_maxdd_pct"] = round(100 * mdd, 2)
hwm = state["campaign"]["equity_hwm"]; E = state["account"]["equity"]
res["dd_from_state_hwm_pct"] = round(100 * (E / hwm - 1), 2)
res["pause_level_0.8xHWM"] = round(0.8 * hwm, 2)
json.dump(res, open(os.path.join(OUT, "live.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "nights"}, indent=1))
for x in nights:
    print(x["date"], x["basket"][:26].ljust(26), x["pnl_state"], round(x["pnl_fills"], 2), x["invested"], x["E_entry"],
          round(x["ret_E"], 2), round(x["ret_unit"], 2), x["pct_state"], round(x["expo"], 3))
