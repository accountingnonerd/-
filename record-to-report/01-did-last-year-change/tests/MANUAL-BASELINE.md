# Manual baseline: the same check by hand

**Status: estimated, not measured.** No accountant has been timed yet. The counts are exact
(they come from the test files). The minutes are those counts multiplied by assumed rates.
Replace them with stopwatch times after the test in `ACCOUNTANT-TEST-SCRIPT.md`.

## The steps by hand
1. Find last year's final (adjusted) trial balance in the workpapers.
2. Run the client's trial balance for the same date, on the same basis, and export it.
3. Put the two side by side in Excel. Line the accounts up: they are rarely in the same
   order or spelled the same way, and zero balances drop out of one export but not the other.
4. Subtract, account by account. Ignore rounding if last year's figures are whole dollars.
5. For each difference, work out what it means: income statement (last year's profit
   changed), balance sheet, retained earnings (an earlier year changed), or her own
   adjustment that was never posted.
6. Write the correcting entry and the questions for the client.

## Estimated time

Assumed rates: 20 seconds to line up and compare one account; 3 minutes to set up the two
files side by side; 5 minutes to work out and write up each difference (or each pair that
moves together); 5 minutes for the entry and the client questions when anything changed.

| Case | Accounts to line up | Differences to explain | Estimated minutes by hand |
|---|---|---|---|
| 01, 06, 11, 12, 16 (agree) | 13 to 34 | 0 (06, 12: a renamed account to recognize) | 8 to 15 each |
| 07 (merged account) | 34 | 1 pair | 19 |
| 02, 10 (one transaction changed) | 33 to 34 | 1 pair | 19 to 24 each |
| 03 (a backdated bill, and a reclassification) | 34 | 2 pairs | 24 |
| 04 (an earlier year changed) | 28 | 1 pair | 22 |
| 05 (adjustments not posted, whole dollars) | 34 | 2 entries, plus 18 rounding differences to dismiss | 27 |
| 13 (books do not balance) | 28 | 1, and a damaged file | 22 |
| 08, 09, 14, 15 (wrong date, basis, report, same file) | n/a | caught only if she looks at the headings | 1 to 3 each, or a wasted half hour if she does not |

That is about **4 hours** for the 16 cases. A client whose books still agree takes 10 to 15
minutes; a client whose books changed takes 20 to 30 minutes, before any time spent
tracing the transactions in the audit log.

The tool takes under a second per case and states the result on one page. The time it
does not save: tracing the client's transactions, deciding whether to amend, and talking
to the client.

## What the manual method is exposed to in these files

| Case | What is wrong | Consequence if missed |
|---|---|---|
| 02 | A December deposit of $4,250 deleted after filing | Opening cash is wrong; if the client re-enters it this year, the income is reported twice |
| 03 | A $1,860 bill backdated into the closed year; $640 moved from office supplies to meals | Opening payables wrong; meals are only partly deductible, so the return's lines no longer match the books |
| 04 | A 2024 equipment purchase re-entered as an expense | Retained earnings and fixed assets no longer agree with Schedule L; depreciation schedule out of step |
| 05 | Her depreciation and accrued wages entries were never posted | This year's books start $11,150 off; depreciation taken twice or not at all |
| 09 | Today's trial balance run on cash basis | Every receivable and payable looks like a difference; hours spent on a false alarm |
| 10 | A 2025 check voided after filing; last year's total typed wrong | A $975 change hidden among a total that never balanced |
| 13 | The client's file does not balance | Any entry posted on top of a damaged file makes it worse |
