# TZA day leg TP/stop on 1-minute RTH bars. entry = close of 09:31 bar (+0.01 slippage);
# TP fills only on trade-THROUGH (high >= tp+0.01); stop-market fill = stop - 0.03; exit = close of 15:48 bar.
import json,collections,statistics as st,math,sys
bars=json.load(open('tza_1m_0914_1012.json'))
days=collections.OrderedDict()
for b in bars: days.setdefault(b['begins_at'][:10],[]).append(b)
f=lambda b,k: float(b[k+'_price'])
def sim(day,tp,stop):
    e0=[b for b in day if b['begins_at'][11:16]=='13:31']
    if not e0: return None
    e=f(e0[0],'close')+0.01
    tpp=math.ceil(e*(1+tp)*100)/100 if tp else None
    sp=e*(1-stop) if stop else None
    last=None
    for b in day:
        t=b['begins_at'][11:16]
        if t<='13:31': continue
        if t>'19:48': break
        if sp and f(b,'low')<=sp: return (sp-0.03)/e-1,'stop'
        if tpp and f(b,'high')>=tpp+0.01: return tpp/e-1,'tp'
        last=b
    return f(last,'close')/e-1,'close'
print('days',len(days))
for tp in (None,0.0075,0.01,0.0125,0.015,0.02):
  for stop in (None,0.01,0.015,0.02):
    r=[x for x in (sim(d,tp,stop) for d in days.values()) if x]
    v=[a for a,_ in r]; k=collections.Counter(c for _,c in r)
    print(f"tp={tp} stop={stop}: n={len(v)} mean={st.mean(v)*100:+.3f}% sd={st.pstdev(v)*100:.2f} score={st.mean(v)/st.pstdev(v):.2f} win={sum(a>0 for a in v)/len(v)*100:.0f}% worst={min(v)*100:+.2f} {dict(k)}")
