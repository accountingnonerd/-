# Results: Order-to-Cash 02, "What's really collectible?"

Version 1.0.0, run 2026-11-16 with `node run-tests.js` against `agent/whats-really-collectible.html`.

**17 of 17 cases passed; 2,066 of 2,066 individual checks.**

The acceptance test has 17 cases: A/R aging detail reports as of October 31, 2026, in the layouts of
QuickBooks Online, QuickBooks Desktop and Xero, from a model of open items for invented businesses
(3 clean, 5 with a planted problem, 9 ugly). Each case checks the status and every warning, the
aging before and after the clean-up, every credit applied, every customer in credit, duplicates,
small and old balances, the write-off, the ranked worklist with each customer's next step, and, where
typed in, the tie to the balance sheet and the allowance. The rules are in the docstring of
`make_cases.py`; the key is worked out from the model, never by reading the files back.

## Case by case

| Case | What it is | Type | Expected verdict | Checks passed | Run time (ms) | Result |
|---|---|---|---|---|---|---|
| 01 | QuickBooks Online, a clean book | clean | COMPUTED | 154/154 | 135 | PASS |
| 02 | QuickBooks Online, A/R from the balance sheet typed in: it ties | clean | TIES | 155/155 | 171 | PASS |
| 03 | Planted: unapplied payments, a credit memo, a customer who paid twice | planted | COMPUTED | 160/160 | 136 | PASS |
| 04 | Planted: the same invoice entered twice; a twice-weekly flat bill that is not a duplicate | planted | COMPUTED | 163/163 | 103 | PASS |
| 05 | Planted: the balance sheet's A/R is $3,150.00 more than the aging | planted | DIFFERS | 156/156 | 167 | PASS |
| 06 | Xero: a credit note and an overpayment | ugly | COMPUTED | 111/111 | 94 | PASS |
| 07 | QuickBooks Desktop: no as-of date, days from the Aging column; a credit memo refunded by check | ugly | COMPUTED | 152/152 | 108 | PASS |
| 08 | Invoices over a year old, small leftover balances; allowance rates and the allowance on the books | ugly | COMPUTED | 166/166 | 222 | PASS |
| 09 | QuickBooks Online as CSV: dollar signs, parentheses, jobs under customers | ugly | COMPUTED | 95/95 | 84 | PASS |
| 10 | The wrong report: A/P aging detail | ugly | NOT_RECOGNIZED | 4/4 | 59 | PASS |
| 11 | The summary report, with no invoices in it | ugly | NOT_RECOGNIZED | 4/4 | 60 | PASS |
| 12 | Planted: the report's total line does not agree with its lines | planted | COMPUTED | 167/167 | 97 | PASS |
| 13 | Planted: three lines pasted in twice | planted | COMPUTED | 160/160 | 99 | PASS |
| 14 | Allowance rates typed in; a journal entry in A/R; one customer holds a large share | ugly | COMPUTED | 89/89 | 185 | PASS |
| 15 | Two real payments of $500 on the same day, no number: identical lines, both kept | ugly | COMPUTED | 112/112 | 94 | PASS |
| 16 | No as-of date in the file: the page asks for it, then reviews | ugly | COMPUTED | 102/102 | 151 | PASS |
| 17 | Planted: one check for two invoices; a payment posted to the wrong customer | planted | COMPUTED | 116/116 | 108 | PASS |

## What went wrong along the way

### First run: 14 of 14, which proved little
The first build passed every case at once. That says the tool and the answer key followed the same
rules, both written by us, not that the rules were right. The reviews below were the real test.

### The accounting review
A separate AI session, told to review the tool as a skeptical CPA who does monthly closes and
compiles statements, read the source and ran it on its own cases. Its sixteen findings; those that
changed answers:
- **A credit that exactly paid off a customer disappeared.** Invoices of $500 and $300 with one
  unapplied $800 check produced no clean-up item and "Nothing to check". Credits are now applied
  first, and only what is left over is a credit balance (case 17).
- **Identical lines were deleted as "pasted twice".** Two real $500 payments on the same day, with no
  number, look exactly alike; one was dropped and the customer would have been chased for money it
  had paid. Lines are now removed only when the report's own total proves they were pasted in (cases
  13 and 15).
- **With no as-of date, everything was "current"** and the page said no customer was overdue. It now
  stops and asks for the date (case 16).
- **The worklist chased what the page said not to chase:** small balances proposed for write-off, the
  copy of a suspected duplicate, journal entries. They are now left out of the reminders.
- **Small balances were proposed for write-off on new invoices.** Now only part-paid invoices more than
  60 days past due, with a note that short payments are usually discounts, card fees or sales tax.
- **Jobs were merged into their customer** for the clean-up, so a payment on one job was applied to
  another job's invoice, and duplicates were tested across properties. The clean-up now works job by
  job; a job's credit that may belong to another job is flagged for confirmation.
- **A credit balance matching another customer's open invoice** is now flagged as a payment probably
  posted to the wrong customer (case 17).
- **The write-off wording was wrong under the allowance method,** the ASU 2025-05 sentence was imprecise
  (the expedient is open to all entities; the after-year-end collections election is the private-
  company one), and credit balances need reclassifying to a liability, never writing off to income.
  The page now asks for the allowance on the books and proposes the adjusting entry (case 08).
- Also: refund checks in QuickBooks Desktop were read as invoices (case 07); recurring billing raised
  duplicate warnings (case 04); unknown transaction types now stop; cash-basis reports are flagged; the
  page says "you propose; the client decides", since collections and write-offs are the client's
  decisions.

### The cold-user check
A separate AI session played a 60-year-old partner, from screenshots only. It knew what to do in about
15 seconds. What changed:
- **the letters contradicted themselves**: a "final notice" that said "more than 90 days past due" listed
  invoices 6 and 59 days past due. Letters now name the age of the oldest invoice, list only invoices
  that are chased, and leave placeholders for the contact and payment details;
- the total after the clean-up was higher than the report's, with no explanation; the page now shows
  the reconciliation and names the customer who paid twice;
- letters can be held for a customer in dispute, in bankruptcy or on a plan, and are held entirely when
  the aging does not agree with the balance sheet;
- a place to type the as-of date and the allowance already on the books; dated sign-off lines; tables
  that scroll on a phone.

## Broken on purpose: do the tests notice?

Twenty copies, each with one rule removed or reversed, run against the final build. **All 20 were
caught.** One ("weekly billing flagged as duplicates") survived the first time because the test's weekly
bills were exactly 7 days apart and never reached the rule; the bills are now twice a week.

| Copy | What was broken | Cases that failed |
|---|---|---|
| m01 | Credits never matched exactly | 4 |
| m02 | Credits not applied to the oldest invoices | 3 |
| m03 | A credit left over not reported | 3 |
| m04 | A payment posted to the wrong customer not spotted | 1 |
| m05 | Duplicate invoices not flagged | 1 |
| m06 | Recurring billing flagged as duplicates | 1 |
| m07 | Small balances flagged when new | 1 |
| m08 | Days counted from the invoice date, not the due date | 14 |
| m09 | Identical lines always dropped | 1 |
| m10 | Pasted copies never removed | 1 |
| m11 | The report's total not checked | 1 |
| m12 | The balance sheet not compared | 1 |
| m13 | Worklist ranked by overdue only | 15 |
| m14 | Write-offs still chased | 1 |
| m15 | Allowance includes write-offs | 1 |
| m16 | Allowance adjustment ignores write-offs | 1 |
| m17 | Jobs merged into the customer for the clean-up | 1 |
| m18 | No as-of date treated as current | 1 |
| m19 | Desktop refund checks not recognized | 1 |
| m20 | Journal entries not flagged | 1 |

## Rebuild from the prompt

A fresh AI session was given only `REBUILD-PROMPT.md` (and allowed to read `run-tests.js` to see
how the test drives the page). It was not allowed to open the original build, the case generator or
the answer key. Its build, in `rebuild-check/rebuild-1/`, passed on the **first run: 17 of 17 cases,
2,066 of 2,066 checks**. No fixes were needed.

It listed 14 places where the prompt was silent and it had to choose (in
`rebuild-check/rebuild-1/NOTES.md`). None changed an answer in the tests. Where its choice could
differ from the original's in a future case, the prompt now says what the original does: the
recurring-billing exception covers both duplicate tests, the total line is read from column A, the
file's as-of date wins over a typed one, the order of the two identical-line warnings, how the
verdict counts items to post, and when the allowance is worked out.
