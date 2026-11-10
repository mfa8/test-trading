import json, sys
RAW = sys.argv[1]
for f in ['d2','x3','x6']:
    j = json.load(open('%s/%s.json' % (RAW, f)))
    g = j.get('guide')
    print(f, 'guide type', type(g).__name__, 'len', len(json.dumps(g)), '| first 300 chars:', json.dumps(g)[:300])
    for r in j['data']['results']:
        for b in r['bars'][-3:]:
            print('  ', r['symbol'], b['begins_at'][:10], b['open_price'], b['close_price'], b['volume'], b.get('interpolated'))
j = json.load(open('%s/x4.json' % RAW))
for r in j['data']['results']:
    if r['symbol'] == 'AMZN':
        for b in r['bars']:
            if '2008-10-27' <= b['begins_at'][:10] <= '2008-10-31': print('AMZN', b)
j = json.load(open('%s/d0a.json' % RAW))
for r in j['data']['results']:
    if r['symbol'] in ('NVDA','QQQ'):
        for b in r['bars']:
            if '2000-10-25' <= b['begins_at'][:10] <= '2000-11-01': print(r['symbol'], b['begins_at'][:10], b['open_price'], b['close_price'], b['volume'])
