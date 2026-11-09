import statistics as st, math, random
import verify as V
rows=V.rows
def on1acct(k): r=rows[k+1]; return 0.0 if r["earn"] else r["on"]
for lo in ("2015-01-01","1999-01-01"):
    pool=[k for k,r in enumerate(rows) if r["t"]>=lo and not r["earn"] and k+11<len(rows)]
    ev=[k for k in pool if rows[k]["on"]<=-0.04]
    idio=[k for k in ev if rows[k]["qon"]>=-0.005]; oth=[k for k in ev if rows[k]["qon"]<-0.005]
    a=[on1acct(k) for k in idio]; b=[on1acct(k) for k in oth]
    # permutation test of difference in means
    rnd=random.Random(7); allv=a+b; d0=st.mean(a)-st.mean(b); c=0; B=20000
    for _ in range(B):
        rnd.shuffle(allv); 
        if abs(st.mean(allv[:len(a)])-st.mean(allv[len(a):]))>=abs(d0): c+=1
    print(lo,"idio n%d %.2f%% vs market-gap n%d %.2f%%  diff %.2f welch t %.2f perm p %.3f"%(len(a),st.mean(a)*100,len(b),st.mean(b)*100,d0*100,V.welch(a,b),c/B))
    # sum10 random-date p for idio
    s=[V.fwd(k)["s10"] for k in idio]; u=[V.fwd(k)["s10"] for k in pool]; mu=st.mean(u)
    c=0
    for _ in range(B):
        m=st.mean(rnd.sample(u,len(s)))
        if abs(m-mu)>=abs(st.mean(s)-mu): c+=1
    print("   idio sum10 mean %.2f%% sd %.2f vs pool sd %.2f; welch t %.2f; random-date p %.3f; z using pool sd %.2f"%(st.mean(s)*100,st.stdev(s)*100,st.stdev(u)*100,V.welch(s,u),c/B,(st.mean(s)-mu)/(st.stdev(u)/math.sqrt(len(s)))))
    # threshold -4.8
    print("   on1<=-4.8: idio %d/%d all %d/%d"%(sum(on1acct(k)<=-0.048 for k in idio),len(idio),sum(on1acct(k)<=-0.048 for k in ev),len(ev)))
