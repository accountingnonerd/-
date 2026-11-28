Agent file: `why-wont-the-bank-rec-tie.html`

**27 of 27 cases passed; 833 of 833 individual checks.**

| Case | What it is | Type | Checks passed | Run time (ms) | Result |
|---|---|---|---|---|---|
| 01 | A normal quarter: generic bank CSV, QuickBooks Online ledger; checks outstanding, a deposit in transit, fees and interest not in the books | clean | 36/36 | 129 | PASS |
| 02 | The bank's download newest first, with a check-number column | ugly | 36/36 | 116 | PASS |
| 03 | A summary block above the bank's lines; a Xero ledger with three accounts, the checking account chosen | ugly | 37/37 | 138 | PASS |
| 04 | No heading row, no balance column (the accountant types the statement's beginning and ending balances); QuickBooks Desktop ledger | ugly | 36/36 | 192 | PASS |
| 05 | Planted: two checks entered for the wrong amount, an online payment with its digits swapped, a customer payment entered twice | planted | 39/39 | 444 | PASS |
| 06 | Planted: card sales recorded one by one that land as one deposit; a refund paid out entered as money in; withdrawals and deposits columns | planted | 39/39 | 135 | PASS |
| 07 | Planted: two checks over six months old, two over 90 days (one at about 165 days), and a deposit recorded but never made | planted | 39/39 | 141 | PASS |
| 08 | The books file starts on the bank file's first day: two checks written in December clear in January and are recognized as recorded before | ugly | 37/37 | 349 | PASS |
| 09 | Planted: a line missing from the bank's download, so its running balance jumps | planted | 4/4 | 94 | PASS |
| 10 | The wrong books file: a trial balance | ugly | 4/4 | 81 | PASS |
| 11 | The wrong bank file: the books' ledger dropped as the bank's download | ugly | 4/4 | 81 | PASS |
| 12 | Planted: $100.00 that no transaction explains (the bank's beginning balance does not fit the books), so it does not tie | planted | 38/38 | 105 | PASS |
| 13 | The ledger as CSV with dollar signs and parentheses; two bank accounts, the accountant chooses the second | ugly | 37/37 | 262 | PASS |
| 14 | No balances anywhere: the page matches, lists, and asks for the statement's balances before it can prove the tie | ugly | 37/37 | 111 | PASS |
| 15 | A credit card account: this version reconciles bank accounts only, and says so | ugly | 4/4 | 78 | PASS |
| 16 | A customer's check number on a payment received; a coffee, a building maintenance bill and a returned check that only look like bank fees | planted | 36/36 | 98 | PASS |
| 17 | Rent paid every month: January's is missing from the books, and December's (cleared in December) must not be taken for it | planted | 36/36 | 93 | PASS |
| 18 | The same payment to the same vendor on 12/30 (cleared in December) and 1/2: not entered twice | ugly | 34/34 | 91 | PASS |
| 19 | The bank paid check 6001 twice and paid check 6003, which the books voided; check 6002 for the same amount is still outstanding | planted | 36/36 | 199 | PASS |
| 20 | The statement ends 3/31 though the last line is 3/27; a pending line; amounts with DR, CR, USD and a true minus sign | ugly | 36/36 | 113 | PASS |
| 21 | A bank line whose amount cannot be read: the page stops rather than drop it | ugly | 4/4 | 70 | PASS |
| 22 | Payroll posted to a sub-account, Checking:Payroll: the sub-account is part of the bank account | ugly | 35/35 | 94 | PASS |
| 23 | One deposit in the books that the bank shows as two lines; a bank check for the same amount as a book check but a different number | ugly | 36/36 | 94 | PASS |
| 24 | Two old checks of $100, one still outstanding: the page cannot tell which and asks; the accountant ticks December's | planted | 35/35 | 195 | PASS |
| 25 | Same files as 08, but the accountant ticks only one of the two suggested lines: the other stays unexplained and it does not tie | ugly | 38/38 | 192 | PASS |
| 26 | The readers' sample: Mapleton Landscaping, with the reader's decisions (fix the check entered for the wrong amount, remove the deposit entered twice, keep the stale check outstanding) | planted | 40/40 | 346 | PASS |
| 27 | The sample again, with the stale check reversed to a liability: it leaves the outstanding total and the books go up by the same $415.00 | planted | 40/40 | 414 | PASS |
