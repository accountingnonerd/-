# Procure-to-Pay, episode 01: Who gets a 1099?

Version 1.1.0, 2026-11-11. Part of [Series 1: Procure-to-Pay](../README.md), which also holds the value test this tool had to pass.

## The problem

Every January, someone at an accounting firm goes through each business client's payments
for the year to decide who gets a Form 1099. In practitioners' words: "We print out the GL
for the year or YTD and manually search the transactions for Vendors eligible for 1099's"
([Intuit Accountants Community](https://accountants.intuit.com/community/easyacct-discussions/discussion/how-to-print-1099-vendor-list/00/229893)).
Bookkeeping software has a 1099 report, but it relies on flags someone had to set on each
vendor during the year.

The job has traps: the same vendor typed three ways, payments split between check and card,
law firms that are corporations, a check entered twice. And January 2027 is the first
filing season under a new limit. For payments made in 2026 the general limit is $2,000,
not $600 ([IRS instructions, Rev. December 2026](https://www.irs.gov/instructions/i1099mec)).

This agent does that one job: a payments file in, a 1099 worksheet out.

## What it adds to what she already has

QuickBooks Online and Xero have 1099 reports, but they count only vendors someone flagged
for 1099 (and, in QuickBooks, accounts mapped to a 1099 box). This tool reads every
payment in the export, flagged or not. It also catches what flags cannot: one vendor
typed several ways, a check entered twice, a refund that pulls a vendor under the limit,
and a file whose totals do not tie. Use it beside the software's report: a vendor on this
worksheet and not on that report was probably never flagged.

## How to use it

1. Open `agent/who-gets-a-1099.html` in any browser. It needs no installation and no internet.
2. Drop in the client's payments for the tax year (Excel or CSV). In QuickBooks: Reports,
   "Transaction List by Vendor", whole year, Export to Excel.
3. Read "Check these first", work down the sections, type your name, tick the W-9 boxes,
   and press "Print or save as PDF". The printout is the workpaper.

The file is read on your computer. Nothing is uploaded, stored or sent.

## What the worksheet contains

- **Check these first.** File problems and judgment calls, before anything else.
- **Control totals.** Dollars by payment method, tied to the sum of the lines read and to
  the file's own total line. If they do not tie, a red STOP box says so and every printed
  page carries a warning.
- **File a 1099.** Vendor, form and box, amount, reason, and a W-9 tick box.
- **Probably exempt.** Vendors whose name says they are a corporation.
- **Needs your judgment.** Vendors where the agent will not guess, each with the question
  to answer and a line for your decision.
- **Close to the limit.** Vendors within 25% of the limit.
- **No 1099.** Everyone else, each with the reason.
- **Source lines.** The file rows behind every vendor.

## Limits

It is a first pass for an accountant to review. It does not:

- see any W-9. It cannot know that an LLC is taxed as a corporation, or that an "Inc." is not;
- check taxpayer ID numbers or handle backup withholding, which requires a form at any amount;
- know state rules. Some states may still use $600. It flags vendors between $600 and
  $2,000, but does not say which states;
- cover Forms 1099-INT, 1099-DIV, 1099-K, or 1042-S for payees outside the US;
- know the 2027 limit, which may be adjusted for inflation. It refuses 2027 files;
- handle fiscal-year payers. It assumes a calendar year and goes by payment date;
- tell an employee paid as a contractor from a real contractor, or spot a tax-exempt payee;
- see payments that are not in the file, such as cash or a personal account;
- split one vendor across two forms. A landlord who also did repairs goes to judgment;
- read PDFs, scans or Word files. It reads Excel and CSV exports only;
- read dates in day/month order. It assumes US dates.

It judges what a payment was for from the account it was coded to and from the vendor's
name. A contractor coded to "Supplies" will land in "No 1099". That table is there to be skimmed.

Positions it takes that a practitioner may want to know:
- Zelle counts toward the limit, like a check. Zelle is not a card or a third-party
  network and files no Form 1099-K. The IRS instructions do not name Zelle; this follows
  common practice ([NerdWallet](https://www.nerdwallet.com/taxes/learn/zelle-taxes),
  [CPA Practice Advisor](https://www.cpapracticeadvisor.com/2022/11/18/zelle-is-being-used-by-small-business-owner/73295/)).
- PayPal and Venmo payments do not count, but if they would tip a vendor over the limit
  the vendor goes to judgment, because personal ("friends and family") transfers are not
  reported by the service.
- A refund from a vendor reduces that vendor's total. If the refund is the only reason a
  vendor is under the limit, the vendor goes to judgment.
- Bills, vendor credits and journal entries are not payments and are not counted.

## What is in this folder

| Path | What it is |
|---|---|
| `agent/who-gets-a-1099.html` | The agent. One file, works offline. |
| `agent/who-gets-a-1099.src.html` | The readable source. Same page, but loads its spreadsheet reader from a CDN. |
| `agent/build.py` | Pastes the spreadsheet reader into the source to make the offline file. |
| `tests/cases/` | 15 test files. All invented, no client data. |
| `tests/make_cases.py` | Writes the test files and the answer key. Every expected answer is worked by hand in this file, with the reason. |
| `tests/answer-key.json` | The answer key. |
| `tests/run-tests.js` | Runs any build of the agent against the key in a real browser. |
| `tests/RESULTS.md` | Results case by case, the cold-user check, and what went wrong along the way. |
| `tests/MANUAL-BASELINE.md` | The same files by hand: steps and estimated minutes. |
| `ACCOUNTANT-TEST-SCRIPT.md` | A 25-minute script for testing with a real accountant. |
| `REBUILD-PROMPT.md` | One prompt that rebuilds the agent from nothing. |
| `article/ARTICLE.md` | The LinkedIn article (draft). `article/PREVIEW.html` shows it with its images. |
| `article/images/` | The cover and the five figures, rendered from `article/visuals/` with `node render.js`. |

## Run the tests

```bash
cd tools && npm install
```

```bash
cd procure-to-pay/01-who-gets-a-1099/tests && node run-tests.js
```

To test a rebuilt agent, pass its path:

```bash
node run-tests.js /path/to/your/who-gets-a-1099.html
```

Playwright with Chromium must be installed. "The same agent" means it passes these tests,
not that its code is identical.

## Third-party code

The offline file contains [SheetJS Community Edition](https://sheetjs.com) 0.18.5,
Apache License 2.0, used to read Excel files.
