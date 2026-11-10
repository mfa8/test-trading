"""Adjudicator: raw-data inspection only (no simulation)."""
import json, sys, collections
RAW = sys.argv[1]
FILES = ['d0a','d0b','d1','d2','x1','x2','x3','x4','x5','x6']
keys = collections.Counter(); sess = collections.Counter(); interp_vals = collections.Counter()
per = collections.defaultdict(lambda: collections.Counter())
tails = collections.Counter()
for f in FILES:
    j = json.load(open('%s/%s.json' % (RAW, f)))
    top = list(j.keys()) if isinstance(j, dict) else type(j)
    d = j['data'] if 'data' in j else j
    syms = [r['symbol'] for r in d['results']]
    print(f, 'top keys', top, 'symbols', syms)
    for r in d['results']:
        s = r['symbol']
        bars = r['bars']
        print('   %-5s n=%5d %s .. %s' % (s, len(bars), bars[0]['begins_at'][:10], bars[-1]['begins_at'][:10]))
        for b in bars:
            for k in b: keys[k] += 1
            sess[b.get('session')] += 1
            interp_vals[repr(b.get('interpolated'))] += 1
            tails[b['begins_at'][10:]] += 1
            v = b.get('volume')
            if v is None or float(v) <= 0: per[s]['zero_or_missing_vol'] += 1
            if b.get('interpolated'): per[s]['interpolated'] += 1
            if b.get('interpolated') and v is not None and float(v) > 0: per[s]['interp_with_volume'] += 1
            if (v is None or float(v) <= 0) and not b.get('interpolated'): per[s]['zero_vol_not_interp'] += 1
print('bar keys', dict(keys)); print('session values', dict(sess)); print('interpolated values', dict(interp_vals)); print('begins_at tails', dict(tails))
for s in sorted(per): print(s, dict(per[s]))
