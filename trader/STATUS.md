# T2X STATUS
mode: IN_POSITION (S1 MUU 1sh @35.59, stop GTC 33.76)
zone: STANDARD f=1.0 r=6% | PRESS no | DOWNSHIFT no
E_broker/E_bid/E_adj: 100.00 / 100.00 / 100.00 | day P/L: 0 | HWM: 100.00
D=10 g=7.2%/session vs glide 106.5 (behind, PRESS possible from session 3)
active pair: SOX regime (SOXL ATR ~12) BUT SOXL unaffordable whole-share at E=100 -> long-semis leg = MUU (Tier B intraday) / NDX pair for carries; SOXS affordable for down legs
position: MUU 1sh entry 35.5899 stop 34.34 GTC (trailed 11:00) openP/L +0.27R; time-stop 12:01 if < 36.51
entries: 1 today / 1 week / 1 campaign | budget: IM_FREE
account_mode: IM_FREE (RH limited_margin ••••8334; evidence in capabilities.json)
stops: NATIVE(GTC)+SYNTHETIC | data: REALTIME quotes+SIP bars | ext_hours: OK
wake cadence: every decision boundary while flat; 1-min chain while in position; crons as backstop
last error: none | open alerts: none
to stop me: create trader/HUMAN_STOP (or tell me in chat); after HALTED/DONE disable the routines
