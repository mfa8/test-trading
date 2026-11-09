import statistics as st, math
import verify as V
rows=V.rows; N=V.N; dates=V.dates
for d in ["2005-11-28","2008-04-16","2008-11-12","2010-07-28","2016-12-28","2017-02-22","2017-04-03","2022-08-05","2025-11-24"]:
    i=dates.index(d)
    print(d)
    for j in range(i-1,i+3):
        o,c,h,l,v=N[dates[j]]
        print("   %s O %.4f H %.4f L %.4f C %.4f V %.0f"%(dates[j],o,h,l,c,v))
# second-moment ratio
def on1acct(k): r=rows[k+1]; return 0.0 if r["earn"] else r["on"]
for lo,q in (("2015-01-01",True),("2005-01-01",True),("2015-01-01",False),("1999-01-01",False)):
    pool=[k for k,r in enumerate(rows) if r["t"]>=lo and not r["earn"] and k+11<len(rows)]
    ev=[k for k in pool if rows[k]["on"]<=-0.04 and (not q or rows[k]["qon"]>=-0.005)]
    a=[on1acct(k) for k in ev]; b=[on1acct(k) for k in pool]
    m2a=st.mean(x*x for x in a); m2b=st.mean(x*x for x in b)
    print(lo,q,"E[x^2] ratio %.2f  var ratio %.2f  sd ev %.2f%%"%(m2a/m2b, st.variance(a)/st.variance(b), st.stdev(a)*100))
