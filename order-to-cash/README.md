# Order-to-Cash

Everything from the sale to the cash in the bank, and the sales the IRS hears about from
someone else.

```
Invoice or sale  ->  Card, app or marketplace payment  ->  Payout to the bank  ->  Receivables  ->  Sales tax  ->  Year end: 1099-K
```

## Episodes

| No. | Tool | Step | What it adds to what she already has | Version | Date |
|---|---|---|---|---|---|
| 01 | [Does the 1099-K tie?](01-does-the-1099k-tie/) | Year end | Turns a client's year of Square, Stripe or PayPal transactions into what the 1099-K should show, month by month, and the bridge from that gross to the books and to the bank deposits, with the entry that grosses up net deposits. | 1.0.0 | in progress |

## Stage 1: how episode 01 was chosen

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
