# Order-to-Cash, episode 01: Does the 1099-K tie?

Version 1.0.0, 2026-11-14. Series 1, Agent 4. Part of [Order-to-Cash](../README.md), which holds
the Stage 1 evidence and the value test this tool had to pass.

## The problem

Card processors and payment apps report a business's gross sales to the IRS on Form 1099-K:
before refunds and fees, with sales tax and tips inside. The bank sees only the payouts. Many
small clients' books record each payout as sales, so the books come in below the 1099-K, and the
IRS matching program notices. Intuit's own help page warns that "the client may receive an IRS
notice if the gross receipts don't reflect amounts from the 1099-K."

## What it adds to what she already has

The processor's dashboard shows the transactions; the bank feed shows the payouts; tax software
takes whatever she types. This tool turns a year of the processor's transactions into what the
1099-K should say, month by month, and ties it three ways: to the 1099-K's box 1a, to the return's
lines, and to the deposits. It writes the entry for books that recorded payouts as sales.

## How to use it

1. Open `agent/does-the-1099k-tie.html` in any browser. It needs no installation and no internet.
2. If you have the client's 1099-K, type box 1a. Then drop in the year's export from Square
   (Transactions CSV), Stripe (itemized balance activity) or PayPal (activity download).
3. Read the verdict and "Check these first", decide the sales tax and tips boxes, fill in the
   client and your name, and press "Print or save as PDF".

The file is read on your computer. Nothing is uploaded, stored or sent.

## Limits

It does not:
- read the 1099-K itself. Type box 1a; check the payee TIN, backup withholding (box 4) and state
  boxes on the form, as the page lists;
- read Shopify, Venmo, Cash App for business, Etsy, Amazon, eBay or other marketplaces, or
  Square's Transfers report;
- decide whether sales tax and tips belong in gross receipts. It includes them, as the 1099-K does,
  shows the amounts and the rule, and lets you leave them out;
- decide whether a no-fee PayPal transfer was personal. It leaves it out and asks;
- know the processor's opening balance. The balance line is the change over the year;
- see what Square deducts from deposits outside the transactions export (loan repayments, instant
  deposit fees, hardware);
- read a layout it has not seen. The Square, Stripe and PayPal layouts in the tests were built from
  the products' published column names, not from real client exports;
- convert a foreign-currency sale without PayPal's conversion lines.

## What is in this folder

| Path | What it is |
|---|---|
| `agent/does-the-1099k-tie.html` | The tool. One file, works offline. |
| `agent/does-the-1099k-tie.src.html` | The readable source. It loads its spreadsheet reader from a CDN. |
| `agent/build.py` | Pastes the spreadsheet reader into the source to make the offline file. |
| `tests/cases/` | 14 test cases, 13 files. Three invented businesses. |
| `tests/make_cases.py` | Builds the test files from a transaction model, and writes the answer key. |
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
cd order-to-cash/01-does-the-1099k-tie/tests && node run-tests.js
```

## Third-party code

The offline file contains [SheetJS](https://sheetjs.com) Community Edition 0.18.5 (Apache License
2.0), used to read Excel and CSV files.
