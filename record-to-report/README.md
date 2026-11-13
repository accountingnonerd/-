# Record-to-Report (the close)

Everything from recording the month's transactions to the statements and the return that
are built on them.

```
Transactions  ->  Bank reconciliations  ->  Adjusting entries  ->  Review  ->  Statements and the return  ->  Close the year
```

## Episodes

| No. | Tool | Step | What it adds to what she already has | Version | Date |
|---|---|---|---|---|---|
| 01 | [Did last year change?](01-did-last-year-change/) | Opening a new year | Compares last year's final trial balance from her file with the client's books as they stand today, for the same date. Lists every account that moved, says whether last year's profit changed, finds the adjusting entries the client never posted, and drafts the entry that puts the opening balances back. | 1.0.0 | 2026-11-13, [published](https://www.linkedin.com/feed/update/urn:li:ugcPost:7527075530622431233) |

## Stage 1: how episode 01 was chosen

### Evidence
- **The rule.** The IRS instructions for Form 1120-S (2025) say of Schedule L: "The balance
  sheets should agree with the corporation's books and records."
  ([IRS](https://www.irs.gov/instructions/i1120s)) The beginning-of-year column on this
  year's return is last year's ending column. If the client's books for last year have
  changed since the return was filed, this year's return starts from figures the books no
  longer show.
- **Where the beginning balances come from.** Intuit's ProSeries help page on an
  out-of-balance Schedule L: "Beginning balances are found on the previous year's tax
  return as ending balances in Schedule L, column (d)."
  ([Intuit](https://accountants.intuit.com/support/en-us/help-article/financial-reports/schedule-l-balance-sheet-balance-form-1065-1120s/L7wtgo31D_US_en_US))
- **It happens.** A preparer, January 2020, Intuit Accountants Community: "I am unable to
  reconcile Dec 2019 bank statements so I can prepare the taxes.. I have tried everything.
  The owner deleted several transactions. they are correct now, however the beginning
  balance is different."
  ([thread](https://accountants.intuit.com/community/practice-advice-17/quickbook-online-beg-balance-difference-5671))
- **The method practitioners give.** Reply to "Why does my ending balance sheet not match
  up", August 2020: "1) Something is entered incorrectly. 2) Something isn't entered.
  3) Beginning balances are incorrect. Tie out ALL numbers the the trial balance, and
  you'll find the error."
  ([thread](https://accountants.intuit.com/community/proconnect-product-discussions-6/why-does-my-ending-balance-sheet-not-match-up-94933))
- **Why it matters which accounts moved.** On a prior-year change, August 2024: "If there
  isn't any change to the 2022 taxable income, there is no need to amend the return. Just
  adjust the beginning retained earnings on the next open year to file by overriding the
  prior retained earnings balance."
  ([thread](https://accountants.intuit.com/community/proseries-tax-discussions/discussion/amending-return-to-update-schedule-l-balance-sheet-beginning/00/305002))
  So the first question is always: did last year's income change, or only the balance sheet?

### What she already has, and what it leaves
- **QuickBooks Online:** a closing date, an audit log, and an "Exceptions to Closing Date"
  report that lists transactions changed after the books were closed. They list
  transactions. They do not compare the books with her final figures, they see nothing if
  no closing date was set, and they cannot see adjusting entries she made only in her
  workpapers or her tax software.
- **QuickBooks Desktop Accountant:** Client Data Review has a "Troubleshoot Prior Account
  Balances" tool that compares the client's balances with the balances from the
  accountant's last review. It works only in Desktop, and only if she used Client Data
  Review last year.
- **Xero:** lock dates and a history on each transaction. No comparison with her figures.
- **Tax software:** carries last year's Schedule L forward. It cannot see the client's
  books.

### Candidates considered

| Candidate | Who, how often | By hand | Error cost | Why software has not solved it | Verdict |
|---|---|---|---|---|---|
| **Did last year change?** Last year's final trial balance against the client's books today, same date | Every business client with a balance sheet on the return, once a year, before the new year's work starts | 15 min if nothing changed; 45 to 90 min to find what changed (estimate) | This year's return starts from balances the books no longer show; a deleted or backdated transaction in a filed year goes unnoticed; adjusting entries never posted are made again or lost | The ledger lists changed transactions but does not compare them with her final figures; her adjusting entries often live outside the ledger | **Chosen** |
| Month-over-month changes turned into client questions | Monthly and quarterly bookkeeping clients | 20 to 40 min per client per month (estimate) | Errors found at year end instead of in the month | Small-firm review tools already do this inside QuickBooks Online and Xero (for example Xenett, listed at $7.50 per client per month, and Keeper) | Later, if a gap is found |
| Stale reconciling items (old uncleared checks and deposits) | Every client with a bank reconciliation, monthly | 10 to 20 min (estimate) | Cash overstated or understated; unclaimed property | The ledger's reconciliation report already lists uncleared items with their dates | Later |

### What a top practitioner would insist on
- **Start from her final figures,** including her own adjusting entries, not from the books
  as they stood before she adjusted them.
- **Same date, same basis.** A cash-basis trial balance compared with an accrual-basis one,
  or December 2025 with December 2026, proves nothing. Say so and stop.
- **Separate the income question from the balance sheet question.** A change to last year's
  income or expenses may mean an amended return. A change that only moves money between
  balance sheet accounts does not. A change to retained earnings means a year before last
  changed.
- **Recognize her own entries.** If an account differs by exactly her adjustment, the client
  never posted it. That is a request to the client, not a mystery.
- **Do not cry wolf over rounding** when last year's figures were in whole dollars.
- **Recognize renamed and merged accounts** instead of reporting one account as deleted and
  another as new.
- **Hand back the entry,** but leave the decision to her: post it, or reverse the client's
  change in last year, or amend.

### Value test
1. **She already has:** QuickBooks or Xero, the audit log, a closing date, and last year's
   final trial balance in her workpapers.
2. **Left by hand:** lining up two trial balances account by account, working out what each
   difference means, and tracing it.
3. **Input she has:** last year's final trial balance (Excel or CSV) and a trial balance
   exported today for the same date. Two copies of one kind of report.
4. **Output where she works:** a workpaper for the file, a list of what to ask the client,
   and the journal entry to post.
5. **If everything is set up perfectly** (a closing date with a password, and her
   adjusting entries posted in the books), the books will agree. She still has to prove it
   before she relies on the opening balances; the tool does that in a minute. It earns its
   keep with new clients, clients who know the password, Xero clients, and adjusting
   entries that lived only in her workpapers.
