# Rebuild prompt

Paste everything between the two lines into a fresh AI coding session. The result is "the
same agent" if it passes the same acceptance test: `node tests/run-tests.js path/to/your-build.html`.

---

````text
Build a single self-contained HTML file called `whats-really-collectible.html`. It is a tool for a US accountant who does monthly closes and year-end work for small businesses. She is expert in accounting, impatient with software, and works on a desktop. She gives it the client's A/R aging detail report exported to Excel or CSV from QuickBooks Online, QuickBooks Desktop or Xero. It gives back a receivables review: what to clean up in the ledger first (unapplied payments and credits, customers in credit, invoices entered twice, payments posted to the wrong customer), who to chase first with a draft letter each, and the allowance and write-offs at the close. Everything runs in the browser; nothing is uploaded. All arithmetic is in whole cents (integers), in code.

## Screen
- Load SheetJS 0.18.5 with `<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>`.
- Start screen (`<section id="start">`): title "What's really collectible?", one sentence saying what it does, then:
  - an optional text input `id="ar-start"`: "Accounts receivable on the balance sheet, same date (optional)";
  - one large drop box: a `<label>` wrapping a hidden `<input type="file" id="file" accept=".csv,.txt,.xlsx,.xls,.xlsm">`, "Drop the A/R aging detail here, or click here to choose it". It also accepts drag and drop anywhere on the page. Reading starts as soon as a file is chosen (no button);
  - `<div id="problem" hidden role="alert">` for refusals;
  - which report to export from each product (the detail, not the summary); what it adds; a button "See it work on a made-up sample" that runs a small built-in QuickBooks Online sample; "Where your data goes: nowhere"; "You propose; the client decides"; "Version 1.0.0."
- A `.pdf` file is refused at once in #problem ("... is a PDF. Export the A/R aging detail to Excel or CSV and drop that."); any extension other than xlsx/xlsm/xls/csv/txt is refused too.
- Read the file with `XLSX.read`: CSV/TXT as text with `{type:"string", raw:true}`, anything else as `{type:"array"}`. Take the sheet with the most rows via `sheet_to_json(ws, {header:1, raw:true, defval:null, blankrows:true})`.
- After reading, hide the start screen and show the workpaper (`<section id="report">`) with one main button "Print or save as PDF" (`window.print()`) and a small "Start over with another file" link. Large type (18px or more), plain words, high contrast, light background, print styles, works at phone width (wide tables scroll inside a box).
- Set `window.__report` to the report object (below, without any internal fields) every time the review is produced or redone. Clear it (`undefined`) when a new file starts loading. If the file is NOT_RECOGNIZED, set `window.__report` and show the message in #problem, staying on the start screen. If anything throws, show the error in #problem and set `window.__report = {status:"ERROR", message}`.

## Part 1. Reading the aging: readAging(rows)
### Amounts and dates
- An amount is a number (cents = round(n*100)) or text like `1,234.56`, `$1,234.56`, `(1,234.56)`, `-1,234.56`, `1,234.56-`. Parentheses or a minus make it negative; `$`, commas and spaces are ignored. Blank, `-`, en dash or em dash is no amount (0).
- Dates become day numbers (days since 1970-01-01, UTC). Accept: an Excel serial number between 20000 and 80000 (day = n - 25569); `YYYY-MM-DD`; `M/D/YYYY` or `M/D/YY` (US order); `15 Oct 2026` or `15-Oct-2026`; `October 31, 2026` or `Oct. 31 2026`.

### Finding the layout
Scan the first 20 rows; lower-case and trim each cell. The first row that matches decides:
1. it has `transaction type`, `num` and `open balance` → QuickBooks Online ("qbo");
2. it has `type`, `num`, `open balance` and (`name` or `customer`) → QuickBooks Desktop ("desktop");
3. it has `invoice number`, `due date` and `total` → Xero ("xero");
4. it has a cell exactly `current`, `1 - 30`, `1-30`, `31 - 60`, `older`, `91 and over` or `> 90`, and `total`, and neither `num` nor `invoice number` → a summary.
Title lines are the rows above the heading row (or the first 12 rows if none), each row's non-empty cells joined by spaces.
- If the title lines match `a/p aging|accounts payable|aged payables|payables` (any case), or the heading row has `vendor` or `supplier`: status NOT_RECOGNIZED with exception `NOT_RECOGNIZED` (stop): "This is an accounts payable aging: what the client owes. I need the accounts receivable aging ...".
- Else if it is a summary, or the titles say `aging summary` or `aged receivables summary` and no layout was found: status NOT_RECOGNIZED with exception `SUMMARY_ONLY` (stop): "This is the A/R aging summary ... I need the A/R aging detail ...".
- Else if no layout: status NOT_RECOGNIZED with exception `NOT_RECOGNIZED` (stop).

### Rows
Map each heading text to its first column. For each row below the heading row:
- Skip blank rows. Once the grand total has been read, every later row is footer text (keep it for the basis).
- First cell exactly `total` (any case): the grand total; its amount is in the `total` column (Xero) or `open balance` column (QuickBooks). A first cell starting with `total` followed by more words is a subtotal: skip it.
- The date is in `invoice date` (Xero) or `date` (QuickBooks). If it does not parse: in Xero, a row whose only non-empty cell is the first one is a contact heading (remember it as the current customer); otherwise, if the row has other content and a non-empty date cell, record it as unread (row number); otherwise it is a section heading such as "Current" or "1 - 30 days past due". Skip it either way.
- Xero item: customer = the current contact; num = `invoice number`; due = `due date`; open = amount = `total`. Type: if open < 0, "Payment" if `reference` contains `overpayment` or `prepayment`, else "Credit Memo"; if open >= 0, "Journal Entry" if `reference` contains `journal`, else "Invoice".
- QuickBooks item: customer = `customer` (QBO) or `name` (Desktop), falling back to the other; num = `num`; due = `due date`; open = `open balance`; amount = `amount` if that column exists, else open. Type from `transaction type` or `type`, lower-cased: contains `credit` → "Credit Memo"; else `payment` or `deposit` → "Payment"; else `journal` → "Journal Entry"; else `check` or `refund` → "Refund"; else `invoice`, `statement charge`, `charge` or `finance` → "Invoice"; anything else → record as unknown (row number and type) and leave the row out. If there is an `aging` column, keep its number (blank = 0).
- For every item: job = the customer text trimmed ("Customer:Job" is its own job); parent = the part before the first `:`, trimmed (the customer). If the due date is missing, use the date. Keep a signature: all the row's cells joined, plus the current Xero contact.
- As-of date: in the title lines, the first match of `as of` or `as at` followed by `October 31, 2026` / `Oct 31 2026`, or `31 October 2026`, or `10/31/2026`. Never the footer.
- Basis: `cash basis` or `accrual basis` anywhere in the title lines or the footer.
- Company: the first non-empty title line that does not match `aging|aged|as (of|at)|ageing|basis`.

## Part 2. The review: review(rows, fileName, {asOf, keep})
- If the file has no as-of date, no typed as-of date, and no Aging column: status `NEEDS_DATE`, exception `DATE_REQUIRED` (stop). Show (in the report section) a #verdict, a #stop-banner with the message, an input `id="asof"` and a button `id="set-asof"` "Review it". When she types a date and presses it, run the review again with that date.
- Identical lines: items with the same signature as an earlier item are extra copies. If the report has a total line and (sum of all items' open - sum of the extra copies' open) equals it exactly, remove the copies, set `duplicates_removed` = the number removed, and raise `DUPLICATE_ROWS` (stop). Otherwise keep them and raise `IDENTICAL_LINES` (care), listing them ("two real payments on the same day look like this").
- days past due = as-of day - due day; with no as-of date, the Aging column's value. Buckets: days <= 0 current; 1-30 d1_30; 31-60 d31_60; 61-90 d61_90; 91-180 d91_180; 181-365 d181_365; over 365 over365.
- total = sum of open of all items (after any removed copies). customers = number of distinct parents. buckets = sum of open by bucket of every item ("as reported, re-aged by due date").

### Clean-up, job by job (jobs sorted by name)
Each item has rem = open. Within a job: credits = items with open < 0, sorted by date then num; targets = items with open > 0 of type Invoice or Refund, sorted by date then num.
1. Exact matches: for each credit in order, the first target whose rem equals -credit.rem and is untouched (rem == open). Record `{customer: job, credit: num or type, creditType, creditDate, invoice: target num, invoiceDate, amount}` (amount in dollars); set both rem to 0.
2. Apply the rest: for each credit with rem still non-zero, apply it to the targets in order, oldest first, taking min(what is left of the credit, target rem). If anything was applied, record `{customer: job, credit: num or type, creditType, amount applied, invoices: [nums]}` in applyOldest. The credit's rem becomes minus what is left.
3. What is left of the job's credits (sum of -rem over its credits), if not zero, is a credit balance `{customer: job, amount}`: owed to the customer, never chased.
After all jobs: pos = items with rem > 0. For each credit balance (cents C, parent P):
- misposting: if exactly one item in pos has parent != P, type Invoice, rem == C and open == C, record `{customer: job, maybeFor: that item's job, invoice: its num}` in mispostings and set maybeFor on the credit balance (else null);
- paidTwice = the invoice number of the first exact match of the same job whose amount equals C, else null;
- otherJobs = true if any item in pos has parent P and a different job.
creditBalances = `[{customer, amount, paidTwice, otherJobs, maybeFor}]`.

### Duplicates, job by job
Invoices of the job with open > 0, sorted by date then num. For every pair (x earlier, y later): a duplicate if (x.num == y.num, or x.amount == y.amount and x.amount >= 100 cents and |y.date - x.date| < 7 days), unless the job has 3 or more such invoices with x's amount (recurring billing). Record `{customer: job, a: x.num, b: y.num, amount}`; y is a "later copy".

### Write-offs, worklist, concentration
- small = items in pos of type Invoice with rem < 1000 cents, open < amount (part-paid) and days > 60.
- old = items in pos of type Invoice with days > 365, not in small.
- write-off = small + old, except old invoices she unticked (opts.keep[num] true). writeOff = sum of their rem.
- chased = items in pos of type Invoice with days > 0, not in the write-off, not a later copy. (Journal entries and refunds are never chased.)
- worklist: per parent (sorted by name) with chased items: overdue = sum of rem; over60 = sum of rem of those with days > 60; oldestDays = max days; invoices = count; step by oldestDays: <= 30 "Friendly reminder"; <= 60 "Second request and a call"; <= 90 "Call about the account"; <= 180 "Past-due notice"; else "Final request". Sort by over60 descending, then overdue descending, then customer name.
- owed = sum of rem over pos; inCredit = sum of the credit balances. (total = owed - inCredit always.) bucketsClean = sum of rem over pos by bucket.
- concentration: each parent whose sum of rem over pos * 100 >= 20 * owed: `{customer, share: round(cents*1000/owed)/10}`.
- journalEntries = the number of items of type Journal Entry.

### Exceptions `{code, level, message}`, in this order, only when they apply
- `UNKNOWN_TYPE` stop: rows with a transaction type it does not know, left out.
- `UNREAD_ROWS` stop: rows whose date could not be read, left out.
- `TOTAL_MISMATCH` stop: the report's total line differs from the sum of its lines (after removed copies).
- `NO_TOTAL_LINE` info: there is no total line.
- `DATE_UNKNOWN` care: no as-of date in the file and none typed (the Aging column was used).
- `FUTURE_DATED` care: items dated after the as-of date.
- `CASH_BASIS` care: the report is cash basis; the allowance and the tie do not apply.
- `UNAPPLIED_CREDITS` care: any exact match or applyOldest entry.
- `CREDIT_BALANCES` care: any credit balance, naming paid-twice, possible misposting and other jobs.
- `DUPLICATE_INVOICES` care: any duplicate pair.
- `OVER_A_YEAR` care: any old invoice ("untick any to keep in the allowance instead").
- `SMALL_BALANCES` info: any small balance (usually a discount, card fee or sales tax).
- `JOURNAL_ENTRIES` care: journal entries in receivables, left out of the reminders.
- `CONCENTRATION` info: any concentrated customer.
Status `COMPUTED`.

### Typed A/R from the balance sheet: compareAR
If she typed A/R (on the start screen in #ar-start, or later in `input#ar` and `button#compare`, Enter also works): typedAR = typed, difference = typed - total. Zero → status `TIES`. Otherwise status `DIFFERS` and add `DIFFERS_FROM_BALANCE_SHEET` (stop) at the front of the exceptions; letters are held. Blank → back to COMPUTED.

### Allowance: rates by bucket
Inputs `input#rate-current`, `#rate-d1_30`, `#rate-d31_60`, `#rate-d61_90`, `#rate-d91_180`, `#rate-d181_365`, `#rate-over365` (percent; blank = 0), optional `input#existing-allowance` (dollars), and `button#apply-rates`. For each bucket: base = sum of rem of items in pos in that bucket, not in the write-off, not of type Refund; amount = round-half-up(base * rate / 100) cents. allowance = sum of the bucket amounts; allowanceByBucket = `{bucket: {base, rate, amount}}`. If existing allowance was typed: allowanceAdjustment = allowance - (existing - writeOff) (positive: Dr Bad debt expense / Cr Allowance; negative: a release).

Every time she types something and presses a button (or ticks a box), run the whole review again from the file with everything she has typed so far (as-of date, kept invoices, typed A/R, rates, existing allowance, held letters), re-render, and keep the scroll position and what she typed.

## The report object (window.__report), money in dollars as numbers
version "1.0.0", file, status, exceptions, layout (readable name), company, asOf ("YYYY-MM-DD" or null), basis, rows (number of items), total, reportTotal, customers, buckets {7 buckets}, bucketsClean, matches, applyOldest, creditBalances, mispostings, duplicates, small (sorted invoice numbers), old (sorted invoice numbers), writeOff, owed, inCredit, worklist [{customer, overdue, over60, oldestDays, step, invoices}], concentration, journalEntries, and when they apply duplicates_removed (a number), typedAR, difference, rates, allowance, allowanceByBucket, existingAllowance, allowanceAdjustment.

## The workpaper
- Heading "What's really collectible?", layout, as-of date, file name; fields Client (pre-filled with the company), Prepared by, Prepared on, Reviewed by, Reviewed on.
- `<div id="verdict">`: "[Company]: $X owed by N customers (and $Y owed to M customers in credit); $Z to chase." where N counts customers with something owed, M the customers in credit, Z the worklist total; then "K items to post in the ledger first, then run this again." or "Nothing to post in the ledger first." When DIFFERS: "The aging does not agree with the balance sheet: $D apart."
- `<div id="stop-banner">` listing every stop exception, each starting "Stop."; hidden (the `hidden` attribute) when there are none.
- The typed A/R line (#ar, #compare, "Ties exactly." or "Differs by $D."), and when there is no as-of date, #asof and #set-asof "Set the date".
- The aging table: "As reported, re-aged by due date" and "Owed after the clean-up", seven buckets and a total; under it "The aging total, $T, = owed by customers $O less owed to customers in credit $C", and that credit balances belong with the liabilities, not netted against receivables.
- "Check these first": the care and info exceptions, care first, labelled "Decide." and "For your file.".
- "1. Clean first": a table of exact matches ("likely; confirm with the remittance"), a table of credits applied to the oldest invoices ("if the remittance names other invoices, follow the remittance"), customers the client owes (misposting: move it and apply it; paid twice: refund or confirm; other jobs: confirm which; else a deposit or overpayment), with the note to reclassify credit balances to a liability (Dr Accounts receivable, Cr Customer credits payable) and never write them off to income (unclaimed property); the duplicate pairs (credit memo in the current period, not voiding in a closed period).
- "2. Who to chase": the worklist table with a "Hold letter" checkbox per customer (class `hold`; for disputes, bankruptcy (automatic stay), payment plans); then, unless DIFFERS, one collapsible draft letter per customer not held: "Dear [contact name], <customer>," an opening sentence by step naming the oldest invoice's days past due, each invoice (number, date, open amount, days past due), the total, "Payment details: [how to pay]. If you have already paid, thank you, and please send the payment details so we can apply it.", "Kind regards, [name], <company>, [phone or email]".
- "3. Allowance and write-offs": a sentence that the rates are her judgment from the client's history (the page does not guess them), and ASU 2025-05 (years beginning after December 15, 2025): any entity may assume current conditions continue for current receivables; a private company may also elect to consider collections after the balance sheet date and must disclose it. The rate inputs, existing allowance, button; the allowance table "Allowance for credit losses"; net realizable receivables = owed - writeOff - allowance; the entries; the proposed write-offs table (old invoices with a checkbox, class `wo`, ticked by default; small balances always), recorded as one credit memo per invoice with a non-taxable "Bad debt" item dated in the open period (not a journal entry to A/R); the sales tax note; and the tax note (deductible only if included in income and shown worthless; age alone is not proof; the allowance is not deductible).
- "What I read": layout, items, customers, total and the report's own total, basis.
- Footer: "Made by "What's Really Collectible?" version 1.0.0, on this computer. The file was read here and not sent anywhere. Arithmetic is done in whole cents. This is a workpaper for review: you propose; the client decides what to apply, write off and send."
````

---

## What a rebuild has to match

The acceptance test reads `window.__report` and the visibility of `#stop-banner` / `#problem`; the
element IDs above are the ones it types into and presses. Wording on the page may differ.
