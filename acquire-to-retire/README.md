# Acquire-to-Retire

Everything from a client deciding to buy equipment, a vehicle or an improvement, to the year it is
sold, scrapped or fully depreciated.

```
Purchase  ->  Capitalize or expense  ->  Asset schedule  ->  Depreciation  ->  Sale or disposal
 (bill)        (policy, de minimis)       (tax software or      (tax return,      (gain or loss,
                                           Excel)                books)            schedule updated)
```

## Episodes

| No. | Tool | Step | What it adds to what she already has | Version | Date |
|---|---|---|---|---|---|
| 01 | [What goes on the asset schedule?](01-what-goes-on-the-asset-schedule/) | Year end | Reads the client's general ledger for the year and finds what the depreciation schedule needs: purchases recorded as assets, purchases buried in repairs and supplies, assets sold or written off, and whether the books still agree with last year's schedule and this year's depreciation. | 1.0.0 | 2026-11-25 |

## Stage 1: how episode 01 was chosen (2026-11-18)

### Evidence
- **It is every client with equipment, every year end.** Year-end checklists start depreciation
  from a list of additions and disposals: "Depreciation starts from this list, and reconstructing it
  in March from faded memory is how deductions get missed"
  ([Beancount year-end checklist, Oct 2026](https://beancount.io/blog/2026/10/13/year-end-bookkeeping-closing-checklist-cpa-handoff-lock-guide)).
  A fixed asset checklist asks for "Beginning balance + additions - disposals = ending balance, by
  asset class, for both cost and accumulated depreciation"
  ([Manifest checklist](https://app.manifest.ly/public/checklists/fixed-assets-management-checklist)).
- **Purchases end up in expense accounts.** A practice-management article on client mistakes:
  "Clients who are not knowledgeable about accounting may charge fixed assets to expense accounts"
  ([Woodard](https://report.woodard.com/articles/those-mistakes-clients-always-make-dembwr), via a
  search summary; the page could not be opened from the build environment).
- **The books and the depreciation schedule drift apart.** The depreciation schedule usually lives in
  the tax software; the books have their own fixed asset and accumulated depreciation accounts.
  Intuit's community answers for a mismatch are a manual adjusting entry, account by account, and
  QuickBooks Online computes depreciation itself only on its Advanced plan
  ([QuickBooks community](https://quickbooks.intuit.com/learn-support/en-us/reports-and-accounting/why-doesn-t-the-quickbooks-balance-for-my-fixed-assets-match-my/00/889813);
  [Intuit help, via search summary](https://quickbooks.intuit.com/learn-support/en-us/manage-fixed-assets/record-and-depreciate-assets/00/186373)).
  Tax software support pages exist for the result: "balance sheet out of balance, depreciation
  difference" ([Thomson Reuters UltraTax help](https://www.thomsonreuters.com/en-us/help/ultratax-cs/depreciation/balance-sheet-out-of-balance-depreciation-diff)).
- **The rule the review applies.** The de minimis safe harbor lets a business without an applicable
  financial statement expense items of $2,500 or less per invoice or item ($5,000 with one), if it
  also expenses them in its books and elects it on each year's return (Treas. Reg.
  1.263(a)-1(f); IRS Notice 2015-82). Anything above it is a capitalization question.

### What she already has, and what it leaves
- **The depreciation module in her tax software** (or Excel): it depreciates what is entered. It
  does not know what was bought this year unless someone finds it.
- **The ledger:** QuickBooks Online Advanced and Xero have fixed asset registers; most small clients
  do not use them, and a register still only knows what was coded to it.
- **Left by hand:** reading the year's ledger for purchases, in the asset accounts and in repairs,
  supplies and computer expense; finding sales and write-offs; rolling cost and accumulated
  depreciation forward and tying them to last year's schedule and this year's depreciation.

### Candidates considered

| Candidate | Who, how often | By hand | Error cost | Why software has not solved it | Verdict |
|---|---|---|---|---|---|
| **Year-end fixed asset review from the general ledger** | Every client with equipment, vehicles or improvements, every year end | 45 to 90 minutes per client (estimate) | Missed depreciation, expensed items that should be capitalized (or the reverse), gains on sales never recorded, books that do not agree with the return | The depreciation module only sees what is entered; nobody reads the ledger for it | **Chosen** |
| A depreciation calculator (book and tax) | Same | Done by the tax software already | High if wrong: MACRS tables, bonus and section 179 rules change | Tax software does it; duplicating it adds risk, not value | Rejected |
| Loan schedule tied to the lender statement | Clients with debt, monthly and year end | 20 to 60 minutes per loan | Interest and principal split wrong; current portion missing | Lenders send statements; nobody splits them | Next, under financing |

### Value test
1. **Common:** every business client with equipment, every year. Passes.
2. **Painful by hand:** a year of ledger lines read account by account. Passes.
3. **Between the apps:** reads the ledger export and produces the list the depreciation module and
   the adjusting entries need. Passes.
4. **Checkable:** every line on the output points to a ledger line. Passes.
