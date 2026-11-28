# Record-to-Report, episode 02: Why won't the bank rec tie?

Version 1.0.0. Series 2, Agent 1. Part of [Record-to-Report](../README.md), which holds the Stage 1
evidence and the value test this tool had to pass.

## The problem

The bank reconciliation is the most common monthly job in the close, and the place where errors from
everywhere else show up. When it ties at the first try, the ledger's reconcile screen is enough. When
it does not, or when a client hands over three months at once, the accountant is left comparing two
long lists by eye: the check entered as $425.10 that the bank paid as $452.10, the deposit entered
twice, the refund entered as money in, the card sales recorded one by one that arrive as one deposit,
the December check that cleared in January. And before any of that, working out which old checks were
still outstanding when the bank file starts.

## What it does

You give it two files: the transactions downloaded from the bank's website, and the books' ledger
detail for the same account (Excel or CSV, from QuickBooks Online, QuickBooks Desktop or Xero). It
works in four steps, and each screen says which step you are on and what is yours to do:

1. **Give the two files.** The page reads both and checks that each adds up: the bank's running
   balance day by day, and the ledger against its own totals.
2. **Check what was read** (you check): the statement dates, the beginning and ending balances, and
   which account in the books is the bank account. If the download has no balances, you type them.
3. **Decide what was found** (you decide). It matches checks by number, then by amount and date, then
   several book entries to one bank line (card batches) and one entry to several lines. What is left
   it lists:
   - book entries that look wrong: a check for a different amount, digits swapped, money in and out
     reversed, a voided check the bank paid, a check paid twice, an entry made twice. Each stays
     undecided until you say what it is;
   - bank items not in the books (fees, interest, returned items, anything else), with a suggested
     treatment you can change;
   - what is outstanding, with its age: stale-dated checks over six months, old checks over 90 days,
     and deposits or payments not at the bank after 10 days.
   It also works out what was outstanding before the bank's first date from the two starting
   balances, and asks you when more than one answer fits.
4. **Print the reconciliation** (built from your choices): the proof (adjusted bank against
   adjusted books), the entries and corrections, and the questions for the client.

The files are read on your computer. Nothing is uploaded, stored or sent.

## Use it

Download [`agent/why-wont-the-bank-rec-tie.html`](agent/why-wont-the-bank-rec-tie.html) (on GitHub:
open it, then "Download raw file") and double-click it. It works in any browser, with no installation
and no internet. Try it first with the made-up client in [`sample/`](sample/), which also says what
you should see.

## Build it yourself

The whole tool comes from one prompt, [`PROMPT.txt`](PROMPT.txt). You can paste it into an AI
assistant and get your own copy, then check it against the sample.

**What you need:** a computer with a browser and an internet connection (the page you build loads its
spreadsheet reader from cdnjs.cloudflare.com each time it opens; the ready-made tool in `agent/` works
offline), and an AI chat assistant that can write a long piece of code in one reply, such as Claude at
claude.ai. The reply is long, so a free plan may hit its limit partway; a paid plan is safer. About 15
minutes, most of it waiting. The prompt was checked by having a fresh Claude session rebuild the tool
from it and run it against the tests (see `rebuild-check/`).

1. Open [`PROMPT.txt`](PROMPT.txt) on GitHub and press the **Copy raw file** button (the two squares
   at the top right of the file). Copying it from the page itself can change quotes and line breaks.
2. Start a new chat in your AI assistant, paste the prompt, and send it.
3. Wait for the reply: one long block of code, around 1,000 lines. If the assistant offers the file as
   a download, or shows it in a side panel with a download or copy button, use that. If the reply
   stops partway, write: "Please send the complete file again in one code block."
4. If there is no download: copy the whole code block into a plain-text editor and save it as
   `why-wont-the-bank-rec-tie.html`. On Windows, use Notepad, and set "Save as type" to "All files",
   or it saves as .html.txt. On a Mac, use TextEdit: choose Format, then Make Plain Text, and when it
   asks, choose "Use .html".
5. Double-click the file. It opens in your browser with the title "Why won't the bank rec tie?" and
   two boxes to drop files in.
6. Download the two files in [`sample/`](sample/): the bank download goes in the box "The bank's
   download", the ledger in "The books' ledger". Follow the steps on the screen, then compare with [`sample/README.md`](sample/README.md).

**If it does not work:**
- *A blank page or half a page:* the code was cut off. Ask for the complete file again.
- *Nothing happens when you drop a file:* the page could not load its spreadsheet reader. Check the
  internet connection or the firewall, or use the ready-made file in `agent/`.
- *A box forgets what you typed:* tell the assistant exactly that, and ask it to keep what you type
  and apply it only when you press "Use these" or Enter.
- *Different numbers from the sample:* tell the assistant what you expected, quoting the line from
  `sample/README.md`, and ask it to fix the file so it follows the prompt exactly.
- *Still stuck:* use the ready-made file in `agent/`. It is the same tool, tested.

## Limits

It does not:
- reconcile credit cards or loans. It says so and stops;
- make one reconciliation per month for a span of months. It makes one, at the statement date, for
  the whole span;
- take last reconciliation's outstanding list as a file. When the starting balances leave more than
  one answer, it asks you to tick the items from that list;
- look for gaps in the check sequence, or agree the books' balance with the trial balance;
- read dates written day first (31/12/2026). A day over 12 shows the problem and it stops; a file
  whose days are all 12 or under would be read as month first, so check the dates in step 2;
- read a layout it has not seen. The layouts were built from the banks' and the products' published
  formats, not from real client exports;
- post anything. It proposes entries and corrections; you decide.

## What is in this folder

| Path | What it is |
|---|---|
| `agent/why-wont-the-bank-rec-tie.html` | The tool. One file, works offline. |
| `agent/why-wont-the-bank-rec-tie.src.html` | The readable source; it loads its spreadsheet reader from a CDN. |
| `agent/build.py` | Pastes the spreadsheet reader into the source to make the offline file. |
| `PROMPT.txt` | The prompt that rebuilds the tool. The master copy. |
| `sample/` | An invented client: the bank download, the ledger, and what you should see. |
| `tests/cases/` | The test files, all invented businesses. |
| `tests/rules.py` | The rules, written out, and the model that applies them. |
| `tests/make_cases.py` | Builds the test files from a model of events and works out the answer key with `rules.py`. |
| `tests/answer-key.json` | The answer key. |
| `tests/run-tests.js` | Runs any build of the tool against the key in a real browser. |
| `tests/RESULTS.md` | Results case by case, what the reviews changed, and the broken copies the tests caught. |
| `tests/MANUAL-BASELINE.md` | The same work by hand, with estimated minutes. |
| `ACCOUNTANT-TEST-SCRIPT.md` | A 25-minute script for testing with a real accountant. |
| `rebuild-check/` | A build made from the prompt by a fresh AI session, and its test results. |

## Run the tests

```bash
cd tools && npm install
```

```bash
cd record-to-report/02-why-wont-the-bank-rec-tie/tests && node run-tests.js
```

## Third-party code

The offline file contains [SheetJS](https://sheetjs.com) Community Edition 0.18.5 (Apache License
2.0), used to read Excel and CSV files.
