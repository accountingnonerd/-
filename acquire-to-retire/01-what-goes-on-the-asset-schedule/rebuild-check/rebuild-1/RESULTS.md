Agent file: `what-goes-on-the-asset-schedule.html`

**22 of 22 cases passed; 758 of 758 individual checks.**

| Case | What it is | Type | Expected verdict | Checks passed | Run time (ms) | Result |
|---|---|---|---|---|---|---|
| 01 | QuickBooks Online, a clean year: purchases recorded as assets, depreciation booked | clean | COMPUTED | 34/34 | 125 | PASS |
| 02 | QuickBooks Online, last year's schedule and this year's depreciation typed in: both agree | clean | COMPUTED | 40/40 | 237 | PASS |
| 03 | Planted: an HVAC unit, laptops and a machine expensed; a quarterly service contract that is routine | planted | COMPUTED | 36/36 | 107 | PASS |
| 04 | Planted: a truck sold with the proceeds credited to Vehicles; accumulated depreciation untouched | planted | COMPUTED | 36/36 | 102 | PASS |
| 05 | Planted: no depreciation booked; the tax software's figure typed in | planted | COMPUTED | 37/37 | 166 | PASS |
| 06 | Planted: opening cost and accumulated depreciation differ from last year's schedule | planted | COMPUTED | 41/41 | 174 | PASS |
| 07 | Xero Account Transactions: default account names; lighting expensed as a repair | ugly | COMPUTED | 35/35 | 144 | PASS |
| 08 | QuickBooks Desktop General Ledger: account numbers, Debit and Credit, no period | ugly | COMPUTED | 37/37 | 99 | PASS |
| 09 | QuickBooks Online as CSV: dollar signs, parentheses; a returned part credited to the asset | ugly | COMPUTED | 36/36 | 89 | PASS |
| 10 | A bill entered twice and reversed; an addition by journal entry; the reclassed repair is not proposed again | ugly | COMPUTED | 37/37 | 106 | PASS |
| 11 | The wrong report: a trial balance | ugly | NOT_RECOGNIZED | 4/4 | 80 | PASS |
| 12 | The wrong report: an A/R aging | ugly | NOT_RECOGNIZED | 4/4 | 91 | PASS |
| 13 | Planted: a line missing from the export, so Furniture and Equipment does not add up | planted | COMPUTED | 36/36 | 106 | PASS |
| 14 | The client has audited statements: a $5,000 threshold typed in | ugly | COMPUTED | 35/35 | 171 | PASS |
| 15 | An asset account named 'Shop Assets': the page asks, the accountant marks it as a fixed asset | ugly | COMPUTED | 33/33 | 130 | PASS |
| 16 | QuickBooks Online, a fiscal year ending June 30 (still twelve months) | ugly | COMPUTED | 35/35 | 102 | PASS |
| 17 | A sale booked properly: cost and accumulated depreciation removed, gain recorded | clean | COMPUTED | 36/36 | 104 | PASS |
| 18 | QuickBooks Online fixed asset tracking: 'Original cost' and 'Depreciation' sub-accounts, nested, with parent totals | ugly | COMPUTED | 35/35 | 115 | PASS |
| 19 | Accounts named after assets that are not assets (a truck loan, a note payable, a gain); amortization; a down payment in auto expense | planted | COMPUTED | 41/41 | 105 | PASS |
| 20 | A truck bought net of a trade-in, loan payments posted to Vehicles, land and a building bought in November | planted | COMPUTED | 41/41 | 117 | PASS |
| 21 | Purchases already reclassed, a part refund, a bill split over two accounts, a transfer between asset accounts, a return; three tools that are not routine | planted | COMPUTED | 42/42 | 117 | PASS |
| 22 | The readers' sample: Ridgeline Landscaping, with the reader's decisions, last year's schedule, this year's depreciation and the sold truck's figures typed | planted | COMPUTED | 47/47 | 925 | PASS |
