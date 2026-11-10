import json,sys
base='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/'
for f in ['rev/d0a.json','rev/d0b.json','rev/d1.json','rev/d2.json','rev/x1.json','rev/x2.json','rev/x3.json','rev/x4.json','rev/x5.json','rev/x6.json','rev/fresh_1109.json','pm/day_0908_1110.json']:
    d=json.load(open(base+f))
    print(f)
    for x in d['data']['results']:
        b=x['bars']
        nz=sum(1 for q in b if not q.get('volume'))
        ni=sum(1 for q in b if q.get('interpolated'))
        ses=set(q.get('session') for q in b)
        print('  ',x['symbol'],len(b),b[0]['begins_at'][:10] if b else None,b[-1]['begins_at'][:10] if b else None,'zeroVol',nz,'interp',ni,ses)
print(json.dumps(json.load(open(base+'pm/day_0908_1110.json'))['data']['results'][0]['bars'][-3:],indent=0))
