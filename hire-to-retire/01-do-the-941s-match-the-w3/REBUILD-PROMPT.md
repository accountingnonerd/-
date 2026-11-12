Build a single self-contained HTML file called `do-the-941s-match-the-w3.html`. It is a tool for a US accountant who is expert in payroll tax, impatient with software, and working on a desktop. She drops in a client's filed Forms 941 for the year and the Form W-3, as PDFs (several files, or one combined year-end packet). She gets back a printable reconciliation of the W-3 against the four quarters, the one the IRS tells employers to keep. Everything runs in the browser. Nothing is uploaded. Do all arithmetic in whole cents, in code.

## Screen
- Start screen: the title "Do the 941s match the W-3?", one sentence saying what it does, and one large drop area ("Drop the 941s and the W-3 here, or click to choose them") wrapping an `<input type="file" multiple accept=".pdf">`. Below it, in a few short lines:
  - what it adds: the provider files both forms but proving they agree is left to her; the IRS matches them about two years later and sends a letter;
  - which files: filed copies from the provider, filled-in IRS forms, or one year-end packet; scans cannot be read;
  - which rule: the IRS General Instructions for Forms W-2 and W-3 (2026), with boxes 2, 3, 5 and 7 against the 941s and the tax check (employer plus employee);
  - that after a change of provider she should drop in both W-3s;
  - that files never leave the computer, and that the result is a reconciliation she must review and sign.
- No settings. While reading, show "Reading the forms...". If the files cannot be used, stay on the start screen and show "I could not use those files." with the reason directly under the drop area.
- After reading, replace the start screen with the reconciliation. Above it: one main button "Print or save as PDF" (`window.print()`); a second button "Add another file" wrapping an `<input type="file" id="addfile" multiple accept=".pdf">`, which re-runs everything with the files already given plus the new ones (skip a file with the same name and size); and a small "Start over" link. Add print styles: compact type, table headers repeated, tables allowed to break between rows.
- Large type (18px or more), plain words, high contrast, light background.
- Read PDFs with pdf.js 3.11.174 from `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js`. Create its worker from a Blob of the worker script's text (fetched from the same CDN path, `pdf.worker.min.js`), because a worker cannot load across origins from a local file.

## Reading each page
For every page, collect:
- the text runs from `getTextContent()`. Each has `str`, `x0 = transform[4]`, `x1 = x0 + width`, and a vertical centre `yc = transform[5] + 0.32 * fontSize`, where `fontSize = hypot(transform[0], transform[1])`;
- the form fields from `getAnnotations()`. Take widgets whose `fieldValue` is a non-empty string, as tokens at their rectangle (`x0`, `x1`, `yc` = rectangle middle). Checked checkboxes become the token `X`.

All coordinates are PDF points, with the origin at the bottom left. A "row" means tokens whose `yc` is within 7 points of a label's `yc`. To find a label, group text runs into lines (runs whose `yc` are within 2.5 points), and look for a line where the label pattern starts at one of its runs.

### What each page is (first match wins)
1. Under 25 characters of text and no filled fields: a scan.
2. "Correcting quarter" and "Correcting calendar year": page 2 of a 941-X, which holds the corrections.
2a. "941-X" and "Adjusted Employer": page 1 of a 941-X.
3. "Form 944" and "ANNUAL Federal Tax Return": Form 944.
4. "941-V" and "Payment Voucher": a voucher, not needed.
5. "941", "QUARTERLY Federal Tax Return" and "Wages, tips, and other compensation": Form 941, page 1.
6. "941" and "Part 2" or "deposit schedule" or "Part 5": a later page of the 941, not needed.
7. "Transmittal of Wage and Tax Statements", "Social security wages" and "Medicare wages and tips": Form W-3.
8. "W-3" and "Transmittal": a W-3 instructions page, not needed.
9. "Wage and Tax Statement": a W-2, not needed.
10. Anything else: not a payroll form.

### Reading a Form 941 page
- Year: from "941 for YYYY".
- Layout: if the text contains a form code matching `9501\d\d`, or the page has filled fields, it is the official IRS form. Otherwise it is a payroll provider's own layout.
- Line labels, as regular expressions at the start of a line:

  | Line | Label pattern |
  |---|---|
  | 2 | `Wages, tips, and other compensation` |
  | 3 | `Federal income tax withheld from wages` |
  | 5a | `Taxable social security wages` |
  | 5b | `Taxable social security tips` |
  | 5c | `Taxable Medicare wages` |
  | 5d | `(Taxable wages & tips subject to )?Additional Medicare Tax withholding` |
  | 5e | `Total social security and Medicare taxes` |
  | 5f | `Section 3121\(q\)` |
  | 6 | `Total taxes before adjustments` |
  | 7 | `Current quarter.s adjustment for fractions of cents` |
  | 8 | `Current quarter.s adjustment for sick pay` |
  | 9 | `Current quarter.s adjustments for tips and group-term life` |
  | 10 | `Total taxes after adjustments(?!\s+and)` |
  | 11 | `Qualified small business payroll tax credit` |
  | 12 | `Total taxes after adjustments and nonrefundable credits` |
  | 13 | `Total deposits for this quarter` |

  Only tokens on the label's row more than 20 points to the right of the label's start count.
- Official IRS layout: each amount is a dollars part and a cents part in fixed columns. The IRS also prints the line number just left of the dollars column, so the columns must exclude it.
  - Ordinary lines: dollars between x = 443 and 550, cents between 550 and 582.
  - Lines 5a to 5d: column 1 dollars 212 to 285 and cents 285 to 313; column 2 dollars 350 to 421 and cents 421 to 449.
  - A token is in a dollars column only if its right edge is more than 2 points past the column's left edge, its left edge is more than 2 points before the column's right edge, and it looks like a number (digits, commas, optional minus or parentheses). The 2-point margin matters: the printed two-digit line numbers "10", "11" and "12" just touch the dollars column and must not be read as digits.
  - A cents token starts inside the cents column and has one to three digits; take its first two.
  - A dollars token that already contains a decimal point is the whole amount.
  - A line with nothing in its columns is zero.
- Provider layout: amounts have a decimal point and two decimals (`89,552.25`). Ordinary lines take the last such amount on the row. Lines 5a to 5d take the last two: column 1, then column 2.
- Amount text can look like `48250`, `48,250`, `48,250.00`, `-0`, or `(1,234.00)`. Parentheses or a minus sign mean negative.
- Quarter:
  - Official layout: find the labels `1: January`, `2: April`, `3: July`, `4: October`. The marked one has an `X` or a check token on its row that starts within 30 points to the left of the label.
  - Otherwise, or if none or several are marked: look for `Quarter\s*:?\s*([1-4])` or `\bQ([1-4])\b` in the page text.
- EIN: take every token, text runs and form-field values alike, whose `yc` is within 8 points of the "Employer identification number" label and whose left edge is more than 60 points right of the label's start, and which consists only of digits and hyphens. Join them in left-to-right order without the hyphens. If that gives nine digits, format as `NN-NNNNNNN`. Otherwise use the first `\d{2}-\d{7}` in the page text.
- Name: the tokens right of "Name (not your trade name)" or "Name:".

### Reading a Form 941-X (amended return)
- From page 2, the corrections page:
  - quarter: a token `1` to `4` in the header band (yc above 700) starting between x = 512 and 548;
  - year: a token `20xx` in the header band;
  - if there is no year on page 2, take a `20xx` token on page 1 between x = 415 and 495 and yc 540 to 590, which is the "calendar year" box.
- Lines on page 2, anchored by these labels (start of a line):

  | 941 line | 941-X label | Column 4 (tax) read too? |
  |---|---|---|
  | 2 | `compensation \(Form 941, line 2\)` | no |
  | 3 | `from wages, tips, and other` | no |
  | 5a | `\(Form 941 or 941-SS, line 5a,` | yes |
  | 5b | `941 or 941-SS, line 5b` | yes |
  | 5c | `941 or 941-SS, line 5c` | yes |
  | 5d | `Additional Medicare Tax\s*$` | yes |

  - Read column 3 (the difference): dollars x = 376 to 434, cents 434 to 458.
  - For lines 5a to 5d, also read column 4 (the tax correction): dollars 498 to 556, cents 556 to 580.
  - Use the same dollars and cents method as the 941.
- Later pages of a 941-X repeat the header but have no corrections. A 941-X is unreadable only if none of its pages has corrections.

### Reading a Form W-3 page
- Year: from "Transmittal of Wage and Tax Statements YYYY".
- Layout: if the text contains `33333` or the page has filled fields, it is the official IRS form.
  - In the IRS layout, a box's value sits below its label: tokens 2 to 20 points below the label, whose horizontal centre is between 6 points left of the label start and 148 points right of it.
  - In a provider layout, the value is on the label's row, more than 150 points to the right.
  - Take the last token that reads as an amount.
- Box labels: `1 Wages, tips, other compensation`, `2 Federal income tax withheld`, `3 Social security wages`, `4 Social security tax withheld`, `5 Medicare wages and tips`, `6 Medicare tax withheld`, `7 Social security tips`, and `14 Income tax withheld by payer of third-party sick pay`. Box 14 spans two columns: in the IRS layout its value may be up to 310 points right of its label. A box with no value is zero.
- Also read:
  - `c Total number of Forms W-2`;
  - `e Employer identification number` (EIN);
  - `f Employer.s name`;
  - `h Other EIN used this year`.

## The reconciliation
1. If no 941 and no W-3 page was found:
   - if a Form 944 was found, refuse with `FORM_944` and say this tool is for quarterly 941 filers;
   - otherwise refuse with `NO_FORMS`. If the files were scans, name them, say to ask the provider for the filed PDFs (or use an IRS account transcript), and say all four 941s and the W-3 are needed.
2. W-3s.
   - Several W-3s for the same EIN (or one listing the other's EIN in box h): add them box by box (`W3_ADDED`, information only). This is the usual case after a change of provider. Say to ask each provider for proof that it filed (the SSA's acknowledgment), and to check employees near the $184,500 wage base in case the new provider restarted year-to-date figures.
   - Different EINs: use the first (`TWO_W3`).
   - None: `NO_W3`.
3. Tax year = the W-3's year, else the most common 941 year.
   - A 941 for another year is left out: `WRONG_YEAR`.
   - A 941 with no quarter is left out: `QUARTER_UNKNOWN`.
   - If any 941 line could not be read: `UNREAD_LINES`, and those lines count as zero.
4. One 941 per quarter.
   - Two copies with identical figures count once (`DUPLICATE_SAME`, information only).
   - Two different copies of a quarter: `DUPLICATE_QUARTER`, showing the lines that differ. Do not choose one, and do not compute the reconciliation.
   - A quarter with no 941: `MISSING_QUARTER`, naming the quarters ("quarters 1, 2 and 3"). If all four are missing, say there are no 941s, only a W-3, and to add them with "Add another file".
   - `SCANNED` for each file with pages that have no text.
5. Arithmetic inside each 941 as filed, before any 941-X, with a tolerance of 1 cent: `ARITHMETIC`, naming the quarter.
   - Line 5a column 2 = 12.4% of column 1; 5b the same; 5c = 2.9%; 5d = 0.9%. Round half up to the cent.
   - 5e = 5a + 5b + 5c + 5d column 2.
   - 6 = 3 + 5e + 5f.
   - 10 = 6 + 7 + 8 + 9.
6. Amended returns, applied after the arithmetic check.
   - A 941-X for the tax year: add its column 3 differences to that quarter's lines 2, 3 and 5a to 5d column 1. Add its column 4 corrections to 5a to 5d column 2, and to 5e. Raise `AMENDED_INCLUDED` (information), listing the changes, because the IRS says current-year adjustments belong in the reconciliation.
   - A 941-X for another year: `AMENDED_OTHER_YEAR` (information), left out.
   - Unreadable, or for a quarter with no 941: `AMENDED_RETURN`, saying to add it by hand.
7. EIN.
   - If a quarter's EIN differs from the W-3 EIN and is not in W-3 box h: `EIN_MISMATCH`. This stops the status from being `AGREES`. Say:
     - the amounts agree only if both EINs are counted together, and the IRS matches by EIN;
     - first find out why that quarter used that EIN;
     - if it was properly used (for example an earlier entity's EIN), the W-3 should show it in box h;
     - if the 941 went in under the wrong EIN by mistake, that is fixed with the IRS on the 941 side.
   - If it is in box h: `OTHER_EIN_LISTED`, information only.
8. W-3 internal checks (`W3_INTERNAL`). The tolerance is $1.00 plus 2 cents per W-2 in box c.
   - Box 5 must not be less than box 3 + box 7.
   - Box 4 must be within the tolerance of 6.2% of (box 3 + box 7), and box 6 must not be below 1.45% of box 5 less the tolerance. Skip both when the 941s have line 9 amounts, because uncollected tax is not in boxes 4 and 6.
9. Reconcile, unless there is no W-3 or there is a duplicate quarter:

   | W-3 box | 941 line | Counts toward status? |
   |---|---|---|
   | 1 | line 2 | no: the IRS does not compare it |
   | 2 less box 14 | line 3 | yes |
   | 3 | line 5a column 1 | yes |
   | 5 | line 5c column 1 | yes |
   | 7 | line 5b column 1 | yes |

   - For each, show Q1 to Q4, the 941 total, the W-3 amount and the difference (W-3 minus 941 total). A row agrees only if the difference is exactly zero.
   - A box 1 difference is shown as "check". If it is the only difference, raise `BOX1_DIFFERS`, naming valid reasons such as third-party sick pay.
   - When a row does not agree, look at the 15 non-empty sets of quarters that are present. If the absolute difference equals one set's total for that line, record those quarters as `pattern` (the first such set in binary order 1, 2, 1+2, 3, 1+3, 2+3, 1+2+3, 4, and so on).
   - Tax check: compare Σ(941 lines 5e + 7 + 9) with W-3 box 4 + box 6 + the employer's share. The employer's share is 6.2% of (box 3 + box 7) plus 1.45% of box 5, each rounded to the cent.
     - Line 9 counts, because uncollected employee tax on tips and group-term life is in neither box 4 nor box 6.
     - Line 8 does not count, because the insurer's withholding on third-party sick pay is in boxes 4 and 6 but taken off the 941 on line 8.
     - It agrees within $1.00 plus 2 cents per W-2.
   - Information notes:
     - `UNCOLLECTED_TAX` when the 941s have line 9 amounts. Say W-2 box 12 codes A and B, or M and N, should add up to them.
     - `THIRD_PARTY_SICK_PAY` when W-3 box 14 or any line 8 is not zero. Say how they were treated, and that this assumes the W-2s include the sick pay.
   - If any status row or the tax check disagrees, raise `MISMATCH`. Lead with the cause and the next step; the amounts stay in the table. Describe each difference by direction ("$11,232.82 lower on the W-3"), never with a minus sign.
     - If every disagreeing row has the same pattern and the W-3 is lower: "The W-3 leaves out the wages of quarters ...". Most likely the earlier provider filed its own W-2s and W-3 for those quarters, so ask it for that W-3 and add it with "Add another file". If it never filed one, those W-2s and a W-3 still have to be filed.
     - If the W-3 is higher: check for a missing quarter or a 941 under another EIN.
     - Otherwise: W-2c and W-3c if the W-2s are wrong, 941-X if a 941 is wrong.
     - Always: keep the reconciliation for a possible Letter 99C.
10. Status:
    - `NOT_RECONCILED` if there is a duplicate quarter or no W-3;
    - otherwise `INCOMPLETE` if a quarter is missing;
    - otherwise `AGREES` if rows 2, 3, 5 and 7 and the tax check agree and there is no `EIN_MISMATCH`;
    - otherwise `DOES_NOT_AGREE`.

## The reconciliation page, in this order
1. Heading "941 to W-3 reconciliation, YYYY". Under it, one verdict sentence in plain words: green for agrees, red for does not agree or incomplete, amber for not reconciled. When the amounts agree but `EIN_MISMATCH` is raised, say exactly that. Then the employer, the EIN, today's date, and the rule applied (boxes 2, 3, 5 and 7 compared by the IRS; the tax check; box 1 shown but not compared). Beside it, four text inputs that print: Prepared by, Date, Reviewed by, Date.
2. If the status is not `AGREES`, a red box in an element with `id="stop-banner"` headed "What to do", holding the message of the most serious exception. In priority order, the serious ones are `MISSING_QUARTER`, `DUPLICATE_QUARTER`, `NO_W3`, `SCANNED`, `MISMATCH` and `EIN_MISMATCH`. No element with that id otherwise.
3. "Check these first": every other exception in plain words. Serious first, then the rest. Information notes go last and look quieter. If there are none, say so.
4. The reconciliation table, and the tax check showing its arithmetic.
5. "What I read from each 941": every line read, by quarter, plus a row with the EIN on each 941 (highlight one that differs) and a row with the file and page of each quarter. If several W-3s were added, a table of each W-3's boxes 1 to 7 and 14 with its file and page; otherwise one line naming where the W-3 was read.
6. "Every page I was given": file, page, what it is, and whether it was used.
7. Footer:
   - that it compares the forms with each other, not with IRS records;
   - what it does not do: no W-2 by W-2 checks, no state forms, no 940, no deposits, no Schedule B, no scans;
   - who it is not for: aggregate filers (section 3504 agents, PEOs), successor-employer arrangements, household employers, and 943, 944 or CT-1 filers;
   - that some differences can be valid;
   - that nothing was uploaded, and that the accountant is responsible for the review.
8. In print, put a running header on each page with the employer, EIN and year (and "DOES NOT AGREE" or "NOT FINISHED" when it applies), and "Page x of y".

## Contract for testing
After the files are read, set `window.__report` to:
```
{ year, ein, employer, status, quartersFound: [1,2,3,4],
  quarters: { "1": { file, page, ein, lines: { "2":..., "3":..., "5a1":..., "5a2":..., "5b1":..., "5b2":..., "5c1":..., "5c2":..., "5d1":..., "5d2":..., "5e":..., "7":..., "8":..., "9":... } }, ... },
  w3: { file, page, boxes: { b1, b2, b3, b4, b5, b6, b7, b14 } } | null,      // added together if there were several
  recon: { b1: { total941, w3, diff, agrees, pattern? }, b2, b3, b5, b7, tax: { total941, w3, diff, agrees } } | null,
  exceptions: [ { code, message, quarter? } ],
  pages: [ { file, page, kind, used } ] }
```
- Dollar values are numbers in dollars. `quartersFound` lists the quarters actually used, in order.
- In the tax check, say where the tolerance comes from ($1.00 plus 2 cents for each W-2 in box c).
- Quarter lines include any current-year 941-X corrections. `recon.b2.w3` is box 2 less box 14.
- On `ARITHMETIC`, put the quarter number in `quarter`.
- If the files cannot be used, set `window.__report = { fatal, message }`, with `fatal` equal to `NO_FORMS` or `FORM_944`, and show the message in a visible element with `id="problem"` on the start screen.
- A quarter with two different 941s still counts in `quartersFound`; only the reconciliation is withheld.
- Set `window.__report` to `undefined` when new files are given, and set it once the result (or refusal) is on screen.
