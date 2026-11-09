import numpy as np
rng=np.random.default_rng(7)
N=400000
# 6 held nights before earnings blackout: 11/9-10,10-11,11-12,12-13, 13-16 (weekend), 16-17
def sim(wk, we, dist, drift=0.0, cush=(0.90,0.91)):
    sig=np.array([wk,wk,wk,wk,we,wk])
    if dist=='n':
        z=rng.standard_normal((N,6))
    else:
        df=3; z=rng.standard_t(df,(N,6))/np.sqrt(df/(df-2))
    r=np.exp(drift+z*sig)-1          # NVDL night simple return
    path=np.cumprod(1+r,axis=1)
    mn=path.min(axis=1)
    out={c:(mn<=c).mean() for c in cush}
    out['end_sd']=np.std(np.log(path[:,-1]))
    out['p_any_night_le_-10']=(r<=-0.10).any(axis=1).mean()
    return out
cases={'corrected Fri (NVDL 4.1/6.0)':(0.041,0.060),'stream Fri (4.6/6.7)':(0.046,0.067),'sticky (5.0/7.0)':(0.050,0.070),'stress (7.9/11)':(0.079,0.11)}
for k,(wk,we) in cases.items():
    for d in ['n','t3']:
        for drift in [0.0,0.003]:
            o=sim(wk,we,d,drift)
            print(f"{k:30s} {d:3s} drift{drift:+.3f}  P(cum<=-10%)={o[0.90]:.3f} P(cum<=-9%)={o[0.91]:.3f} 6n sd={o['end_sd']:.3f} P(any night<=-10%)={o['p_any_night_le_-10']:.3f}")
