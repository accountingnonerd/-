# Results: Record-to-Report 01, "Did last year change?"

Version 1.0.0, run 2026-11-13 with `node run-tests.js` against `agent/did-last-year-change.html`.

**22 of 22 cases passed; 343 of 343 individual checks.**

The acceptance test has 22 cases and 43 files: 1 clean, 7 with a planted change or problem, and 14 ugly
(other layouts, wrong exports, rounding, renamed and merged accounts). The answer key is worked out
in `make_cases.py` from a ledger model of four invented companies and the change planted in each,
never by reading the files back.

## Case by case

| Case | What it is | Type | Expected verdict | Checks passed | Run time (ms) | Result |
|---|---|---|---|---|---|---|
| 01 | Nothing changed (QuickBooks Online) | clean | AGREES | 11/11 | 135 | PASS |
| 02 | Planted: a December deposit deleted after filing | planted | CHANGED | 25/25 | 117 | PASS |
| 03 | Planted: a backdated bill, and office supplies moved to meals | planted | CHANGED | 31/31 | 129 | PASS |
| 04 | Planted: a 2024 equipment purchase re-entered as an expense (Desktop) | planted | CHANGED | 25/25 | 163 | PASS |
| 05 | Her adjusting entries never posted; workpaper in whole dollars | ugly | CHANGED | 33/33 | 136 | PASS |
| 06 | Xero: one account renamed, nothing else changed | ugly | AGREES | 12/12 | 124 | PASS |
| 07 | Office Supplies merged into Office Expenses | ugly | CHANGED | 12/12 | 130 | PASS |
| 08 | Today's report run for the wrong year | ugly | NOT_COMPARABLE | 7/7 | 102 | PASS |
| 09 | Today's report on cash basis, last year's on accrual | ugly | NOT_COMPARABLE | 7/7 | 95 | PASS |
| 10 | Planted: a 2025 check voided; last year's CSV has a mistyped total and no date | planted | CHANGED | 26/26 | 110 | PASS |
| 11 | Last year's file is a post-closing trial balance | ugly | AGREES | 11/11 | 112 | PASS |
| 12 | Account numbers turned off since last year; one account renamed | ugly | AGREES | 12/12 | 114 | PASS |
| 13 | Planted: the client's books do not balance (Desktop) | planted | CHANGED | 16/16 | 140 | PASS |
| 14 | The wrong report: a balance sheet in place of a trial balance | ugly | NOT_COMPARABLE | 7/7 | 101 | PASS |
| 15 | The same file given twice | ugly | NOT_COMPARABLE | 7/7 | 115 | PASS |
| 16 | Files put in the wrong boxes (workpaper given as today's) | ugly | AGREES | 13/13 | 132 | PASS |
| 17 | Planted: a $5,000 distribution added to last year after filing | planted | CHANGED | 19/19 | 130 | PASS |
| 18 | Post-closing final with distributions closed into retained earnings | ugly | AGREES | 11/11 | 99 | PASS |
| 19 | Her workpaper in Debit/Credit pairs, rounding put in retained earnings; depreciation not posted | ugly | CHANGED | 25/25 | 115 | PASS |
| 20 | A cash-basis export that does not say it is cash basis | ugly | NOT_COMPARABLE | 7/7 | 95 | PASS |
| 21 | The wrong client's file in box 2 | ugly | NOT_COMPARABLE | 8/8 | 118 | PASS |
| 22 | Planted: all of last year's meals moved into office expenses | planted | CHANGED | 18/18 | 149 | PASS |

## What went wrong along the way

### First run: 10 of 16
- **The answer key was wrong.** It said Harbor Light had 34 accounts; it has 33. The key now
  counts the accounts from the model instead of a typed number.
- **A title read as column headings.** The workpaper's title "Trial balance, final, December 31,
  2025" contains "final", and the balance sheet report's title starts with "Balance". Both were
  taken for the heading row. A heading row now has to name at least two columns.

### The accounting review
A separate AI session, told to act as a skeptical CPA who prepares business returns, read the
source and ran it on its own trial balances. It found twelve problems. What changed:
- **The entry could count a transaction twice.** If the client deleted a deposit and entered it
  again in January, the drafted entry would restore it as well. The page now says to undo or
  re-date the client's change in last year first, and to post the entry only if the transaction was
  not entered again this year.
- **Owners' accounts were treated as ordinary balance sheet accounts.** A distribution added to last
  year moves K-1s, Schedule M-2 and basis, and a correcting line dated this year would read as this
  year's distribution. These accounts now get their own warning, and no entry is drafted (case 17).
- **A guessed merge could hide a real change.** Meals moved in full into office expenses looked like
  a merge and gave "still agrees", losing the meals limit. A merge now needs the two names to share a
  word, never gives "still agrees", and says the return's lines no longer tie (cases 07 and 22).
- **Post-closing files with distributions closed** (textbook practice) gave a false change. The other
  file's distributions are now closed the same way (case 18).
- **Rounding was too generous.** Rounding to the dollar cannot make a difference over 50 cents; the
  allowance was 99 cents. It is now 50 cents per account, plus up to $5 in retained earnings where a
  workpaper puts its rounding, and a whole-dollar file out of balance by $5 or less is compared
  rather than stopped.
- **Adjustment columns as Debit and Credit pairs lost every credit.** They are now read (case 19).
- **Basis is often not stated.** QuickBooks Desktop prints it outside the cells, and workpapers rarely
  say. A file with no receivables or payables, against a final that has them, now stops as a likely
  cash-basis export (case 20).
- **The wrong client's file** was compared account by account. Fewer than half the accounts matching
  now stops the comparison (case 21).
- **Two files without dates crashed the page.** Fixed.
- **Wording:** "profit changed" now counts only the client's changes, not your unposted adjustments or
  rounding; a change to retained earnings says which direction; an expense account with a credit
  balance is no longer called "income"; and "zero or not in the export today" replaces "deleted".
  The page also notes payroll, sales-tax and 1099 effects, the prior-period adjustment route when she
  will not amend, and setting a closing or lock date afterwards.

Not changed, and listed as limits: tax-only adjustments in her workpaper are reported as "not posted"
(the page tells her to leave them out); partnerships' capital is not split by partner; the export
date of the client's file is not checked against the date of her final.

### The cold-user check
A separate AI session played a 60-year-old partner who had never seen the tool, using only
screenshots. It understood the start screen in about ten seconds. What changed:
- the conditions for posting the entry were generic and sat under the table. They are now specific
  to the case ("your adjustments: one or the other, never both"; "the client's changes: undo them
  first") and sit above it;
- box 1 now says "your adjusted trial balance, after your adjusting entries" and "Excel or CSV"; a
  PDF gets a plain refusal;
- the likely cause is named: "Checking and Bakery Sales are both $4,250.00 lower: it looks like a
  deposit or sale in last year was deleted or voided";
- stop messages were printed twice; parentheses around "lower" read as negative numbers; the
  sign-off lines appeared on a page that compared nothing. All fixed.

## Broken on purpose: do the tests notice?

Each copy below has one rule removed or reversed, applied to the final build.

| Copy | What was broken | Result |
|---|---|---|
| m01 | No rounding allowance for a whole-dollar final | caught, 3 cases fail |
| m02 | Your unposted adjustments not recognized | caught, 2 |
| m03 | Xero's month columns read instead of year-to-date | caught, 2 |
| m04 | No check that both files are for the same date | caught, 1 |
| m05 | Sign of last year's profit change reversed | caught, 6 |
| m06 | Merged accounts not recognized | caught, 1 |
| m07 | The entry's retained earnings line on the wrong side | caught, 6 |
| m08 | An export date and time above the headings read as the balance date | **not caught** |
| m09 | Post-closing files not recognized | caught, 2 |
| m10 | A file's own total line not checked | caught, 1 |
| m11 | Account numbers ignored when matching | caught, 1 |
| m12 | Files in the wrong boxes not swapped back | caught, 1 |
| m13 | Owners' accounts treated as ordinary balance sheet accounts | caught, 1 |
| m14 | A cash-basis export that does not say so, not suspected | caught, 1 |
| m15 | The wrong client's file not detected | caught, 1 |
| m16 | Distributions not closed against a post-closing final | caught, 1 |
| m17 | Adjustment Debit and Credit columns ignored | caught, 1 |
| m18 | A merge guessed without a shared word in the names | caught, 1 (after case 22 was added; it survived the first time) |

**m08 is not caught.** No test file puts an export date and time above the column headings:
QuickBooks Online prints its export time in the footer, where the tool never looks for the date,
and the Desktop and Xero layouts here have none. The rule is unproved until a layout with one is added.

## Rebuild from the prompt

See the bottom of this file once the rebuild check has run.
