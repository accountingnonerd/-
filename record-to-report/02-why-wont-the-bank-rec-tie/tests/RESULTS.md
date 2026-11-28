# Results: Record-to-Report 02, "Why won't the bank rec tie?"

Version 1.0.0, run with `node run-tests.js` against `agent/why-wont-the-bank-rec-tie.html`.

**28 of 28 cases passed; 839 of 839 individual checks.**

The acceptance test has 28 cases, each a pair of files: a bank download and a ledger, for invented
businesses. The bank files come in five layouts: amount and balance columns; newest first with a
check-number column; a summary block above the lines; no heading row; and withdrawals and deposits
columns. The ledgers come from QuickBooks Online, QuickBooks Desktop and Xero, as Excel or CSV. Most
are built from a model of a quarter's events (deposits, checks, online payments, fees, interest, and
the bank's lag in clearing them). The rest are short pairs written by hand for one point each.
1 case is clean, 11 have problems planted in them, and 16 are ugly. Each case checks:
- the status and every message;
- the account, the dates, the balances, and how many lines matched;
- every batch, split, near miss and entry made twice, with the decision made;
- every outstanding item with its age, and every bank item not in the books with its kind;
- what was outstanding before the bank's dates, and the ticks where the page asks;
- the proof: adjusted bank, adjusted books, the difference, and whether it ties.

Cases 26 and 27 are the readers' sample, Mapleton Landscaping (also in `../sample/`). The test makes
the reader's decisions and checks the result. The rules are written out in `rules.py`. The answer key
is worked out from the model with those rules in `make_cases.py`, never by reading the files back.

## Case by case

| Case | What it is | Type | Checks passed | Run time (ms) | Result |
|---|---|---|---|---|---|
| 01 | A normal quarter: generic bank CSV, QuickBooks Online ledger; checks outstanding, a deposit in transit, fees and interest not in the books | clean | 36/36 | 136 | PASS |
| 02 | The bank's download newest first, with a check-number column | ugly | 36/36 | 122 | PASS |
| 03 | A summary block above the bank's lines; a Xero ledger with three accounts, the checking account chosen | ugly | 37/37 | 111 | PASS |
| 04 | No heading row, no balance column (the accountant types the statement's beginning and ending balances); QuickBooks Desktop ledger | ugly | 37/37 | 218 | PASS |
| 05 | Planted: two checks entered for the wrong amount, an online payment with its digits swapped, a customer payment entered twice | planted | 39/39 | 446 | PASS |
| 06 | Planted: card sales recorded one by one that land as one deposit; a refund paid out entered as money in; withdrawals and deposits columns | planted | 39/39 | 158 | PASS |
| 07 | Planted: two checks over six months old, two over 90 days (one at about 165 days), and a deposit recorded but never made | planted | 39/39 | 132 | PASS |
| 08 | The books file starts on the bank file's first day: two checks written in December clear in January and are recognized as recorded before | ugly | 37/37 | 379 | PASS |
| 09 | Planted: a line missing from the bank's download, so its running balance jumps | planted | 4/4 | 109 | PASS |
| 10 | The wrong books file: a trial balance | ugly | 4/4 | 90 | PASS |
| 11 | The wrong bank file: the books' ledger dropped as the bank's download | ugly | 4/4 | 110 | PASS |
| 12 | Planted: $100.00 that no transaction explains (the bank's beginning balance does not fit the books), so it does not tie | planted | 38/38 | 121 | PASS |
| 13 | The ledger as CSV with dollar signs and parentheses; two bank accounts, the accountant chooses the second | ugly | 37/37 | 975 | PASS |
| 14 | No balances anywhere: the page matches, lists, and asks for the statement's balances before it can prove the tie | ugly | 37/37 | 124 | PASS |
| 15 | A credit card account: this version reconciles bank accounts only, and says so | ugly | 4/4 | 82 | PASS |
| 16 | A customer's check number on a payment received; a coffee, a building maintenance bill and a returned check that only look like bank fees | planted | 36/36 | 111 | PASS |
| 17 | Rent paid every month: January's is missing from the books, and December's (cleared in December) must not be taken for it | planted | 36/36 | 96 | PASS |
| 18 | The same payment to the same vendor on 12/30 (cleared in December) and 1/2: not entered twice | ugly | 34/34 | 112 | PASS |
| 19 | The bank paid check 6001 twice and paid check 6003, which the books voided; check 6002 for the same amount is still outstanding | planted | 36/36 | 243 | PASS |
| 20 | The statement ends 3/31 though the last line is 3/27; a pending line; amounts with DR, CR, USD and a true minus sign | ugly | 36/36 | 123 | PASS |
| 21 | A bank line whose amount cannot be read: the page stops rather than drop it | ugly | 4/4 | 89 | PASS |
| 22 | Payroll posted to a sub-account, Checking:Payroll: the sub-account is part of the bank account | ugly | 35/35 | 133 | PASS |
| 23 | One deposit in the books that the bank shows as two lines; a bank check for the same amount as a book check but a different number | ugly | 36/36 | 113 | PASS |
| 24 | Two old checks of $100, one still outstanding: the page cannot tell which and asks; the accountant ticks December's | planted | 35/35 | 188 | PASS |
| 25 | Same files as 08, but the accountant ticks only one of the two suggested lines: the other stays unexplained and it does not tie | ugly | 38/38 | 200 | PASS |
| 26 | The readers' sample: Mapleton Landscaping, with the reader's decisions (fix the check entered for the wrong amount, remove the deposit entered twice, keep the stale check outstanding) | planted | 40/40 | 345 | PASS |
| 27 | The sample again, with the stale check reversed to a liability: it leaves the outstanding total and the books go up by the same $415.00 | planted | 40/40 | 371 | PASS |
| 28 | Statement balances typed wrong (beginning plus the lines is not the ending): the page stops and keeps the boxes to correct them | ugly | 5/5 | 180 | PASS |

## What changed the tool

### The accounting review
A separate AI session, told to act as a skeptical CPA who reconciles small-business bank accounts
every month, read the source and the rules and ran 18 file pairs of its own. Its verdict on the first
version: **not ready to release.** "The proof layout is fine, but several rules make it tie on the
wrong answer or propose entries that are wrong." What it found, all fixed and now in the tests:
- **The start of the bank file was a plug.** Whatever set of old items added up to the difference at
  the start was taken as outstanding, so the reconciliation tied by construction. In one of its files,
  an unrecorded $1,200 loan payment was hidden as "recorded before the books file". Now, when two sets
  fit, the page asks which checks are still out (case 24). It never moves a bank line out of "not in
  the books" unless the accountant ticks it (cases 08 and 25). When nothing fits, it says so (case 12).
- **Check numbers matched in both directions.** A customer's check number on a payment received
  was paired with the company's own check of that number. Now only money out matches by number (case 16).
- **"Fee" matched coffee.** The word "fee" inside "coffee" made a coffee a bank charge, and a returned
  check was booked as a bank charge. Now only whole fee phrases count, and a returned item goes back
  to the customer's balance (case 16).
- **Last December's rent matched January's.** The 60-day look-back reached a December payment that
  had already cleared (case 17). The same payment either side of the start was called "entered twice"
  (case 18).
- **A check the bank paid twice was absorbed** by a different check of the same amount (case 19). A
  check voided in the books but paid by the bank is now its own item (case 19).
- **The reconciliation was dated at the last bank line,** not the statement date, and pending lines
  counted as cleared (case 20).
- **Bad input passed silently.** Dates like 31/12/2026 rolled into later years. Amounts written "100.00 DR",
  "USD 600.00" or with a true minus sign were dropped. Now an impossible date is not a date, those
  amounts are read, and a dated line whose amount cannot be read stops the page (cases 20 and 21).
- Also: credit card accounts now stop with a clear message (case 15). Sub-accounts of the bank account are
  included (case 22). One deposit the bank shows as two lines is matched (case 23). Voided checks of
  $0.00 are no longer listed as outstanding deposits. A newest-first file with several lines on one
  day no longer stops as "does not add up": the running balance is checked day by day.
- On wording: stale-dated (six months, UCC 4-404) is now kept apart from unclaimed property (the
  state's dormancy period, often 1 year for wages and 3 to 5 for vendors). A "bank error" choice was
  added, and entries now carry a date.

### The first-time-user review
A separate session played a staff accountant who had never seen the tool, working from the screen
only. The first client worked end to end. The second could not be finished honestly. "The page will
print 'It ties' while it is showing an unexplained difference in the opening balances, and that
warning is left off the printout." Fixed:
- "It ties" now needs nothing undecided and nothing left at the start. Until then the headline says
  "Not finished: N items to decide". The printout carries the messages and the open items.
- When the bank file has no balances, the boxes say "(required)". Step 2 shows the books' balance
  the day before the bank's first date, to compare with the beginning balance.
- Enter applies what was typed. A books file dropped in the bank box is caught at once, with a "Swap
  the two files" button. The status line counts missing balances.
- Corrections show their effect on the books' balance. Messages whose items are all decided say
  "Done." instead of "Decide."

### Running the readers' sample
Running the sample through the page found two more things:
- With a stale check still to decide, the headline said "It ties" while step 4 said "Not finished". A
  stale check left outstanding still reconciles: it is a decision to make, not a difference. The page
  now says "It ties ... Still to decide: 1 stale check".
- Reversing a stale check to a liability made the entry but left the check in the outstanding total,
  so the proof no longer matched the entries. Now the reversed check leaves the outstanding total and
  the books go up by the same amount (case 27).

### The rebuild check
A fresh AI session rebuilt the tool from `PROMPT.txt` alone and ran it against these tests: 22 of 27
cases on the first run, 27 of 27 after one round of fixes taken from the prompt (see
`../rebuild-check/rebuild-1/`). It listed the places where the prompt was unclear; the prompt now says
them plainly. It also found that balances typed wrong stopped the page with no way to correct them
but starting over. Now step 2 stays on screen (case 28).

### Broken copies the tests missed at first
25 copies of the tool were made, each with one rule broken. Six got past the first tests:
- check numbers matched without regard to direction;
- a 90-day window for non-checks instead of 60;
- a numbered bank check allowed to match a book check of another number;
- "entered twice" allowed across the start;
- suggested bank lines counted without the accountant's tick;
- 150 days as stale instead of 180.

Test data was added for each (cases 07, 16, 17, 18, 23 and the new case 25). Three more copies broke
the stale-check reversal (cases 26 and 27). All 28 are caught.

## How long it takes
By hand, a quarter's catch-up for one checking account that does not tie at the first try takes
about 2 to 3 hours (see `MANUAL-BASELINE.md`; an estimate, not a measurement). The page reads, matches
and lists in under a second for every case above. What it leaves to the accountant: checking what was
read, deciding each odd pair, the treatment of each bank item, and what to do with stale checks.
