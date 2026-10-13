# Walk-forward test of the overnight ranking: does trailing-W overnight score pick next-week winners?
import json,statistics as st,math
R=json.load(open('daily_1y_20261012.json'))['data']['results']+json.load(open('daily_1y_univ_20261012.json'))['data']['results']
U={}
for r in R:
    if r['symbol']=='TZA': continue
    b=[x for x in r['bars'] if not x.get('interpolated')]
    U[r['symbol']]={x['begins_at'][:10]:(float(x['open_price']),float(x['close_price'])) for x in b}
dates=sorted(set.intersection(*[set(v) for v in U.values()]))
syms=sorted(U)
ON={s:[U[s][dates[i]][0]/U[s][dates[i-1]][1]-1 for i in range(1,len(dates))] for s in syms}  # ON[s][k] = night ending dates[k+1]
und={'NVDL':'NVDA','NVDX':'NVDA'}
N=len(dates)-1
def run(W,step=5,start=120,fixed=None):
    out=[]
    for k0 in range(start,N,step):
        if fixed: picks=fixed
        else:
            sc={s:st.mean(ON[s][k0-W:k0])/(st.pstdev(ON[s][k0-W:k0]) or 1) for s in syms}
            picks=[];seen=set()
            for s in sorted(sc,key=sc.get,reverse=True):
                u=und.get(s,s)
                if u in seen: continue
                picks.append(s);seen.add(u)
                if len(picks)==2: break
        for k in range(k0,min(k0+step,N)):
            out.append(st.mean(ON[s][k] for s in picks))
    m=st.mean(out);sd=st.pstdev(out);cum=math.prod(1+x for x in out)-1
    return f"n={len(out)} mean={m*100:+.3f}% sd={sd*100:.2f} score={m/sd:+.3f} cum={cum*100:+.0f}% win={sum(x>0 for x in out)/len(out)*100:.0f}%"
print('dates',dates[0],dates[-1],'nights',N,'universe',len(syms))
for W in (20,30,60,120):
    print(f"rank W={W:>3} weekly:",run(W))
for fx in (['NVDL'],['NVDL','METU'],['METU'],['NVDL','GGLL'],syms):
    print(f"fixed {'ALL' if fx is syms else '+'.join(fx)}:",run(0,fixed=fx))
