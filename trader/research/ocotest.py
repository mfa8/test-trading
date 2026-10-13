# OCO (TP + stop-market) backtest for the TZA day leg on 5-min RTH bars.
# entry ~09:32 = mid of 09:30 bar; scan bars from 09:35 to 15:45; exit 15:49 = close of 15:45 bar.
# same-bar TP+stop ambiguity -> stop first (conservative); stop fill = stop*(1-0.0005).
import json,sys,collections,statistics as st
F=sys.argv[1]
bars=json.load(open(F))['data']['results'][0]['bars']
days=collections.OrderedDict()
for b in bars:
    days.setdefault(b['begins_at'][:10],[]).append(b)
def f(b,k): return float(b[k+'_price'])
def sim(day,tp,stop):
    e=(f(day[0],'open')+f(day[0],'close'))/2
    for b in day[1:]:
        t=b['begins_at'][11:16]
        if t>'19:45': break
        if stop and f(b,'low')<=e*(1-stop): return e*(1-stop)*(1-0.0005)/e-1,'stop'
        if tp and f(b,'high')>=e*(1+tp): return tp,'tp'
        last=b
    return f(last,'close')/e-1,'close'
res={}
for tp in (None,0.0075,0.01,0.0125,0.015):
    for stop in (None,0.005,0.0075,0.01,0.015,0.02):
        r=[sim(d,tp,stop) for d in days.values() if len(d)>70]
        x=[a for a,_ in r]; k=collections.Counter(b for _,b in r)
        res[(tp,stop)]=(st.mean(x)*100,st.pstdev(x)*100,sum(1 for a in x if a>0)/len(x)*100,min(x)*100,dict(k),len(x))
for (tp,stop),(m,sd,w,mn,k,n) in res.items():
    print(f"tp={tp} stop={stop}: n={n} mean={m:+.3f}% sd={sd:.2f} win={w:.0f}% worst={mn:+.2f}% {k}")
