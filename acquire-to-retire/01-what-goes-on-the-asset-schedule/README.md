# Acquire-to-Retire, episode 01: What goes on the asset schedule?

Version 1.0.0. Series 1, Agent 5. Part of [Acquire-to-Retire](../README.md), which holds the
Stage 1 evidence and the value test this tool had to pass.

## The problem

At year end, the depreciation schedule in the tax software only knows what someone entered. What
the client bought, sold and scrapped during the year is in the general ledger: some of it in the
fixed asset accounts, some of it buried in repairs, supplies and small tools, and some of it (the
money from a truck that was sold) credited straight to the asset account. Finding it means reading a
year of ledger lines. Missed, it means depreciation never taken, equipment expensed that should have
been capitalized, gains never recorded, and books that no longer agree with the return.

## What it does

You give it the client's general ledger for the year (Excel or CSV, from QuickBooks Online,
QuickBooks Desktop or Xero). It works in four steps, and each screen says which step you are on and
what is yours to do:

1. **Give the ledger.** The page reads it and checks that every account adds up to the report's own
   totals.
2. **Check the accounts** (you check). The page sorts the accounts by name: fixed assets,
   accumulated depreciation, depreciation expense, expense accounts where purchases hide, and the
   rest. You correct any it got wrong.
3. **Decide what was found** (you decide). It lists the purchases recorded as assets (flagging
   trade-ins, land, journal entries and loan payments); the bills over $2,500 in expense accounts,
   each undecided until you choose capitalize or keep as expense; the credits to asset accounts,
   sorted into returns, sales already booked, and money received for a sold asset (you type its cost
   and depreciation to date from the schedule and it works out the gain or loss); and the checks
   against last year's schedule and this year's depreciation.
4. **Print the workpaper** (built from your choices): what to add to and take off the depreciation
   schedule, the proposed entries, the questions for the client, and the roll-forward.

The file is read on your computer. Nothing is uploaded, stored or sent.

## Use it

Download [`agent/what-goes-on-the-asset-schedule.html`](agent/what-goes-on-the-asset-schedule.html)
(on GitHub: open it, then "Download raw file") and double-click it. It works in any browser, with no
installation and no internet. Try it first with the made-up client in [`sample/`](sample/), which
also says what you should see.

## Build it yourself

The whole tool comes from one prompt, [`PROMPT.txt`](PROMPT.txt). You can paste it into an AI
assistant and get your own copy, then check it against the sample.

**What you need:** a computer with a browser, and an AI chat assistant that can write a long piece
of code in one reply, such as Claude at claude.ai. The reply is long, so a free plan may hit its
limit partway; a paid plan is safer. About 15 minutes, most of it waiting. The prompt was checked by
having fresh Claude sessions rebuild the tool from it and run it against the tests and the sample.

1. Open [`PROMPT.txt`](PROMPT.txt) on GitHub and press the **Copy raw file** button (the two
   squares at the top right of the file). Copying it from the page itself can change quotes and
   line breaks.
2. Start a new chat in your AI assistant, paste the prompt, and send it.
3. Wait for the reply: one long block of code, around 1,000 lines. If the assistant offers the file
   as a download, download it. If the reply stops partway, write: "Please send the complete file
   again in one code block."
4. If there is no download: copy the whole code block into a plain-text editor (Notepad on Windows;
   on a Mac, TextEdit after choosing Format, Make Plain Text) and save it as
   `what-goes-on-the-asset-schedule.html`.
5. Double-click the file. It opens in your browser with the title "What goes on the asset
   schedule?" and a box to drop a file.
6. Download the two files in [`sample/`](sample/) and drop the ledger in. Follow the steps on the
   screen, then compare with [`sample/README.md`](sample/README.md).

**If it does not work:**
- *A blank page or half a page:* the code was cut off. Ask for the complete file again.
- *Different numbers from the sample:* tell the assistant what you expected, quoting the line from
  `sample/README.md`, and ask it to fix the file so it follows the prompt exactly.
- *Still stuck:* use the ready-made file in `agent/`. It is the same tool, tested.

## Limits

It does not:
- depreciate anything. Method, life, bonus and section 179 stay in the tax software;
- see inside a bill. A bill over $2,500 can hold items under it, and the de minimis safe harbor is
  per invoice or per item, so you check the invoice;
- know what the client did with an asset. A credit to an asset account could be a sale, a trade-in,
  an insurance payout or a correction: the questions for the client ask;
- read leases, construction in progress or intangibles, or split a building's price between land
  and building;
- find a purchase in an account whose name gives no hint (you can mark any account in step 2);
- read a layout it has not seen. The layouts were built from the products' published report
  layouts, not from real client exports.

## What is in this folder

| Path | What it is |
|---|---|
| `agent/what-goes-on-the-asset-schedule.html` | The tool. One file, works offline. |
| `agent/what-goes-on-the-asset-schedule.src.html` | The readable source; it loads its spreadsheet reader from a CDN. |
| `agent/build.py` | Pastes the spreadsheet reader into the source to make the offline file. |
| `PROMPT.txt` | The prompt that rebuilds the tool. The master copy. |
| `sample/` | An invented client: the ledger, last year's schedule, and what you should see. |
| `tests/cases/` | 22 test cases, all invented businesses. |
| `tests/make_cases.py` | Builds the test files from a model and works out the answer key; the rules are in its docstring. |
| `tests/answer-key.json` | The answer key. |
| `tests/run-tests.js` | Runs any build of the tool against the key in a real browser. |
| `tests/RESULTS.md` | Results case by case, what the reviews changed, and the broken copies the tests caught. |
| `tests/MANUAL-BASELINE.md` | The same review by hand, with estimated minutes. |
| `ACCOUNTANT-TEST-SCRIPT.md` | A 25-minute script for testing with a real accountant. |
| `rebuild-check/` | Builds made from the prompt by fresh AI sessions, and their test results. |
| `article/` | The LinkedIn article and its images. |

## Run the tests

```bash
cd tools && npm install
```

```bash
cd acquire-to-retire/01-what-goes-on-the-asset-schedule/tests && node run-tests.js
```

## Third-party code

The offline file contains [SheetJS](https://sheetjs.com) Community Edition 0.18.5 (Apache License
2.0), used to read Excel and CSV files.
