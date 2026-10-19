import json,statistics as st,sys
files=sys.argv[1:]
out={}
for f in files:
    for r in json.load(open(f))['data']['results']:
        sym=r['symbol']; bars=[b for b in r['bars'] if not b.get('interpolated')]
        bars.sort(key=lambda b:b['begins_at'])
        rets=[]
        for a,b in zip(bars,bars[1:]):
            c=float(a['close_price']); o=float(b['open_price'])
            rets.append((a['begins_at'][:10], o/c-1))
        def stats(x):
            v=[r*100 for _,r in x]; m=st.mean(v); sd=st.pstdev(v)
            return {"n":len(v),"mean":round(m,2),"sd":round(sd,2),"score":round(m/sd,2) if sd else None,"win":round(100*sum(a>0 for a in v)/len(v)),"worst":round(min(v),1)}
        out[sym]={"last_night":rets[-1][0],"last_close":float(bars[-1]['close_price']),"n30":stats(rets[-30:]),"n250":stats(rets[-250:]) if len(rets)>=250 else stats(rets),"big":[(d,round(r*100,1)) for d,r in rets[-250:] if abs(r)>0.08]}
json.dump(out,open('rank.json','w'),indent=1)
rows=sorted(out.items(),key=lambda kv:-(kv[1]['n30']['score'] or -9))
print(f"{'sym':6} {'last':>10} | {'30n mean':>8} {'sd':>5} {'score':>6} {'win':>4} | {'250n mean':>9} {'score':>6} n")
for s,v in rows:
    a=v['n30'];b=v['n250']
    print(f"{s:6} {v['last_night']:>10} | {a['mean']:8.2f} {a['sd']:5.2f} {a['score']:6.2f} {a['win']:4} | {b['mean']:9.2f} {b['score']:6.2f} {b['n']}  big:{v['big'][:3]}")
