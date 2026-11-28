# Sample: Mapleton Landscaping LLC (invented)

Use these files to try the tool, or to check a version you rebuilt from the prompt, before you use a
real client's files. Everything here is made up: the business, the customers, the vendors, the
amounts.

| File | What it is |
|---|---|
| `mapleton-checking-bank-download-q1-2026.csv` | The bank's download for the checking account, January 1 to March 31, 2026: date, description, amount, running balance. 62 lines. |
| `mapleton-general-ledger.xlsx` | The client's general ledger, as QuickBooks Online exports it (Reports, General Ledger, Export to Excel), July 1, 2025 to April 20, 2026. One account, Checking. |

## What you should see

**Step 1. Give the two files.** Drop the CSV in the box "The bank's download" and the ledger in "The books' ledger". The
line at the top reads:

> Mapleton Landscaping LLC, Checking, 3/31/2026. Not finished: 2 items to decide before it can be
> called reconciled.

and under it: 57 bank lines matched of 62; 6 items outstanding; 5 bank items not in the books; 2
entries that look wrong.

**Step 2. Check what was read.** Compare with the statement:
- statement 1/1/2026 to 3/31/2026;
- beginning balance $81,868.88, ending balance $108,730.18 (both from the file);
- the bank account in the books: Checking;
- books' balance the day before 1/1/2026, $77,821.42; books' balance on 3/31/2026, $113,641.41.

They are right, so press "This is right: go to step 3".

**Step 3a. Two book entries that look wrong.** The page decides neither of them.

| What it found | In the books | At the bank | A reasonable decision |
|---|---|---|---|
| Same check number, different amount | 2/10/2026, #1033 Coastal Insurance, -$683.50 | 2/15/2026, CHECK 1033, -$638.50 | **Books wrong: correct them.** The bank paid what was written on the check; the books swapped two digits. |
| Entered twice? | 3/4/2026 and 3/6/2026, Birch Dental Group, $4,120.00 each | once, matched to the 3/4/2026 entry | **Entered twice: remove one.** One payment, recorded twice. |

Once both are decided, the top line already reads "It ties: adjusted bank and adjusted books are both
$109,509.83. Still to decide: 1 stale check (step 3c)." The counts drop too (5 bank items to 4, 6
outstanding to 4): each pair that was counted on both sides is now one item.

**Step 3b. Four bank items not in the books.** The page suggests a treatment from each description:
three monthly service fees of $25.00 (bank service charge) and $18.42 of interest (interest income).
They are right; change nothing.

**Step 3c. Outstanding.** Check #998 to Greenfield Tools, $415.00, dated 8/14/2025, is 229 days old:
stale-dated. Choose **Keep outstanding** and ask the client whether the payee received it. (If you
choose "Reverse to a liability" instead, the check leaves the outstanding total, the books go up by
the same $415.00, and an entry to a liability account is added. It still ties.)

Also listed, nothing to decide: checks #1031 ($1,423.00) and #1032 ($568.75) from the last week of
March, and a deposit of $3,186.40 from Granite Schools on 3/31/2026, in transit. The card sales of
2/21 to 2/23 are shown matched to the one bank deposit of $766.55 on 2/24 that adds them up.

**Step 4. The reconciliation.** The line at the top now reads:

> Mapleton Landscaping LLC, Checking, 3/31/2026. It ties: adjusted bank and adjusted books are both
> $109,509.83.

| | |
|---|---|
| Balance per bank statement, 3/31/2026 | $108,730.18 |
| Add: deposits in transit (1) | $3,186.40 |
| Less: outstanding checks and payments (3) | -$2,406.75 |
| **Adjusted bank balance** | **$109,509.83** |
| Balance per books, 3/31/2026 | $113,641.41 |
| Add or less: bank items not in the books (4) | -$56.58 |
| Add or less: corrections of book entries | -$4,075.00 |
| **Adjusted book balance** | **$109,509.83** |
| Difference | $0.00: reconciled |

The corrections are the check (+$45.00) and the duplicate deposit (-$4,120.00). Below the proof:
four entries dated 3/31/2026 (three bank charges, the interest), the two corrections to make in the
books, and one question for the client about check #998.

If your rebuilt tool shows the same, it works. If it does not, see "If it does not work" in the
episode's README.
