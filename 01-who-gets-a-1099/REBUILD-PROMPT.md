Build a single self-contained HTML file called `who-gets-a-1099.html`. It is a tool for a US accountant who is expert in tax, impatient with software, and working on a desktop. She gives it one file, the list of everything a client paid during the year, and gets back a printable worksheet saying which vendors need a Form 1099, whose W-9 to check, and why. Everything runs in the browser. Nothing is uploaded. Do all arithmetic in whole cents, in code.

## Screen
- Start screen: the title "Who gets a 1099?", one sentence saying what it does, and one large drop area ("Drop the client's payments file here, or click to choose it") wrapping an `<input type="file">` for .csv and .xlsx. Under it, in a few short lines: which file to bring (all payments for the tax year, one line per check or charge), which rule applies ($2,000 for 2026 payments, $600 for 2025 and earlier), that the file never leaves the computer, and that the result is a worksheet she must review. No settings. The only other control is a small link that runs a built-in made-up sample.
- After a file is read, replace the start screen with the worksheet, one main button "Print or save as PDF" (`window.print()`), and a small "Start over" link. Add print styles: compact type, table headers repeated, a running page header with the file name and page numbers.
- Large type (18px or more), plain words, high contrast, light background. Stack table rows as cards on a phone.
- Read .csv with your own parser (quoted fields, commas inside quotes, a leading BOM, blank lines, CRLF). Read .xlsx with SheetJS from `https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js`, first sheet, raw cell values. Excel dates arrive as serial numbers (days since 1899-12-30): treat a number between 20000 and 80000 in the date column as a date.
- If the file cannot be used, stay on the start screen and show "I could not use that file." with the reason in plain words, directly under the drop area.

## Reading the file
All keyword matching below is on whole words, after lower-casing, deleting periods and apostrophes, and turning `&` into "and" and other punctuation into spaces.

1. Header row: the first of the top 40 rows with a date heading and an amount heading.
   - Date: date, transaction date, txn date, payment date, check date.
   - Amount: one column (amount, paid amount, total), or a debit and a credit column, or a payment/withdrawal column with an optional deposit column (payment minus deposit).
   - Payee: name, payee, vendor, vendor name, paid to, supplier. If none exists, use a column headed "description".
   - Optional: type (type, transaction type); number (num, no, number, check #, check no, check number, ref, reference); memo (memo, memo/description, description, notes); paying account (bank account, paid from, payment account); expense category (category, expense account).
   - A column headed "account" or "split" can be either. If more than half of its values on dated rows contain checking, savings, bank, cash, card, visa, mastercard, amex, discover or paypal, it is the paying account. Otherwise it is the expense category.
2. If there is no payee column, the file is grouped by vendor: a row with text in only one cell, no date and no amount is a vendor name for the lines under it.
3. A line is a row below the header with a readable date and a readable amount. Amounts may look like `1200`, `$1,200.00`, `(450.00)` (negative), `300.00-` (negative), `-550.00`. Dates may look like `1/5/26`, `01/19/2026`, `2026-02-14`, `Mar 3, 2026`. Two-digit years are 20xx. Keep each line's row number as it appears in the file, counting from 1 and counting title and blank rows. A line with a blank payee belongs to a vendor named exactly `(no name)`.
4. A row with a date but no readable amount is an unreadable line. It goes in no total. Remember which vendor it belonged to.
5. A row with no date whose first text is "Total", "TOTAL" or "Grand Total" is the file's own total. A row with no date whose first text starts with "Total " (such as "Total for Rivera Plumbing") is a vendor subtotal.
6. If there is a type column, the type decides what a line is:
   - Not a payment, never counted: the type is exactly bill, vendor credit, credit, purchase order, item receipt, journal entry, general journal or credit memo. Keep these lines aside.
   - Type contains "bill payment" or "bill pmt": a payment of the absolute value of the amount, whatever its sign.
   - Type contains refund, deposit or credit card credit: a refund, so minus the absolute value.
7. For all other lines, whichever sign most of them have is "a payment" and the opposite sign is a refund. With debit and credit columns, use debit minus credit as the written amount first. Payments are positive from here on.
8. Tax year: the year most payment lines fall in. Payment lines in another year are left out of every vendor and reported. If the tax year is after 2026, stop: this version only knows the rules through 2026 and must not guess.
9. Dollar limit: $2,000 for 2026 payments, $600 for 2025 and earlier. A vendor exactly at the limit counts.

## Vendors
- Vendor key: the matching form of the name, with these words dropped: llc, inc, incorporated, corp, corporation, co, company, ltd, pllc, pc, lp, llp, the, and. Names with the same key are one vendor. Its name is the most common spelling. Show every spelling that was combined.
- "Looks incorporated": the name contains inc, incorporated, corp, corporation or pc. LLC, LLP, PLLC, Ltd and Co say nothing about tax status.
- Payment method of each line:
  - network: the type, paying account or number contains paypal, venmo, stripe, square or cash app, or the memo contains paypal, venmo or cash app;
  - card: the type, paying account or number contains card, ccard, visa, mastercard, amex, american express, discover or pos;
  - bank: everything else (check, ACH, wire, Zelle, cash, unknown).
- For each vendor: R = net bank dollars, C = card, N = network, T = R + C + N, all for the tax year.
- Kind of each line, from its expense category:
  - X (not a vendor payment): payroll, wages, salary, salaries, tax, taxes, owner, owners, draw, distribution, transfer, loan, credit card payment, interest, bank fees, insurance, license, licenses, permit, permits;
  - R (rent): rent, rental, lease;
  - S (service): contract, contractor, subcontractor, subcontractors, labor, outside services, professional, consulting, repair, repairs, maintenance, janitorial, cleaning, landscaping, commission, commissions, marketing, advertising, accounting, bookkeeping, design, security, training, legal, preparation, service, services;
  - G (goods): supplies, supply, materials, inventory, cost of goods, purchases, merchandise, equipment, tools, furniture, fuel, utilities, telephone, internet, freight, shipping, postage, storage, meals, travel, software, subscription, subscriptions, dues, parts, food.
  - Decide in this order: X if it matches X and not S; else R if it matches R; else S if S and not G; else G if G and not S; else unknown.
  - If the category is "accounts payable" (a bill payment), take the kind from that vendor's set-aside bill lines: the kind with the most bill dollars. Those bill lines' categories and memos also count in every category or memo test below.
  - If there is no category, or it is accounts payable with no bills, use the vendor name: R for realty, properties, leasing; S for plumbing, electric, hvac, roofing, landscaping, cleaning, janitorial, consulting, design, photography, repair, construction, carpentry, painting, bookkeeping, accounting, cpa, marketing, staffing, towing, upholstery, service, services; G for supply, supplies, hardware, lumber, wholesale, distributor, distributors, utility, utilities, power, energy, water, and big retailers and carriers (Amazon, Home Depot, Staples, Office Depot, Costco, Walmart, FedEx, UPS, Verizon, Comcast). If both S and G words match, or neither, it is unknown.
- Kind of the vendor, first match wins:
  1. EXCLUDED if the name contains irs, internal revenue, treasury, department of, state of, city of, franchise tax, gusto, adp, paychex, card services, bank, credit union, insurance or state farm.
  2. ATTORNEY if the name contains law, attorney, attorneys, lawyer, esq or legal, or a category contains "legal" without "professional".
  3. MEDICAL if the name contains md, dds, dmd, medical, clinic, dental, chiropractic, physician, health or hospital, or a category contains medical, dental or health care without supplies or insurance.
  4. Exception to 2 and 3: if the name matched but the vendor's goods-category dollars are more than all its other dollars together, the kind is unknown, and the reason must say the name and the books disagree.
  5. MIXED if its bank dollars include both S and G lines.
  6. Otherwise the kind with the most dollars, all methods (S service, R rent, G goods, X excluded, unknown).

## One bucket per vendor, first match wins
1. The `(no name)` vendor: `REVIEW`.
2. EXCLUDED: `NOT_REPORTABLE`. Give the specific reason (payroll, taxes or government, insurance, owner draw, loan or interest, transfer or bank).
3. T is zero or less: `NOT_REPORTABLE` (refunds, credits or deposits only).
4. A category or memo mentions royalty or royalties and R is $10 or more: `REVIEW` (royalties go on 1099-MISC box 2 from $10).
5. Goods: `NOT_REPORTABLE`.
6. One of the vendor's rows is an unreadable line: `REVIEW` (its true total is unknown).
7. Its bank dollars include both rent lines and service lines, R reaches the limit, and it is not ATTORNEY or MEDICAL: `REVIEW` (two different forms).
8. MIXED where service bank dollars are under the limit but service plus goods bank dollars reach it: `REVIEW`. If service dollars alone reach the limit, treat it as a service vendor, report all of R, and add a caution that the amount includes goods.
9. R at or over the limit:
   a. R minus possible duplicates (see checks) falls under the limit: `REVIEW`.
   b. ATTORNEY: `NEC`, even if incorporated. If a memo or category mentions "settlement": `REVIEW`.
   c. MEDICAL: `MISC_MEDICAL`, even if incorporated. Say tax-exempt and government hospitals are excepted.
   d. Looks incorporated: `CONFIRM_CORP` (probably exempt; a W-9 showing C or S corporation settles it). But if a category or memo of its lines contains legal, attorney or law: `REVIEW`, because law firms are not exempt.
   e. Rent: `MISC_RENT`. Say it is not required when paid to a real estate agent or property manager.
   f. Unknown: `REVIEW` (cannot tell what the payment was for).
   g. Service: `NEC`.
10. R under the limit:
   a. R plus the vendor's bank refunds (as a positive number) reaches the limit: `REVIEW` (under the limit only because of refunds or credits).
   b. ATTORNEY and R is $600 or more: `REVIEW` (fees under the limit need no form, but settlement money paid to an attorney goes on 1099-MISC box 10 from $600).
   c. N is more than zero and R + N reaches the limit: `REVIEW` (PayPal and Venmo payments count if sent as personal payments).
   d. It is a look-alike of another vendor and together they reach the limit (see checks): `REVIEW`.
   e. R is at least 75% of the limit: `CLOSE`.
   f. Otherwise `NOT_REPORTABLE`. If T reaches the limit, say the card portion is why.
   For 2026 files, when R is between $600 and the limit in 10e or 10f, add a sentence telling her to check whether her state still uses the $600 limit.

Form and box: `NEC` is form `1099-NEC`, box `1a` for 2026 payments and box `1` for 2025 and earlier. `MISC_RENT` is `1099-MISC` box `1`. `MISC_MEDICAL` is `1099-MISC` box `6`. Every other bucket has form and box null.

## Checks. Never fix silently; report.
Raise each as an exception with a code and a plain-English message that gives row numbers:
- `TOTAL_MISMATCH`: the file's own total differs from the sum of all its lines exactly as written (set-aside bills included, signs as written; compare absolute values).
- `SUBTOTAL_MISMATCH`: in a grouped file, a vendor subtotal differs from the written sum of the lines since the previous subtotal.
- `NOT_PAYMENTS`: lines set aside in step 6 of Reading the file, with a count by type.
- `UNREADABLE_LINES`, `OUTSIDE_YEAR`. In the outside-year message, name any vendor whose payments in that other year reach that year's limit.
- `PARTIAL_YEAR`: the first payment in the tax year is after January 31 or the last is before December 1.
- `DUPLICATE`, one per group: payment lines with the same vendor, date, amount and number (two blank numbers count as the same). Keep every copy in the totals. Same date and amount with different numbers is not a duplicate.
- `SAME_VENDOR`, one per pair: two vendors, neither goods nor excluded, whose keys look alike (every word of one is in the other and a shared word has 4 or more letters, or the keys with spaces removed are each 8 or more characters and within edit distance 2), where R of at least one is under the limit and their combined R reaches it.
- `REFUND`: one exception listing the negative lines in the tax year that belong to a vendor who also has a positive line. A payee with only money coming in is not a refund.

## Worksheet, in this order
1. Heading with the tax year. Directly under it, one line of counts that link to the sections: vendors to file and their dollar total, probably exempt, needs judgment, close to the limit, no 1099. Then one line saying whether every payment line is accounted for and whether the file's own total agrees. Then the source file name, the number of payment lines, the dates the payments run from and to, the limit applied, and the due dates (1099-NEC to the IRS and the payee by January 31, which is February 1 in 2027 because the 31st is a Sunday). For 2026 say that nonemployee compensation is box 1a on the 2026 form and was box 1 before. Beside the heading, three text inputs she can type in and that print: Client, Prepared by, Reviewed by. Keep Prepared by and Reviewed by when she starts over with another file.
2. If the file's total or a subtotal does not tie: a large red warning in an element with `id="tie-banner"` telling her not to file from this worksheet and to ask the client for a new export. Mark the counts line "not confirmed" and repeat a short warning in the running header of every printed page. No element with that id otherwise.
3. "Check these first": every exception, then the names of the `REVIEW` vendors, then any vendor in the first two tables that carries a caution. If there is nothing, say so. The `NOT_PAYMENTS` message lists each set-aside line with vendor, type, amount and row, and names any vendor that has bills but no payment in the file.
4. Tables in this order: File a 1099; Probably exempt; Needs your judgment; Close to the limit; No 1099. Under each heading, one sentence beginning "Next:" that says what to do. Columns: vendor (with its row numbers as ranges), form and box, bank dollars, the reason as a full sentence that ends in a question when it is a judgment call, and a real checkbox "W-9 on file". In Needs your judgment, each row also has a multi-line text box "Your decision" that grows as she types and prints in full. Each table ends with a subtotal row.
5. Control totals: bank, card, network and outside-year dollars; their sum; the sum of the payment lines read and whether the two tie; the count of lines that were not payments; the file's own total and whether it ties to the lines as written (say in words why this can differ from the payments total). Then bank dollars for each table above, summing to the bank total.
6. A collapsed "Source lines" table listing every line of every vendor outside the No 1099 table: row, date, number, amount, counted or not, category, memo. It prints only while open.
7. Footer: what the tool does not do (it has seen no W-9; no TIN checks, state rules, backup withholding, 1099-INT/DIV/K or 1042-S; cannot spot an employee paid as a contractor or a tax-exempt payee; knows only the payments in the file; assumes a calendar-year client), and that the accountant is responsible for review.

## Contract for testing
After each file, set `window.__report` to:
```
{ taxYear, threshold,                       // threshold in dollars: 2000 or 600
  controls: { linesRead, totalPayments, accountedFor, ties,
              byMethod: { bank, card, network }, outsideYearTotal, outsideYearLines,
              unreadableLines, notPaymentLines, fileTotal, fileTotalTies },
  exceptions: [ { code, message } ],
  vendors: [ { name, spellings: [..], bucket, form, box, reportable, card, network, total, why, rows: [..] } ] }
```
Dollar values are numbers in dollars. `linesRead` counts payment lines only (not set-aside bills, not unreadable lines), including outside-year ones, and `totalPayments` is their sum. `outsideYearLines`, `unreadableLines` and `notPaymentLines` are counts. `accountedFor` is every vendor's `total` plus `outsideYearTotal`. `reportable` is R. `rows` are file row numbers. `form` and `box` are strings or null. `fileTotal` is positive, and it and `fileTotalTies` are null when the file has no total row.
If the file cannot be used, show no worksheet and set `window.__report = { fatal, message }`, with `fatal` equal to `NO_COLUMNS` (no date and amount headings, or no payment lines), `UNSUPPORTED_YEAR`, or `UNREADABLE_FILE` (wrong file type or a file that will not open).
