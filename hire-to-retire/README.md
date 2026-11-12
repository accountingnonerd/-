# Series 2: Hire-to-Retire (payroll)

Everything from paying people to the year-end forms that report what was paid and withheld.

```
Payroll run  ->  Tax deposits  ->  Quarterly 941  ->  Year end: W-2s and W-3  ->  Payroll on the books
```

## Episodes

| No. | Tool | Step | What it adds to what she already has | Version | Date |
|---|---|---|---|---|---|
| 01 | [Do the 941s match the W-3?](01-do-the-941s-match-the-w3/) | Year end | Reads the filed PDFs and produces the 941-to-W-3 reconciliation the IRS tells employers to keep, with every difference explained or flagged. | 1.0.0 | 2026-11-12 |

## Stage 1: how episode 01 was chosen

### Evidence
- **The rule.** The IRS General Instructions for Forms W-2 and W-3 (2026) say: "Reconcile the
  amounts shown in boxes 2, 3, 5, and 7 from all 2026 Forms W-3 with their respective amounts
  from the 2026 yearly totals from the quarterly Forms 941". The 941 tax amounts "should be
  approximately twice the amounts shown on Form W-3". The instructions also say: "Retain your
  reconciliation information in case you receive inquiries from the IRS or the SSA."
  ([IRS](https://www.irs.gov/instructions/iw2w3))
- **The cost of not doing it.** The IRS and SSA run Combined Annual Wage Reporting, a matching
  program that "compares the Federal Income Tax (FIT) withheld, Medicare wages, Social
  Security wages, and Social Security tips reported to the IRS on the Forms 94X ... against the
  amounts reported to SSA via the processed totals of the Forms W-2". Cases are reviewed about
  two years later ("during 2026 IRS is analyzing tax year 2024"). The employer gets a
  Letter 99C and has 45 days to answer. Otherwise "the employer will be subject to the
  additional tax increase outlined in the correspondence."
  ([IRS](https://www.irs.gov/businesses/small-businesses-self-employed/combined-annual-wage-reporting-employment-tax-problem-inquiries))
- **It happens in practice.** QuickBooks community thread:
  ["941 does not agree to W3"](https://quickbooks.intuit.com/community/employees-and-payroll-2/941-does-not-agree-to-w3-742).
  The usual causes are a provider switch mid-year, an amended 941, a quarter filed under
  another EIN, and payroll run by hand for part of the year.

### Candidates considered

| Candidate | Who, how often | By hand | Error cost | Why software has not solved it | Verdict |
|---|---|---|---|---|---|
| **Four 941s against the W-3** | Every payroll client, each January | 20 to 40 min per client (estimate) | Letter 99C two years later; tax, penalties, interest | Providers file both, but the proof is left to the accountant, and fails when anything changed mid-year | **Chosen** |
| Payroll provider's annual report against the general ledger | Every payroll client, year end | 30 to 60 min (estimate) | Wrong wages on the business return | Two different inputs (provider report and ledger). Belongs with Record-to-Report | Later |
| W-2 review before filing (wage base, 2% shareholder health insurance in box 1, box 5 at least box 3 plus box 7) | Every payroll client, December and January | 15 to 30 min (estimate) | W-2c corrections, lost health insurance deduction for S corporation owners | Needs to know who the 2% shareholders are, which is not in the provider's export | Episode 02 candidate |

### What a top payroll practitioner would insist on
- **Read what was filed.** Read the PDFs the provider filed, not a summary someone retyped.
- **Name the line and box behind every figure:** the file, the page, the quarter and the 941 line.
- **Explain the expected differences.** The tax check is "approximately twice", not equal:
  rounding, the employee-only Additional Medicare Tax, and line 7 fractions of cents.
- **Never let a missing, duplicated or wrong-year quarter pass silently.**
- **Turn a difference into a next step:** W-2c and W-3c, or 941-X.
- **Produce something to keep.** It is the document the IRS says to retain.

### Value test
1. **She already has:** a payroll provider that files the 941s and the W-2s and W-3.
2. **Left by hand:** proving the two agree, and keeping the proof. Above all, when the client
   changed providers, amended a quarter, or ran some payroll by hand.
3. **Input she has:** the PDFs of the filed forms, separate or as one year-end packet.
4. **Output where she works:** a signed reconciliation for the payroll file, ready to send
   with a Letter 99C reply.
5. **If everything is set up perfectly:** it ties, and she still gets the retained
   reconciliation in a minute instead of half an hour. The tool earns most of its keep when
   something changed during the year.
