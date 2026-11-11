# Series 1: Procure-to-Pay

Everything between a client deciding to buy something and the year-end forms that report
what was paid.

```
Vendor set up  ->  Bill  ->  Payment  ->  Vendor statement  ->  Year end: 1099s, cutoff
 (W-9)                                       reconciled
```

## Episodes

| No. | Tool | Step | What it adds to what she already has | Version | Date |
|---|---|---|---|---|---|
| 01 | [Who gets a 1099?](01-who-gets-a-1099/) | Year end | Reads every payment, not only the vendors someone flagged for 1099. Finds the same vendor under three spellings, checks entered twice, and files that do not add up. | 1.1.0 | 2026-11-11 |

## Value test for episode 01

1. **What she already uses.** QuickBooks Online and Xero each have a 1099 report, and
   both leave out card payments automatically. Xero counts contacts that someone marked
   as 1099 contacts. QuickBooks counts vendors marked "Track payments for 1099", paid from
   accounts mapped to a 1099 box. Filing services such as Track1099 file what that
   report produces.
2. **What it leaves by hand.** Anyone whose flag or mapping was never set is missing.
   Intuit keeps a help page for exactly this:
   ["Fix missing contractors and wrong amounts on 1099s"](https://quickbooks.intuit.com/learn-support/en-us/help-article/electronic-tax-filing/fix-missing-contractors-wrong-amounts-1099s/L0MspaDKN_US_en_US).
   Its community has threads titled
   ["some vendors are missing from 1099 prepare"](https://quickbooks.intuit.com/community/taxes-8/some-vendors-are-missing-from-1099-prepare-16215).
   On write-up software with no such report, "We print out the GL for the year or YTD
   and manually search the transactions for Vendors eligible for 1099's"
   ([Intuit Accountants Community](https://accountants.intuit.com/community/easyacct-discussions/discussion/how-to-print-1099-vendor-list/00/229893)).
3. **Starts from an export she has.** Yes: the year's payments, from any ledger, as Excel or CSV.
4. **Result goes where she works.** A signed, printable workpaper. The vendor list feeds
   whichever filing service she already uses.
5. **If the software is set up perfectly.** The software's report is then mostly right,
   and the tool becomes the reviewer's check. It still catches what flags cannot: one
   vendor typed three ways, a check entered twice, a refund that hides a vendor, a law
   firm that is incorporated, and a file whose totals do not tie. For clients whose
   flags were never set, which is common in catch-up and write-up work, it does the
   whole first pass.

## Candidates for later episodes
- Vendor statement against the payables ledger.
- Bills paid after year end that belong to the old year.

See [`../SERIES.md`](../SERIES.md) for all five processes and the value test.
