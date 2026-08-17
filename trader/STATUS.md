# T2X STATUS
mode: FLAT (session 2; S1 ARMED from open — MUU gap +6.1%)
zone: STANDARD f=1.0 r=6% | PRESS no | DOWNSHIFT no
E_broker/E_bid/E_adj: 100.00 / 100.00 / 100.00 | day P/L: 0 | HWM: 100.00
D=10 g=7.2%/session vs glide 106.5 (behind, PRESS possible from session 3)
active pair: SOX regime (SOXL ATR ~12) BUT SOXL unaffordable whole-share at E=100 -> long-semis leg = MUU (Tier B intraday) / NDX pair for carries; SOXS affordable for down legs
position: none | armed: S1 MUU/SOXS 09:40-10:30 + S2 10:00-14:30; S3 OFF
entries: 0 today / 0 week / 0 campaign | budget: IM_FREE, no day-trade cap
account_mode: IM_FREE (RH limited_margin ••••8334; evidence in capabilities.json)
stops: NATIVE(GTC)+SYNTHETIC | data: REALTIME quotes+SIP bars | ext_hours: OK
wake cadence: every decision boundary while flat; 1-min chain while in position; crons as backstop
last error: none | open alerts: none
to stop me: create trader/HUMAN_STOP (or tell me in chat); after HALTED/DONE disable the routines
