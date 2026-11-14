# Results: Order-to-Cash 01, "Does the 1099-K tie?"

Version 1.0.0, run 2026-11-14 with `node run-tests.js` against `agent/does-the-1099k-tie.html`.

**14 of 14 cases passed; 660 of 660 individual checks.**

The acceptance test has 14 cases from a transaction model of three invented businesses (a café on
Square, an online shop on Stripe, a print seller on PayPal): 3 clean, 4 with a planted problem and
7 ugly. Each case checks the status, every warning, box 1a, box 3, the twelve monthly boxes, the
bridges to the return and the bank, and every line of the entry. The answer key is worked out in
`make_cases.py` from the model, never by reading the files back.

## Case by case

| Case | What it is | Type | Expected verdict | Checks passed | Run time (ms) | Result |
|---|---|---|---|---|---|---|
| 01 | Square café, full year: cash, gift cards, tips and sales tax | clean | COMPUTED | 48/48 | 211 | PASS |
| 02 | Square café with the 1099-K typed in: it ties | clean | TIES | 50/50 | 249 | PASS |
| 03 | Stripe shop: refunds, disputes, a euro charge, dates in UTC only | ugly | COMPUTED | 54/54 | 81 | PASS |
| 04 | PayPal seller: refunds, personal transfers, a bank top-up, a hold, a chargeback, a euro sale, a purchase from the balance | ugly | COMPUTED | 58/58 | 95 | PASS |
| 05 | Planted: two exports pasted together, June counted twice | planted | COMPUTED | 50/50 | 213 | PASS |
| 06 | Planted: a Stripe export with no September | planted | COMPUTED | 48/48 | 96 | PASS |
| 07 | A PayPal export from December 2024 to January 2026 | ugly | COMPUTED | 49/49 | 73 | PASS |
| 08 | Planted: the 1099-K includes a second location not in this export | planted | DIFFERS | 51/51 | 273 | PASS |
| 09 | Square export in Excel with a totals row, blank lines, parentheses | ugly | COMPUTED | 48/48 | 260 | PASS |
| 10 | Not a processor export: a bank statement | ugly | NOT_RECOGNIZED | 5/5 | 47 | PASS |
| 11 | Square: partial refunds, and a January refund of a December 2024 sale | ugly | COMPUTED | 51/51 | 167 | PASS |
| 12 | PayPal: a pending and a denied payment | ugly | COMPUTED | 48/48 | 84 | PASS |
| 13 | Stripe with local dates and the 1099-K typed in: it ties | clean | TIES | 48/48 | 134 | PASS |
| 14 | Planted: the 1099-K typed in is lower than the year's payments | planted | DIFFERS | 52/52 | 136 | PASS |

## What went wrong along the way

### First run: 8 of 14
Box 3, the number of payment transactions, counted cash-only sales. A cash sale is a sale, but not
a 1099-K payment. Every Square case failed on that one figure.

### The tax review
A separate AI session, told to act as a skeptical CPA who handles 1099-K reconciliations and IRS
notices, read the source. It found sixteen problems; the ones that changed answers:
- **Gift cards were counted twice.** A gift card sold by card is already in the 1099-K and in gross
  receipts; the tool added the redemption again. Redemptions are now left out (with a note for
  accrual-method deferral).
- **Sales tax on cash sales stayed in gross receipts** when tax was taken out, because only the card
  share was removed.
- **Sales tax and tips were taken out of gross receipts by default.** In California, and in states
  whose tax falls on the seller (Arizona, Hawaii, New Mexico), sales tax belongs in gross receipts with
  a deduction; a sole owner keeps the tips. Gross receipts now include both, matching the 1099-K, and
  leaving them out is a box the accountant ticks, with a warning that line 1 will then be below the
  1099-K.
- **PayPal payments marked "Refunded" dropped out of gross.** PayPal re-labels a refunded payment; it
  was still paid. They now count (case 04).
- **The entry left the books short** of the money still held by the processor, and treated personal
  transfers and bank top-ups as sales. It now has lines for both, and states that sales after the
  entry equal the 1099-K gross.
- **No 1099-K may come at all:** PayPal need not issue one below $20,000 and 200 transactions. The page
  now says so (four PayPal cases).
- **A supplier's refund through PayPal would have counted as a sale,** and purchases paid from the
  balance went unremarked. Both are now "other activity" to classify (case 04).
- Also: the two year-end edges of a UTC export are now reported separately, with both possible box
  1a figures; merchant fees name their lines; a missing month asks rather than stops.

Not changed, and listed as limits: the 1099-K form itself is not read (payee TIN, backup withholding,
state boxes); the page lists them as checks. Shopify, Venmo, marketplaces and Square's Transfers
report are not read.

### The cold-user check
A separate AI session played a 60-year-old partner, from screenshots only. It understood the start
screen in about ten seconds. What changed:
- the bank bridge's bold total was not the sum of the lines above it; it now foots top to bottom;
- when the 1099-K does not tie, the page kept offering figures for the return; it now says "not for
  the return yet" above them, and opens the months;
- the euro sale was knowingly left out of gross; it is now included at PayPal's rate;
- box 1a can be typed before the file is dropped, so the first answer is "ties" or "does not";
- client name and EIN lines on the workpaper; the monthly boxes no longer run off the page.

## Broken on purpose: do the tests notice?

Seventeen copies, each with one rule removed or reversed, run against the final build. **All 17 were
caught.**

| Copy | What was broken | Cases that failed |
|---|---|---|
| m01 | Cash sales counted in 1099-K gross | 6 |
| m02 | Refunds netted out of gross | 3 |
| m03 | Duplicate lines not removed | 1 |
| m04 | Missing months not checked | 1 |
| m05 | Personal transfers counted as sales | 1 |
| m06 | Foreign-currency sales left out | 1 |
| m07 | Pending and denied payments counted | 1 |
| m08 | Refunded PayPal payments dropped from gross | 1 |
| m09 | Gift card redemptions added to gross receipts | 6 |
| m10 | Sales tax on cash sales left in | 6 |
| m11 | UTC dates not flagged | 1 |
| m12 | Every sale treated as paid out in the year | 6 |
| m13 | The entry ignores the processor's balance | 13 |
| m14 | Dispute reversals not netted | 1 |
| m15 | Box 1a typed in but not compared | 2 |
| m16 | A supplier's refund counted as a sale | 1 |
| m17 | The year chosen as the latest, not the busiest | 3 |

## Rebuild from the prompt

A fresh AI session was given only `REBUILD-PROMPT.md` (and the spreadsheet library) and told not to
look at anything else. What it built was run through the same acceptance test.

| Rebuild | Result | What went wrong | What changed in the prompt |
|---|---|---|---|
| 1 (`rebuild-check/rebuild-1.html`) | 12 of 14 cases, 658 of 660 checks | It reported duplicates as an object, not a number, and showed the "not an export I know" refusal outside the element the test reads. Every figure was right. | `duplicates` is a plain number; refusals go in `#problem`. |
| 2 (`rebuild-check/rebuild-2.html`) | **14 of 14 cases, 660 of 660 checks** | Nothing. | None. |

"The same agent" means a build that passes these 14 cases. Rebuild 2 differs from the original in
wording, layout and choices the prompt left open, and is the same agent by that test.
