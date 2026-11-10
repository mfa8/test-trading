import csv, statistics as st, math
E='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/exec_timing/'
def load(fn): return list(csv.DictReader(open(E+fn)))
def desc(x,label):
    if len(x)<2: print(f"  {label:38} n={len(x)}"); return
    m=st.mean(x); sd=st.stdev(x); t=m/(sd/math.sqrt(len(x)))
    print(f"  {label:38} n={len(x):3d} mean {m:+7.1f}bp sd {sd:6.1f} t {t:+.2f} median {st.median(x):+7.1f} neg {sum(1 for v in x if v<0)}/{len(x)}")
A=[r for r in load('tierA.csv') if r['sym']=='NVDL' and r['earn']=='0' and r['o0930'] and r['p0935']]
print('tierA NVDL non-earnings mornings',len(A),A[0]['date'],A[-1]['date'])
for name,f in (('open->09:35 (5-min bar close)',lambda r: 1e4*(float(r['p0935'])/float(r['o0930'])-1)),
               ('open->bridge proxy 09:31:05',lambda r: 1e4*(float(r['ref_bb'])/float(r['o0930'])-1)),
               ('open->5min OHLC4',lambda r: 1e4*(float(r['ref_5ohlc4'])/float(r['o0930'])-1))):
    print(name)
    gap=lambda r: 100*(float(r['o0930'])/float(r['prev_close'])-1)
    desc([f(r) for r in A],'all')
    desc([f(r) for r in A if gap(r)<-2],'gap<-2%')
    desc([f(r) for r in A if -2<=gap(r)<=2],'mid')
    desc([f(r) for r in A if gap(r)>2],'gap>+2%')
    desc([f(r) for r in A if abs(gap(r))>2],'|gap|>2%')
    desc([f(r) for r in A if r['date']<'2026-09-08'],'before 2026-09-08 (pre-live)')
    desc([f(r) for r in A if r['date']<'2026-09-08' and abs(gap(r))>2],'pre-live |gap|>2%')
    desc([f(r) for r in A if r['date']<'2026-09-08' and gap(r)<-2],'pre-live gap<-2%')
    desc([f(r) for r in A if r['date']<'2026-09-08' and gap(r)>2],'pre-live gap>+2%')
    desc([f(r) for r in A if r['date']>='2026-09-08'],'from 2026-09-08 (live overlap)')
    for mth in ('02','03','04','05','06','07','08','09','10'):
        desc([f(r) for r in A if r['date'][5:7]==mth],'month '+mth)
B=[r for r in load('tierB.csv') if r['sym']=='NVDL' and r['earn']=='0']
print('\ntierB NVDL 1-minute mornings',len(B),B[0]['date'],B[-1]['date'])
gapB=lambda r: 100*(float(r['o0930'])/float(r['prev_close'])-1)
for name,f in (('open->09:31 bar OHLC4 (study live ref)',lambda r:1e4*(float(r['ref'])/float(r['o0930'])-1)),
               ('open->09:31 bar close',lambda r:1e4*(float(r['c0931'])/float(r['o0930'])-1)),
               ('open->09:31 bar open',lambda r:1e4*(float(r['o0931'])/float(r['o0930'])-1)),
               ('open->bridge proxy from 5min',lambda r:1e4*(float(r['ref_bb'])/float(r['o0930'])-1)),
               ('bridge proxy vs 09:31 OHLC4 (proxy error)',lambda r:1e4*(float(r['ref_bb'])/float(r['ref'])-1)),
               ('open->09:35',lambda r:1e4*(float(r['p0935'])/float(r['o0930'])-1))):
    print(name)
    desc([f(r) for r in B],'all')
    desc([f(r) for r in B if abs(gapB(r))>2],'|gap|>2%')
    desc([f(r) for r in B if abs(gapB(r))<=2],'|gap|<=2%')
    desc([f(r) for r in B if r['date'][5:7]=='09'],'Sep'); desc([f(r) for r in B if r['date'][5:7]=='10'],'Oct')
# sd of first-minute move to size the noise
x=[1e4*(float(r['ref'])/float(r['o0930'])-1) for r in B]
print('sd open->09:31 OHLC4 (bp):',round(st.stdev(x),1))
