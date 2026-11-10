import json, math, random
rows=json.load(open('c2_rows.json'))
def R(row,w): 
    s=0.98 if row[4] else 0.25
    return s*(w*row[2]+(1-w)*row[3]-0.0009)
from collections import defaultdict
def blocks(sub):
    by=defaultdict(list)
    for r in sub: by[r[0][:4]].append(r)
    return [by[y] for y in sorted(by)]
rng=random.Random(777)
def growth(rs): return 100*sum(math.log(1+x) for x in rs)/len(rs)
for lab,f in [('2015-20',lambda r:r[0]<'2021'),('2021-26',lambda r:r[0]>='2021'),('all',lambda r:True)]:
    sub=[r for r in rows if f(r)]; bl=blocks(sub); diffs=[]
    for _ in range(2000):
        path=[]
        for _ in range(len(bl)): path+=bl[rng.randrange(len(bl))]
        diffs.append(growth([R(r,0.5) for r in path])-growth([R(r,1) for r in path]))
    diffs.sort(); print(lab,'split-NVDL growth diff 90%% CI [%.3f, %.3f] median %.3f'%(diffs[100],diffs[1900],diffs[1000]), 'share of draws with diff >= -0.010: %.3f'%(sum(1 for d in diffs if d>=-0.010)/2000))
# PAUSE / KILL within 250 nights, random start inside first block
def events(path,w):
    eq=1.0; hist=[1.0]; pause=False; kill=False
    for r in path[:250]:
        eq*=1+R(r,w); hist.append(eq)
        if eq<=0.8*max(hist[-20:]): pause=True
        if eq<=0.5: kill=True
    return pause,kill
sub=rows; bl=blocks(sub)
cnt={1:[0,0],0.5:[0,0],0:[0,0]}; B=2000
for _ in range(B):
    first=bl[rng.randrange(len(bl))]; off=rng.randrange(len(first)); path=first[off:]
    while len(path)<250: path=path+bl[rng.randrange(len(bl))]
    for w in cnt:
        p,k=events(path,w); cnt[w][0]+=p; cnt[w][1]+=k
for w in cnt: print('w=%s P(PAUSE within 250) %.1f%% P(KILL within 250) %.2f%%'%(w,100*cnt[w][0]/B,100*cnt[w][1]/B))
