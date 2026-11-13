# T3X WEEK 10 (Mon 11/9 – Fri 11/13): two crash nights, PAUSE, a 24-hour lockout

**E 103.61 (11/6 close) → 80.10 (Friday close, night 48 marked): −23.51 (−22.7%) on the week.**
- Realised in the account: **−23.46** on four round trips (N43 −15.84, N44 −5.43, N45 +1.04, and the share bought as N46 and sold Friday −3.23).
- Campaign since the T3X start: 98.75 → 80.10 (−18.65). Since your original $100: −19.90.
- HWM 107.11; E is 25.2% below it. PAUSE level 82.89 (E is below). KILL 50.

## The nights
| night | size | result | what happened |
|---|---|---|---|
| 43 (11/6→11/9) | NVDL ×4 | **−15.84** (−16.6%) | weekend: Nvidia's board opened a review of its CEO |
| 44 (11/9→11/10) | NVDL ×3 + NVDX ×1 | **−5.43** (−7.1%) | second day of the story plus a hot CPI print |
| 45 (11/10→11/11) | NVDL ×1 (PAUSE) | **+1.04** (+5.4%) | chip rebound |
| 46 (11/11→11/12) | NVDL ×1 (PAUSE) | **−5.72** (−27.8%), marked | the CEO resigned; NVDL opened 26% lower; the sale was missed |
| 47 (11/12→11/13) | NVDL ×1 carried | **+0.47** (+2.6%), marked | no order at either end |

- **By the rules the week's nights total −25.48.** The account lost 2.02 less than that because of two failures (Thursday's lockout, Friday's broker outage). That is luck.
- **Campaign: 47 nights, −24.00 on the strategy basis** (21 wins, 26 losses). Three nights (43, 44, 46) lost 26.99; the other 44 made +2.99.
- **PAUSE did its job.** It triggered Tuesday at 82.31. On Thursday's crash the account held one share instead of about four, which would have cost about 22 to 24.
- **Night 48 (weekend hold): NVDL 1 @ 17.8252.** The exit is Mon 11/16 at 09:31:05.

## What changed this week
- **11/9:** rules v2.1 (size follows the market trend; one symbol with a fractional top-up; weekly research loop), on your instruction to review the plan.
- **11/10:** hardened order tools (v2.2) deployed after two independent reviews. The post-mortem on your question "how are we just losing money" was verified and filed (`research/POSTMORTEM-20261110.md`).
- **11/12:** the session was locked out for 24 hours when the weekly usage allowance for its model ran out.
- **11/13:** lean running (no 8-minute scans, fewer steps, no multi-agent reviews unless needed); a mark rule for missed trades; helper scripts moved into the repo.

## Audit (lean this week: no multi-agent audit, because of the usage limit)
- **Cash path, fill by fill, from 103.58 on 11/6 to the broker's 62.29 tonight: matches to the cent**, with 0.00 unexplained.
- Ten order intents logged this week; ten broker fills; no order on 11/12; no orphan orders.
- **One rule breach:** the 09:31 sale of night 46 was missed (lockout). Friday's sale was 41 minutes late (broker outage). Both are recorded as failures.
- Thursday's records are reconstructed from bars and flagged as such. Nothing was back-filled into the live shadow samples.
- The outage itself was reviewed by five read-only agents before Friday's sale (`research/lab/20261113/outage_review_result.json`).

## Risk, plainly
- The post-mortem's numbers stand: before costs the edge is about +0.2% a night and unproven; a 2× Nvidia overnight loss of 14.5% or more has come about once a year, and this fortnight brought two.
- Nvidia now has an interim CEO, a congressional hearing request for 11/18 and earnings on 11/17. Nights will stay large in both directions.
- At one share (22% of E) a 27% overnight fall costs about 6% of the account. At normal size it costs about 27%.
- **The session itself is now a risk.** It used about a quarter of a week's allowance on Friday alone. If it locks out again while holding a position, nothing sells until the reset or until you act.

## For you to decide
1. **Usage:** turn on extra usage with a cap, move this session to a cheaper model, or keep it as is.
2. **Ultracode** (multi-agent reviews by default): keep it on or turn it off for this session.
3. **Memory:** running `/compact` in this session about once a day would cut the cost of every step by half or more. I cannot run it myself.
4. **Watchdog** (alerts your phone if I go silent; no broker access): schedule it, yes or no. The platform refused my attempt.
5. **Daily "sale done" alert at about 09:35 ET:** yes or no.

## Next week
- **Sat 11/14, 14:23:** lab cycle, single-threaded (earnings-night test). No orders.
- **Mon 11/16:** §3(f) edge-decay check before anything else; sell night 48 at 09:31; night 49 at 15:52 (PAUSE session 5 of 5).
- **Tue 11/17:** sell at 09:31; **no purchase** (Nvidia reports after the close).
- **Wed 11/18:** re-enter at 15:52. Normal size returns only if equity is above 82.89; otherwise PAUSE continues at one share.
- **Thu 11/26:** market closed. **Fri 11/27:** half day (trend read 12:50, purchase 12:52).
