# Rebuild prompt

Paste everything between the two lines into a fresh AI coding session. The result is "the
same agent" if it passes the same acceptance test: `node tests/run-tests.js path/to/your-build.html`.

---

````text
Build a single self-contained HTML file called `did-last-year-change.html`. It is a tool for a US accountant who prepares business returns from clients' books. She is expert in accounting, impatient with software, and works on a desktop. She gives it two trial balances for the same date (normally December 31 of last year): (1) last year's final, adjusted trial balance from her workpapers, the one the return was prepared from; (2) a trial balance for the same date exported from the client's QuickBooks or Xero today. It tells her whether last year's books still agree with her final figures, what changed, what it means for last year's return, and drafts a correcting entry. Everything runs in the browser; nothing is uploaded. All arithmetic is in whole cents (integers), debit positive, credit negative, in code.

## Screen
- Load SheetJS 0.18.5 with `<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>`.
- Start screen: title "Did last year change?", one sentence saying what it does, then two large drop boxes side by side (stacked on a phone), numbered 1 and 2. Each is a `<label>` wrapping a hidden `<input type="file" accept=".csv,.txt,.xlsx,.xls,.xlsm">`:
  - box 1, input `id="final"`: "Last year's final trial balance". Under it: "Your adjusted trial balance, after your adjusting entries: the one the return was prepared from. Excel or CSV. Drop it here, or click to choose it."
  - box 2, input `id="today"`: "The same date, from the client's books today". Under it: "A trial balance for the last day of last year, exported today. Excel or CSV."
  Each box also accepts drag and drop, and shows the file name with a tick once given. When both files are present, compare at once (no button). Below the boxes: how to export the trial balance from QuickBooks Online, QuickBooks Desktop and Xero; what it adds (the software lists changed transactions, this compares the books with her own final figures, including adjustments that exist only in her workpapers); a link "See it work on a made-up sample"; "Where your data goes: nowhere"; and "You stay in charge: whether to post the entry, reverse the client's change or amend last year's return is your decision." Footer: "Version 1.0.0."
- A `.pdf` file, or any other extension than xlsx/xlsm/xls/csv/txt, is refused at once with a plain message under the boxes ("... is a PDF. I can only read Excel or CSV files ...").
- Read a file with `XLSX.read`: CSV/TXT as text with `{type:"string", raw:true}` (so every cell stays a string), anything else as `{type:"array"}`. Take the sheet with the most rows, via `sheet_to_json(ws, {header:1, raw:true, defval:null, blankrows:true})`. If both files have exactly the same bytes, that is the SAME_FILE case below.
- After comparing, replace the start screen with the workpaper. Above it: one main button "Print or save as PDF" (`window.print()`) and a small "Start over with other files" link. Large type (18px or more), plain words, high contrast, light background, print styles.
- Set `window.__report` to the report object (below) after every comparison. Never leave the page blank: if anything throws, show the error under the boxes and set `window.__report = {status:"ERROR", message}`.

## Reading a trial balance: readTB(rows)
### Amounts
A cell is an amount if it is a number (cents = round(n*100)) or text like `1,234.56`, `$1,234.56`, `(1,234.56)`, `-1,234.56`, `1,234.56-`, `1,234.56 CR` (negative), `1,234.56 DR`. Parentheses, a leading or trailing minus, and CR make it negative; `$`, commas and spaces are ignored. Blank, `-`, en dash or em dash is "no amount". Any other text in an amount column is "unreadable".

### Column headings
Classify each heading cell (lower-cased, trimmed) in this order:
1. `ytd debit` or `debit - year to date` → ytdDr; `ytd credit` or `credit - year to date` → ytdCr.
2. exactly `debit`, `debits`, `dr` → dr; exactly `credit`, `credits`, `cr` → cr.
3. Let side = Dr if the heading ends in `debit(s)` or `dr`/`dr.`, Cr if it ends in `credit(s)` or `cr`/`cr.`, else none.
4. contains `unadjusted`, `per books`, `before adj`, or starts with `books` or `book balance` → unadj (or unadjDr / unadjCr with a side).
5. starts with `aje`, `ajes`, `adj`, `adj.`, `adjustment(s)`, `adjusting entries` (optionally after `net `) → aje (or ajeDr / ajeCr).
6. contains `final`, or starts with `adjusted`, `per return`, `balance`, `ending balance`, or is `amount` → with a side, dr or cr; otherwise final.
7. `acct`, `acct.`, `#`, `no`, `no.`, `code`, or `account`/`acct` followed by `#`, `no`, `num`, `number` or `code` → num.
8. `account`, `account name`, `description`, `name`, `account description` → name.
The heading row is the first of the first 40 rows that has no numeric cell, has at least two classified cells, and has (dr and cr) or ytdDr or final. Remember the first column of each kind; then, if there is no ytdDr and no final, use the LAST dr and the LAST cr column in the row (a workpaper's final pair comes last).
- Mode: "ytd" if ytdDr exists (Xero: its Debit and Credit columns are the month's movement and must be ignored), else "signed" if final exists, else "drcr".
- If no heading row is found: if the text of the first 12 rows matches `balance sheet|statement of financial position|profit (and|&) loss|income statement|statement of operations|general ledger|transaction (detail|list)|journal|aged (receivables|payables)|cash flows?`, it is "not a trial balance: this is a <that> report"; otherwise "I could not find Debit and Credit columns, or a column of final balances". If a heading row is found but the title lines above it match that pattern and do not contain "trial balance", it is also not a trial balance.

### Rows below the heading row
For each row, until the grand total:
- The label is the name column's text if there is one; otherwise the first non-empty, non-numeric cell left of the first amount column (skipping the number column). The number is the num column's text.
- The amounts that count are ytdDr/ytdCr, or dr/cr, or final, by mode.
- Blank row (no label, number or amount): skip.
- Grand total: label `total`, `totals` or `grand total` (any case), or a row with amounts and no label or number after at least one account. Record its amounts and stop reading accounts; every later row is footer text.
- A label starting with `total` followed by more words is a section subtotal: skip.
- A row with a label and no amount is a heading: skip it, and if the label (lower-cased) is one of revenue, income, trading income, other income, direct costs, cost of sales, cost of goods sold, expenses, expense, operating expenses, other expenses, other expense (income statement) or assets, current assets, fixed assets, non-current assets, bank, inventory, liabilities, current liabilities, non-current liabilities, long term liabilities, equity (balance sheet), it starts a section that applies to the following accounts. Remember the section's name too.
- A row whose counting amounts include unreadable text is recorded as unread (row number and label) and left out.
- Otherwise it is an account: cents = final (signed), or debit minus credit. If the file has unadj or unadjDr/unadjCr columns, keep the account's unadjusted amount; if it has aje or ajeDr/ajeCr columns, keep its adjustment (ajeDr minus ajeCr). Keep the row number (1-based).
### Account labels
- `Sales (200)`: a trailing parenthesis holding up to 10 letters/digits/dots/hyphens, at least one digit, is the code; the rest is the name.
- Split the name on `:` (sub-accounts). Each part may start with a number followed by a middle dot `·`, bullet, hyphen, en dash or space (`10100 · Checking`, `1000 Checking`); strip it. The account number is the number column, else the code, else the last part's number, else the first part's number. The name is the stripped parts joined with `:`.
- Normalized name: lower case, `&` → ` and `, remove `(a/r)` and `(a/p)`, every run of characters other than a-z, 0-9 and `:` → one space, no spaces around `:`, trimmed. The leaf is the part after the last `:`.
### Date, basis, company
- Title lines are the rows above the heading row (each row's non-empty cells joined by spaces). The as-of date is found in: first, a title line containing `as of` or `as at`; then any single cell above the heading row that does not contain a time like `9:41`; then the heading cells. Never in the footer below the total (QuickBooks puts its export date and time there).
- Date formats: `December 31, 2025`, `Dec 31, 25`, `Dec. 31 2025`, `31 December 2025`, `12/31/2025`, `12/31/25`, `2025-12-31`. Two-digit years are 20xx.
- Basis: `cash basis` or `accrual basis` anywhere in the title lines or footer.
- Company: the first title line that does not contain `trial balance`, `as of`, `as at`, `basis` or `workpaper`, and contains no date.
### Checks on the file itself
- sum = the sum of all accounts' cents (0 when it balances).
- whole = at most 10% of the accounts have cents (the workpaper is in whole dollars).
- The total line ties if: signed mode, its final amount equals sum; otherwise its debit equals the sum of the debit column as read, and its credit the sum of the credit column.
- hasAje = the file has aje, ajeDr or ajeCr columns.

## Which accounts are which
For each file:
1. Retained earnings: name matches `retained earnings|accumulated (deficit|earnings)|earnings retained` → type RE (strength 3).
2. An account under a section heading takes that section's type, BS or PL (strength 3).
3. Account numbers follow the usual plan if: at least 80% of accounts have a number starting with a digit; the retained earnings account (if it has a number) starts with 3; some number starts with 1, 2 or 3; and the file has no sections. Then a number starting with 1, 2 or 3 is BS, any other digit PL (strength 2).
4. File order: find the last retained earnings row. Accounts before it are BS. After it, accounts stay BS while their name matches `equity|capital|draw|drawings|distribution|dividend|investment|contribution|introduced|member|partner|owner|shareholder|stockholder|stock|shares|treasury|paid-in|paid in|surplus|aaa|accumulated adjustments` and not `income|revenue|sales|fees earned`; from the first one that does not, everything is PL (strength 1). Only accounts without a type yet are set.
5. Otherwise guess from the name (strength 0): BS if it matches `accumulated (depreciation|amortization)|payable|prepaid|deposit|receivable|accrued|loans?|notes?|due (to|from)|inventory|allowance|equipment|vehicles?|furniture|building|land|cash|checking|savings|bank|undeposited|credit card|liabilit|petty` or the owner pattern below; else PL if it matches `income|revenue|sales|expense|cost of|fees|wages|salar|compensation|labor|guaranteed|rent|utilities|insurance|depreciation|interest|taxes|licenses|advertising|supplies|repairs|meals|travel|car|truck|fuel|dues|postage|telephone|charges|commission`; else BS.
6. Owner account: a BS account that is numbered 3xxx under the usual plan, or sits in a section named "equity", or whose name matches `distribution|draws?|drawings|dividend|capital (not followed by lease, improvement, asset, expenditure)|contribution|funds introduced|investment (not followed by income)|paid-in|paid in|stock|shares|shareholder|stockholder|partner|member|owner|equity|aaa|accumulated adjustments` (whole words where sensible) and not "accumulated depreciation".

## Comparing: the order matters
Status is one of AGREES, CHANGED, NOT_COMPARABLE. Each exception has `code`, `level` (stop, care or info) and a plain-English `message`. When a step says "stop", set status NOT_COMPARABLE, list no accounts, draft no entry, and return.
1. Same bytes in both boxes: SAME_FILE (stop) → stop.
2. Swap: if the box-2 file hasAje and the box-1 file does not, swap them and add SWAPPED (info), naming both files.
3. Either file is not a trial balance: NOT_A_TB (stop) for each, saying which box and what report it is → stop.
4. Both dates known and different: DATE_MISMATCH (stop). Both bases known and different: BASIS_MISMATCH (stop). If neither of those, and at least one basis is unknown, and the final has a nonzero account whose name matches `receivable|payable` but not `payroll|tax|wage|accrued|loan|note|shareholder|officer|interest`, while the client's file has none: BASIS_SUSPECTED (stop; "that is what a cash-basis report looks like"). Any of these → stop.
5. Company names both known and sharing no word of 4+ letters (ignoring company, corporation, incorporated, limited): COMPANY_DIFFERS (care).
6. asOf = the final's date, else the client file's date (ISO `YYYY-MM-DD`, or null). For each file: no date → DATE_UNKNOWN (care); out of balance by $5.00 or less and whole → ROUNDING_IMBALANCE (info); otherwise out of balance → OUT_OF_BALANCE (stop level, but keep comparing); total line does not tie → TOTAL_MISMATCH (stop level, keep comparing); unread rows → UNREAD_ROWS (stop level, keep comparing).
7. Classify both files. Within a file, accounts with the same number and normalized name are added together (DUPLICATE_ACCOUNT, care).
8. Post-closing: if one file has no nonzero PL account and the other has some, the first is post-closing. Close the other file: add all its PL accounts into its RE account (create one named "Retained Earnings" if it has none) and drop them. If the post-closing file has no nonzero account matching `distribution|draws?|drawings|dividend` and the other file has, close those into RE too. Add POST_CLOSING (info).
9. Match accounts, each pass only taking one-to-one matches (exactly one candidate on each side): (a) same account number on both sides; (b) same normalized full name; (c) same leaf. A pair matched by number whose normalized names differ is RENAMED (info). Then, among the accounts still unmatched, an account on each side with exactly the same nonzero balance, unique on both sides, is a guessed rename: pair them and add RENAMED_GUESS (care).
10. If the pairs matched in (a)-(c) are fewer than half of the larger file's account count: WRONG_CLIENT (stop) → stop.
11. For every pair, and every unmatched account (the other side counts as 0): d = today − final. Type: the stronger classification of the two sides (the final's on a tie). Owner if either side is an owner account. Status:
    - d = 0: "same" (or "renamed" / "renamed?" for renamed pairs);
    - else, if the final has an adjustment a ≠ 0 and |d + a| ≤ 50 cents when the final is whole (0 otherwise): "aje" (her adjustment was never posted);
    - else, if the final is whole and the client's file is not, and |d| ≤ 50 cents, or the account is RE and |d| ≤ $5.00: "rounding";
    - else "new" (only in today's file), "missing" (only in the final) or "changed".
12. Merged: for each "missing" account g with a nonzero final balance, look for exactly one "changed" account m with m.diff = g.final, the same type, neither an owner account, m.final either 0 or the same sign as g.final, and the two names sharing a word of 4+ letters other than expense(s), account(s), other, general, misc, miscellaneous, cost(s), income. If found, both become "merged?" and MERGED_GUESS (care) says profit is unchanged but last year's books no longer show the two amounts separately, and the return's lines may no longer tie.
13. Real differences are statuses changed, new, missing and aje. Profit: NI = −(sum of PL balances), for final and today; netIncome = {final, today, change: today − final, changeApartFromRounding}. Post-closing: netIncome is null. Retained earnings (credit positive) = −(sum of RE balances); retainedEarnings.change = today − final (null when post-closing).
14. Exceptions from the real differences (leave "aje" ones out of the first four):
    - CHANGED_PL (stop) for PL accounts: list them; the profit effect is −(sum of their diffs), stated as higher or lower ("If the change is right, last year's return may need amending"), or "the same in total, but amounts moved between lines of the return". When exactly one BS account (not an owner account) has diff = −(a PL account's diff), name the likely cause: an income account against an asset lower = "a deposit or sale in last year was deleted or voided"; an expense against a liability higher = "a bill was added and dated last year"; an expense lower against an asset higher = "a payment or check in last year was voided or deleted"; and so on.
    - CHANGED_BS (stop) for BS accounts that are not owner accounts.
    - OWNER_CHANGED (stop) for owner accounts: K-1s, Schedule M-2 and basis change even though profit does not; correct them in last year's books.
    - PRIOR_YEARS_CHANGED (stop) for RE (RETAINED_EARNINGS_CHANGED when post-closing), with direction.
    - AJE_NOT_POSTED (care), listing each account and its adjustment: the client posts them dated the balance date, or she uses the correcting entry, one or the other, never both; tax-only adjustments are left out.
    - ROUNDING (info) if any account's status is rounding.
    - TYPE_GUESS (care) for each real, merged or renamed account whose type was guessed from its name.
    Add a sentence about payroll, sales-tax and 1099 filings when a changed PL or BS account's name matches `wage|salar|payroll|sales tax|contract labor|subcontract|officer`.
15. The correcting entry, dated the day after asOf (null date if asOf is unknown). Withhold it (entry null, with the reason shown) if any OUT_OF_BALANCE was raised, any owner account changed, there is no RE account, or a real difference's type was guessed from its name. Otherwise, for every real difference on a BS account: amount = the adjustment itself for "aje", else −d (back to the final). The other side, −(sum of those), goes to the RE account. No BS differences: no entry. Lines `{account, debit, credit}` in dollars (one of them 0), plus totalDebit and totalCredit. `account` is the account's name exactly as stored after label parsing, without its number (`Checking`, not `1000 Checking`); the other side uses the RE account's name.
16. Questions for the client: the changed balances with "higher"/"lower" (no parentheses) and "What was added, deleted or changed, and why?"; a request to post her adjusting entries dated the balance date; "Did you merge ...?".
17. Status: CHANGED if there is any real difference or any merge; otherwise AGREES.

"Higher"/"lower" for an account: compare the change with the account's normal side (the sign of its final balance, or today's if the final is zero); RE is always credit-normal.

## The workpaper (in this order)
- Heading: "Did last year change?", the company, the balance date, both file names; Prepared by / Date / Reviewed by / Date lines (not when NOT_COMPARABLE).
- `<div id="verdict">`: NOT_COMPARABLE → "I cannot compare these two files."; AGREES → "Last year's books still agree with your final trial balance." (plus what was allowed for: rounding, a renamed account, post-closing); CHANGED → "Last year's books have changed since your final trial balance." (or "Last year's books do not have your adjusting entries." when the only real differences are unposted adjustments, or "Last year's books have changed: accounts were merged." when there are no real differences), with how many accounts differ and the profit change apart from rounding.
- `<div id="stop-banner">`: visible, and listing the messages, only when there is an exception with code OUT_OF_BALANCE, TOTAL_MISMATCH, UNREAD_ROWS, NOT_A_TB, DATE_MISMATCH, BASIS_MISMATCH, BASIS_SUSPECTED, SAME_FILE or WRONG_CLIENT; otherwise hidden. When NOT_COMPARABLE, show nothing after it.
- "Check these first": the other exceptions, stop first, then care, then info.
- "What changed": every account with status changed, new, missing, aje, merged? or renamed?: final and today balances as `1,234.56 Dr`/`Cr`, the difference without a sign, and what it means in words.
- Last year's profit and retained earnings, final against today, and the check that the differences on all accounts add to zero.
- "Correcting entry, <date>": above the table, the conditions that apply: for her adjustments, one or the other, never both, and reverse accruals as usual; for the client's changes, undo or re-date the change in last year first, post only if they were mistakes, the client will not undo them, and the transaction was not entered again this year; if a change was right, consider amending, or keep this year's beginning balance sheet as filed and show a prior-period adjustment on Schedule M-2.
- "To ask the client", then a note to set a closing date with a password or a Xero lock date.
- "Every account compared" (collapsed): number, name, type and how it was decided, both balances with file row numbers, difference, result.
- "What I read from each file": layout, date and where it came from, basis, accounts read, whether debits equal credits, whether the total line agrees.
- Footer: where the data went (nowhere), arithmetic in whole cents, the accountant remains responsible.

## The report object (window.__report), amounts in dollars
```
{ version:"1.0.0", status, asOf:"YYYY-MM-DD"|null,
  files:{ final:{name, rows (accounts read), asOf, basis, layout, company, balances, total, totalTies, wholeDollars}, today:{...} },
  exceptions:[{code, level, message, ...}],
  accounts:[{name, finalName, todayName, number, type:"BS"|"PL"|"RE", typeHow, final, today, diff, status, finalRow, todayRow, aje}],   // names without numbers; name = today's name, else the final's
  netIncome:{final, today, change, changeApartFromRounding}|null,
  retainedEarnings:{final, today, change}|null,
  entry:{date, lines:[{account, debit, credit}], totalDebit, totalCredit}|null,
  questions:[...], controls:{accountsCompared, differences, rounding, roundingAccounts, diffTotal, diffsTie} }
```
`rows` is the number of accounts read from that file before any merging or closing.

## A made-up sample
Behind "See it work on a made-up sample", two small built-in trial balances: a bakery's final workpaper (with Per books, Adjustments and Final columns; a depreciation adjustment of $6,000) and a QuickBooks export for the same date in which a $4,150 deposit was deleted and the depreciation entry was never posted.
````
