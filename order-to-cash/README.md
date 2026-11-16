# Order-to-Cash

Everything from the sale to the cash in the bank, and the sales the IRS hears about from
someone else.

```
Invoice or sale  ->  Card, app or marketplace payment  ->  Payout to the bank  ->  Receivables  ->  Sales tax  ->  Year end: 1099-K
```

## Episodes

| No. | Tool | Step | What it adds to what she already has | Version | Date |
|---|---|---|---|---|---|
| 01 | [Does the 1099-K tie?](01-does-the-1099k-tie/) | Year end | Turns a client's year of Square, Stripe or PayPal transactions into what the 1099-K should show, month by month, and the bridge from that gross to the books and to the bank deposits, with the entry that grosses up net deposits. | 1.0.0 | **parked** 2026-11-15: built and tested, not released |
| 02 | [What's really collectible?](02-whats-really-collectible/) | Monthly and year end | Turns the A/R aging detail into the review: credits matched to the invoices they belong to, customers in credit, duplicates and mis-postings, a ranked list of who to chase with a draft letter each, and the allowance and write-offs from the accountant's loss rates. | 1.0.0 | awaiting approval |

## Stage 1: how episode 01 was chosen (parked)

### Evidence
- **The rule.** The IRS instructions for Form 1099-K define box 1a: "'Gross amount' means the
  total dollar amount of total reportable payment transactions for each participating payee
  without regard to any adjustments for credits, cash equivalents, discount amounts, fees,
  refunded amounts, shipping amounts, or any other amounts. The dollar amount of each
  transaction is determined on the date of the transaction." Boxes 5a to 5l give the gross for
  each month. ([IRS](https://www.irs.gov/instructions/i1099k))
- **Who gets one.** "If your customers or clients pay you directly by credit, debit or gift card,
  you'll get a Form 1099-K from your payment card processor no matter how many payments you got
  or how much they were for." Payment apps and marketplaces report above $20,000 and 200
  transactions. ([IRS](https://www.irs.gov/businesses/understanding-your-form-1099-k))
- **The cost of a mismatch.** Intuit's ProConnect help page: "the client may receive an IRS notice
  if the gross receipts don't reflect amounts from the 1099-K. To avoid this, be sure to include
  amounts from Form 1099-K when calculating gross receipts or sales."
  ([Intuit](https://accountants.intuit.com/support/en-us/help-article/form-1099-k/entering-form-1099-k-transactions-proconnect-tax/L1sbeU13g_US_en_US))
- **It happens.** A preparer, August 2022: "The 1099K shows more than what the deposits in the
  bank are... Ebay withholds funds from the seller for various fees and deposits into the seller's
  bank account the customer charges minus fees... Do I gross up sales that were recorded as net
  deposits?" ([thread](https://accountants.intuit.com/community/proconnect-tax-discussions/discussion/1099-for-s-corp/00/229306))
- **And the sales tax inside it.** February 2024: "I have a client with a 1099-K that includes
  sales taxes collected. Should Line 1 (gross receipts or sales) on my client's business return
  match the 1099-K or should I subtract the sales tax?" A reply quotes the Schedule C
  instructions: whether collected sales tax belongs in gross receipts depends on whether the
  state imposes the tax on the seller or the buyer. A later poster: "$176K in a 1099... The sales
  tax exceeds $13K so I'm not sure how to handle this."
  ([thread](https://accountants.intuit.com/community/proseries-tax-discussions/discussion/accounting-treatment-for-1099-k-that-includes-sales-tax/00/283709))

### What she already has, and what it leaves
- **The bank feed** in QuickBooks or Xero sees the payout: sales less fees, less refunds, less
  chargebacks, plus sales tax and tips. Many small clients' books record that payout as sales.
- **Sync apps** (A2X, Synder and others) record gross sales and fees for clients who pay for
  them. They do not produce the 1099-K reconciliation for the return, and many small clients
  have none.
- **The processor's dashboard** shows the transactions and the 1099-K. It does not say what
  belongs on which line of the return, or how the deposits tie.
- **Tax software** takes the gross receipts she types in.

### Candidates considered

| Candidate | Who, how often | By hand | Error cost | Why software has not solved it | Verdict |
|---|---|---|---|---|---|
| **Does the 1099-K tie?** A year of processor transactions to the 1099-K, the return and the deposits | Every client who takes cards or app payments; each January to April, when the 1099-K arrives | 30 to 90 minutes per processor account (estimate): export, pivot by month, separate refunds, fees, sales tax, tips, cash | An IRS notice (underreported income) when gross receipts are below the 1099-K; or income overstated by sales tax and tips; fees never deducted | The bank feed sees only net payouts; sync apps cost money and stop short of the return | **Chosen** |
| Processor payouts to a journal entry, monthly | Monthly bookkeeping clients with card sales | 15 to 30 minutes per month (estimate) | Sales understated and fees missing during the year | Sync apps exist for clients who pay for them | Folded into the chosen tool: its entry is the year's gross-up |
| Receivables aging review with a memo | Accrual clients with receivables, year end | 20 to 40 minutes (estimate) | Bad debts not written off; overstated income | The aging report exists in every ledger; the judgment is hers | Later |

### What a top practitioner would insist on
- **Use the IRS definition of gross,** not the processor's "net sales": before refunds, fees and
  discounts, including sales tax, tips and shipping, on the date of the transaction.
- **Tie three ways:** to the 1099-K (box 1a and each month), to the bank deposits (payouts), and
  to the return's lines (gross receipts, returns and allowances, merchant fees).
- **Separate what is not sales:** sales tax collected for the state, tips paid to staff, personal
  transfers through a payment app, money moved in from the bank.
- **Notice what is missing:** a month with no activity, an export that stops early, overlapping
  exports that count a month twice.
- **Watch the year-end edges:** sales on December 31 paid out in January; refunds in January of
  last year's sales; time zones that move a late sale into the next year.
- **Leave the judgment to her:** whether sales tax goes in gross receipts depends on the state;
  whether a payment-app transfer was personal is a question for the client.

### Value test
1. **She already has:** the bank feed, the processor's dashboard and 1099-K, and tax software.
2. **Left by hand:** grossing up net deposits, separating sales tax, tips and refunds, and proving
   the 1099-K ties to the return.
3. **Input she has:** the processor's transaction export for the year (Square, Stripe or PayPal),
   as CSV or Excel. One file in.
4. **Output where she works:** a reconciliation for the tax file, the figures for the return's
   lines, and an entry for the books.
5. **If everything is set up perfectly** (a sync app recording gross sales and fees), the books
   are right, but the 1099-K still has to be reconciled to the return: sales tax, tips, refunds
   and year-end timing still separate the 1099-K from gross receipts.

## Stage 1: how episode 02 was chosen

Chosen under the rule set on 2026-11-15: solve a common problem in the core work, one that most
small-firm accountants meet every month, not a niche corner.

### Evidence
- **It is common.** Intuit's 2025 QuickBooks small business late payments report (2,487 US small
  businesses), as reported by press summaries: 56% have outstanding unpaid invoices, owed $17,500 on
  average, and 47% have invoices more than 30 days overdue. Xero's data puts the average invoice at
  28.3 days to pay in late 2025, 8.4 days late. (Both from secondary summaries; the primary reports
  could not be opened from the build environment.)
- **It is the accountant's job at every close.** CPA Practice Advisor's year-end receivables checklist
  for accountants: "CPAs should work with clients to review aging reports, focusing on accounts that
  have remained outstanding for over 90 days", and "identify any unapplied credits or overpayments in
  their records and encourage them to contact customers to confirm applications to open balances or
  issue refunds as necessary."
  ([CPA Practice Advisor, Nov 2024](https://www.cpapracticeadvisor.com/2024/11/07/end-of-year-accounts-receivable-checklist-ensuring-financial-stability-for-your-clients-into-the-new-year/152124/))
- **Why the clean-up is needed.** In QuickBooks, an unapplied payment or credit memo leaves the net
  aging correct but both the credit and the invoice "still listed" as open, so the aging overstates
  what is overdue. ([CPA Practice Advisor](https://www.cpapracticeadvisor.com/2019/02/26/quickbooks-data-file-analysis-with-the-client-data-review-tool/764/))
- **The year-end allowance.** ASU 2025-05 lets entities measure credit losses on current receivables
  assuming current conditions continue, and lets private companies consider cash collected after
  year end before the statements are issued. It is effective for annual periods beginning after
  December 15, 2025, so December 31, 2026 is the first year end for calendar-year clients.
  ([RSM](https://www.rsmus.com/insights/financial-reporting/amended-guidance-for-measuring-credit-losses-on-short-term-receivables);
  [Deloitte](https://dart.deloitte.com/USDART/home/news/all-news/2025/jul/fasb-amends-guidance-measurement-credit-losses-accounts-receivable-contract-assets))
- **The tax side.** A business bad debt is deductible "only if the amount you were owed is included in
  your gross income in the current or prior year"; a cash-method business generally cannot deduct an
  unpaid invoice. ([IRS Topic 453](https://www.irs.gov/taxtopics/tc453))

### What she already has, and what it leaves
- **The ledger's A/R aging report** (QuickBooks Online and Desktop, Xero): totals by bucket and by
  customer. It does not say which credits belong to which invoice, which invoices look duplicated,
  which customer to call first, or what to reserve.
- **Invoice reminders** in the ledger, and paid collection tools (Chaser, Upflow and others): they
  chase invoices; they do not clean the ledger or produce the accountant's workpaper.
- **Excel:** where the review happens today, by hand.

### Candidates considered

| Candidate | Who, how often | By hand | Error cost | Why software has not solved it | Verdict |
|---|---|---|---|---|---|
| **Receivables review: collect, clean, reserve** | Every client with invoices, every month or quarter, and every year end | 30 to 90 minutes per client (estimate) | Overstated receivables and income; cash not collected; credits that belong to customers; an allowance nobody can support | The aging lists; nobody turns it into actions, clean-up and a supported allowance | **Chosen** |
| 13-week cash flow forecast from the AR and AP agings | Clients with tight cash, monthly | 1 to 3 hours (estimate) | Surprises in payroll and supplier payments | Forecasting apps exist but need a subscription and setup | Next, built on this episode's receivables reading |
| Does the 1099-K tie? | Clients taking cards, at tax time | 50 to 90 minutes (estimate) | IRS notice | Covered under episode 01 | Built and parked |

### What a top practitioner would insist on
- **Tie first:** the aging must agree with A/R on the balance sheet, and with its own total line.
- **Clean before you chase:** apply unapplied payments and credit memos to the invoices they belong to
  before anyone calls a customer about an invoice that is already paid.
- **Rank by money and age,** not alphabetically: the large old balances first.
- **Say what each step is:** reminder, call, final notice, collection agency, write-off.
- **Support the allowance:** specific accounts identified, rates shown, the judgment hers.
- **Mind the tax line:** write-offs are deductible only on the accrual method, and the allowance is
  not deductible at all.

### Value test
1. **She already has:** the A/R aging report, invoice reminders, Excel.
2. **Left by hand:** matching credits to invoices, spotting duplicates and tiny balances, ranking whom
   to chase, writing the reminders, and supporting the allowance.
3. **Input she has:** the A/R aging detail report, exported to Excel or CSV. One file in.
4. **Output where she works:** a workpaper for the file, a clean-up list to work through in the
   ledger, reminders to send, and a proposed write-off entry.
5. **If everything is set up perfectly** (payments always applied, reminders automatic), she still
   ranks the old balances, decides what to write off, and supports the allowance at year end.
