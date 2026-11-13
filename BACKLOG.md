# Backlog

Candidate problems, filed under the process they belong to, plus reader suggestions and
killed ideas. A candidate is chosen only after it passes Stage 1 and the value test in
[SERIES.md](SERIES.md).

## 1. Procure-to-Pay
- **Built:** 01 Who gets a 1099? (version 1.1.0).
- **Vendor statement against the payables ledger.** Not yet researched.
- **Bills paid after year end that belong to the old year** (the search for unrecorded
  liabilities at year end). Not yet researched.

## 2. Hire-to-Retire (payroll)
- **Built:** 01 Do the 941s match the W-3? (version 1.0.0).
- **W-2 review before filing.** Check each employee against the wage base, box 5 against
  boxes 3 and 7, box 12 codes, and 2% S corporation shareholder health insurance in box 1.
  Needs a list of 2% shareholders, which the provider's export does not carry.
- **Payroll provider's annual report against the general ledger.** Two inputs; may belong
  in Record-to-Report.
- **Read real providers' filed copies.** Episode 01 was tested on the IRS forms and one
  provider layout drawn by us. Collect one filed 941 and W-3 each from Gusto, ADP, Paychex and
  QuickBooks Payroll (with client data removed) and add them to the tests.

## 3. Record-to-Report (close)
- **Built:** 01 Did last year change? (version 1.0.0).
- **Month-over-month changes with client questions.** Flux software exists (FloQast,
  Numeric and others) for larger finance teams, and small-firm review tools (Xenett, listed at
  $7.50 per client per month, Keeper) already do it inside QuickBooks Online and Xero. Needs a
  gap those tools leave before it is built.
- **Stale reconciling items.** The ledger's reconciliation report already lists uncleared
  items with their dates.
- **Did last year change? follow-ups** from its review: a test layout with an export date
  and time above the column headings; real QuickBooks Desktop and Xero exports (client data
  removed); tax-only adjustments marked as such in the workpaper.
- **Financial statement footing and cross-tie.** Forums where this is discussed (Fishbowl,
  Going Concern) blocked automated reading. SEC EDGAR filings would be the test inputs.

## 4. Order-to-Cash
- **Processor payouts to a journal entry.** A Stripe, Square or Shopify payout report,
  turned into gross sales, fees and refunds that tie to the bank deposit, for clients
  with no sync app. Sync apps exist (A2X, Synder, Webgility and others); the gap is the
  client without one.
- **Receivables aging review** with a memo for the file.

## 5. Acquire-to-Retire (fixed assets)
- **A general ledger sweep for purchases that may need to be capitalized**, measured
  against the client's capitalization policy and the de minimis safe harbor (to be
  verified in Stage 1).
- **Fixed asset roll-forward against the trial balance.**

## Outside the five processes
- **Brokerage 1099 entry sheet** (individual tax). Strong evidence, a good fit for
  February:
  - "Manual entry of the brokerage 1099s is very time consuming... many of my clients
    have several 1099s so a lot open/close PDFs to get to those totals." (April 2026,
    [Intuit Accountants Community](https://accountants.intuit.com/community/practice-advice-17/what-still-has-too-much-manual-follow-up-in-your-tax-workflow-today-5852))
  - "a 45 page 1099-B summary statement, over a million in proceeds/basis, with 45k in
    wash sales" ([thread](https://accountants.intuit.com/community/proseries-product-discussions-9/is-there-an-easier-way-to-input-transactions-on-the-1099-b-when-there-are-wash-sales-or-other-adjustments-83114))
  - Risk: practitioners disagree on summarizing wash sales
    ([thread](https://accountants.intuit.com/community/proseries-product-discussions-9/large-amounts-of-stock-transactions-from-1099b-with-wash-sales-81704)).

  Parked: it does not belong to one of the five processes. It may become a short tax series.

## Killed
- **PDF bank statement to a transaction list** (2026-11-11). The evidence was weak. The
  field is crowded with paid converters that already claim a balance tie-out, so it
  fails value test question 5.

## Reader suggestions
Replies to each article's closing question go here, with the date, the process they
belong to, and a link.

- Series 1, Agent 3 (Record-to-Report 01) published 2026-11-13: [LinkedIn post](https://www.linkedin.com/feed/update/urn:li:ugcPost:7527075530622431233). No replies collected yet.
- Series 1, Agent 2 (Hire-to-Retire 01) published 2026-11-12: [LinkedIn post](https://www.linkedin.com/feed/update/urn:li:ugcPost:7526706866022699008). No replies collected yet.
- Series 1, Agent 1 (Procure-to-Pay 01) published 2026-11-11: [LinkedIn post](https://www.linkedin.com/feed/update/urn:li:ugcPost:7526375179346870272). No replies collected yet.

## Sources we could not read
Reddit (r/Accounting, r/taxpros, r/Bookkeeping), TaxProTalk, Fishbowl, Going Concern,
AccountingWEB, Xero Central and the QuickBooks community all refuse automated reading.
A thread that is pasted in can be quoted.
