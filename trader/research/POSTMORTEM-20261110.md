# Post-mortem of the losses, 2026-11-10

The owner asked on 11/10: "how are we just losing money? you can do better." This is the answer, checked by four independent read-only analysts and one adversarial reviewer. None had broker access. Raw output and scripts: `research/lab/20261110/postmortem/`.

## The short answer

The account did not bleed slowly. On Friday 11/6 it stood at 103.61, above its 98.75 start. It then held about 90% of its money in a fund that moves twice as much as NVIDIA through two nights on which NVIDIA fell. Those two nights lost 21.27. The other 42 nights together made 1.50.

Nights like that are part of this strategy, and there is no proven profit to absorb them. Three fixes were checked. None holds.

## Where the money went

Account: 98.75 → 82.41, down 16.34. Overnight trades lost 19.76; the suspended day leg had made 3.24.

| Piece of the overnight loss | Dollars |
|---|---|
| Night 43 (Fri 11/6 → Mon 11/9, the CEO-review weekend) | −15.84 |
| Night 44 (Mon 11/9 → Tue 11/10) | −5.43 |
| The other 42 nights | +1.50 |
| **Total** | **−19.76** |

The same total split another way, in exact dollars:

| Source | Dollars |
|---|---|
| Close-to-open move of what was held | −9.61 |
| Sells below the official open | −7.29 |
| Buys above the official close | −2.85 |

- The first era (nights 1–24, a mixed basket) made +3.28. The NVDA-only era (nights 25–44) lost 23.04.
- Over the campaign NVIDIA fell 24.5% and the 2× fund 45.7% if simply held. Holding only overnight lost far less than that.

## What the timing numbers do and do not mean

My first reading was that about half the loss was my trade timing and could be fixed. The review showed that reading was too strong.

- **Counted by night, neither gap is statistically solid.** Sells: −0.21% a night against the official open (t −1.6; 90% interval −0.42% to 0.00%). Buys: −0.08% (t −1.3). I had quoted larger t-values that counted two orders sent in the same minute as separate observations.
- **The sell gap is price movement, not bad fills.** It is how the price moved in the 65 seconds between the open and my order. Fills were at or above the quoted bid. In 167 earlier mornings that movement averaged +3bp and had no link to the prior trend.
- **The buy gap belongs to funds no longer traded.** METU, AAPU and AMZU account for 2.67 of the 2.85. NVDL and NVDX entries cost 0.19 over 39 nights.
- **At-limit fills are genuine.** 15-second bars for 11/10 and 11/6 show the price was already below my limit when the order arrived; the order then filled on the bounce, above the market at arrival.

## Is there an edge at all?

- Before costs, a 2× NVIDIA overnight position earned about +0.25% a night in 2015–26, and +0.15% without earnings nights, which the engine sits out (t 2.5; the 95% interval reaches zero).
- NVIDIA was picked with hindsight. Ten other large technology stocks average +0.04% a night on the same calculation.
- Live fills ran 0.28% a night behind the official prices. If that persisted, nothing would be left. If only 0–10bp of it repeats, the net edge is about +0.1% to +0.15% a night.
- 44 nights cannot tell an edge of +0.15% from zero: the standard error is 0.61% a night. A result this bad is roughly a 1-in-5 to 1-in-10 draw even if the edge is real.
- The rules planned on +0.30% a night. That figure was too high and has been corrected in `RULES_v3.md` and `STATUS.md`.

## The three fixes that were checked

| Fix | Result | Decision |
|---|---|---|
| Sell at the opening price instead of 09:31 | Worth between −$1.70 and +$1.70 a month at full size; the sign is unknown, and Robinhood's documents conflict on whether an order queued before the open fills in the opening auction. About 500 mornings would be needed to confirm a benefit. | Not adopted. The one-share pilot I wrote down that afternoon is withdrawn: it contradicted the test fixed in advance in §3(g). The 09:29 shadow log continues. |
| Buy at the close instead of 15:52 | No gap on NVDL (2.7bp, t 0.3). | Closed. |
| Split the position with an index fund (TQQQ) | Failed its pre-registered test: it gave up 0.07% to 0.12% a night of growth against an allowance of 0.01%, and was no safer in a crash. It did cut volatility by a quarter. | Rejected. No other weight will be tried. |

## What to expect from here

Under the present rules, from 82.41, on the reviewer's corrected simulation:

- After one year the median is about 75 to 95.
- 25% to 45% chance of being back above 98.75 within a year; 2% to 3% within 20 nights.
- 10% to 20% chance of reaching the 50 stop.
- A 2× NVIDIA overnight loss of 14.5% or more, outside earnings, has come about once a year. Losses of 25% or more came three times since 2019. Five of the 16 worst such nights since 2015 came with QQQ above its trend line, when the engine holds full size.
- At $82 even a real edge pays about $1 to $3 a month, against monthly swings near $10. During PAUSE (one share, market below its trend line) the expectation is about zero.

## What can and cannot be done

- **Research cannot fix this.** No tested change shows a benefit, and searching for new variants on a 44-night sample would mostly find noise.
- **Position size is the one lever that works**, and it only trades swings for expected dollars: half size halves both; cash is zero of both.
- **Default, unless the owner says otherwise:** the campaign keeps running under the present rules (the owner's standing instruction), with PAUSE at one share through 11/16 and cash on the 11/17 earnings night.

## Errors in my own records, corrected

- t-values in the lab ledger and journal counted legs, not nights.
- "Half market, half timing" set a random draw beside a noisy estimate as if both were known costs; the three components as first written also left out a +0.38 cross term.
- Close-to-open figures quoted for TQQQ, SOXL, UPRO and QQQ covered 43 nights, not 44.
- The ledger said an earlier test found blends "a wash"; that was true only of SOXL.
- The 11/10 journal said the bid stayed above my limit while the sells rested; it had not.
- The profit column of `trades.csv` changes units in nights 1–11 and sums to −15.69; fills give −19.76.
- The options sleeve odds in §12 rest on the old planning edge and are marked stale.
