# Rebuild 1: notes

Built only from `PROMPT-as-given.txt`. I did not open the answer key, the case files, `make_cases.py`, `rules.py`, `sample/README.md`, any `agent/` folder or the scratchpad. I read `run-tests.js` to see how it drives the page. Before the first run I checked the page only on its own built-in sample.

## Scores

| Run | Cases | Checks |
|---|---|---|
| first-run.txt | **22 / 27** | **824 / 833** |
| second-run.txt (after 1 round of fixes) | 27 / 27 | 833 / 833 |
| final-run.txt, RESULTS.md | 27 / 27 | 833 / 833 |

One round of fixes was enough. A third run was not needed.

## Failures on the first run

| Case | Failed checks |
|---|---|
| 03 Xero, summary block, three accounts | raises nothing else (got `LATE_ITEMS`); lateItems expected 0, got 1 |
| 08 books start on the bank's first day | the same two checks |
| 24 two old $100 checks, ticked | the same two checks |
| 25 like 08, one line ticked | the same two checks |
| 19 check paid twice, voided check paid | book entries that look wrong: the "paid twice" item had bookDate `2026-01-05`, expected `null` |

## Fix 1: book checks flagged as "late payment" (cases 03, 08, 24, 25)

What I built: every outstanding item over 10 days that was not stale or old got flagged late. That included a book check 11 to 90 days old.

What the specification says:

> "A book check over 180 days is stale (UCC 4-404); over 90, old. Anything else outstanding over 10 days is a late deposit (money in) or late payment."

and, in the messages:

> "LATE_ITEMS (care): deposits or electronic payments not at the bank after 10 days"

Fix: an item can be flagged late only if it is **not a book check**.

Cause: **the specification is unclear, and I misread it.** Read literally, "anything else" means anything not flagged so far, and that includes a check 11 to 90 days old. The intended meaning (anything that is not a book check) shows only in the LATE_ITEMS wording ("deposits or electronic payments"). An accountant would also know that a check outstanding for 30 days is normal. Rewording the line to "Any other outstanding item that is not a book check, over 10 days, is ..." would prevent this.

## Fix 2: "paid twice" has no book line (case 19)

What I built: I gave the "paid twice" near miss the book line that the first payment of the check had matched, and reported that line's date as bookDate.

What the specification says:

> "Otherwise, if that check number was already matched or paired: near miss "paid twice"."

and, in the report:

> "near [{id, kind, decision, bankDate, bankAmount, bankDesc, bookDate, bookAmount (null for voided but paid and paid twice), num, name, type}]"

Fix: for "paid twice", bookDate (and name and type) are null, and num is the bank line's check number.

Cause: **the specification is incomplete.** Every other near miss names its book line: "with the first of them" for a different amount, "a voided book line with that num" for voided but paid. "Paid twice" names none. The report section says bookAmount is null for "paid twice" but says nothing about bookDate. The same section also makes bookAmount null for "voided but paid", which does have a book line (and the expected output does give it a bookDate). So bookAmount being null was not a reliable sign that there is no book line. I had to guess, and guessed wrong.

## Places I had to guess that the tests passed (still gaps)

These did not fail, but the specification left them open or, read literally, gave the wrong answer:

1. **Book lines of "voided but paid" and "paid twice" in the outstanding list.** Step 9 says outstanding includes "the undecided or "not" near misses' and entries' book lines". Read literally, that puts a $0 voided line in the list, and for "paid twice" it adds a line that is already matched (double counting it and breaking the proof). I left both out.
2. **Reversed stale check, sign.** "its amount is added to the book corrections". The check's amount is negative, so adding it moves the books the wrong way. The correct effect is minus the amount: the books go up by the check, and case 27 confirms this ("the books go up by the same $415.00"). The wording is wrong as written.
3. **The undecided decision value** for `near` and `duplicates`. The report section gives "undecided" only for outstanding stale checks. I used "undecided" for these too (null would also have been a reasonable reading).
4. **`accounts`** ("accounts (names)"): all accounts read, sub-accounts included, or only the accounts listed in the select? I used all the accounts kept, in the order read.
5. **Order of the start modes.** "Candidates add up to R all together" and "no candidates and R is not 0" are listed with the no-candidates case last, but it has to be tested before the "20 candidates or fewer" search. The order is implied, not stated.
6. **startLeft when the beginning balance is unknown**: null or 0? Not stated. I used null.
7. **BANK_FILE_GAPS**: "The first day where it fails is a gap ... carry on". Is every later failing day also a gap, or only the first? I recorded all of them.
8. **BALANCES_DISAGREE when one balance is typed and the other comes from the file.** The text says "(from the file, or both typed)". I checked whenever both balances are known and the ending was not worked out from the beginning.
9. **Messages after a decision.** It is not said whether CHECK_AMOUNT_DIFFERS, START_AMBIGUOUS, START_BANK_LINES and similar messages stay once she has decided or ticked. I kept them, since the thing was still found.
10. **CARD_NOT_SUPPORTED**: "show only that message". I took this to mean no ACCOUNT_CHOSEN either, and left the rest of the reconciliation out of the report.
11. **Stop screens.** With BALANCES_DISAGREE caused by typed balances, "nothing below Check these first" would hide the boxes she needs to correct them. I kept step 2 visible in that case. The specification does not address this.
12. **Description column "if it would be the date column, none".** With exact heading matching this cannot happen. Either substring matching was meant somewhere, or the clause is dead.
13. **The "as of" date** may be in the same cell as "Ending balance as of" or in the next cell. I handled both. Not stated.
14. **Excel serials held as text in a CSV** (raw:true keeps every cell as a string). Only a number counts as a serial. I left text serials as not a date.
15. **Bank lines after the statement end date**, if she types an end date earlier than the last line: nothing says to leave them out. I kept them all.
16. **3c wording** says "Which of these checks from before [start]", but step 7's candidates also include non-check items dated 10 days or fewer before the start.
17. **Step 4's tick**: the tick rules cover steps 2 and 3 only. I ticked step 4 after Print was pressed.
18. **Bank-only lines that belong to an undecided near miss**: they get a treatment select, but should they produce journal entries? I made no entry for them (they await the decision in 3a).
19. **Rule 1 "the first of them"**: first in book order, not nearest in days. I took it literally. Nothing says whether rule 1 has a date window. I used none.
20. **Books file given alone** (before the bank file): only the bank-only case is described. I wait for the bank file.

## Suggestions to improve the specification

1. Step 9: write "Any outstanding item that is **not a book check** and is over 10 days old is a late deposit (money in) or late payment."
2. Rule 1 "paid twice": say "(no book line: bookDate, name and type are null; num is the bank's check number)". In the report, write "bookDate null for paid twice".
3. Step 9: say which near-miss book lines become outstanding ("check amount differs, transposed, sign and entered twice; not voided but paid, which is $0, nor paid twice, which has none").
4. Step 9: change "its amount is added to the book corrections" to "the book corrections change by minus its amount (the books go up by the check)".
5. Report: give the undecided value for `near[].decision` and `duplicates[].decision` ("undecided").
6. Report: define `accounts` ("every account kept, sub-accounts included, in file order").
7. Step 7: list the modes in the order they are tested, with the no-candidates case before "20 candidates or fewer".
8. State the value of startLeft and startDifference when mode is "unknown".
9. Step 7 of the bank reading: say whether every failing day is a gap or only the first.
10. Say whether the "kind found" messages and START_* stay raised after she decides or ticks.
11. Say what the page shows on a stop caused by balances she typed (the step 2 boxes must stay reachable).
12. Remove or explain the description-equals-date-column clause, or say where substring matching applies.
13. Say whether the "as of" date can be in the next cell, and whether a CSV text serial is a date.
14. Say what happens to bank lines dated after a typed statement end date.
15. Say when step 4 gets its tick.
16. Small: the 3c prompt says "checks" while the candidates include other items within 10 days; "Reply with the whole file in a single code block" is fine for a chat request but should not be the only delivery instruction for a build that is tested from disk.

## Follow-up (by the requester, after this rebuild)

The rebuild was made from `PROMPT-as-given.txt`, a frozen copy. Afterwards the master `PROMPT.txt` was
changed to close the gaps listed above: late items exclude book checks; what "paid twice" and "voided
but paid" report; their book lines are not outstanding; the sign of a reversed stale check; "undecided"
as the starting decision; what `accounts` holds; the order of the start modes and null values when the
beginning balance is unknown; only the first gap; when BALANCES_DISAGREE applies; messages stay after a
decision; no tick for step 4; the books file waits for the bank file; all bank lines count whatever the
end date. One gap was a fault in the tool itself: balances typed wrong stopped the page and hid the
boxes to correct them. That is fixed and tested (case 28, added after this run; this build has 27 cases
in its results).
