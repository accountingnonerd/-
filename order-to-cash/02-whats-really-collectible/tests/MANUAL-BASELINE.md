# Manual baseline: the same review by hand

**Status: estimated, not measured.** No accountant has been timed yet. The minutes are counts from
the test files multiplied by assumed rates. Replace them with stopwatch times after the test in
`ACCOUNTANT-TEST-SCRIPT.md`.

## The steps by hand
1. Export the A/R aging detail; open it in Excel; tie it to A/R on the balance sheet.
2. Scan for negative lines (payments, credit memos); find the invoice each belongs to.
3. Look for invoices entered twice, small leftover balances and invoices over a year old.
4. Sort customers by what is overdue and how old; decide the next step for each.
5. Write the reminders.
6. Work out the allowance from the client's loss rates; propose write-offs and entries.

## Estimated time

Assumed rates: 10 minutes to export, open and tie; 1 minute per credit line to find its invoice; 10
minutes to scan for duplicates, small and old balances; 20 seconds per customer to rank and decide; 3
minutes per reminder; 15 minutes for the allowance and entries.

For a typical test file (about 140 open items, 35 customers, 30 overdue, 5 credits): 10 + 5 + 10 + 12 + 90 + 15 minutes, about **2 hours
20 minutes**, most of it the reminders (90 minutes). Without the reminders: about 50 minutes.
The tool takes under a second and drafts every reminder; the time it does not save is reading them,
talking to the client, and deciding.

## What the manual method is exposed to in these files

| Case | What is wrong | Consequence if missed |
|---|---|---|
| 03 | Four payments never applied; a customer who paid twice | Four customers chased for invoices they paid; a refund owed and not made |
| 04 | An invoice entered twice | Sales and receivables overstated; a customer chased for the copy |
| 05 | The balance sheet's A/R is $3,150 more than the aging | A receivable on the balance sheet with no customer behind it |
| 08 | Invoices over a year old; small leftover balances | Receivables overstated; reminders for $0.75 |
| 12, 13 | A total typed over; lines pasted twice | A review built on the wrong numbers |
| 17 | One check paying two invoices; a payment posted to the wrong customer | Two customers chased, one refunded in error |
