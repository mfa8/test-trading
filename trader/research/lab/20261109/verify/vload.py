"""Independent loader for the t8 verification. Reads only the JSON bar files."""
import json
import numpy as np
import pandas as pd

D = '/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/rev/'
FILES = ['d0a', 'd0b', 'd1', 'd2', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6']
LAST = '2026-11-06'   # spec: data through 2026-11-06 (2026-11-09 bars are today's/interpolated)


def load_raw():
    """symbol -> list of (file, bar dict), in file order."""
    raw = {}
    for f in FILES:
        j = json.load(open(D + f + '.json'))
        for r in j['data']['results']:
            raw.setdefault(r['symbol'], []).extend((f, b) for b in r['bars'])
    return raw


def build(raw, last=LAST, drop_zero_vol=True, report=None):
    out = {}
    for s, bars in raw.items():
        rows = {}
        ndup = nconf = nint = nzv = 0
        for f, b in bars:
            d = b['begins_at'][:10]
            if b.get('interpolated'):
                nint += 1
                continue
            v = b.get('volume')
            if drop_zero_vol and (v is None or float(v) <= 0):
                nzv += 1
                continue
            try:
                o = float(b['open_price']); c = float(b['close_price'])
                h = float(b['high_price']); l = float(b['low_price'])
            except (TypeError, ValueError, KeyError):
                nzv += 1
                continue
            if not (o > 0 and c > 0):
                nzv += 1
                continue
            if d in rows:
                ndup += 1
                if abs(rows[d][0] - o) > 1e-9 or abs(rows[d][3] - c) > 1e-9:
                    nconf += 1
                continue
            rows[d] = (o, h, l, c, float(v or 0))
        df = pd.DataFrame.from_dict(rows, orient='index', columns=['o', 'h', 'l', 'c', 'v'])
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        if last:
            df = df[df.index <= pd.Timestamp(last)]
        out[s] = df
        if report is not None:
            report[s] = dict(n=len(df), first=str(df.index[0].date()), last=str(df.index[-1].date()),
                             dup=ndup, dup_conflict=nconf, interp=nint, zerovol=nzv)
    return out
