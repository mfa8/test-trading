# Overnight (close->next open) vs intraday (open->close) vs hold, per symbol, over windows.
import json,statistics as st,sys
R=json.load(open('daily_1y_20261012.json'))['data']['results']
for r in R:
    b=[x for x in r['bars'] if x.get('session','reg')=='reg' and not x.get('interpolated')]
    o=[float(x['open_price']) for x in b]; c=[float(x['close_price']) for x in b]; d=[x['begins_at'][:10] for x in b]
    print(r['symbol'],len(b),d[0],d[-1])
    for w in (30,60,120,250):
        if len(b)<w+1: continue
        on=[o[i]/c[i-1]-1 for i in range(len(b)-w,len(b))]
        intra=[c[i]/o[i]-1 for i in range(len(b)-w,len(b))]
        f=lambda v:f"{st.mean(v)*100:+.2f}%/{st.pstdev(v)*100:.2f} s={st.mean(v)/st.pstdev(v):+.2f} w={sum(x>0 for x in v)/len(v)*100:.0f}%"
        cum=lambda v: (lambda p:p)( __import__('math').prod(1+x for x in v)-1)
        print(f"  {w:>3}d overnight {f(on)} cum {cum(on)*100:+.0f}% | intraday {f(intra)} cum {cum(intra)*100:+.0f}%")
