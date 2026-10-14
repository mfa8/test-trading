# usage: python3 hb.py "<note>" HH:MM   (UTC target; sleeps min(480s, until target); never rolls to next day)
import sys,datetime,time,os
note=sys.argv[1]; hh,mm=map(int,sys.argv[2].split(':'))
now=datetime.datetime.now(datetime.timezone.utc)
t=now.replace(hour=hh,minute=mm,second=0,microsecond=0)
d=max(0,min(480,(t-now).total_seconds()))
log=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','scan.log')
try: open('/tmp/t3x_scan.log','a').write(f"{now.isoformat()} {note}\n")
except Exception: pass
time.sleep(d); print(datetime.datetime.now(datetime.timezone.utc).isoformat())
