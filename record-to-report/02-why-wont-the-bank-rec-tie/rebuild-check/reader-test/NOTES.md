# Reader test: "Build it yourself", followed as an accountant who has never seen the tool

Date: 2026-11-28. Persona: a good accountant, not technical, new to the tool. I followed the article's
section "Build it yourself" step by step, using only the article and the public GitHub repository,
fetched while logged out. I played the AI assistant for steps 2 to 4.

**Result: a reader who follows the article gets exactly what it promises.** The page I generated
from PROMPT.txt worked on the first try. Every figure and line in the article and in the sample
README matched, and no fix was needed, so there is no `after-one-fix.html`. The hesitations are
about finding things (links, the repository's front page) and a few statements that do not match
what the screen shows in between.

## Sources used

| Source | How |
|---|---|
| Article text | `br-article.txt` (text extracted from the PDF), given to me |
| Article PDF | `pdf/article.pdf`, fetched from `raw.githubusercontent.com/.../article/why-wont-the-bank-rec-tie-article.pdf`. I used it only to check the link targets and the characters the text extraction lost |
| Master prompt | `fetched/PROMPT.txt` (34,050 bytes, 34,046 characters) from `raw.githubusercontent.com/accountingnonerd/-/main/record-to-report/02-why-wont-the-bank-rec-tie/PROMPT.txt` |
| Episode README | `fetched/agent-README.md` |
| Sample README | `fetched/sample-README.md` |
| Sample files | `downloads/mapleton-checking-bank-download-q1-2026.csv`, `downloads/mapleton-general-ledger.xlsx` (raw downloads, HTTP 200) |
| Repository front page, Record-to-Report README, LinkedIn post text | `fetched/repo-README.md`, `fetched/rtr-README.md`, `fetched/LINKEDIN-POST.txt` |
| GitHub file pages | Opened logged out with Playwright to check that the buttons the article names exist |

**The stand-in I needed:** this sandbox blocks `cdnjs.cloudflare.com`. Playwright's `page.route`
served `/home/user/one-painful-problem/tools/node_modules/xlsx/dist/xlsx.full.min.js` (SheetJS 0.18.5,
the same version the prompt names) at the prompt's exact cdnjs URL. I read nothing else in the local
checkout.

**Note on the text file:** `br-article.txt` lost the list numbers (1. to 6.), several colons
("Series 2, Agent 1: a free tool", "save as a PDF:") and the "(" before "The ready-made tool in the
repository works offline.)". The PDF has all of them. This is a problem with the extraction, not
with the article.

## Do the GitHub prompt and the article agree?

They agree. Every on-screen text that the article quotes is in PROMPT.txt word for word:

| Article quotes | PROMPT.txt |
|---|---|
| "Why won't the bank rec tie?" and two boxes | title; box 1 "The bank's download", box 2 "The books' ledger" |
| "Not finished: 2 items to decide before it can be called reconciled." | "Not finished: N items to decide before it can be called reconciled." |
| press "This is right" | button "This is right: go to step 3" |
| "Books wrong: correct them" | check amount differs, `fix` |
| "Entered twice: remove one" | entered twice, `fix` |
| keep the stale check outstanding | "Keep outstanding" |
| "It ties: adjusted bank and adjusted books are both $109,509.83." | "It ties: adjusted bank and adjusted books are both $X." |
| print or save as a PDF | button "Print or save as PDF" |
| loads its spreadsheet reader from the internet | `<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/...">` |

Where they differ:

1. **"It ties" with a decision still open.** Page 5 says: "Now it never says 'ties' while anything
   is undecided or unexplained." The prompt says: "A stale check not yet decided does not stop the
   tie; it is listed as still to decide." The page then reads "It ties: ... Still to decide: 1 stale
   check (step 3c)." I saw exactly that after step 3a, before step 3c.
2. **Size of the prompt.** The article says "about 33,000 characters". It is 34,046.
3. **How matching works.** The article says "then the same amount within a few days". The prompt
   looks from 60 days before (180 days for checks) to 5 days after. This is a simplification and
   harmless.

The PDF's links are correct. Page 6 links to PROMPT.txt. Page 7 links to the CSV, the xlsx and
`sample/README.md`. Page 8 links to the episode folder and PROMPT.txt.

## Step by step

### What you need
- Worked. One hesitation: "The reply is long (about 1,000 lines)". Mine was 1,272 lines, which is
  close enough.

### Step 1: "Copy the prompt"
> "The repository's name is a single hyphen, so the address ends in "/-", and that is right. Open
> PROMPT.txt and press the "Copy raw file" button (two small squares, top right of the file)."

- In the PDF, "Open PROMPT.txt" is a link, so this works when you read the PDF directly.
- **Hesitation: links on LinkedIn.** As far as I know, links inside a PDF posted as a LinkedIn
  document cannot be clicked. A reader on LinkedIn then has three options:
  - the folder link in the post text, which LINKEDIN-POST.txt does include;
  - the typed address on page 8, two pages after this step;
  - the front page of the repository.
- **Hesitation: the typed address breaks across lines** at "02-why-wont-" / "the-bank-rec-tie". A
  reader cannot tell whether that hyphen belongs to the address or was added by the line break. Here
  it belongs to the address.
- **Hesitation: "the address ends in '/-'".** That is true of the repository's address. The
  PROMPT.txt address contains "/-/" in the middle and ends in "PROMPT.txt". A reader comparing
  addresses may think the one in front of them is wrong.
- **Hesitation: the repository's front page does not list this tool.**
  `github.com/accountingnonerd/-` (README.md) shows only the Series 1 table, with no Series 2 and no
  "Why won't the bank rec tie?". `record-to-report/README.md` lists episode 02 as "not yet
  published". A reader who arrives at the front page has to guess to go into record-to-report, then
  02-why-wont-the-bank-rec-tie.
- The buttons exist when logged out. On each file page I found `copy-raw-button` with the tooltip
  "Copy raw file" and `download-raw-button` with the tooltip "Download raw file", next to "Raw". The
  "Copy path" button at the top left uses a similar copy icon, so "top right" matters. It would be
  safer to say "next to Raw".

### Step 2: "Paste it into a new chat ... and send it"
- Worked. A paste of 34,000 characters in claude.ai usually appears as an attached "pasted text"
  block, not as text in the message box. A first-time reader may think the paste went wrong. The
  article could say that this is normal.

### Step 3: "Wait for one long block of code"
- Worked: one block of 1,272 lines. No hesitation.

### Step 4: "Save it as a web page"
- Worked: saved as `first-generated.html`. The Notepad and TextEdit instructions are clear.

### Step 5: "Open it"
> "You should see "Why won't the bank rec tie?" and two boxes to drop files into."

- Seen exactly: the tab title and the heading, and two boxes. Screenshot: `step5-open.png`.
- This only worked because I served SheetJS locally. Without it, behind a firewall, my build showed
  "The page could not load its spreadsheet reader ..." (`extra-no-reader.png`). The prompt does not
  require that message, so another assistant's build may do nothing at all. That is the case the
  article's "Nothing happens when you drop a file" advice covers. The advice is right.

### Step 6: "Try it on the sample client"
> "Download the Mapleton bank download and the Mapleton ledger. On each page, press "Download raw
> file". Drop the bank file in box 1 and the ledger in box 2"

- The step gives no file names or paths in the text; it relies on the PDF links. On LinkedIn (see
  step 1), the reader has to find `sample/` in the folder. "Download raw file" exists on both the CSV
  page and the xlsx page.
- **Hesitation: "box 1" and "box 2".** The prompt calls them box 1 and box 2, but it only fixes the
  labels "The bank's download" and "The books' ledger". My build numbered them; another build may
  not. Naming the boxes ("the box 'The bank's download'") is safer.
- After both files: the top line matched exactly. Step 2 balances matched. "This is right" worked.
  In 3a, "Books wrong: correct them" (#1033) and "Entered twice: remove one" (Birch Dental) worked.
- **Hesitation: the screen says "It ties" before step 3c.** After the two decisions in 3a, the top
  line already read "It ties: adjusted bank and adjusted books are both $109,509.83. Still to decide:
  1 stale check (step 3c)." The article skips this in-between state. Together with the page 5 claim,
  a reader may wonder whether something is wrong, or stop there.
- **Hesitation: 3b is not mentioned.** "What you should see" goes from 3a to 3c, so a reader does not
  know whether to touch 3b. The sample README says the suggestions are right. Nothing needs to
  change.
- In 3c, "Keep outstanding" for #998 worked. The final top line matched exactly. Screenshots:
  `step6-final-top.png` (the top line) and `step6-final.png` (the proof in step 4). The full page is
  `first-final-fullpage.png` and the print view is `first-print-view.png`.
- I also tried the README's alternative, "Reverse to a liability". The check leaves the outstanding
  list and the books go up by $415.00. AJE 5 is Dr Checking, Cr Outstanding checks payable
  (unclaimed property). It still ties, at $109,924.83. The README does not give that figure.

## Expected vs seen

Source A = article, S = sample README. Seen = my build from PROMPT.txt, run on the downloaded
sample files.

| # | Src | Expected | Seen | OK |
|---|---|---|---|---|
| 1 | A | 62 bank lines for the quarter | 62 lines from 1/1/2026 | yes |
| 2 | A | about a hundred entries in the books | 101 entries in Checking (1 after the statement date) | yes |
| 3 | A | #1033 entered $683.50, paid $638.50 | 2/10/2026 #1033 Coastal Insurance -$683.50 / 2/15/2026 CHECK 1033 -$638.50 | yes |
| 4 | A | $4,120.00 entered twice, two days apart | Birch Dental Group 3/4/2026 and 3/6/2026, $4,120.00 each | yes |
| 5 | A, S | three card sales = one deposit of $766.55 | 2/21 $189.60 + 2/22 $362.15 + 2/23 $214.80 = $766.55 on 2/24/2026 | yes |
| 6 | A | three monthly service fees and a little interest | 3 x -$25.00, +$18.42 | yes |
| 7 | A | $415.00 check from last August | #998 Greenfield Tools, 8/14/2025, -$415.00 | yes |
| 8 | A, S | first top line: "Mapleton Landscaping LLC, Checking, 3/31/2026. Not finished: 2 items to decide before it can be called reconciled." | identical | yes |
| 9 | S | 57 bank lines matched of 62; 6 items outstanding; 5 bank items not in the books; 2 entries that look wrong | identical | yes |
| 10 | S | statement 1/1/2026 to 3/31/2026 | 1/1/2026 to 3/31/2026 (end date: the last line's date) | yes |
| 11 | A, S | beginning $81,868.88, ending $108,730.18, both from the file | $81,868.88 (from the file), $108,730.18 (from the file) | yes |
| 12 | S | bank account in the books: Checking | Checking | yes |
| 13 | S | books the day before 1/1/2026: $77,821.42 | $77,821.42 | yes |
| 14 | S | books on 3/31/2026: $113,641.41 | $113,641.41 | yes |
| 15 | S | 3a: 2/10/2026 #1033 Coastal Insurance -$683.50 vs 2/15/2026 CHECK 1033 -$638.50 | identical, effect +$45.00 | yes |
| 16 | S | 3a: 3/4 and 3/6/2026 Birch Dental $4,120.00 each, bank once, matched to 3/4 | identical, effect -$4,120.00 | yes |
| 17 | S | 3b: "Four bank items": 3 x $25.00 bank service charge, $18.42 interest income | 4 after the 3a decisions (5 before: CHECK 1033 is there until decided); suggestions as stated | yes, see note |
| 18 | S | 3c: #998, $415.00, 8/14/2025, 229 days, stale-dated | identical | yes |
| 19 | S | also #1031 $1,423.00, #1032 $568.75, Granite Schools $3,186.40 on 3/31/2026 | identical (before 3a, the #1033 book entry and the 3/6 Birch deposit, flagged "not at the bank after 10 days", are also listed) | yes, see note |
| 20 | A, S | final top line: "... It ties: adjusted bank and adjusted books are both $109,509.83." | identical | yes |
| 21 | S | Balance per bank statement, 3/31/2026: $108,730.18 | $108,730.18 | yes |
| 22 | S | Add: deposits in transit (1): $3,186.40 | $3,186.40 (1) | yes |
| 23 | S | Less: outstanding checks and payments (3): -$2,406.75 | -$2,406.75 (3) | yes |
| 24 | A, S | Adjusted bank balance $109,509.83 | $109,509.83 | yes |
| 25 | S | Balance per books, 3/31/2026: $113,641.41 | $113,641.41 | yes |
| 26 | S | Bank items not in the books (4): -$56.58 | -$56.58 (4) | yes |
| 27 | S | Corrections of book entries: -$4,075.00 (+$45.00 and -$4,120.00) | -$4,075.00 | yes |
| 28 | A, S | Adjusted book balance $109,509.83 | $109,509.83 | yes |
| 29 | S | Difference "$0.00: reconciled" | "$0.00: reconciled" | yes |
| 30 | S | four entries dated 3/31/2026 (three bank charges, the interest) | AJE 1 to 3 Dr Bank service charges / Cr Checking $25.00; AJE 4 Dr Checking / Cr Interest income $18.42 | yes |
| 31 | S | two corrections to make in the books | #1033 from -$683.50 to -$638.50; Birch Dental 3/6/2026 entered twice, delete or void | yes |
| 32 | A, S | one question: did the payee of #998 receive it? | "Check #998 to Greenfield Tools, $415.00, dated 8/14/2025, has not cleared after 229 days: did the payee receive it?" | yes |
| 33 | S | Reverse instead: leaves outstanding, books +$415.00, liability entry, still ties | yes; ties at $109,924.83 | yes |

No figure differs. The two notes are about counts that change on screen and that the README does not
explain (row 17: 5 bank items before 3a, 4 after; row 19: 6 outstanding before 3a, 4 after).

## Bugs and fixes

None in the build: no page errors and no console errors. No fix was needed, so there is no
`after-one-fix.html`.

Things that are quirks of my build, not problems with the article or the prompt:
- the line "You are looking at step N" depends on where the page is scrolled;
- the BANK_ONLY message stays labelled "Decide." after you accept the suggestions, which is what the
  prompt says to do.

At phone width (390 px) there is no sideways scroll (`first-phone.png`).

## Suggestions, most important first

1. **Make the links work for a LinkedIn reader.**
   - Links in a PDF document post are, as far as I know, not clickable on LinkedIn.
   - In step 1, say "use the link in the post (or in the first comment), then open PROMPT.txt".
   - In step 6, name the folder: "open the sample folder, then each file".
   - Print the folder address once, unbroken. Avoid the break at "02-why-wont-" / "the-bank-rec-tie",
     where a reader cannot tell whether the hyphen belongs to the address.
2. **Put the episode on the repository's front page.**
   - `README.md` at github.com/accountingnonerd/- has no Series 2 row and no link to this tool.
   - `record-to-report/README.md` still says "not yet published".
   - The article points readers to that address ("ends in '/-'"), so it is where many will land.
3. **Fix the contradiction about "ties".**
   - Page 5: "it never says 'ties' while anything is undecided or unexplained". The tool says "It
     ties ... Still to decide: 1 stale check (step 3c)" after 3a.
   - Either reword page 5 ("while an entry that looks wrong, or a difference at the start, is
     undecided"), or add the in-between line to "What you should see".
4. **Say in "What you should see" (and in sample/README.md) that the counts change as you decide.**
   - After 3a, CHECK 1033 leaves the bank items (5 becomes 4), and the #1033 entry and the 3/6 Birch
     deposit leave the outstanding list (6 becomes 4).
   - Say also: "3b: nothing to change".
   - The README's "5 bank items" in step 1 against "Four bank items" in 3b looks like an error unless
     this is explained.
5. **Name the boxes, not their numbers.** "Drop the bank file in the box 'The bank's download' and the
   ledger in 'The books' ledger'". The prompt does not require a build to show the numbers 1 and 2.
6. **Tell the reader that a long paste may appear as an attachment** ("pasted text") in the AI chat,
   and that this is fine. Say "about 34,000 characters", not 33,000.
7. **Make the address hint clearer.** Say "the repository's address ends in '/-'" (not "the
   address"), and place "Copy raw file" as "next to Raw, top right". The "Copy path" icon at the top
   left looks the same.
8. **Small text fixes.** On page 8, "This is the first agent of Series 2: five more processes" should
   read "four more": each series is five agents (repository README). "Then the same amount within a
   few days" understates the windows (up to 60 days, or 180 for checks); "nearby dates" would be
   accurate.

## Files in this folder

- `first-generated.html`: the page I wrote from PROMPT.txt alone, in one go.
- `step5-open.png`, `step6-final-top.png`, `step6-final.png`: the screenshots asked for.
- `first-after-load.png`, `first-final-fullpage.png`, `first-print-view.png`, `first-phone.png`,
  `extra-no-reader.png`: extra screenshots.
- `first-run.json`: everything read from the screen at each step, and `window.__report`.
- `fetched/`, `downloads/`, `pdf/`: what I fetched from GitHub.
- The Playwright scripts are in the session scratchpad, not here.

## Follow-up (by the requester, after this test)

Applied: the "never says ties" sentence reworded; the in-between "It ties ... Still to decide: 1 stale
check" line and the count changes added to the article and the sample README; "change nothing" in 3b;
about 34,000 characters; "four more to come"; the boxes named by their labels; the matching window
stated; "next to Raw"; a note that a long paste may show as an attachment; the PDF says its links may
not open on LinkedIn and spells out the folders unbroken; Series 2 added to the repository's front page.
