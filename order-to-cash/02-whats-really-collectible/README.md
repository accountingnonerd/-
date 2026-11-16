# Order-to-Cash, episode 02: What's really collectible?

Version 1.0.0, 2026-11-16. Series 1, Agent 4. Part of [Order-to-Cash](../README.md), which holds
the Stage 1 evidence and the value test this tool had to pass.

## The problem

Most small businesses that invoice have money owed to them that is late. Every month, and above all
at year end, the accountant is supposed to turn the A/R aging into decisions: which payments were
never applied, who to chase and how, what to write off, and what allowance the statements need. The
aging report lists the open items; it does none of that.

## What it adds to what she already has

The ledger's aging lists what is open; reminders and collection apps chase invoices. This tool reads
every line of the aging and produces the accountant's review: credits matched to the invoices they
belong to, duplicates and mis-postings found, customers in credit set aside, a ranked list of who to
chase with a draft letter each, an allowance from her rates, and the write-offs and entries.

## How to use it

1. Open `agent/whats-really-collectible.html` in any browser. It needs no installation and no internet.
2. If you have it, type A/R from the balance sheet. Then drop in the A/R aging detail (QuickBooks
   Online or Desktop, or Xero's Aged Receivables Detail), Excel or CSV.
3. Post the clean-up in the ledger and run it again; then read the worklist and letters, type the
   loss rates, and press "Print or save as PDF".

The file is read on your computer. Nothing is uploaded, stored or sent.

## Limits

It does not:
- know the client's loss history. You type the rates; it does not guess them;
- know about disputes, bankruptcies, payment plans, retainage or deposits. Hold a customer's letter by
  ticking it; retainage and deposits need your judgment;
- see unbilled work, contract assets or customer deposits outside the aging;
- convert foreign currencies, or treat finance charges differently from invoices;
- know what the client's remittances say. Its matches are likely matches, to confirm;
- send anything. The letters are drafts for the client to review and send;
- read a layout it has not seen. The layouts in the tests were built from the products' published
  report layouts, not from real client exports.

## What is in this folder

| Path | What it is |
|---|---|
| `agent/whats-really-collectible.html` | The tool. One file, works offline. |
| `agent/whats-really-collectible.src.html` | The readable source. It loads its spreadsheet reader from a CDN. |
| `agent/build.py` | Pastes the spreadsheet reader into the source to make the offline file. |
| `tests/cases/` | 17 test cases. Invented businesses. |
| `tests/make_cases.py` | Builds the test files from a model of open items, and writes the answer key; the rules are in its docstring. |
| `tests/answer-key.json` | The answer key. |
| `tests/run-tests.js` | Runs any build of the tool against the key in a real browser. |
| `tests/RESULTS.md` | Results case by case, what the reviews changed, and the broken copies the tests caught. |
| `tests/MANUAL-BASELINE.md` | The same work by hand, with estimated minutes. |
| `ACCOUNTANT-TEST-SCRIPT.md` | A 25-minute script for testing with a real accountant. |
| `REBUILD-PROMPT.md` | One prompt that rebuilds the tool from nothing. |
| `article/` | The article, the LinkedIn carousel, and the scripts that make them. |

## Run the tests

```bash
cd tools && npm install
```

```bash
cd order-to-cash/02-whats-really-collectible/tests && node run-tests.js
```

## Third-party code

The offline file contains [SheetJS](https://sheetjs.com) Community Edition 0.18.5 (Apache License
2.0), used to read Excel and CSV files.
