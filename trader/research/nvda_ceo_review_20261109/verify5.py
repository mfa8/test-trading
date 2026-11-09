import statistics as st, math
import verify as V
rows=V.rows
def on1acct(k): r=rows[k+1]; return 0.0 if r["earn"] else r["on"]
pool=[k for k,r in enumerate(rows) if r["t"]>="2015-01-01" and not r["earn"] and k+11<len(rows)]
ev=[k for k in pool if rows[k]["on"]<=-0.04]
print("ALL 2015-2026 events with further crash or on1<=-5.1:")
for k in ev:
    f=V.fwd(k)
    hits=[(rows[k+j]["t"],round(rows[k+j]["on"]*100,2)) for j in range(1,11) if not rows[k+j]["earn"] and rows[k+j]["on"]<=-0.05]
    if f["fur"] or on1acct(k)<=-0.051:
        print("  ",rows[k]["t"],"gap %+.2f qqq %+.2f on1 %+.2f"%(rows[k]["on"]*100,rows[k]["qon"]*100,on1acct(k)*100),"hits",hits)
# vol-matched baseline for idio 2015 on1<=-3 and further (quintiles of trailing 60 non-earn sd)
import numpy as np
on=[r["on"] for r in rows]; earn=[r["earn"] for r in rows]
tv=[float('nan')]*len(rows); buf=[]
for k in range(len(rows)):
    if len(buf)>=40: tv[k]=st.stdev(buf[-60:])
    if not earn[k]: buf.append(on[k])
for lo in ("2015-01-01","2005-01-01","1999-01-01"):
    pl=[k for k in pool if True] if lo=="2015-01-01" else [k for k,r in enumerate(rows) if r["t"]>=lo and not r["earn"] and k+11<len(rows)]
    pv=np.array([tv[k] for k in pl]); ok=~np.isnan(pv); qs=np.quantile(pv[ok],[.2,.4,.6,.8])
    q=lambda k: int(np.searchsorted(qs,tv[k]))
    e=[k for k in pl if on[k]<=-0.04 and rows[k]["qon"]>=-0.005]
    for name,fn in (("on1<=-3",lambda k: on1acct(k)<=-0.03),("further",lambda k: V.fwd(k)["fur"])):
        byq={i:np.mean([fn(k) for k in pl if not math.isnan(tv[k]) and q(k)==i]) for i in range(5)}
        print(lo,name,"event quintiles",[q(k) for k in e],"vm base %.1f%%"%(100*np.mean([byq[q(k)] for k in e])))
