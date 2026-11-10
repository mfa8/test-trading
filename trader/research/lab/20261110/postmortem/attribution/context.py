import json, math, statistics as st
P='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/'
d=json.load(open(P+'day_0908_1110.json'))
B={}
for r in d['data']['results']:
    B[r['symbol']]=[(b['begins_at'][:10],float(b['open_price']),float(b['close_price']),bool(b.get('interpolated')) or b['volume']==0) for b in r['bars']]
print(f"{'sym':5} {'nights':>6} {'ovn sum%':>9} {'ovn cmpd%':>9} {'mean%':>7} {'sd%':>6} {'win':>5} {'worst%':>7} {'best%':>7} | {'intraday cmpd% (same span)':>26} | {'B&H c0909->c1110':>16} {'c0909->o1110':>13} {'c0909->c1109':>13} | ovn cmpd excl 2 worst")
for s in ['NVDL','NVDX','NVDA','TQQQ','QQQ','SOXL','UPRO','METU','AAPU','AMZU']:
    bars=B[s]
    idx={b[0]:i for i,b in enumerate(bars)}
    i0=idx['2026-09-09']
    ov=[]; intr=[]
    for i in range(i0,len(bars)-1):
        a=bars[i]; n=bars[i+1]
        if n[3] or a[3]: continue
        ov.append((a[0],n[0],n[1]/a[2]-1))
    for i in range(i0+1,len(bars)):
        if bars[i][3]: continue
        intr.append(bars[i][2]/bars[i][1]-1)
    r=[x[2] for x in ov]
    cm=math.prod(1+x for x in r)-1
    last=bars[-1]
    c0=bars[i0][2]
    bh_c=(last[2]/c0-1) if not last[3] else None
    bh_o=(last[1]/c0-1) if not last[3] else None
    c1109=bars[idx['2026-11-09']][2]/c0-1
    # intraday compounded for sessions with exits through the last overnight
    ni=len(ov)
    ic=math.prod(1+x for x in intr[:ni-1 if False else ni])-1 if False else None
    # intraday over sessions 09-10 .. last overnight's exit session minus? use sessions 09-10..11-09 (the days the account sat in cash between the exits and next entries)
    days=[bars[i] for i in range(i0+1,idx['2026-11-09']+1)]
    ic=math.prod(b[2]/b[1] for b in days)-1
    rs=sorted(r)
    cm2=math.prod(1+x for x in rs[2:])-1
    f=lambda v: f"{100*v:+.2f}" if v is not None else 'n/a'
    print(f"{s:5} {len(r):6d} {100*sum(r):+9.2f} {100*cm:+9.2f} {100*st.mean(r):+7.3f} {100*st.stdev(r):6.2f} {sum(1 for x in r if x>0):3d}/{len(r)} {100*min(r):+7.2f} {100*max(r):+7.2f} | {100*ic:+26.2f} | {f(bh_c):>16} {f(bh_o):>13} {f(c1109):>13} | {100*cm2:+.2f}   last ovn {ov[-1][0]}->{ov[-1][1]}")
# NVDA nights detail for the two worst
for s in ('NVDA','NVDL','QQQ'):
    bars=B[s]
    for i in range(len(bars)-1):
        if bars[i][0] in('2026-11-04','2026-11-05','2026-11-06','2026-11-09'):
            a,n=bars[i],bars[i+1]
            print(s,a[0],'O',a[1],'C',a[2],'intraday %+.2f%%'%(100*(a[2]/a[1]-1)),'-> next open',n[1],'ovn %+.2f%%'%(100*(n[1]/a[2]-1)), '(interp)' if n[3] else '')
# strategy on NVDL: overnight-only vs our realized, first-day equity
