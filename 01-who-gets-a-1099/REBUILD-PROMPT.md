Build a single self-contained HTML file called `who-gets-a-1099.html`. It is a tool for a US accountant who is expert in tax, impatient with software, and reading on a desktop screen. She gives it one file, the list of everything a client paid during the year, and gets back a printable worksheet saying which vendors need a Form 1099, which need a W-9 checked, and why. Everything runs in the browser. Nothing is uploaded.

## Screen
- Start screen: the title "Who gets a 1099?", one sentence saying what it does, and one large drop area ("Drop the payments file here, or click to choose it") wrapping an `<input type="file">` that accepts .csv and .xlsx. Say on this screen that the file never leaves the computer and that the result is a worksheet she must review. No settings and no other controls, apart from a small link that runs a built-in made-up sample.
- After a file is read, replace the start screen with the worksheet and one main button, "Print or save as PDF" (`window.print()`), plus a small "Start over" link. Add print styles.
- Large type (18px or more), plain words, high contrast, light background.
- Read .csv with your own parser (quoted fields, commas inside quotes, a leading BOM, blank lines, CRLF). Read .xlsx with SheetJS loaded from `https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js`, first sheet, raw cell values. Excel dates arrive as serial numbers (days since 1899-12-30); treat a number between 20000 and 80000 in the date column as a date.
- Do all arithmetic in whole cents.

## Reading the file
1. Header row: the first of the top 40 rows that has a date heading and an amount heading. Match headings case-insensitively.
   - Date: date, transaction date, txn date, payment date, check date.
   - Amount: one column (amount, paid amount, total), or a debit and credit pair, or a payment/withdrawal column with an optional deposit column.
   - Payee: name, payee, vendor, vendor name, paid to, supplier. If none of these exists, use "description".
   - Optional: type (type, transaction type); number (num, no, number, check #, check no, check number, ref, reference); memo (memo, memo/description, description, notes); paying account (bank account, paid from, payment account); expense category (category, expense account).
   - A column headed "account" or "split" can be either one. If more than half of its values contain checking, savings, bank, cash, card, visa, mastercard, amex, discover or paypal, it is the paying account. Otherwise it is the expense category.
2. If there is no payee column, the file is grouped by vendor: a row with text in only one cell and no date is a vendor name that applies to the lines under it.
3. A payment line is a row below the header with a readable date and a readable amount. Amounts may look like `1200`, `$1,200.00`, `(450.00)` (negative), `300.00-` (negative), `-550.00`. Dates may look like `1/5/26`, `01/19/2026`, `2026-02-14`, `Mar 3, 2026`. Two-digit years are 20xx. Remember each line's row number as it appears in the file, counting from 1 and counting title and blank rows.
4. A row with a date but no readable amount is an unreadable line. Count it and report it. It goes in no total.
5. A row with no date whose first text is "Total", "TOTAL" or "Grand Total" is the file's own total. A row with no date whose first text starts with "Total " (for example "Total for Rivera Plumbing") is a vendor subtotal.
6. Sign: with one amount column, whichever sign most lines have is "a payment", and the opposite sign is a refund. With debit and credit, the column filled on more lines is the payment column. Payments are positive from here on, refunds negative.
7. Tax year: the year most payment lines fall in. Lines dated in another year are left out of every vendor and reported. If the tax year is after 2026, stop and say this version only knows the rules through 2026.
8. Dollar limit: $2,000 for 2026 payments, $600 for 2025 and earlier. A vendor "at least" at the limit counts.

## Vendors
- Vendor key: lower-case the name, delete periods and apostrophes, turn `&` and other punctuation into spaces, then drop the words llc, inc, incorporated, corp, corporation, co, company, ltd, pllc, pc, lp, llp, the, and. Names with the same key are one vendor. Show every spelling that was combined.
- "Looks incorporated": the name contains the word inc, incorporated, corp, corporation, pc or ltd. LLC, LLP and PLLC say nothing about tax status.
- Payment method of each line:
  - network: type, paying account or number mentions paypal, venmo, stripe, square or cash app, or the memo mentions paypal, venmo or cash app;
  - card: type, paying account or number contains the word card, visa, mastercard, amex, american express, discover or pos;
  - bank: everything else (checks, ACH, wire, Zelle, cash, unknown).
- For each vendor: R = net bank dollars, C = card, N = network, T = R + C + N.
- Kind of each line from its expense category, using whole-word matches:
  - X (not a vendor payment): payroll, wages, salary, tax, taxes, owner, draw, distribution, transfer, loan, credit card payment, interest, bank fees, insurance, license, permit;
  - R (rent): rent, rental, lease;
  - S (service): contract, contractor, subcontractor(s), labor, outside services, professional, consulting, repair(s), maintenance, janitorial, cleaning, landscaping, commission(s), marketing, advertising, accounting, bookkeeping, design, security, training, legal, preparation, service(s);
  - G (goods): supplies, materials, inventory, cost of goods, purchases, merchandise, equipment, tools, furniture, fuel, utilities, telephone, internet, freight, shipping, postage, storage, meals, travel, software, subscription(s), dues, parts, food.
  - Decide in this order: X if it matches X and not S; else R if it matches R; else S if S and not G; else G if G and not S; else unknown.
  - If the line has no category, use the vendor name: R for realty, properties, leasing; S for plumbing, electric, hvac, roofing, landscaping, cleaning, janitorial, consulting, design, photography, repair, construction, carpentry, painting, bookkeeping, accounting, cpa, marketing, staffing, towing, upholstery, service(s); G for supply, supplies, hardware, lumber, wholesale, distributor(s), utility, utilities, power, energy, water and big retailers and carriers (Amazon, Home Depot, Staples, Office Depot, Costco, Walmart, FedEx, UPS, Verizon, Comcast). If both S and G words match, or neither, it is unknown.
- Kind of the vendor, first match wins:
  1. EXCLUDED if the name contains irs, internal revenue, treasury, department of, state of, city of, franchise tax, gusto, adp, paychex, card services, bank, credit union, insurance or state farm.
  2. ATTORNEY if the name contains the word law, attorney, lawyer, esq or legal, or a category contains "legal" without "professional".
  3. MEDICAL if the name contains md, dds, dmd, medical, clinic, dental, chiropractic, physician, health or hospital, or a category contains medical, dental or health care without supplies or insurance.
  4. MIXED if its bank dollars include both S and G lines.
  5. Otherwise the kind with the most dollars (S service, R rent, G goods, X excluded, unknown).

## One bucket per vendor, first match wins
1. EXCLUDED kind: `NOT_REPORTABLE`.
2. T is zero or less: `NOT_REPORTABLE`.
3. Goods: `NOT_REPORTABLE`.
4. MIXED where service bank dollars are under the limit but service plus goods bank dollars reach it: `REVIEW`. (If service dollars alone reach the limit, treat it as a service vendor, report all of R, and note that it includes goods.)
5. R at or over the limit:
   a. R minus possible duplicates (see checks) falls under the limit: `REVIEW`.
   b. ATTORNEY: `NEC` (Form 1099-NEC box 1, even if incorporated). If a memo or category mentions "settlement": `REVIEW`.
   c. MEDICAL: `MISC_MEDICAL` (Form 1099-MISC box 6, even if incorporated).
   d. Looks incorporated: `CONFIRM_CORP` (probably exempt, the W-9 must confirm). But if any of its lines' category or memo contains the word legal, attorney or law: `REVIEW`, because law firms are not exempt.
   e. Rent: `MISC_RENT` (Form 1099-MISC box 1; say it is not required when paid to a real estate agent or property manager).
   f. Unknown: `REVIEW` (cannot tell what the payment was for).
   g. Service: `NEC`.
6. R under the limit:
   a. N is more than zero and R + N reaches the limit: `REVIEW` (PayPal and Venmo payments count if sent as personal payments).
   b. It is a look-alike of another vendor and together they reach the limit (see checks): `REVIEW`.
   c. R is at least 75% of the limit: `CLOSE`.
   d. Otherwise `NOT_REPORTABLE`. If T reaches the limit, say the card portion is why.

## Checks. Never fix silently; report.
Raise each as an exception with a code and a plain-English message with row numbers:
- `TOTAL_MISMATCH`: the file's own total differs from the sum of its payment lines.
- `SUBTOTAL_MISMATCH`: a vendor subtotal differs from the lines above it (grouped files).
- `UNREADABLE_LINES`, `OUTSIDE_YEAR`.
- `PARTIAL_YEAR`: the first payment in the tax year is after January 31 or the last is before December 1.
- `DUPLICATE`, one per group: lines with the same vendor, date, amount and number (two blank numbers count as the same). Keep them in the totals. Same date and amount with different numbers is not a duplicate.
- `SAME_VENDOR`, one per pair: two vendors, neither goods nor excluded, whose keys look alike (all the words of one are in the other and a shared word has 4 or more letters, or the keys with spaces removed are each 8 or more characters and within edit distance 2), where R of at least one is under the limit and their combined R reaches it.
- `REFUND`: one exception listing every negative line in the tax year.

## Worksheet layout, in this order
1. Heading with tax year, source file name, limit applied, and blank lines for Client, Prepared by, Reviewed by.
2. If the file's total or a subtotal does not tie, a large red warning in an element with `id="tie-banner"` telling her not to rely on the worksheet. No element with that id otherwise.
3. "Check these first": every exception, then the names of the `REVIEW` vendors. If there are none, say so.
4. Control totals: bank, card, network and outside-year dollars, their sum, the sum of all payment lines, whether those two tie, and the file's own total with whether it ties.
5. Tables in this order: File a 1099; Probably exempt, confirm with W-9; Needs your judgment; Close to the limit; No 1099 (collapsed). Columns: vendor, form and box, bank dollars, the reason in a full sentence, and an empty "W-9 on file?" tick box. Each vendor can expand to show its source lines with row numbers.
6. Footer: what the tool does not do (it has seen no W-9, no TIN checks, no state rules, no 1099-INT/DIV/K), and that the accountant is responsible for review.

## Contract for testing
After each file, set `window.__report` to:
```
{ taxYear, threshold,                       // threshold in dollars: 2000 or 600
  controls: { linesRead, totalPayments, accountedFor, ties,
              byMethod: { bank, card, network }, outsideYearTotal, outsideYearLines,
              unreadableLines, fileTotal, fileTotalTies },   // last two are null when the file has no total row
  exceptions: [ { code, message } ],
  vendors: [ { name, spellings: [..], bucket, form, box, reportable, card, network, total, why, rows: [..] } ] }
```
Dollar values are numbers in dollars. `linesRead` counts every payment line, including outside-year ones. `totalPayments` is the sum of all of them. `accountedFor` is the sum of every vendor's `total` plus `outsideYearTotal`. `reportable` is R, and `rows` are file row numbers. `fileTotal` is a positive number.
If the file cannot be used, show the reason on the start screen, show no worksheet, and set `window.__report = { fatal, message }` with `fatal` equal to `NO_COLUMNS` (no date and amount headings, or no payment lines) or `UNSUPPORTED_YEAR`.
