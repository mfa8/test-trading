import csv, math, statistics as st, json
R="/home/user/test-trading/trader/research/edge_decay/"
rows=list(csv.DictReader(open(R+"overnight_thru_20261023.csv")))
diffs=[float(r["nvdl_on"])-2*float(r["nvda_on"]) for r in rows if r["nvdl_on"] and r["earn"]=="0"]
drag_med=st.median(diffs)
# (open, close) official RH daily bars, adjustment none
L={"2026-10-23":(30.905,30.91),"2026-10-26":(31.50,32.37),"2026-10-27":(33.00,32.92),"2026-10-28":(33.47,32.15),"2026-10-29":(31.845,31.60),"2026-10-30":(30.14,28.97)}
A={"2026-10-23":(210.99,210.96),"2026-10-26":(213.105,216.00),"2026-10-27":(218.31,217.94),"2026-10-28":(219.915,215.38),"2026-10-29":(214.36,213.66),"2026-10-30":(208.94,204.64)}
import datetime as dt
d=sorted(L); new=[]
for i in range(len(d)-1):
    t,t1=d[i],d[i+1]
    rl=L[t1][0]/L[t][1]-1; ra=A[t1][0]/A[t][1]-1
    cl=2*ra+drag_med if abs(rl-2*ra)>0.01 else rl
    gap=(dt.date.fromisoformat(t1)-dt.date.fromisoformat(t)).days
    new.append(dict(date=t,next=t1,gapdays=gap,earn="0",preann="",nvda_on="%.6f"%ra,nvdl_on="%.6f"%rl,nvdl_clean="%.6f"%cl,proxy2x="%.6f"%(2*ra-0.0004)))
assert rows[-1]["next"]=="2026-10-23"
allr=rows+new
out=R+"overnight_thru_20261030.csv"
with open(out,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in allr]
def stats(v):
    m=st.mean(v); s=st.stdev(v); return dict(n=len(v),mean_pct=round(100*m,3),sd_pct=round(100*s,3),t=round(m/(s/math.sqrt(len(v))),2))
def w120(asof,key):
    ok=[r for r in allr if r[key] not in ("",None) and r["date"]<=asof]
    return stats([float(r[key]) for r in ok if r["earn"]=="0"][-120:])
res={"drag_median_pct":round(100*drag_med,3),
 "new_nights":[(r["date"],r["next"],round(100*float(r["nvdl_on"]),3),round(100*float(r["nvdl_clean"]),3),round(200*float(r["nvda_on"]),3)) for r in new],
 "repro_1022_raw":w120("2026-10-22","nvdl_on"),
 "now_1029_raw":w120("2026-10-29","nvdl_on"),"now_1029_clean":w120("2026-10-29","nvdl_clean"),"now_1029_proxy":w120("2026-10-29","proxy2x"),
 "window_first_night":[r["date"] for r in allr if r["nvdl_on"] and r["earn"]=="0"][-120]}
print(json.dumps(res,indent=1))
