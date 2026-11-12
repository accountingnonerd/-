# Manual baseline: the same reconciliation by hand

**Status: estimated, not measured.** No accountant has been timed yet. The counts are exact
(they come from the forms). The minutes are those counts multiplied by assumed rates.
Replace them with stopwatch times after the test in `ACCOUNTANT-TEST-SCRIPT.md`.

## The steps by hand
This follows the IRS General Instructions for Forms W-2 and W-3 (2026), "Reconciling Forms W-2,
W-3, 941...":
1. Open the four 941s and the W-3. In a year-end packet, find them among the vouchers,
   second pages and W-2s.
2. Copy ten figures from each 941 into a spreadsheet: lines 2, 3, 5a, 5b and 5c
   (column 1 and column 2), 5d column 2, 5e and 7. That is 40 figures.
3. Copy seven W-3 boxes (1 to 7).
4. Add the quarters. Compare boxes 1, 2, 3, 5 and 7 with their lines.
5. Compare the 941 taxes with twice boxes 4 and 6, remembering the Additional Medicare Tax
   is withheld from the employee only. This is the step most often skipped.
6. If anything differs, work out which quarter or form causes it.
7. Write it up for the payroll file.

## Estimated time

Assumed rates: 10 seconds to find and copy one figure; 1 minute for each of the six
comparisons; 5 minutes to write it up. Finding the cause of a difference: 10 minutes for
each case that has one.

| Case | Figures to copy | Comparisons | A difference to explain? | Estimated minutes by hand |
|---|---|---|---|---|
| 01, 02, 03, 11 (agree) | 47 | 6 | no | 19 each |
| 04, 07, 08, 12 (do not agree) | 47 | 6 | yes | 29 each |
| 06, 09, 10 (a quarter missing or unusable) | 37 to 47 | 6 | yes | 27 to 29 each |
| 05 (two different Q2 941s) | 57 | 6 | yes | 30 |
| 15 (no W-3) | 40 | 0 | no | 12 |

That is about **5 hours** for the 13 cases that contain payroll forms. A single clean client
takes about 20 minutes.

## What the manual method is exposed to in these files

| Case | What is wrong | Consequence if missed |
|---|---|---|
| 04 | New provider's W-3 leaves out January to June | Letter 99C two years later for about $107,000 of wages "missing" from the W-2s |
| 07 | A 941's Medicare tax is $90 more than 2.9% of its wages | An overstated 941 that nobody notices because line 5e adds up |
| 08 | Two digits swapped in W-3 box 3 | SSA records $27,000 less in social security wages than the 941s |
| 11 | The first quarter was filed under an old EIN, and W-3 box h is blank | The IRS cannot match that quarter to the W-3 |
| 12 | A 941-X is on file, and the W-3 includes its correction | A difference that looks like an error but is explained by the amendment |
