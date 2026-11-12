Build a single self-contained HTML file called `do-the-941s-match-the-w3.html`. It is a tool for a US accountant who is expert in payroll tax, impatient with software, and working on a desktop. She drops in a client's filed Forms 941 for the year and the Form W-3, as PDFs (several files, or one combined year-end packet). She gets back a printable reconciliation of the W-3 against the four quarters, the one the IRS tells employers to keep. Everything runs in the browser. Nothing is uploaded. Do all arithmetic in whole cents, in code.

## Screen
- Start screen: the title "Do the 941s match the W-3?", one sentence saying what it does, and one large drop area ("Drop the 941s and the W-3 here, or click to choose them") wrapping an `<input type="file" multiple accept=".pdf">`. Below it, in a few short lines:
  - what it adds: the provider files both forms but proving they agree is left to her; the IRS matches them about two years later and sends a letter;
  - which files: filed copies from the provider, filled-in IRS forms, or one year-end packet; scans cannot be read;
  - which rule: the IRS General Instructions for Forms W-2 and W-3 (2026);
  - that files never leave the computer, and that the result is a reconciliation she must review and sign.
- No settings. While reading, show "Reading the forms...". If the files cannot be used, stay on the start screen and show "I could not use those files." with the reason directly under the drop area.
- After reading, replace the start screen with the reconciliation, one main button "Print or save as PDF" (`window.print()`), and a small "Start over" link. Add print styles: compact type, table headers repeated.
- Large type (18px or more), plain words, high contrast, light background.
- Read PDFs with pdf.js 3.11.174 from `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js`. Create its worker from a Blob of the worker script's text (fetched from the same CDN path, `pdf.worker.min.js`), because a worker cannot load across origins from a local file.

## Reading each page
For every page, collect:
- the text runs from `getTextContent()`. Each has `str`, `x0 = transform[4]`, `x1 = x0 + width`, and a vertical centre `yc = transform[5] + 0.32 * fontSize`, where `fontSize = hypot(transform[0], transform[1])`;
- the form fields from `getAnnotations()`. Take widgets whose `fieldValue` is a non-empty string, as tokens at their rectangle (`x0`, `x1`, `yc` = rectangle middle). Checked checkboxes become the token `X`.

All coordinates are PDF points, with the origin at the bottom left. A "row" means tokens whose `yc` is within 7 points of a label's `yc`. To find a label, group text runs into lines (runs whose `yc` are within 2.5 points), and look for a line where the label pattern starts at one of its runs.

### What each page is (first match wins)
1. Under 25 characters of text and no filled fields: a scan.
2. "941-X" and "Adjusted Employer": an amended 941.
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
  - A token is in a dollars column if it overlaps it and looks like a number (digits, commas, optional minus or parentheses).
  - A cents token starts inside the cents column and has one to three digits; take its first two.
  - A dollars token that already contains a decimal point is the whole amount.
  - A line with nothing in its columns is zero.
- Provider layout: amounts have a decimal point and two decimals (`89,552.25`). Ordinary lines take the last such amount on the row. Lines 5a to 5d take the last two: column 1, then column 2.
- Amount text can look like `48250`, `48,250`, `48,250.00`, `-0`, or `(1,234.00)`. Parentheses or a minus sign mean negative.
- Quarter:
  - Official layout: find the labels `1: January`, `2: April`, `3: July`, `4: October`. The marked one has an `X` or a check token on its row that starts within 30 points to the left of the label.
  - Otherwise, or if none or several are marked: look for `Quarter\s*:?\s*([1-4])` or `\bQ([1-4])\b` in the page text.
- EIN: on the row of "Employer identification number", join the digit tokens more than 60 points right of the label. If that gives nine digits, format as `NN-NNNNNNN`. Otherwise use the first `\d{2}-\d{7}` in the page text.
- Name: the tokens right of "Name (not your trade name)" or "Name:".

### Reading a Form W-3 page
- Year: from "Transmittal of Wage and Tax Statements YYYY".
- Layout: if the text contains `33333` or the page has filled fields, it is the official IRS form.
  - In the IRS layout, a box's value sits below its label: tokens 2 to 20 points below the label, whose horizontal centre is between 6 points left of the label start and 148 points right of it.
  - In a provider layout, the value is on the label's row, more than 150 points to the right.
  - Take the last token that reads as an amount.
- Box labels: `1 Wages, tips, other compensation`, `2 Federal income tax withheld`, `3 Social security wages`, `4 Social security tax withheld`, `5 Medicare wages and tips`, `6 Medicare tax withheld`, `7 Social security tips`.
- Also read:
  - `c Total number of Forms W-2`;
  - `e Employer identification number` (EIN);
  - `f Employer.s name`;
  - `h Other EIN used this year`.

## The reconciliation
1. If no 941 and no W-3 page was found:
   - if a Form 944 was found, refuse with `FORM_944` and say this tool is for quarterly 941 filers;
   - otherwise refuse with `NO_FORMS`. If the files were scans, say to ask the provider for the filed PDFs.
2. Tax year = the W-3's year, else the most common 941 year.
   - A 941 for another year is left out: `WRONG_YEAR`.
   - A 941 with no quarter is left out: `QUARTER_UNKNOWN`.
   - If any 941 line could not be read: `UNREAD_LINES`, and those lines count as zero.
3. One 941 per quarter.
   - Two copies with identical figures count once (`DUPLICATE_SAME`, information only).
   - Two different copies of a quarter: `DUPLICATE_QUARTER`, showing the lines that differ. Do not choose one, and do not compute the reconciliation.
   - A quarter with no 941: `MISSING_QUARTER`.
4. Other exceptions:
   - `SCANNED` for each file with pages that have no text;
   - `AMENDED_RETURN` if a 941-X is present (never add its corrections; say the difference should equal its change);
   - `TWO_W3` if there is more than one W-3 (use the first);
   - `NO_W3` if there is none.
5. Arithmetic inside each 941, with a tolerance of 1 cent: `ARITHMETIC`, naming the quarter.
   - Line 5a column 2 = 12.4% of column 1; 5b the same; 5c = 2.9%; 5d = 0.9%. Round half up to the cent.
   - 5e = 5a + 5b + 5c + 5d column 2.
   - 6 = 3 + 5e + 5f.
   - 10 = 6 + 7 + 8 + 9.
6. EIN:
   - If a quarter's EIN differs from the W-3 EIN and is not in W-3 box h: `EIN_MISMATCH`, saying box h should show it.
   - If it is in box h: `OTHER_EIN_LISTED`, information only.
7. W-3 internal checks, as `W3_INTERNAL`:
   - box 5 must not be less than box 3 + box 7;
   - box 4 must be within ($1.00 + 1 cent per W-2 in box c) of 6.2% of (box 3 + box 7);
   - box 6 must not be less than 1.45% of box 5 minus that same tolerance.
8. Reconcile, unless there is no W-3 or a duplicate quarter:

   | W-3 box | 941 line | Matched by the IRS and SSA? |
   |---|---|---|
   | 1 | line 2 | no (show it, but say it is not matched) |
   | 2 | line 3 | yes |
   | 3 | line 5a column 1 | yes |
   | 5 | line 5c column 1 | yes |
   | 7 | line 5b column 1 | yes |

   - For each, show Q1 to Q4, the 941 total, the W-3 amount and the difference (W-3 minus 941 total). It agrees only if the difference is exactly zero.
   - When it does not agree, look at the 15 non-empty sets of quarters that are present. If the absolute difference equals one set's total for that line, record those quarters as `pattern` (the first such set in binary order 1, 2, 1+2, 3, 1+3, 2+3, 1+2+3, 4, and so on).
   - Tax check: the 941 total of (line 5e + line 7) against 2 × box 4 + 2 × box 6 − Σ line 5d column 2, because the Additional Medicare Tax is withheld from the employee only. It agrees within $1.00.
   - If anything disagrees, raise `MISMATCH` listing each box, the amounts and the difference. If every disagreeing box has the same pattern, say every difference equals those quarters exactly: the W-3 probably leaves out their wages (common after a change of payroll provider), or those 941s were filed twice. Give the next steps (W-2c and W-3c if the W-2s are wrong, 941-X if a 941 is wrong), and say to keep the reconciliation for a possible Letter 99C.
9. Status:
   - `NOT_RECONCILED` if there is a duplicate quarter or no W-3;
   - otherwise `INCOMPLETE` if a quarter is missing;
   - otherwise `AGREES` if all five rows and the tax check agree;
   - otherwise `DOES_NOT_AGREE`.

## The reconciliation page, in this order
1. Heading "941 to W-3 reconciliation, YYYY". Under it, one verdict sentence in plain words: green for agrees, red for does not agree or incomplete, amber for not reconciled. Then the employer, the EIN, today's date, and the rule applied. Beside it, two text inputs that print: Prepared by and Reviewed by.
2. If the status is not `AGREES`, a large red box in an element with `id="stop-banner"` saying the forms do not agree, or the reconciliation is not finished, and that the first item below says why. No element with that id otherwise.
3. "Check these first": every exception in plain words, the stopping ones first. If there are none, say so.
4. The reconciliation table, and the tax check showing its arithmetic.
5. "What I read from each 941": every line read, by quarter, with the file and page of each quarter. Add one line naming where the W-3 was read.
6. "Every page I was given": file, page, what it is, and whether it was used.
7. Footer: what it does not do (no W-2 by W-2 checks, no state forms, no 940, no deposits, no Schedule B, no scans, no 941-X corrections added in), that some differences can be valid (for example third-party sick pay or prior-year adjustments), that nothing was uploaded, and that the accountant is responsible for the review.

## Contract for testing
After the files are read, set `window.__report` to:
```
{ year, ein, employer, status, quartersFound: [1,2,3,4],
  quarters: { "1": { file, page, lines: { "2":..., "3":..., "5a1":..., "5a2":..., "5b1":..., "5b2":..., "5c1":..., "5c2":..., "5d1":..., "5d2":..., "5e":..., "7":... } }, ... },
  w3: { file, page, boxes: { b1, b2, b3, b4, b5, b6, b7 } } | null,
  recon: { b1: { total941, w3, diff, agrees, pattern? }, b2, b3, b5, b7, tax: { total941, w3, diff, agrees } } | null,
  exceptions: [ { code, message, quarter? } ],
  pages: [ { file, page, kind, used } ] }
```
- Dollar values are numbers in dollars. `quartersFound` lists the quarters actually used, in order.
- On `ARITHMETIC`, put the quarter number in `quarter`.
- If the files cannot be used, set `window.__report = { fatal, message }`, with `fatal` equal to `NO_FORMS` or `FORM_944`.
