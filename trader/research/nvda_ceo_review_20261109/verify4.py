import statistics as st, math
import verify as V
rows=V.rows; idx=V.idx
def on1acct(k): r=rows[k+1]; return 0.0 if r["earn"] else r["on"]
S=["2017-02-22","2017-04-03","2019-01-25","2022-08-05","2022-08-31","2023-10-16","2025-04-15","2025-11-24"]
out=[]
for d in S:
    k=idx[d]; f=V.fwd(k); r=rows[k]
    out.append((d,r["on"],r["qon"],f["oc"],on1acct(k),f["s5"],f["s10"],f["fur"]))
    print("%s gap %+.2f qqq %+.2f earn %d | oc %+.2f on1 %+.2f s5 %+.2f s10 %+.2f fur %d"%(d,r["on"]*100,r["qon"]*100,r["earn"],f["oc"]*100,on1acct(k)*100,f["s5"]*100,f["s10"]*100,f["fur"]))
pool=[k for k,r in enumerate(rows) if r["t"]>="2015-01-01" and not r["earn"] and k+11<len(rows)]
for j,name in ((3,"oc"),(4,"on1"),(5,"s5"),(6,"s10")):
    a=[o[j] for o in out]
    if name=="on1": b=[on1acct(k) for k in pool]
    elif name=="oc": b=[V.fwd(k)["oc"] for k in pool]
    else: b=[V.fwd(k)[name] for k in pool]
    print(name,"mean %+.2f%% neg %d/8 t %+.2f boot %s"%(st.mean(a)*100,sum(x<0 for x in a),V.welch(a,b),[round(v*100,2) for v in V.boot(a)]))
print("fur",sum(o[7] for o in out))
# QQQ gap relative to SPY-like? print nights 2023-10-16 etc
