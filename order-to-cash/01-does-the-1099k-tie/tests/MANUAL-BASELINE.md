# Manual baseline: the same reconciliation by hand

**Status: estimated, not measured.** No accountant has been timed yet. The minutes are counts from
the test files multiplied by assumed rates. Replace them with stopwatch times after the test in
`ACCOUNTANT-TEST-SCRIPT.md`.

## The steps by hand
1. Ask the client for the processor's export for the year; open it in Excel.
2. Filter out what is not a card or app sale: refunds, payouts, holds, transfers, cash tenders.
3. Pivot gross by month; compare with boxes 5a to 5l and box 1a.
4. Separate sales tax and tips; add cash sales; total refunds, chargebacks and fees.
5. Tie gross less refunds and fees to the deposits in the bank, allowing for year-end timing.
6. Write the reconciliation for the file and, if the books recorded deposits as sales, the entry.

## Estimated time

Assumed rates: 10 minutes to open and clean an export; 10 minutes for the pivot and the 1099-K
comparison; 10 minutes for tax, tips, cash, refunds and fees; 10 minutes to tie to the bank; 10
minutes to write it up. Add 15 minutes for each problem to find (a duplicate month, a missing
month, a second location, personal transfers, a currency, UTC dates).

| Case | Lines in the export | Problems to find | Estimated minutes by hand |
|---|---|---|---|
| 01, 02, 09, 13 (clean or merely messy) | 870 to 1,860 | 0 | 50 each |
| 03 (Stripe in UTC, disputes) | 720 | 2 | 80 |
| 04 (PayPal: transfers, a hold, a chargeback, a euro sale, a purchase) | 250 | 4 | 110 |
| 05, 06, 08, 14 (pasted, missing month, second location, lower 1099-K) | 230 to 1,870 | 1 to 2 | 65 to 80 |
| 07, 11, 12 (outside the year, last year's refund, unsettled) | 220 to 1,290 | 1 | 65 each |

About **12 hours** for the 13 processor files. A clean client takes about 50 minutes.

## What the manual method is exposed to in these files

| Case | What is wrong | Consequence if missed |
|---|---|---|
| 01 | $2,733.84 of sales tax and $4,034.52 of tips inside the 1099-K; $10,527.00 of cash sales outside it | Line 1 wrong in either direction; an IRS notice if it comes in below the 1099-K unexplained |
| 05 | June pasted in twice | Gross overstated by a month's sales |
| 06 | No September in the export | Gross understated; a notice if the 1099-K has September |
| 08 | The 1099-K includes a second location | Gross receipts $2,184.00 below the 1099-K |
| 04 | $310.00 of personal transfers, a $45.00 supplier refund | Either counted as sales, or customer payments missed |
