# Record-to-Report, episode 01: Did last year change?

Version 1.0.0, 2026-11-13. Series 1, Agent 3. Part of [Record-to-Report](../README.md), which
holds the Stage 1 evidence and the value test this tool had to pass.

## The problem

Every new year starts from last year's ending balances. The return was prepared from the
accountant's final trial balance, and this year's Schedule L starts from it. But the
client's books are still open to the client. A deposit gets deleted, a bill gets backdated,
an old transaction gets re-entered, and the adjusting entries the accountant sent never get
posted. The books no longer agree with what was filed, and nobody notices until the new
year's numbers don't tie.

The IRS instructions for Form 1120-S say of Schedule L: "The balance sheets should agree with
the corporation's books and records." The check is simple to describe and slow to do: line up
two trial balances, account by account, and work out what each difference means.

## What it adds to what she already has

QuickBooks and Xero can list transactions changed after a closing date. They do not compare
the books with *her* final figures, and they cannot see adjusting entries she made only in
her workpapers. This tool does, and it says what each difference means for last year's
return: did last year's profit change, did an earlier year change, or were her own entries
never posted. It drafts the entry that puts the opening balances back, with the conditions
for posting it, and the questions to send the client.

## How to use it

1. Open `agent/did-last-year-change.html` in any browser. It needs no installation and no internet.
2. Drop last year's final (adjusted) trial balance in box 1, and a trial balance for the same
   date exported from the client's books today in box 2. Excel or CSV.
3. Read the verdict and "Check these first", type your name, and press "Print or save as PDF".

The files are read on your computer. Nothing is uploaded, stored or sent.

## What the workpaper contains
- **A one-sentence verdict:** still agrees, has changed, or cannot be compared.
- **Check these first.** Stops: different dates, cash against accrual basis, a file that
  does not balance, a file whose own total line disagrees with its accounts, the wrong
  report, the same file twice, a likely cash-basis export, the wrong client's file. Then: changes to last year's income or expenses (with the
  likely cause when one balance sheet and one income statement account move by the same
  amount), changes to the balance sheet, changes to owners' accounts (K-1s, Schedule M-2,
  basis), changes to earlier years (retained earnings), your
  adjustments not posted, merged and renamed accounts, and rounding.
- **What changed,** account by account, with what each difference means.
- **Last year's profit and retained earnings,** final against today, and a check that the
  differences add to zero.
- **A correcting entry** dated the first day of the new year, with the conditions for
  posting it.
- **Questions for the client.**
- **Every account compared,** with the file row each figure came from and how the tool
  decided whether it is a balance sheet or income statement account.

## Limits

It does not:
- read PDFs or scans. Export the trial balance to Excel or CSV;
- find the transactions that changed. It tells you which accounts and by how much; the audit
  log in QuickBooks Online, or the transaction history in Xero, tells you which entries;
- decide whether a change was right. A missed bill that the client added may be correct, and
  last year's return wrong. That is your call;
- know your client's chart of accounts. It decides balance sheet or income statement from
  account numbers (1 to 3, and 4 to 9), Xero's section headings, or the order of the file
  (ledgers list income and expenses after equity). With none of those it guesses from the
  name, and says so;
- read every layout. It reads Debit and Credit columns, Xero's year-to-date columns, and a
  workpaper with a final balance column (and, if present, books and adjustments columns).
  When a workpaper has several Debit and Credit pairs, it uses the last pair;
- read a QuickBooks Desktop or Xero export it has not seen. The Desktop and Xero layouts in
  the tests were built from those products' documented report layouts, not from real
  client exports;
- compare more than one date, or more than two files;
- split anything among partners. A change to an owner's account (distributions, draws,
  capital, owner loans) is flagged for the K-1s, Schedule M-2 and basis, and no entry is
  drafted; with no retained earnings account, no entry is drafted either;
- know which of your adjustments were tax-only or made only for the return. They show as
  "not posted"; leave them out;
- check when the client's file was exported. An export made before your adjustments would
  show them all as "not posted";
- read a layout that prints an export date and time above the column headings with
  certainty. The tests have no such layout (see `tests/RESULTS.md`).

## What is in this folder

| Path | What it is |
|---|---|
| `agent/did-last-year-change.html` | The tool. One file, works offline. |
| `agent/did-last-year-change.src.html` | The readable source. It loads its spreadsheet reader from a CDN. |
| `agent/build.py` | Pastes the spreadsheet reader into the source to make the offline file. |
| `tests/cases/` | 22 test cases, 43 files. Four invented companies, five export layouts. |
| `tests/make_cases.py` | Builds the test files from a ledger model, and writes the answer key. |
| `tests/answer-key.json` | The answer key. |
| `tests/run-tests.js` | Runs any build of the tool against the key in a real browser. |
| `tests/RESULTS.md` | Results case by case, what the reviews changed, and the broken copies the tests caught. |
| `tests/MANUAL-BASELINE.md` | The same work by hand, with estimated minutes. |
| `ACCOUNTANT-TEST-SCRIPT.md` | A 25-minute script for testing with a real accountant. |
| `REBUILD-PROMPT.md` | One prompt that rebuilds the tool from nothing. |
| `article/` | The article, its images and the scripts that make them. |

## Run the tests

```bash
cd tools && npm install
```

```bash
cd record-to-report/01-did-last-year-change/tests && node run-tests.js
```

Pass another build's path to test it. Playwright with Chromium must be installed.

## Third-party code

The offline file contains [SheetJS](https://sheetjs.com) Community Edition 0.18.5 (Apache
License 2.0), used to read Excel and CSV files.
