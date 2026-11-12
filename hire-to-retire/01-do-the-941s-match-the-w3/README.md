# Hire-to-Retire, episode 01: Do the 941s match the W-3?

Version 1.0.0, 2026-11-12. Part of [Series 2: Hire-to-Retire](../README.md), which holds the
Stage 1 evidence and the value test this tool had to pass.

## The problem

Every January, for every payroll client, someone should check that the year's four Forms 941
agree with the W-3. The IRS General Instructions for Forms W-2 and W-3 (2026) say to reconcile
W-3 boxes 2, 3, 5 and 7 with the year's 941s, and to "retain your reconciliation information
in case you receive inquiries from the IRS or the SSA."

The IRS and SSA run that match themselves (Combined Annual Wage Reporting), about two years
later. A mismatch brings a Letter 99C. The employer has 45 days to answer, or the additional
tax in the letter is assessed.

The payroll provider files both forms, so they usually agree. They stop agreeing when
something changed during the year: a new provider, an amended quarter, a quarter under
another EIN, or payroll run by hand for a while.

## What it adds to what she already has

The provider files the forms. This tool proves they agree, from the filed PDFs themselves, and
produces the reconciliation the IRS says to keep. When they do not agree, it says by how much
and points at the likely cause. The most common cause is a W-3 that leaves out the quarters a
previous provider paid.

## How to use it

1. Open `agent/do-the-941s-match-the-w3.html` in any browser. It needs no installation and no internet.
2. Drop in the year's four 941s and the W-3 as PDFs, as separate files or as one year-end packet.
3. Read the verdict and "Check these first", type your name, and press "Print or save as PDF".
   The printout goes in the payroll file.

The files are read on your computer. Nothing is uploaded, stored or sent.

## What the reconciliation contains
- A one-sentence verdict: agrees, does not agree, not complete, or not reconciled.
- **Check these first.** Missing, duplicated or wrong-year quarters; scans it cannot read; a
  941 that does not add up; a W-3 that does not agree with itself; an EIN missing from W-3
  box h; an amended 941-X.
- **The reconciliation.** W-3 boxes 1, 2, 3, 5 and 7 against the four quarters, with the
  difference. If a difference equals one or more quarters exactly, it says which.
- **The tax check.** 941 lines 5e plus 7, against twice W-3 boxes 4 and 6 less the
  employee-only Additional Medicare Tax.
- **What I read from each 941.** Every figure, by quarter, with the file and page it came from.
- **Every page I was given,** and whether it was used.

## Limits

It does not:
- check the individual W-2s (wage base by employee, box 12 codes, 2% shareholder health
  insurance). That is a separate, planned episode;
- read scans or photos. A person can read them; this tool cannot;
- add a 941-X's corrections into a quarter. It flags the 941-X and says the difference
  should equal the correction;
- know about valid differences it cannot see: third-party sick pay (W-3 boxes 13 and 14),
  prior-year adjustments on a 941, or a successor employer's wages. When it flags a
  difference, the reason is yours to confirm;
- handle Form 944, 943, CT-1 or Schedule H filers, state forms, Form 940, or deposits against
  the IRS account;
- read a 941 or W-3 from a revision other than 2025 or 2026 with certainty. It reads the
  official IRS layout by column position, and provider layouts by their line labels.

## What is in this folder

| Path | What it is |
|---|---|
| `agent/do-the-941s-match-the-w3.html` | The tool. One file, works offline. |
| `agent/do-the-941s-match-the-w3.src.html` | The readable source. It loads its PDF reader from a CDN. |
| `agent/build.py` | Pastes the PDF reader into the source to make the offline file. |
| `tests/cases/` | 15 test cases, 60 PDFs. Invented employers; official IRS blank forms. |
| `tests/forms/` | The official blank IRS forms the test files are built from. |
| `tests/make_cases.py` | Builds the test files from a payroll model, and writes the answer key. |
| `tests/answer-key.json` | The answer key. |
| `tests/run-tests.js` | Runs any build of the tool against the key in a real browser. |
| `tests/RESULTS.md` | Results case by case, and what went wrong along the way. |
| `tests/MANUAL-BASELINE.md` | The same work by hand, with estimated minutes. |
| `ACCOUNTANT-TEST-SCRIPT.md` | A 25-minute script for testing with a real accountant. |
| `REBUILD-PROMPT.md` | One prompt that rebuilds the tool from nothing. |
| `article/` | The article, its images and the scripts that make them. |

## Run the tests

```bash
cd tools && npm install
```

```bash
cd hire-to-retire/01-do-the-941s-match-the-w3/tests && node run-tests.js
```

Pass another build's path to test it. Playwright with Chromium must be installed.

## Third-party code

The offline file contains [pdf.js](https://mozilla.github.io/pdf.js/) 3.11.174 (Mozilla
Foundation, Apache License 2.0), used to read the PDFs.
