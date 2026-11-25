# Results: Acquire-to-Retire 01, "What goes on the asset schedule?"

Version 1.0.0, run with `node run-tests.js` against `agent/what-goes-on-the-asset-schedule.html`.

**22 of 22 cases passed; 758 of 758 individual checks.**

The acceptance test has 22 cases: general ledger reports for 2026 in the layouts of QuickBooks Online
(flat and with nested sub-accounts), QuickBooks Desktop and Xero, from a model of accounts and lines
for invented businesses. 5 are clean, 8 have a problem planted in them, and 9 are ugly. Each case
checks:
- the status and every message;
- the period and every account's role;
- the cost and accumulated depreciation roll-forwards;
- every addition with its flags;
- every credit to an asset account and what kind it is;
- transfers, reversals and likely loan payments;
- every bill in expense accounts, and that none is decided for the accountant;
- possible sales elsewhere, depreciation booked, and the totals;
- where typed in: the checks against last year's schedule and this year's depreciation.

Case 22 is the readers' sample, Ridgeline Landscaping. The test also makes the reader's decisions and
types the sold truck's figures, then checks what is capitalized and the gain. The rules are in the
docstring of `make_cases.py`; the key is worked out from the model, never by reading the files back.

## Case by case

| Case | What it is | Type | Expected verdict | Checks passed | Run time (ms) | Result |
|---|---|---|---|---|---|---|
| 01 | QuickBooks Online, a clean year: purchases recorded as assets, depreciation booked | clean | COMPUTED | 34/34 | 121 | PASS |
| 02 | QuickBooks Online, last year's schedule and this year's depreciation typed in: both agree | clean | COMPUTED | 40/40 | 259 | PASS |
| 03 | Planted: an HVAC unit, laptops and a machine expensed; a quarterly service contract that is routine | planted | COMPUTED | 36/36 | 113 | PASS |
| 04 | Planted: a truck sold with the proceeds credited to Vehicles; accumulated depreciation untouched | planted | COMPUTED | 36/36 | 149 | PASS |
| 05 | Planted: no depreciation booked; the tax software's figure typed in | planted | COMPUTED | 37/37 | 177 | PASS |
| 06 | Planted: opening cost and accumulated depreciation differ from last year's schedule | planted | COMPUTED | 41/41 | 176 | PASS |
| 07 | Xero Account Transactions: default account names; lighting expensed as a repair | ugly | COMPUTED | 35/35 | 120 | PASS |
| 08 | QuickBooks Desktop General Ledger: account numbers, Debit and Credit, no period | ugly | COMPUTED | 37/37 | 145 | PASS |
| 09 | QuickBooks Online as CSV: dollar signs, parentheses; a returned part credited to the asset | ugly | COMPUTED | 36/36 | 87 | PASS |
| 10 | A bill entered twice and reversed; an addition by journal entry; the reclassed repair is not proposed again | ugly | COMPUTED | 37/37 | 111 | PASS |
| 11 | The wrong report: a trial balance | ugly | NOT_RECOGNIZED | 4/4 | 64 | PASS |
| 12 | The wrong report: an A/R aging | ugly | NOT_RECOGNIZED | 4/4 | 66 | PASS |
| 13 | Planted: a line missing from the export, so Furniture and Equipment does not add up | planted | COMPUTED | 36/36 | 107 | PASS |
| 14 | The client has audited statements: a $5,000 threshold typed in | ugly | COMPUTED | 35/35 | 170 | PASS |
| 15 | An asset account named 'Shop Assets': the page asks, the accountant marks it as a fixed asset | ugly | COMPUTED | 33/33 | 126 | PASS |
| 16 | QuickBooks Online, a fiscal year ending June 30 (still twelve months) | ugly | COMPUTED | 35/35 | 115 | PASS |
| 17 | A sale booked properly: cost and accumulated depreciation removed, gain recorded | clean | COMPUTED | 36/36 | 116 | PASS |
| 18 | QuickBooks Online fixed asset tracking: 'Original cost' and 'Depreciation' sub-accounts, nested, with parent totals | ugly | COMPUTED | 35/35 | 115 | PASS |
| 19 | Accounts named after assets that are not assets (a truck loan, a note payable, a gain); amortization; a down payment in auto expense | planted | COMPUTED | 41/41 | 105 | PASS |
| 20 | A truck bought net of a trade-in, loan payments posted to Vehicles, land and a building bought in November | planted | COMPUTED | 41/41 | 105 | PASS |
| 21 | Purchases already reclassed, a part refund, a bill split over two accounts, a transfer between asset accounts, a return; three tools that are not routine | planted | COMPUTED | 42/42 | 110 | PASS |
| 22 | The readers' sample: Ridgeline Landscaping, with the reader's decisions, last year's schedule, this year's depreciation and the sold truck's figures typed | planted | COMPUTED | 47/47 | 949 | PASS |

## What went wrong along the way

### First build: 16 of 16, which proved little
The first build passed every case at once. That said the tool and the answer key followed the same
rules, both written by us, not that the rules were right. The reviews were the real test.

### Broken copies the tests missed at first
Twenty copies of the tool were made, each with one rule broken. Four got past the first tests:
- a bill of exactly $2,500;
- a vendor with only two big bills;
- reversal pairing that ignored the vendor;
- a sale booked properly.

Test data was added for each (case 17 and lines in cases 03, 04 and 07). After the rules changed, a
second set of 24 broken copies was made. Two of them showed rules that changed nothing on a
well-formed file: the "Original cost" sub-account rule and matching a total line to its account by
name. Those rules were removed rather than kept untested. The other 22 are all caught.

### The accounting review
A separate AI session, told to act as a skeptical CPA who prepares year-end returns, read the source
and ran six ledgers of its own. It found the tool not ready. Its findings that changed answers, all
fixed and now in the tests (cases 18 to 21):
- **Bills in expense accounts were ticked "capitalize" by default,** and a bill of exactly $2,500
  counted. Now nothing is decided for the accountant; only bills over the threshold are listed.
- **Purchases already reclassed by journal entry, or partly refunded, were proposed again.** A
  reclass now removes the bills it covers, even when one entry covers several bills; a refund
  reduces the bill it belongs to.
- **Every credit to an asset account was treated as an unrecorded sale.** Credits are now sorted
  into transfers between asset accounts, vendor returns, sales booked properly (with their
  depreciation or a gain or loss) and money received for an asset.
- **QuickBooks' fixed asset tracking sub-accounts were misread.** "Truck:Depreciation" was taken as
  depreciation expense, which doubled the proposed depreciation. Sub-accounts now take their
  parent's sense.
- **Parent totals in a nested ledger caused a false "does not add up".**
- **"Truck Loan", "Equipment Note Payable" and "Gain on Sale of Equipment" were read as assets.**
- **A trade-in recorded net, and loan payments posted to an asset account, passed as additions.**
  Both are now flagged; the payments are left out.
- **"Routine" hid real equipment.** Three different tools from one vendor were called a service
  contract. Now "repeats" needs equal amounts or a contract-like memo, and the bills stay listed.
- Also added: land (not depreciated), amortization in the depreciation account, possible sales in
  other accounts, the mid-quarter warning, vehicles and auto expense accounts reviewed, and wording
  on the de minimis safe harbor, the BAR tests and which depreciation figure to type.

### The first-time-user reviews
Two separate sessions played a staff accountant who had never seen the tool, working from the screen
only.

**The first** found 15 problems. Among them:
- the purchases were pre-decided;
- a sold asset could not be finished on screen;
- the printout was the whole interactive page;
- the step bar never showed where you were.

The tool was rebuilt around its four steps. Each now says what it is for, who acts, and what to do
next. The step bar stays on screen and ticks a step only when it is really done.

**The second**, on the rebuilt tool, finished the whole process from the screen. It found these, all
fixed:
- **A sold asset needs its depreciation up to the sale,** not just last year's figure. Now three
  boxes, with an explanation of how they relate to this year's depreciation.
- **The workpaper was not something to file.** It now has:
  - numbered journal entries in debit and credit columns;
  - the balances after the entries;
  - a target account and a reason for each decision;
  - a final verdict once everything is decided;
  - a print layout without buttons or labels, with a workpaper title and reference;
  - a warning before printing an unfinished workpaper.

That review also caught a bug: typing a sale's figures re-drew the page and lost what was typed in
the next box. The page now works the gain out when you leave the sale's boxes, and case 22 types the
figures box by box the way a person does.

## Rebuild from the prompt

**Developer check (`rebuild-check/rebuild-1/`).** A fresh AI session got only `PROMPT.txt` and was
allowed to read `run-tests.js`. It could not see the tool, the case builder or the answer key.

Its first run is not a clean measure: the prompt and the tests changed while it worked. Its first
build came from the older prompt and was run against the newer test, passing 21 of 22 cases. Rebuilt
to the current prompt, it passed **22 of 22 cases, 758 of 758 checks**.

It also listed the places where the prompt was silent and it had to guess. One of them was a real
bug, in the tool too: "Leasehold Improvements" was read as not an asset because it contains "lease".
That is fixed, and case 20 now tests it. The prompt now says what the tool does for each of the
others:
- the not-recognized message;
- the date format in the report;
- "Total" in any case;
- which columns count as an amount;
- the order sets of bills are tried in for a reclass;
- that moving between boxes must not redraw the page.

**Reader check (`rebuild-check/reader-test/`).** A fresh AI session played a staff accountant who is
not technical, and the assistant that accountant pastes the prompt into. Its only sources were the
article as a reader sees it and the public repository, fetched logged out.

- **The prompt.** The copy in the article and the master on GitHub were identical, byte for byte.
- **Following the steps.** It followed steps 1 to 6. The page it built, from the prompt alone,
  showed every number the article and the sample's README give: $76,050.00 and $26,980.00, a gain
  of $13,375.00, $88,550.00 to add, the four entries, and $257,450.00 and $82,585.00 after them.
- **The one fix it needed.** Its first file lost a figure typed in step 3d when moving to the next
  box. One request to the assistant fixed it. The prompt now says plainly that those boxes are read
  only when Compare is pressed.
- **Its other hesitations, all now covered in the article and the README:**
  - the page needs internet for its spreadsheet reader;
  - Notepad saves .html.txt unless "All files" is chosen;
  - TextEdit asks before it saves as .html;
  - the assistant may show the file in a side panel;
  - the repository's odd name ("-");
  - which button to press in step 2, and which figures to type in step 3d.
