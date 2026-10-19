"""Step 6: collect key numbers from out/*.json into out/key_numbers.json (no new computation)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
L = lambda f: json.load(open(os.path.join(OUT, f)))
st, bt, lv, ex, pr = L("stats.json"), L("bootstrap.json"), L("live.json"), L("extra.json"), L("prep_summary.json")
b1, b20 = L("bootstrap_block1.json"), L("bootstrap_block20.json")
k = {}
for tag in ("NVDL_raw_exEarn", "NVDL_clean_exEarn", "PROXY_2xNVDA_4bp_exEarn"):
    for w in ("full", "trailing250", "trailing120"):
        s = st[tag][w]; k[f"{tag}.{w}"] = dict(n=s["n"], mean_pct=s["mean"], sd_pct=s["sd"], t=s["t"], win=s["win"])
k["NVDL_raw_allNights.full"] = {x: st["NVDL_raw_allNights"]["full"][x] for x in ("n", "mean", "sd", "t")}
k["PROXY_by_year_mean_pct"] = {y: v["mean"] for y, v in st["PROXY_by_year_exEarn"].items()}
d = st["edge_decay_3f"]
k["edge_decay_W120_now"] = dict(raw=d["now_through_night_2026-10-15"]["A_last120_nonearn"]["mean"],
                                raw_t=d["now_through_night_2026-10-15"]["A_last120_nonearn"]["t"],
                                clean=d["clean_now"]["A_last120_nonearn"]["mean"],
                                variantB_raw=d["now_through_night_2026-10-15"]["B_last120_minus_earn"]["mean"],
                                as_of_10_09=d["as_of_Mon_2026-10-12_check(nights<=10-09)"]["A_last120_nonearn"]["mean"],
                                sign="POSITIVE", breakeven_next_night_pct=d["breakeven_next_night_pct_to_flip_A"],
                                min_last257=d["W120_min_last257"], min_life=d["W120_min_life"],
                                frac_le0_life=d["W120_frac_nights_le0_life"], proxy_now=d["proxy_W120_now"],
                                proxy_frac_le0_since2015=d["proxy_W120_frac_le0_since2015"])
k["bootstrap_block5_0.86"] = {n: {x: v[x] for x in ("streak4_27", "bad4_27_le_m9pct", "dd9_27", "median_maxdd_27_pct",
                                                    "pause60_hwm", "pause60_roll20", "pause60_fresh", "recover60",
                                                    "kill250_const", "kill250_rules", "iid_streak4_27_analytic") if x in v}
                              for n, v in bt["series"].items()}
k["bootstrap_block_sensitivity"] = {f"block{b}": {n: dict(dd9_27=v["dd9_27"], pause60_hwm=v["pause60_hwm"], kill250_const=v["kill250_const"])
                                                  for n, v in r["series"].items()} for b, r in ((1, b1), (20, b20))}
k["live"] = dict(n=lv["n"], mean_per_unit=lv["per_unit"]["mean"], sd_per_unit=lv["per_unit"]["sd"], t_vs0=lv["per_unit"]["t_vs0"],
                 mean_on_E=lv["on_E"]["mean"], mean_exposure=lv["mean_exposure"], sum_pnl=lv["sum_pnl_fills"],
                 ci90_per_unit=ex["live_mean_ci90_per_unit"], z=ex, dd_from_hwm=lv["dd_from_state_hwm_pct"],
                 nights_needed_t2=lv["nights_needed_t2_for_0.30_edge"])
k["NVDL_model_same_27_nights"] = st["NVDL_model_over_live_27"]
k["NVDL_last4_compound"] = st["NVDL_4night_compound"]
json.dump(k, open(os.path.join(OUT, "key_numbers.json"), "w"), indent=1)
print(json.dumps(k["bootstrap_block5_0.86"], indent=0)); print(k["edge_decay_W120_now"])
