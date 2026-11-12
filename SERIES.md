# The series

One series per accounting process. Each episode is one tool for one step of that
process, plus one article. Episodes are built one at a time, each through the full cycle
(evidence, acceptance test, build, proof, repository, rebuild prompt, article).

## The idea behind every tool: work between the apps, not instead of them

Accountants already have their tools. The [2026 Intuit QuickBooks Accountant Technology Survey](https://www.cpapracticeadvisor.com/2026/07/02/the-2026-accountant-technology-survey-turning-data-revelations-into-a-firm-of-the-future/185807/)
(725 US accounting and bookkeeping professionals) found:
- the average firm runs on about 10 apps, and one in three uses 11 or more;
- only 41% say their tools are fully integrated;
- accountants lose an average of five hours a week "moving, re-entering, or reconciling
  data across disconnected systems";
- 30% name manual data cleanup as the main thing keeping them from advisory work.

So a tool in this series never replaces the ledger, the tax software or the practice
manager. It takes an export she can already produce, does the checking or bridging she
now does by hand, and returns something that goes straight back into what she already
uses: a workpaper for the file, a journal entry her software imports, or a list of
questions for the client.

## The value test

Every candidate must pass these five questions before anything is built. The answers go
in the episode's README.

1. **What does she already use for this step?** Name the software and what it does.
2. **What does it leave her to do by hand?** With evidence: practitioners' own words,
   the vendor's own help pages, or the primary documents.
3. **Can the tool start from an export she already has?** No new subscription, login or
   setup. One file in.
4. **Does the result go somewhere she already works?** A workpaper, an importable
   entry, or a client request.
5. **If her software is set up perfectly, is there still something left?** Say plainly
   what. If nothing, drop the idea.

## The five processes

The order is the release order. Each series starts in the season when its work peaks.

| No. | Process | What the accountant does for clients | Starts | Why then |
|---|---|---|---|---|
| 1 | [Procure-to-Pay](procure-to-pay/) | vendors, bills, payments, vendor statements, 1099s | Dec 2026 | 1099s are due February 1, 2027 |
| 2 | [Hire-to-Retire (payroll)](hire-to-retire/) | payroll runs, tax deposits, 941s, W-2s, payroll on the books | Jan 2027 | W-2s and the fourth-quarter 941 |
| 3 | Record-to-Report (close) | bank recs, accruals, review, financial statements | Feb 2027 | year-end close before tax returns |
| 4 | Order-to-Cash | invoices, customer payments, card and platform payouts, receivables, sales tax | Mar 2027 | year-end receivables and sales tax |
| 5 | Acquire-to-Retire (fixed assets) | purchases, capitalize or expense, depreciation, disposals | Apr 2027 | the depreciation schedule on the return |

### 1. Procure-to-Pay
- **She already has:** bills and payments in QuickBooks or Xero, bank feeds, a receipt
  app such as Dext or Hubdoc, the software's own 1099 report, and a filing service
  such as Track1099.
- **Left by hand:** deciding who gets a 1099 when the software's report only counts
  vendors someone flagged; matching a vendor's statement to the client's payables; at
  year end, finding January bills that belong to December.
- **Episodes:**
  - 01 [Who gets a 1099?](procure-to-pay/01-who-gets-a-1099/), built, version 1.1.0;
  - candidate: vendor statement against the payables ledger;
  - candidate: bills paid after year end that belong to the old year.

### 2. Hire-to-Retire (payroll)
- **She already has:** a payroll provider (Gusto, ADP, Paychex or the ledger's own
  payroll) that files the returns.
- **Left by hand:** proving the books agree with what the provider filed, above all when
  the client switched providers mid-year or booked payroll by hand.
- **Episodes:**
  - 01 [Do the 941s match the W-3?](hire-to-retire/01-do-the-941s-match-the-w3/), built, version 1.0.0;
  - candidate: W-2 review before filing (wage base, box 12 codes, 2% shareholder health insurance);
  - candidate: the payroll provider's annual report against the general ledger.

### 3. Record-to-Report (close)
- **She already has:** bank reconciliation in the ledger, a close checklist in her
  practice manager. Flux-analysis software exists but is sold to larger finance teams.
- **Left by hand:** explaining month-over-month swings and turning them into questions
  for the client; noticing that last year's closed books were changed after the return
  was filed; chasing reconciling items that have sat for months.
- **Candidates:**
  - month-over-month changes with client questions;
  - "did last year change?": last year's final trial balance against this year's
    opening balances;
  - stale reconciling items.

### 4. Order-to-Cash
- **She already has:** invoicing in the ledger, Stripe, Square or Shopify dashboards, and
  for some clients a sync app.
- **Left by hand:** turning a payout that is net of fees and refunds into gross sales,
  fees and refunds that tie to the bank deposit, for clients with no sync app;
  reviewing old receivables.
- **Candidates:**
  - a processor payout report turned into a journal entry that ties to the deposit;
  - a receivables aging review with a memo for the file.

### 5. Acquire-to-Retire (fixed assets)
- **She already has:** the depreciation module in her tax software, or an Excel schedule.
- **Left by hand:** finding equipment and improvements expensed as repairs or supplies;
  tying the asset schedule to the trial balance.
- **Candidates:**
  - a general ledger sweep for items that may need to be capitalized;
  - the fixed asset roll-forward against the trial balance.

The candidates above have not yet been through Stage 1. Each will be tested against the
evidence and the value test before it is chosen. A candidate that fails is recorded in
`BACKLOG.md` with the reason.

## Work that does not belong to one of the five

Individual tax work, such as summarizing a client's brokerage 1099s, starts from documents
outside the five processes. It is parked in `BACKLOG.md` and may become its own short
series.
