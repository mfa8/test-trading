import json, math, random
REV='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/rev/'
PM='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/'
def loadfiles(files, cutoff='2026-11-06'):
    out={}
    for f in files:
        for x in json.load(open(REV+f))['data']['results']:
            s=x['symbol']
            for b in x['bars']:
                d=b['begins_at'][:10]
                if b.get('interpolated') or not float(b.get('volume') or 0): continue
                if d>cutoff: continue
                if s=='NVDA' and d<='2000-10-27': continue
                out.setdefault(s,{})[d]=(float(b['open_price']),float(b['close_price']))
    return out
B=loadfiles(['d0a.json','d0b.json','d1.json','d2.json'])
# add 11/09 and 11/10 from pm file
pm={}
for r in json.load(open(PM+'day_0908_1110.json'))['data']['results']:
    for b in r['bars']:
        if b.get('interpolated') or not float(b.get('volume') or 0): continue
        pm.setdefault(r['symbol'],{})[b['begins_at'][:10]]=(float(b['open_price']),float(b['close_price']))
def series(extra=False):
    q=dict(B['QQQ']); n=dict(B['NVDA']); t=dict(B['TQQQ'])
    if extra:
        for s,dd in (('QQQ',q),('NVDA',n),('TQQQ',t)):
            for d,v in pm[s].items():
                if d>'2026-11-06': dd[d]=v
    return q,n,t
def build(extra=False):
    q,n,t=series(extra)
    qd=sorted(q); qc=[q[d][1] for d in qd]
    state={}
    for i,d in enumerate(qd):
        if i>=199:
            state[d]=1 if qc[i]>=sum(qc[i-199:i])/199 else 0
    ds=sorted(set(n)&set(t)&set(q))
    ds=[d for d in ds if d>='2015-01-02']
    rows=[]
    for i in range(len(ds)-1):
        a,b=ds[i],ds[i+1]
        rn=2*(n[b][0]/n[a][1]-1); rt=t[b][0]/t[a][1]-1
        rows.append((a,b,rn,rt,state[a]))
    return rows
rows=build()
print('nights',len(rows),rows[0][:2],rows[-1][:2],'UP',sum(r[4] for r in rows),'DOWN',sum(1-r[4] for r in rows))
def R(row,w,trend=True):
    s=(0.98 if row[4] else 0.25) if trend else 0.98
    return s*(w*row[2]+(1-w)*row[3]-0.0009)
def metrics(rs):
    g=100*sum(math.log(1+x) for x in rs)/len(rs)
    worst=100*min(rs)
    eq=1;pk=1;mdd=0
    for x in rs:
        eq*=1+x; pk=max(pk,eq); mdd=min(mdd,eq/pk-1)
    m=sum(rs)/len(rs); sd=math.sqrt(sum((x-m)**2 for x in rs)/(len(rs)-1))
    return g,worst,100*mdd,100*sd
for trend in (True,False):
    print('TREND' if trend else 'ALWAYS 0.98')
    for lab,f in [('2015-20',lambda r:r[0]<'2021'),('2021-26',lambda r:r[0]>='2021'),('all',lambda r:True)]:
        sub=[r for r in rows if f(r)]
        out=[]
        for w in (1,0.5,0):
            out.append(metrics([R(r,w,trend) for r in sub]))
        print(' %s n=%d growth %s | worst %s | mdd %s | sd %s'%(lab,len(sub),' / '.join('%+.4f'%o[0] for o in out),' / '.join('%.2f'%o[1] for o in out),' / '.join('%.1f'%o[2] for o in out),' / '.join('%.2f'%o[3] for o in out)))
        print('    split-NVDL growth %.4f ; halfcash growth %.4f'%(out[1][0]-out[0][0], metrics([ (0.98 if r[4] else 0.25)*(0.5*r[2]-0.00045) if trend else 0.98*(0.5*r[2]-0.00045) for r in sub])[0]))
# sensitivity with extra night 11/06->11/09
rows2=build(True)
print('with extra nights',len(rows2),rows2[-1])
sub=[r for r in rows2 if r[0]>='2021']
print(' 2021-26 growth diff incl extra', metrics([R(r,0.5) for r in sub])[0]-metrics([R(r,1) for r in sub])[0])
# worst nights
srt=sorted(rows,key=lambda r:R(r,1))[:5]
for r in srt: print(r[0],r[1],'NVDL-only %.2f split %.2f tqqq %.2f state %d'%(100*R(r,1),100*R(r,0.5),100*R(r,0),r[4]))
# correlation
import statistics as st
xn=[r[2] for r in rows]; xt=[r[3] for r in rows]
print('corr',st.correlation(xn,xt))
# TQQQ gross mean t
for lab,f in [('2015-20',lambda r:r[0]<'2021'),('2021-26',lambda r:r[0]>='2021'),('all',lambda r:True)]:
    v=[r[3] for r in rows if f(r)]; m=st.mean(v); s=st.stdev(v); print('TQQQ gross',lab,'%.3f sd %.2f t %.2f'%(100*m,100*s,m/(s/math.sqrt(len(v)))))
    v=[r[2] for r in rows if f(r)]; m=st.mean(v); s=st.stdev(v); print('2xNVDA gross',lab,'%.3f sd %.2f t %.2f'%(100*m,100*s,m/(s/math.sqrt(len(v)))))
json.dump(rows,open('c2_rows.json','w'))
