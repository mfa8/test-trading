import statistics as st, math
import verify as V
rows=V.rows
# baseline of non-earn nights themselves
for lo in ("2015-01-01","2005-01-01","1999-01-01"):
    x=[r["on"] for r in rows if r["t"]>=lo and not r["earn"]]
    print(lo,"non-earn nights",len(x),"mean %.3f%% sd %.2f pos %.1f%% |x| %.2f%%  <=-3%%: %.2f%%  <=-5.1%%: %.2f%%"%(st.mean(x)*100,st.stdev(x)*100,100*sum(v>0 for v in x)/len(x),100*st.mean(abs(v) for v in x),100*sum(v<=-0.03 for v in x)/len(x),100*sum(v<=-0.051 for v in x)/len(x)))
# account-style on1 (earn next night -> 0)
def on1acct(k): r=rows[k+1]; return 0.0 if r["earn"] else r["on"]
for lo,q in (("2015-01-01",True),("2015-01-01",False),("1999-01-01",False),("1999-01-01",True)):
    pool=[k for k,r in enumerate(rows) if r["t"]>=lo and not r["earn"] and k+11<len(rows)]
    ev=[k for k in pool if rows[k]["on"]<=-0.04 and (not q or rows[k]["qon"]>=-0.005)]
    a=[on1acct(k) for k in ev]; b=[on1acct(k) for k in pool]
    print(lo,"q" if q else "all","n",len(ev),"on1acct mean %.2f%% vs %.3f%% sd %.2f t %.2f"%(st.mean(a)*100,st.mean(b)*100,st.stdev(b)*100,V.welch(a,b)), "boot",[round(v*100,2) for v in V.boot(a)])
    aa=[abs(v) for v in a]; bb=[abs(v) for v in b]
    print("   |on1| %.2f vs %.2f t %.2f ; <=-3%%: %d/%d base %.2f%%"%(st.mean(aa)*100,st.mean(bb)*100,V.welch(aa,bb),sum(v<=-0.03 for v in a),len(a),100*sum(v<=-0.03 for v in b)/len(b)))
    # episodes: events within 10 nights of the previous kept event dropped
    ep=[];last=-10**9
    for k in ev:
        if k-last>10: ep.append(k); last=k
    fe=[V.fwd(k)["fur"] for k in ep]
    print("   episodes",len(ep),"on1 mean %.2f%%"%(st.mean(on1acct(k) for k in ep)*100),"further %d/%d"%(sum(fe),len(fe)), "binom p", round(V.binom_ge(sum(fe),len(fe),0.0486),4))
