import math
from scipy import stats as st
def p(x,s,model):
    lx=math.log(1+x)
    if model=='N': return st.norm.cdf(lx/s)
    nu=int(model[1]); sc=s*math.sqrt((nu-2)/nu); return st.t.cdf(lx/sc,nu)
def any6(x,s,model,wk=2.1):
    q=(1-p(x,s,model))**5*(1-p(x,s*math.sqrt(wk),model)); return 1-q
for lab,per in (('Fri',0.0381),('sticky',0.0417),('+20vol',None)):
    for sh in (0.34,0.39):
        if per is None:
            # +20 vol pts on 61.5% 11/13 ATM -> 81.5% annual calendar; per TD
            per2=0.815*math.sqrt(7/365/5)
        else: per2=per
        s=per2*math.sqrt(sh)
        out=[lab,sh,'sig %.2f%%'%(s*100),'6n %.1f%%'%(100*s*math.sqrt(7.1)),'NVDL %.1f%% 6n %.1f%%'%(200*s,200*s*math.sqrt(7.1))]
        for x in (-0.05,-0.098):
            out.append('x=%g: '%x+' '.join('%s %.2f%%/%.2f%%'%(m,100*p(x,s,m),100*any6(x,s,m)) for m in ('N','t4','t3')))
        print(*out)
# stress share .60 with +20
s=0.815*math.sqrt(7/365/5)*math.sqrt(0.6)
print('stress sig %.2f%% NVDL %.1f%% 6n %.1f%%'%(100*s,200*s,200*s*math.sqrt(7.1)))
for x in (-0.05,-0.098):
    print(x,' '.join('%s %.2f%%/%.1f%%'%(m,100*p(x,s,m),100*any6(x,s,m)) for m in ('N','t4','t3')))
# morning exit check
need=math.log(168.35/177.05); print('need %.2f%%'%(100*need), 186.64*0.902)
for sn in (0.0224,0.0238,0.0261,0.0325,0.0345):
    for f in (0.25,0.5):
        s=sn*math.sqrt(f)
        print('night sig %.2f%% frac %.2f: N %.3f%% t3 %.3f%%'%(100*sn,f,100*st.norm.cdf(need/s),100*st.t.cdf(need/(s/math.sqrt(3)),3)))
