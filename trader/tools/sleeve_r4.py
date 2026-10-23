#!/usr/bin/env python3
"""RULES_v3 §12(e) R4 contract selection for the FFB-L options sleeve (shadow or live).
usage: sleeve_r4.py E S EXPIRY K:bid:ask [K:bid:ask ...]
  E = account equity (R2 valuation), S = NVDA last, EXPIRY = YYYY-MM-DD (3rd-Friday monthly, 70<=DTE<=150).
  Quotes are call bid/ask per strike for that expiry. Prints the spread-mode pick (W=$10) and the
  L2 call-mode pick, plus every candidate considered, as one JSON line."""
import sys, json, math

def up(x):
    return math.ceil(round(x * 100, 6)) / 100

def main():
    E, S, exp = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    q = {}
    for a in sys.argv[4:]:
        k, b, ak = a.split(':')
        q[float(k)] = (float(b), float(ak))
    F, B = 80.0, min(0.20 * E, E - 80.0)
    W = 10.0 if 150 <= S <= 300 else None
    out = {"E": E, "S": S, "expiry": exp, "B": round(B, 2), "sleeps": B < 8, "spread": None, "call": None, "cands": []}
    if W:
        for k1 in sorted(k for k in q if k >= S):
            k2 = k1 + W
            if k2 not in q:
                continue
            b1, a1 = q[k1]; b2, a2 = q[k2]
            mid = (b1 + a1) / 2 - (b2 + a2) / 2
            nat = a1 - b2
            L0 = up(mid + 0.25 * (nat - mid))
            ok = (100 * L0 + 0.10 <= B) and L0 > 0 and (W / L0 >= 4) and b1 > 0 and (nat - mid <= max(0.06, 0.5 * mid))
            c = {"K1": k1, "K2": k2, "mid": round(mid, 3), "nat": round(nat, 3), "L0": L0, "cost": round(100 * L0 + 0.10, 2),
                 "W_L0": round(W / L0, 1) if L0 > 0 else None, "ok": ok}
            out["cands"].append(c)
            if ok and out["spread"] is None:
                c2 = dict(c); c2["Lmax"] = min(round(nat, 2), math.floor((B - 0.10)) / 100)
                out["spread"] = c2
    for k in sorted(k for k in q if k >= S):
        b, a = q[k]
        mid = (b + a) / 2
        L0 = up(mid + 0.25 * (a - mid))
        if b > 0 and (a - b) <= max(0.03, 0.5 * mid) and 100 * L0 + 0.05 <= B:
            out["call"] = {"K": k, "bid": b, "ask": a, "L0": L0, "cost": round(100 * L0 + 0.05, 2)}
            break
    print(json.dumps(out))

if __name__ == "__main__":
    main()
