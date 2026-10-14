# usage: python3 bridge.py HH:MM:SS   (UTC, today) — exact-time sleep; refuses legs >= 500s
import sys,datetime,time
hh,mm,ss=map(int,sys.argv[1].split(':'))
now=datetime.datetime.now(datetime.timezone.utc)
t=now.replace(hour=hh,minute=mm,second=ss,microsecond=0)
d=(t-now).total_seconds()
assert d<500, f"leg too long: {d:.0f}s"
time.sleep(max(0,d)); print(datetime.datetime.now(datetime.timezone.utc).isoformat())
