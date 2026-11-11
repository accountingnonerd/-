# The $600 rule is gone. Who gets a 1099 this January?

*DRAFT for approval. Not published. Word count of the article body is at the end.*

In August 2022 an accountant asked a forum of tax professionals how to print a list of a client's 1099 vendors. A colleague answered: "No Easy way to print a list out. We print out the GL for the year or YTD and manually search the transactions for Vendors eligible for 1099's."

That search is about to be run again at every firm that keeps books for small businesses, and this time under a new number. This article is about a small tool that does the search, the tests it had to pass, and what it got wrong on the way. It is the first in a series: one painful accounting task per article, one working tool, and the prompt to rebuild it yourself.

## Why now

For payments made in 2026 the general reporting limit is $2,000, up from $600. The [IRS instructions](https://www.irs.gov/instructions/i1099mec), dated 12/2026, say the threshold "increased to $2,000 and may be adjusted for inflation beginning in calendar year 2027." The IRS expects the change to matter: it projects Forms 1099-NEC falling from 68.9 million in 2026 to 56.7 million in 2027 ([Publication 6961](https://www.irs.gov/pub/irs-pdf/p6961.pdf)).

The $600 figure is in every preparer's head and in many checklists. Getting it wrong costs $60 to $340 per form for returns due in 2027, and $690 for intentional disregard ([IRS](https://www.irs.gov/payments/information-return-penalties)).

## How common is the pain

Practitioners say it plainly. Asked what they use to file 1099s, one CPA replied: "Track1099, and we try not to do them in the first place." Another: "I got out of the 1099 business when the NEC was resurrected." A third described the volume: "12 or so clients that we do them for but some clients have 40 or more 1099's" ([thread](https://accountants.intuit.com/community/lacerte-tax-discussions/discussion/who-is-everyone-using-for-thier-1099-filings/00/277504)).

Bookkeeping software has a 1099 report. It depends on someone having flagged each vendor during the year. The first accountant's follow-up in [that 2022 thread](https://accountants.intuit.com/community/easyacct-discussions/discussion/how-to-print-1099-vendor-list/00/229893) describes the result: they print a year of vendor history and review it by eye.

## What the tool does

It is one web page. The accountant drops in the client's payments for the year, as exported from the bookkeeping program. A worksheet comes back: who gets a 1099 and on which form, who is probably exempt, who needs her judgment, who is close to the limit, and the reason for every vendor. She types her name, ticks the W-9 boxes and prints it.

The page contains no live AI. An AI model wrote it; what runs is ordinary code on her own computer, and the file is not uploaded anywhere. The same file always gives the same answer.

### One worked example

Larkspur Cafe is an invented client with 15 payment lines. Three of them read:

| Date | Payee | Amount |
|---|---|---|
| 1/14/2026 | Rivera Plumbing LLC | $700.00 |
| 4/22/2026 | RIVERA PLUMBING | $800.00 |
| 10/6/2026 | Rivera Plumbing, L.L.C. | $900.00 |

Before: three vendors, each far below $2,000, none on anyone's 1099 list.

After: one vendor, $2,400.00, Form 1099-NEC, with the note "Combined spellings" and the three source rows.

The same file pays "Mike Chen" $1,100 and "Mike Chen Electric" $1,200. The tool does not merge those. It puts both under "Needs your judgment" and says that together they come to $2,300. It leaves "Smith Electric" and "Smith Roofing" alone.

## What the tests showed

We wrote the test before the tool: 15 files, 510 payment lines, 99 vendors, with every expected answer worked out by hand from the IRS instructions. Two files should be refused outright. All company names are invented.

The final build passes all 15 files and all 476 individual checks. Each file takes under a quarter of a second. By our estimate the same files take about two hours by hand. That figure is line counts multiplied by assumed reading speeds. No accountant has been timed yet.

Errors we planted that it caught:

- a $1,200 check entered twice, which pushed a carpenter over the limit;
- a vendor subtotal of $4,300 over lines that add to $3,100, which produces a red STOP box;
- three December 2025 payments in a 2026 file;
- a line whose amount reads "see note".

What it got wrong, and who caught it:

- **The answer key.** We asked a separate AI session, acting as a skeptical tax reviewer, to check our hand-worked answers against the IRS text. It marked 8 of 88 as debatable and found a wrong box number: on the 2026 form, nonemployee compensation is box 1a, not box 1.
- **Names.** Our own probing found the tool calling "Tri-County Law Enforcement Supply" a law firm. It also waved through $240 of royalties, which are reportable from $10.
- **Bills.** A QuickBooks vendor report can list a bill and also the payment of that bill. The first build would have counted both. A reviewer playing a 60-year-old partner raised it; test file 15 now covers it.
- **The screen.** The same reviewer found the list of who gets a 1099 below the fold, signature lines that looked typeable and were not, and a nine-page printout. All three were fixed, and a second cold review found seven more problems, which were fixed too.

## Limits

It is a first pass for an accountant to review. It has not seen any W-9, so it cannot know that an LLC is taxed as a corporation. It does not check taxpayer ID numbers, state rules, or backup withholding. It does not cover Forms 1099-INT, 1099-DIV, 1099-K or 1042-S. It refuses 2027 files because the 2027 limit is not yet known. It judges what a payment was for from the account it was coded to and the vendor's name, so a contractor coded to Supplies lands in "No 1099". It reads Excel and CSV, not PDFs.

It also takes positions the IRS text does not spell out. Zelle counts like a check. PayPal and Venmo do not, but a vendor they would tip over the limit goes to judgment.

No practicing accountant has used it yet. That test is next.

## Rebuild it yourself

The prompt below rebuilds the tool. REBUILD_RESULT_PLACEHOLDER "The same agent" here means a page that passes the same tests, not one with identical code.

Repository: REPO_LINK_PLACEHOLDER

## Your turn

What is the most tedious task you will do by hand this season? Reply with the task, the document it starts from, and how many minutes it takes. The next tool in this series comes from those replies.

---

## Appendix: the rebuild prompt, in full

PROMPT_PLACEHOLDER
