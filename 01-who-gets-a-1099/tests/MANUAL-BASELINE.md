# Manual baseline: doing the same 12 files by hand

**Status: estimated, not measured.** No accountant has been timed yet. The counts below
are exact (they come from the test files). The minutes are those counts multiplied by
three assumed rates. Replace this table with stopwatch times after the real-accountant
test in `ACCOUNTANT-TEST-SCRIPT.md`.

## The steps by hand

This is the procedure practitioners describe ("We print out the GL for the year or YTD
and manually search the transactions for Vendors eligible for 1099's",
[Intuit Accountants Community](https://accountants.intuit.com/community/easyacct-discussions/discussion/how-to-print-1099-vendor-list/00/229893)):

1. Print or open the year's payments by vendor.
2. Read every line. For each vendor decide what the payments were for: services, rent,
   legal, medical (candidates) or goods, utilities, payroll, taxes (not candidates).
3. For each candidate, strike the lines paid by card or PayPal.
4. Add up what is left on a calculator. Compare with the limit.
5. Look for the same vendor under another spelling and add those together.
6. Write the vendor, the amount and the form on the 1099 list. Note whether a W-9 is on file.
7. Nothing in the manual method ties the list back to the file total, catches a duplicated
   check, or notices that a subtotal is wrong, unless the preparer happens to see it.

## Counted work and estimated time

Assumed rates: 4 seconds to read a line, 20 seconds to judge a vendor, 60 seconds to
subtotal and write up a vendor that is not an obvious "no".

| Case | Lines to read | Vendors to judge | Vendors needing a subtotal and write-up | Estimated minutes by hand |
|---|---|---|---|---|
| 01 | 36 | 8 | 5 | 10 |
| 02 | 25 | 9 | 6 | 11 |
| 03 | 268 | 18 | 7 | 31 |
| 04 | 15 | 8 | 5 | 9 |
| 05 | 55 | 13 | 7 | 15 |
| 06 | 12 | 6 | 3 | 6 |
| 07 | 21 | 7 | 4 | 8 |
| 08 | 19 | 5 | 3 | 6 |
| 09 | 8 | 4 | 3 | 5 |
| 10 | 9 | 3 | 2 | 4 |
| 11 | 8 | 3 | 1 | 3 |
| 12 | 18 | 4 | 3 | 6 |
| **All 12** | **494** | **88** | **49** | **111** |

Cases 13 and 14 are files the agent must refuse; by hand they take a glance.

Only case 03 is the size of a real small-business year (268 lines). The others are
deliberately short so each hard case can be checked by eye. A real client file of 1,000
lines would scale the reading time, not the judgment time.

## Errors the manual method is exposed to in these files

These are planted in the test files. Whether a person catches them depends on attention;
the estimate above includes no time for looking.

| Case | What is wrong | Consequence if missed |
|---|---|---|
| 04 | One plumber typed three ways, $700 + $800 + $900 | No 1099 issued for a $2,400 vendor |
| 02 | $1,500 of a $2,300 vendor was paid by card | A 1099 issued that is not required |
| 09 | A $1,200 check listed twice | A 1099 issued for $2,400 to a vendor paid $1,200 |
| 10 | Vendor subtotal says $4,300, lines add to $3,100 | A 1099 issued for the wrong amount, or a missing payment never found |
| 11 | Three December 2025 payments in a 2026 file | A vendor paid $1,300 in 2026 treated as $2,200 |
| 05 | "Hartwell & Dunn, P.C." coded to Legal & Professional | A law firm skipped because it is a corporation |
