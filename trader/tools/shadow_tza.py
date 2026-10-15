#!/usr/bin/env python3
"""§11 v1.7 TZA day-leg shadow log (no orders).
usage: shadow_tza.py YYYY-MM-DD BARS.json
BARS.json: list of 1-minute bars (get_equity_historicals interval=5minute is NOT valid; use 1-minute),
or the raw tool response containing them. Times are converted to America/New_York.
entry = OHLC4(09:32 bar) x 1.0002; TP = ceil(entry x 1.010); TP fills only on trade-through
(high >= TP + 0.01); otherwise exit at the close of the 15:48 bar. Prints one JSON line."""
import json, math, sys
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")


def find_bars(o):
    if isinstance(o, list) and o and isinstance(o[0], dict) and "begins_at" in o[0]:
        return o
    if isinstance(o, dict):
        for v in o.values():
            r = find_bars(v)
            if r:
                return r
    if isinstance(o, list):
        for v in o:
            r = find_bars(v)
            if r:
                return r
    return None


def main():
    day, path = sys.argv[1], sys.argv[2]
    bars = find_bars(json.load(open(path))) or []
    f = lambda b, k: float(b[k + "_price"])
    by = {}
    for b in bars:
        t = datetime.fromisoformat(b["begins_at"].replace("Z", "+00:00")).astimezone(ET)
        if t.strftime("%Y-%m-%d") == day:
            by[t.strftime("%H:%M")] = b
    e0 = by.get("09:32")
    if not e0:
        print(json.dumps({"date": day, "status": "no 09:32 bar", "n_bars": len(by)}))
        return
    entry = round((f(e0, "open") + f(e0, "high") + f(e0, "low") + f(e0, "close")) / 4 * 1.0002, 4)
    tp = math.ceil(entry * 1.010 * 100) / 100
    exit_px, how, at, last = None, None, None, None
    for hm in sorted(by):
        if hm < "09:33" or hm > "15:48":
            continue
        b = by[hm]
        if f(b, "high") >= tp + 0.01:
            exit_px, how, at = tp, "tp", hm
            break
        last = (hm, b)
    if exit_px is None:
        if not last or last[0] != "15:48":
            print(json.dumps({"date": day, "status": "incomplete (no 15:48 bar)", "entry": entry, "tp": tp,
                              "last_bar": last[0] if last else None}))
            return
        exit_px, how, at = f(last[1], "close"), "close", "15:48"
    ret = exit_px / entry - 1
    print(json.dumps({"date": day, "sym": "TZA", "entry": entry, "tp": tp, "exit": exit_px, "how": how,
                      "at": at, "ret_pct": round(ret * 100, 3), "ret_net015_pct": round((ret - 0.0015) * 100, 3)}))


if __name__ == "__main__":
    main()
