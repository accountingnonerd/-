Agent file: `whats-really-collectible.html`

**17 of 17 cases passed; 2066 of 2066 individual checks.**

| Case | What it is | Type | Expected verdict | Checks passed | Run time (ms) | Result |
|---|---|---|---|---|---|---|
| 01 | QuickBooks Online, a clean book | clean | COMPUTED | 154/154 | 132 | PASS |
| 02 | QuickBooks Online, A/R from the balance sheet typed in: it ties | clean | TIES | 155/155 | 161 | PASS |
| 03 | Planted: unapplied payments, a credit memo, a customer who paid twice | planted | COMPUTED | 160/160 | 91 | PASS |
| 04 | Planted: the same invoice entered twice; a twice-weekly flat bill that is not a duplicate | planted | COMPUTED | 163/163 | 101 | PASS |
| 05 | Planted: the balance sheet's A/R is $3,150.00 more than the aging | planted | DIFFERS | 156/156 | 156 | PASS |
| 06 | Xero: a credit note and an overpayment | ugly | COMPUTED | 111/111 | 89 | PASS |
| 07 | QuickBooks Desktop: no as-of date, days from the Aging column; a credit memo refunded by check | ugly | COMPUTED | 152/152 | 82 | PASS |
| 08 | Invoices over a year old, small leftover balances; allowance rates and the allowance on the books | ugly | COMPUTED | 166/166 | 222 | PASS |
| 09 | QuickBooks Online as CSV: dollar signs, parentheses, jobs under customers | ugly | COMPUTED | 95/95 | 69 | PASS |
| 10 | The wrong report: A/P aging detail | ugly | NOT_RECOGNIZED | 4/4 | 62 | PASS |
| 11 | The summary report, with no invoices in it | ugly | NOT_RECOGNIZED | 4/4 | 57 | PASS |
| 12 | Planted: the report's total line does not agree with its lines | planted | COMPUTED | 167/167 | 92 | PASS |
| 13 | Planted: three lines pasted in twice | planted | COMPUTED | 160/160 | 95 | PASS |
| 14 | Allowance rates typed in; a journal entry in A/R; one customer holds a large share | ugly | COMPUTED | 89/89 | 190 | PASS |
| 15 | Two real payments of $500 on the same day, no number: identical lines, both kept | ugly | COMPUTED | 112/112 | 88 | PASS |
| 16 | No as-of date in the file: the page asks for it, then reviews | ugly | COMPUTED | 102/102 | 175 | PASS |
| 17 | Planted: one check for two invoices; a payment posted to the wrong customer | planted | COMPUTED | 116/116 | 99 | PASS |
