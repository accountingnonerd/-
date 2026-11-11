# Test results: Who gets a 1099?

Version 1.1.0 changed only wording: the start screen and the "File a 1099" section now say what the tool adds to the software's own 1099 report. Every test below was rerun on 1.1.0 with the same result.

Run on 2026-11-11 in headless Chromium. Rerun with `node run-tests.js`.

## 1. Acceptance test, case by case

**15 of 15 cases passed; 476 of 476 individual checks.**

| Case | What it is | Type | Payment lines | Checks passed | Run time (ms) | Result |
|---|---|---|---|---|---|---|
| 01 | Clean file, one line per payment | clean | 36 | 37/37 | 89 | PASS |
| 02 | Same vendor paid by check and by card; PayPal, Venmo, Zelle; royalties | rules | 26 | 44/44 | 85 | PASS |
| 03 | Full year, grouped by vendor with subtotal rows (Excel) | ugly | 268 | 58/58 | 167 | PASS |
| 04 | Same vendor typed three ways; look-alike vendors | ugly | 15 | 37/37 | 81 | PASS |
| 05 | Attorneys, medical, "Inc." vendors, payroll, taxes, owner draws (Excel) | rules | 59 | 52/52 | 108 | PASS |
| 06 | Messy export: mixed date and number formats, a refund, an unreadable line, a blank payee | ugly | 13 | 36/36 | 74 | PASS |
| 07 | Bank-style export: payments are negative numbers, no category column | ugly | 21 | 34/34 | 69 | PASS |
| 08 | Ledger export with Debit/Credit columns and a Split column | ugly | 19 | 31/31 | 79 | PASS |
| 09 | PLANTED ERROR: duplicated check lines | planted | 8 | 29/29 | 86 | PASS |
| 10 | PLANTED ERROR: subtotal and grand total do not match the lines | planted | 9 | 27/27 | 85 | PASS |
| 11 | PLANTED ERROR: prior-year lines mixed in and the year is incomplete | planted | 8 | 26/26 | 69 | PASS |
| 12 | A 2025 check register with Payment and Deposit columns: the old $600 limit | rules | 19 | 29/29 | 65 | PASS |
| 13 | A 2027 file: rules not built in, must refuse | planted | - | 2/2 | 58 | PASS |
| 14 | A vendor contact list, not payments: must refuse | planted | - | 2/2 | 64 | PASS |
| 15 | Report lists bills and their payments: only payments may count | ugly | 9 | 32/32 | 85 | PASS |

Totals: 510 payment lines, 8 bill and credit lines that must not count, 99 vendors. Six
ugly cases, five with planted errors (three planted in the data, two files to refuse).

What a "check" is: for every case, the tax year, the dollar limit, eleven control totals,
every exception that must be raised and none that must not, the number of vendors, and
for every vendor its bucket, form and box, and check-or-transfer dollars. Some vendors
also have their source rows, their all-methods total or their combined spellings checked.

### The planted errors and what the agent did

| Case | Planted | What the agent did |
|---|---|---|
| 09 | A $1,200 check entered twice, taking Olsen Carpentry to $2,400 | Flagged the pair, kept both in the total, sent Olsen to "Needs your judgment". Flagged a second duplicate that does not change the answer. Left two same-day checks with different numbers alone. |
| 10 | Subtotal says $4,300, lines add to $3,100 | Red STOP box, both mismatches listed as one $1,200 problem, vendor row marked, warning on every printed page. |
| 11 | Three December 2025 payments; file ends in September | Left the three lines out, reported their $1,550, said one of them was over the 2025 limit, and warned the year may be incomplete. |
| 13 | Payments dated 2027 | Refused: the 2027 limit is not known. |
| 14 | A vendor contact list | Refused: no dates or amounts. |

## 2. Do the tests have teeth?

Five deliberately broken copies of the agent were run through the same tests. All failed.

| Broken on purpose | Cases passed | Checks passed |
|---|---|---|
| Uses the old $600 limit for 2026 | 3 of 15 | 440 of 476 |
| Counts card payments | 11 of 15 | 450 of 476 |
| Treats "LLC" as a corporation | 11 of 15 | 466 of 476 |
| Counts bills as payments | 14 of 15 | 462 of 476 |
| Does not combine spellings | 14 of 15 | 471 of 476 |

**A fault in our own test runner.** This check is how we found that the runner had been
ignoring the file path it was given and re-testing the main build every time. Two rebuild
"passes" recorded before that point were therefore not real. The runner was fixed, it now
prints the file it is testing, and every result on this page was produced after the fix.

## 3. Rebuild from the prompt alone

Each rebuild was written by a fresh AI session that was given `REBUILD-PROMPT.md` and
nothing else, and told not to look at any other file. Its output was then run through
the tests above.

| Rebuild | Prompt version | Test set | Cases passed | Checks passed |
|---|---|---|---|---|
| 1 | First draft | Original 14 cases | 14 of 14 | 394 of 394 |
| 2 | Revised after the tax review and cold-user check 1 | Final 15 cases | 15 of 15 | 476 of 476 |
| 3 | Version 1.0.0 prompt | Final 15 cases | 15 of 15 | 476 of 476 |
| 4 | Version 1.1.0 prompt, as published | Final 15 cases | 15 of 15 | 476 of 476 |

Each rebuild passed on its first attempt. The prompt was revised between rebuilds because
the tests and the agent grew, not because a rebuild failed. Rebuild 4 is kept in
`tests/rebuild-check/rebuilt-from-final-prompt.html` so anyone can rerun it. It loads its
spreadsheet reader from a CDN, as the prompt says, so it needs internet for Excel files.

Each rebuilder also listed where the prompt left it guessing. None
of those guesses changed a test result. The ones most likely to matter on other files:
what to do with a row that has an amount but no readable date, how ties between kinds are
broken, and whether a goods vendor with an unreadable line should go to judgment.

"The same agent" means a page that passes these tests. The rebuilds look different and
word their reasons differently.

## 4. Time against the manual baseline

| | By hand (estimate, see `MANUAL-BASELINE.md`) | Agent (measured) |
|---|---|---|
| Case 03, 268 lines | 31 minutes | 0.17 seconds |
| All 13 processable files, 518 lines | 125 minutes | 1.2 seconds in total |

The by-hand figures are counted work multiplied by assumed rates. They have not been
measured. The agent figure is machine time only. Reading the worksheet and making the
judgment calls still takes the accountant's time, and that has not been measured either.

## 5. What was wrong along the way

Problems found before release, by who found them. All are fixed unless marked.

**Independent tax review of the answer key** (a separate AI session with the IRS
instructions, told to find fault). Of 88 expected answers it called 80 correct, 8
debatable, none plainly wrong. Changes made:
- Form 1099-NEC box is 1a on the 2026 form, not 1.
- A vendor with an unreadable line now goes to judgment instead of "No 1099".
- A vendor under the limit only because of a refund now goes to judgment.
- Law firms paid $600 to $1,999 go to judgment (settlement money is reportable from $600).
- A vendor with both rent and service lines goes to judgment (two forms).
- "Ltd" no longer counts as a sign of a corporation.
- Prior-year lines over that year's limit are called out.
- Vendors between $600 and $2,000 carry a note to check the state's limit.

**Our own probing with inputs outside the test set.**
- "Tri-County Law Enforcement Supply" was treated as a law firm and "Health Mart Pharmacy"
  as a medical provider. Now, when the name says one thing and the books say goods, the
  vendor goes to judgment.
- $240 of royalties was passed as under the limit. Royalties now go to judgment from $10.
- Lines with a blank payee were filed as a vendor. They now go to judgment.
- Customer deposits in a check register were reported as refunds.

**Cold-user check 1** (a fresh AI session playing a 60-year-old CPA, working only from
screenshots). Verdict: she could finish from the opening screen, in 10 to 15 seconds.
35 stumbles listed. The serious ones:
- The list of who gets a 1099 was below the fold. A one-line summary now sits under the title.
- Client / Prepared by / Reviewed by looked typeable and were not. They are now.
- W-9 boxes were drawings. They are now real tick boxes that print.
- No section subtotals, and no next step per section. Both added.
- The printout was 9 pages for 18 vendors. It is now 6, with source lines optional.
- Excel files needed internet. The spreadsheet reader is now built into the file.
- A vendor report listing bills as well as bill payments would have been double counted.
  Bills are now set aside, and case 15 tests it.

**Cold-user check 2** (another fresh session, on the reworked screen). Verdict: yes again,
about 10 seconds for the first screen. 12 stumbles. Fixed: the decision box cut off long
text in print; a file that does not add up still showed a green summary; three totals on
one worksheet all said "ties" without explaining how they relate; left-out bills were
listed by row number only; the tables came after the control totals.
**Not fixed, on purpose:** writing a decision does not move the vendor or change the
counts. The worksheet says so. Recalculating would make this a second tool.

## 6. What the agent cannot do

See "Limits" in the folder README. In short: it has not seen a W-9; it does not check
TINs, state rules or backup withholding; it does not cover other 1099 forms; it refuses
2027; it assumes a calendar year and US date formats; it reads only Excel and CSV; and it
judges purpose from account coding and vendor names.

## 7. Not yet tested

- No practicing accountant has used it. `ACCOUNTANT-TEST-SCRIPT.md` is ready.
- No real client export has been run through it. The test files are modeled on QuickBooks
  and bank export layouts, but they were written by us. In particular, the claim that
  QuickBooks vendor reports show bill payments as negative numbers is from memory and
  could not be checked against Intuit's documentation, which blocked automated reading.
  The agent takes the absolute value of a bill payment either way.
- Only Chromium was used. Firefox and Safari are untested. The running page header in
  print needs a recent Chrome or Edge.
