# usage: python3 exit_ovn.py NIGHT YYYYMMDD SYM:QTY:BID [SYM:QTY:BID ...] [--reprice]
# RULES_v3 §5: 09:31:05 marketable limit sell at bid - max(0.02, 0.15%); --reprice -> bid*(1-0.003)
import sys,math,json,uuid,datetime
n=sys.argv[1]; day=sys.argv[2]; rp='--reprice' in sys.argv
legs=[a.split(':') for a in sys.argv[3:] if not a.startswith('--')]
t=datetime.datetime.now(datetime.timezone.utc).isoformat()
for sym,q,b in legs:
    b=float(b); q=int(q)
    l=math.floor((b*(1-0.003) if rp else b-max(0.02,0.0015*b))*100)/100
    d={"t":t,"coid":f"T3X-{day}-{n}-{sym}-X{'2' if rp else ''}","ref_id":str(uuid.uuid4()),"sym":sym,"side":"sell","qty":q,"type":"limit","limit":l,"tif":"gfd","hours":"regular_hours","rule":"RULES_v3 §5 exit 09:31 "+("re-price bid-0.3%" if rp else "marketable limit bid-max(0.02,0.15%)"),"note":f"night {n} exit"}
    open('/home/user/test-trading/trader/orders.jsonl','a').write(json.dumps(d)+"\n")
    print(sym,q,l,d['ref_id'])
