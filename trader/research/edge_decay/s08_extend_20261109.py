import csv, math, statistics as st, json, datetime as dt
# §3(f) Monday 2026-11-09 check: extend overnight_thru_20261030.csv with 5 nights from RH day bars (adjustment none, fetched 11/9 07:50 ET)
R="/home/user/test-trading/trader/research/edge_decay/"
rows=list(csv.DictReader(open(R+"overnight_thru_20261030.csv")))
assert rows[-1]["next"]=="2026-10-30"
diffs=[float(r["nvdl_on"])-2*float(r["nvda_on"]) for r in rows if r["nvdl_on"] and r["earn"]=="0"]
drag_med=st.median(diffs)
L={"2026-10-30":(30.14,28.97),"2026-11-02":(29.75,28.24),"2026-11-03":(29.83,29.43),"2026-11-04":(28.555,27.64),"2026-11-05":(26.43,22.50),"2026-11-06":(24.81,23.71)}
X={"2026-10-30":(16.97,16.26),"2026-11-02":(16.705,15.84),"2026-11-03":(16.71,16.53),"2026-11-04":(16.035,15.51),"2026-11-05":(14.85,12.65),"2026-11-06":(13.92,13.30)}
A={"2026-10-30":(208.94,204.64),"2026-11-02":(207.53,202.06),"2026-11-03":(207.96,206.69),"2026-11-04":(203.50,200.13),"2026-11-05":(196.07,181.60),"2026-11-06":(191.10,186.64)}
d=sorted(L); new=[]; flags=[]
for i in range(len(d)-1):
    t,t1=d[i],d[i+1]
    rl=L[t1][0]/L[t][1]-1; ra=A[t1][0]/A[t][1]-1; rx=X[t1][0]/X[t][1]-1
    flag=abs(rl-rx)>0.01
    cl=2*ra+drag_med if abs(rl-2*ra)>0.01 else rl
    gap=(dt.date.fromisoformat(t1)-dt.date.fromisoformat(t)).days
    new.append(dict(date=t,next=t1,gapdays=gap,earn="0",preann="",nvda_on="%.6f"%ra,nvdl_on="%.6f"%rl,nvdl_clean="%.6f"%cl,proxy2x="%.6f"%(2*ra-0.0004)))
    flags.append((t,t1,round(100*rl,3),round(100*rx,3),round(200*ra,3),flag))
allr=rows+new
with open(R+"overnight_thru_20261106.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in allr]
def stats(v):
    m=st.mean(v); s=st.stdev(v); return dict(n=len(v),mean_pct=round(100*m,4),sd_pct=round(100*s,3),t=round(m/(s/math.sqrt(len(v))),3),win_pct=round(100*sum(x>0 for x in v)/len(v),1))
def w120(asof,key):
    ok=[r for r in allr if r[key] not in ("",None) and r["date"]<=asof and r["earn"]=="0"]
    return stats([float(r[key]) for r in ok][-120:]), ok[-120]["date"]
raw,first=w120("2026-11-05","nvdl_on"); clean,_=w120("2026-11-05","nvdl_clean"); prox,_=w120("2026-11-05","proxy2x")
rep,_=w120("2026-10-29","nvdl_on")
print(json.dumps({"drag_median_pct":round(100*drag_med,4),"new_nights(nvdl,nvdx,2xnvda,flag>1%)":flags,"repro_1102_raw":rep,
 "check_1109_raw":raw,"check_1109_clean":clean,"check_1109_proxy2x":prox,"window_first_night":first,"window_last_night":"2026-11-05->2026-11-06"},indent=1))
