import numpy as np
rng=np.random.default_rng(11); N=400000
def p(f,wk,we,dist,drift=0.0,cush=0.085):
    sig=np.array([wk,wk,wk,wk,we,wk])
    z=rng.standard_normal((N,6)) if dist=='n' else rng.standard_t(3,(N,6))/np.sqrt(3)
    r=np.exp(drift+z*sig)-1
    E=np.cumprod(1+f*r,axis=1)
    return (E.min(axis=1)<=1-cush).mean(), np.std(E[:,-1])
for f,lab in [(0.90,'full ~90%'),(0.75,'3 sh ~75%'),(0.50,'2 sh ~50%'),(0.25,'1 sh ~25%')]:
    row=[]
    for wk,we in [(0.041,0.060),(0.050,0.070),(0.079,0.11)]:
        for d in ['n','t3']:
            pp,sd=p(f,wk,we,d); row.append(f"{pp:.3f}")
    print(lab, 'corr n/t3, sticky n/t3, stress n/t3:', row)
for f in [0.9,0.5,0.25]:
    print(f, 'expected edge 6 nights % of E at 0.2/0.3%:', round(6*0.002*f*100,2), round(6*0.003*f*100,2))
