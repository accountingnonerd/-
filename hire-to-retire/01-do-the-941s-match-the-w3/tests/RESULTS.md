# Test results: Do the 941s match the W-3? version 1.0.0

Run on 2026-11-12 in headless Chromium with the network blocked. Rerun with `node run-tests.js`.

## 1. Acceptance test, case by case

**17 of 17 cases passed; 1,207 of 1,207 individual checks.**

| Case | What it is | Type | Files | Checks passed | Run time (ms) | Result |
|---|---|---|---|---|---|---|
| 01 | Clean year: four filled-in IRS 941s and a W-3 | clean | 5 | 87/87 | 664 | PASS |
| 02 | Year-end packet, printed copies, tips, uncollected tip tax, extra pages to ignore | ugly | 1 | 87/87 | 686 | PASS |
| 03 | Wage base, Additional Medicare Tax and fractions of cents: must still agree | rules | 5 | 87/87 | 677 | PASS |
| 04 | PLANTED: switched providers mid-year; the new W-3 leaves out January to June | planted | 5 | 88/88 | 541 | PASS |
| 05 | Two different 941s for the second quarter: must refuse to pick one | ugly | 6 | 49/49 | 690 | PASS |
| 06 | Only three quarters dropped in: must say the fourth is missing | ugly | 4 | 73/73 | 620 | PASS |
| 07 | PLANTED: a third-quarter 941 whose Medicare tax is not 2.9% of its wages | planted | 5 | 88/88 | 556 | PASS |
| 08 | PLANTED: two digits swapped in W-3 box 3 | planted | 2 | 87/87 | 472 | PASS |
| 09 | The second quarter is a scan with no text: must say it cannot read it | ugly | 5 | 73/73 | 583 | PASS |
| 10 | A 2025 fourth quarter instead of 2026: must leave it out and say why | ugly | 5 | 73/73 | 628 | PASS |
| 11 | First quarter filed under an old EIN; W-3 box h is blank | rules | 5 | 87/87 | 624 | PASS |
| 12 | A filled-in 2026 941-X for the second quarter: must add it in, and then agree | rules | 6 | 87/87 | 796 | PASS |
| 13 | A Form 944 (annual filer): must say this tool is for quarterly 941 filers | planted | 1 | 2/2 | 327 | PASS |
| 14 | A bank statement, not payroll forms: must refuse | planted | 1 | 2/2 | 293 | PASS |
| 15 | Four 941s but no W-3: must total the 941s and say there is nothing to compare | ugly | 4 | 63/63 | 601 | PASS |
| 16 | Provider switch with both providers' W-3s: must add them together and agree | ugly | 6 | 87/87 | 561 | PASS |
| 17 | Third-party sick pay: W-3 box 2 less box 14 must agree with line 3 | rules | 5 | 87/87 | 646 | PASS |

71 PDFs in all. Six ugly cases, five with planted errors (three planted in the data, two
files to refuse), five that test IRS rules.

For each case the checks cover:
- the year, EIN, status and the quarters found;
- every exception raised, and none extra;
- 14 lines read from each 941, and W-3 boxes 1 to 7;
- each reconciliation row's total, difference and verdict;
- the tax check;
- whether the STOP box appears.

Case 04 also checks that the tool names the quarters the difference equals. Case 07 checks
that it names the quarter that does not add up.

### What the planted errors were, and what the tool did

| Case | Planted | What the tool did |
|---|---|---|
| 04 | The new provider's W-3 leaves out January to June | "Does not agree." It said the W-3 leaves out the wages of quarters 1 and 2, every difference equals those quarters exactly, and to ask the earlier provider for its W-3. Given that W-3 (case 16), the year agrees. |
| 07 | A 941 whose Medicare tax is $90 more than 2.9% of its wages | Named quarter 3 and line 5c. The tax check differs by $90.01. |
| 08 | Two digits swapped in W-3 box 3 | Box 3 differs by $27,000.00. The W-3 also fails its own check: box 4 is not 6.2% of box 3. |
| 13 | A Form 944 | Refused: this is for quarterly 941 filers. |
| 14 | A bank statement | Refused: no 941 or W-3 in the file. |

## 2. Do the tests have teeth?

Eight broken copies of the tool, each wrong in one way an expert would care about. All eight
failed.

| Broken on purpose | Cases passed |
|---|---|
| Reads the printed line number as part of the amount (the first build's bug) | 2 of 17 |
| Leaves line 9 (uncollected tip tax) out of the tax check | 15 of 17 |
| Puts line 8 (third-party sick pay) into the tax check | 16 of 17 |
| Ignores W-3 box 14 | 16 of 17 |
| Ignores an amended 941-X | 16 of 17 |
| Uses only the first W-3 after a provider change | 16 of 17 |
| Says "agrees" when a quarter is under another EIN | 16 of 17 |
| Picks the first of two different 941s for a quarter | 16 of 17 |

## 3. Rebuild from the prompt alone

Each rebuild was written by a fresh AI session given only `REBUILD-PROMPT.md`, then run
through the same tests.

REBUILD_TABLE_PLACEHOLDER

## 4. Time against the manual baseline

| | By hand (estimate, see `MANUAL-BASELINE.md`) | The tool (measured) |
|---|---|---|
| One client, forms agree | about 20 minutes | under 1 second |
| One client, forms do not agree | about 30 minutes | under 1 second |
| All 15 cases with payroll forms | about 6 hours | about 10 seconds |

The by-hand figures are counted work multiplied by assumed rates; nobody has been timed.
The tool's figure is machine time only. Reading the result and acting on it still take
the accountant's time.

## 5. What was wrong along the way, and who found it

**The first test run passed 2 of 15 cases.** The IRS prints each line number just left of
the amount, and the tool read it as a digit: line 2's $50,513.80 became $250,513.80. The
W-3 boxes also picked up the value in the next box. Both were fixed by tightening the
column edges.

**Independent tax review** (a separate AI session given the IRS instructions, told to find
fault). It found four places where the rules did not follow the IRS text, all now fixed:
- box 1 is not one of the amounts the IRS compares, so a box 1 difference is now a note, not a mismatch;
- box 2 must be reduced by W-3 box 14 (income tax withheld on third-party sick pay) before comparing with line 3;
- the tax check should be W-3 boxes 4 and 6 plus the employer's share, against 941 lines 5e, 7 and 9;
- a 941-X for the same year belongs in the totals; the first build only flagged it.

It also found that the test model computed line 7 in a way that made the old tax check pass
by construction. It was rebuilt per the 941 instructions. And it judged case 11 wrong: amounts
that agree only when two EINs are combined still draw an IRS letter. Case 11 now expects
"does not agree". Three cases were added: two W-3s after a provider change, third-party sick
pay, and a filled-in 941-X.

**Cold-user check 1** (a fresh AI session playing a 60-year-old partner, working only from
screenshots):
- **Finding the cause:** she could finish, but it took about a minute to find the cause of
  a mismatch, at the end of a 180-word paragraph.
- **Risky advice:** the advice after a provider switch was to file W-2c and W-3c, which could
  have reported the same wages twice. It now says to ask the earlier provider for its W-3 first.
- **Layout:** the table's last columns were cut off, and the tax-check sentence put a number
  next to the wrong words.

**Cold-user check 2,** on the fixed version:
- **Acting on the screen:** she could act correctly in every step.
- **"Add it here":** there was no way to add a file without starting over. "Add another file" was added.
- **EIN case:** the headline contradicted a table that agreed. It now says "the amounts agree,
  but not every quarter was filed under the W-3's EIN".
- **EIN advice:** told her to fix the W-3 without first asking why the EIN differed.
- **Smaller fixes:** minus signs replaced with "lower on the W-3", each W-3 listed separately,
  dates beside the sign-off lines.

## 6. What it cannot do

See "Limits" in the folder README.

## 7. Not yet tested
- No practicing accountant has used it. `ACCOUNTANT-TEST-SCRIPT.md` is ready.
- No real provider's PDFs. The provider layout in the tests was drawn by us, using the IRS
  line wording. Real filed copies from Gusto, ADP, Paychex or QuickBooks Payroll may lay
  lines out differently. Testing one of each is the most important next step.
- Only Chromium. Firefox and Safari are untested. The running print header needs a recent
  Chrome or Edge.
- "Add another file" was tested by hand (five files, then the sixth: "agrees"). It is not in
  the automated test.
