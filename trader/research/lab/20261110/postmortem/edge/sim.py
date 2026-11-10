"""Forward simulation of the account under the present rules (RULES_v3 sections 6, 13, 3(d)).
Unit return of a night: u = 2*(open_t+1/close_t - 1) - 0.0009 (synthetic 2x NVDA, 9bp cost per unit of size).
Size: 0.98 if QQQ close_t >= mean of its previous 199 closes else 0.25; paused night: min(size, 0.25);
NVDA earnings night (flags 2015+ only): 0 when blackout=True.
PAUSE: C = E <= 0.80 * max(last 20 recorded equity values incl. today); starts when C; lasts at least 5 nights,
then until C is false. KILL: E <= 50 -> flat for good (equity frozen).
Start: E = 82.41, pause in force with 5 mandatory nights still to run (nights of 11/10 .. 11/16),
20-session window seeded with the EOD marks 2026-10-14 .. 2026-11-10 from trader/equity.csv.
"""
import csv, math, sys, json
import numpy as np
P='/tmp/claude-0/-home-user-test-trading/0c00e7d9-c916-50ae-ac83-8f6429819f25/scratchpad/pm/edge/'
R=[r for r in csv.DictReader(open(P+'nights.csv')) if r['syn2x_on']!='']
U=np.array([float(r['syn2x_on']) for r in R]); UPs=np.array([r['state']=='UP' for r in R]); EARN=np.array([int(r['earn'])==1 for r in R])
YEAR=np.array([int(r['date'][:4]) for r in R]); DIST=np.array([float(r['dist']) for r in R])
SEED_WINDOW=[103.67,98.24,96.91,98.36,97.01,101.19,97.30,95.69,97.46,99.08,100.90,99.89,95.30,97.54,101.56,98.92,93.06,103.61,87.78,82.41]
E0=82.41; START=98.75; KILL=50.0
HORIZ=(20,60,125,250); T=250

def make_paths(lo,hi,N,rng,mode='year',blk=20,start_filter=None):
    """return index array (N,T) into the global night arrays, drawn from years lo..hi"""
    pool=np.where((YEAR>=lo)&(YEAR<=hi))[0]
    out=np.empty((N,T),dtype=np.int32)
    if mode=='year':
        years=sorted(set(YEAR[pool])); blocks=[np.where(YEAR==y)[0] for y in years]
        for i in range(N):
            first=blocks[rng.integers(len(blocks))]
            if start_filter is not None:
                # draw the first year and offset so that the start night satisfies the filter
                cand=pool[start_filter[pool]]
                s=cand[rng.integers(len(cand))]
                first=np.where(YEAR==YEAR[s])[0]; off=int(s-first[0])
            else:
                off=int(rng.integers(len(first)))
            seq=[first[off:]]; n=len(first)-off
            while n<T:
                b=blocks[rng.integers(len(blocks))]; seq.append(b); n+=len(b)
            out[i]=np.concatenate(seq)[:T]
    elif mode=='replay':   # T consecutive nights from a random start, wrapping inside the pool
        n=len(pool)
        if start_filter is not None:
            cand=np.where(start_filter[pool])[0]; st=cand[rng.integers(len(cand),size=N)]
        else: st=rng.integers(n,size=N)
        out[:]=pool[(st[:,None]+np.arange(T)[None,:])%n]
    elif mode=='block':    # circular moving blocks of length blk
        n=len(pool); nb=math.ceil(T/blk)
        st=rng.integers(n,size=(N,nb))
        idx=(st[:,:,None]+np.arange(blk)[None,None,:])%n
        out[:]=pool[idx.reshape(N,-1)[:,:T]]
    elif mode=='iid':
        out[:]=pool[rng.integers(len(pool),size=(N,T))]
    return out

def run(idx,blackout=True,extra_cost=0.0,demean=None,pause_rule=True,trend_rule=True,e0=E0,seed_window=SEED_WINDOW,pause_left=5,shift=0.0):
    N=idx.shape[0]
    u_all=U-extra_cost+shift
    if demean is not None: u_all=u_all-demean
    E=np.full(N,e0); win=np.tile(np.array(seed_window,float),(N,1)); wp=0  # ring pointer (oldest element position)
    in_pause=np.full(N,pause_left>0); left=np.full(N,pause_left,dtype=np.int32)
    killed=np.zeros(N,bool); reached=np.zeros(N,bool); kill_first=np.zeros(N,bool)
    snap={}; expo=np.zeros(N); pausen=np.zeros(N)
    reach_by={}; kill_by={}; killfirst_by={}
    for k in range(T):
        j=idx[:,k]
        H=win.max(axis=1); C=E<=0.8*H
        if pause_rule:
            rel=in_pause&(left==0)&(~C); in_pause=in_pause&(~rel)
            new=(~in_pause)&C
            dec=in_pause&(left>0); left=np.where(dec,left-1,left)
            left=np.where(new,4,left); in_pause=in_pause|new
            pz=in_pause.copy()
        else: pz=np.zeros(N,bool)
        b=np.where(UPs[j],0.98,0.25) if trend_rule else np.full(N,0.98)
        s=np.where(pz,np.minimum(b,0.25),b)
        if blackout: s=np.where(EARN[j],0.0,s)
        s=np.where(killed,0.0,s)
        expo+=s; pausen+=pz&(~killed)
        E=E*(1+s*u_all[j])
        newk=(~killed)&(E<=KILL); kill_first|=newk&(~reached); killed|=newk
        reached|=(~killed)&(E>START)
        win[:,wp]=E; wp=(wp+1)%win.shape[1]
        if (k+1) in HORIZ:
            snap[k+1]=E.copy(); reach_by[k+1]=reached.mean(); kill_by[k+1]=killed.mean(); killfirst_by[k+1]=kill_first.mean()
    return dict(snap=snap,reach=reach_by,kill=kill_by,killfirst=killfirst_by,expo=expo.mean()/T,pause=pausen.mean()/T)

def table(lab,res):
    print('\n--- %s ---  (mean size held %.2f; share of nights in PAUSE %.0f%%)'%(lab,res['expo'],100*res['pause']))
    print(' nights |   5th   25th   50th   75th   95th |  mean | P(E>98.75 at h) | P(ever >98.75 by h) | P(KILL<=50 by h) | P(KILL before ever >98.75) | P(E<82.41 at h)')
    for h in HORIZ:
        e=res['snap'][h]; q=np.percentile(e,[5,25,50,75,95])
        print(' %6d | %6.2f %6.2f %6.2f %6.2f %6.2f | %6.2f |      %5.1f%%     |       %5.1f%%       |      %5.1f%%      |          %5.1f%%           |     %5.1f%%'%(
            h,q[0],q[1],q[2],q[3],q[4],e.mean(),100*np.mean(e>START),100*res['reach'][h],100*res['kill'][h],100*res['killfirst'][h],100*np.mean(e<E0)))
if __name__=='__main__':
    rng=np.random.default_rng(1110)
    N=200000
    out={}
    def go(lab,lo,hi,mode='year',**kw):
        sf=kw.pop('start_filter',None); blk=kw.pop('blk',20)
        idx=make_paths(lo,hi,N,rng,mode=mode,blk=blk,start_filter=sf)
        res=run(idx,**kw); table(lab,res)
        out[lab]={str(h):dict(pct=[float(x) for x in np.percentile(res['snap'][h],[5,25,50,75,95])],mean=float(res['snap'][h].mean()),p_above_start=float(np.mean(res['snap'][h]>START)),p_ever_above=float(res['reach'][h]),p_kill=float(res['kill'][h]),p_kill_first=float(res['killfirst'][h])) for h in HORIZ}
        return res
    print('E0 %.2f, PAUSE active (5 mandatory nights left), window seed max %.2f -> trigger %.2f; N paths %d'%(E0,max(SEED_WINDOW),0.8*max(SEED_WINDOW[1:]),N))
    print('History pools: 2015-2026 nights %d (DOWN %.1f%%, earnings %d); 2000-2014 nights %d (DOWN %.1f%%)'%(np.sum(YEAR>=2015),100*np.mean(~UPs[YEAR>=2015]),EARN.sum(),np.sum(YEAR<=2014),100*np.mean(~UPs[YEAR<=2014])))
    go('A1 MAIN: 2015-2026 year blocks, present rules incl. earnings blackout',2015,2026)
    go('A2: 2015-2026 year blocks, NO earnings blackout (like-for-like with 2000-2014)',2015,2026,blackout=False)
    go('B1: 2000-2014 year blocks, present rules (no earnings flags exist -> no blackout)',2000,2014,blackout=False)
    go('A3: 2015-2026, 250-night replay from a random start (no reshuffling of years)',2015,2026,mode='replay')
    go('A4: 2015-2026, 20-night blocks',2015,2026,mode='block',blk=20)
    go('A5: 2015-2026, iid nights',2015,2026,mode='iid')
    near=(~UPs)&(DIST>-0.03)
    print('\nstart-filter nights (DOWN, within 3 pct of the line): 2015-26 n %d; 2000-14 n %d'%(np.sum(near&(YEAR>=2015)),np.sum(near&(YEAR<=2014))))
    go('A6: 2015-2026 year blocks, start night drawn from DOWN nights within 3 pct of the line (as now)',2015,2026,start_filter=near)
    go('B2: 2000-2014 year blocks, same start filter',2000,2014,blackout=False,start_filter=near)
    go('B3: 2000-2014, 250-night replay',2000,2014,mode='replay',blackout=False)
    # edge removed: subtract the pool mean of unit returns (ex-earnings mean for the blackout case)
    m15=U[(YEAR>=2015)&(~EARN)].mean()
    go('C1: 2015-2026 year blocks, blackout, NO EDGE (ex-earnings mean %.3f%% removed from every night)'%(100*m15),2015,2026,demean=m15)
    go('C2: 2015-2026 year blocks, blackout, extra 10bp/night execution drag per unit size',2015,2026,extra_cost=0.0010)
    go('C3: 2015-2026 year blocks, blackout, extra 28bp/night drag (the live 44-night fill gap vs official prints)',2015,2026,extra_cost=0.0028)
    go('D1: 2015-2026 year blocks, blackout, trend rule but NO pause rule (for reference)',2015,2026,pause_rule=False,pause_left=0)
    go('D2: 2015-2026 year blocks, blackout, always 0.98 with pause rule (pre-v1.8 sizing)',2015,2026,trend_rule=False)
    go('E1: 2000-2026 year blocks (whole history), no blackout',2000,2026,blackout=False)
    json.dump(out,open(P+'sim_results.json','w'),indent=1)
