# One Painful Problem

A series of small tools for accountants who do client work, and one article per tool.

Each series is five agents, one for each of the five processes accountants run for clients. Each agent takes
one step of one process and builds a tool that works **alongside** the software the
accountant already has: it starts from an export she can already produce and hands back
a workpaper, an importable entry or a client request. See [SERIES.md](SERIES.md) for the
five processes, the release order and the value test every tool must pass.

Every tool in this repository:
- is one screen with one obvious first action, and runs on the accountant's own computer;
- does its arithmetic in code and shows control totals that tie to the source file;
- lists exceptions first and flags what it is unsure of, with the reason;
- ships with its acceptance test, the answer key, the results, and a prompt that rebuilds it.

## Series and episodes

| Series 1 agent | Process | Folder no. | Tool | What it does | Date | Version |
|---|---|---|---|---|---|---|
| 1 | [Procure-to-Pay](procure-to-pay/) | 01 | [Who gets a 1099?](procure-to-pay/01-who-gets-a-1099/) | Reads a client's year of payments and produces the 1099 worksheet: who to file, whose W-9 to check, and why, including vendors the software's 1099 report misses because nobody flagged them. | 2026-11-11 | 1.1.0 |
| 2 | [Hire-to-Retire (payroll)](hire-to-retire/) | 01 | [Do the 941s match the W-3?](hire-to-retire/01-do-the-941s-match-the-w3/) | Reads the filed 941s and W-3 (PDFs) and produces the reconciliation the IRS says to keep, with every difference explained or flagged, including the W-3 that leaves out a previous provider's quarters. | 2026-11-12 | 1.0.0 |
| 3 | [Record-to-Report (close)](record-to-report/) | 01 | [Did last year change?](record-to-report/01-did-last-year-change/) | Compares last year's final trial balance from your file with the client's books today, for the same date: what changed, whether last year's profit or an earlier year changed, which of your adjustments were never posted, and the entry that puts the opening balances back. | 2026-11-13 | 1.0.0 |
| 4 | [Order-to-Cash](order-to-cash/) | 02 | [What's really collectible?](order-to-cash/02-whats-really-collectible/) | Reads a client's A/R aging detail and produces the receivables review: payments and credits never applied, customers the client owes, duplicates and mis-postings to clean first; who to chase, ranked, with a draft letter each; the allowance from your loss rates, the write-offs and the entry. | 2026-11-16 | 1.0.0 |
| 5 | [Acquire-to-Retire](acquire-to-retire/) | 01 | [What goes on the asset schedule?](acquire-to-retire/01-what-goes-on-the-asset-schedule/) | Reads a client's general ledger for the year and finds what the depreciation schedule needs: purchases recorded as assets, bills in expense accounts that may be equipment, sales and write-offs, and whether the books agree with last year's schedule and this year's depreciation; with the entries and the client questions. The first agent published with its rebuild prompt and a sample to check a rebuilt copy. | 2026-11-25 | 1.0.0 |

| Series 2 agent | Process | Folder no. | Tool | What it does | Date | Version |
|---|---|---|---|---|---|---|
| 1 | [Record-to-Report (close)](record-to-report/) | 02 | [Why won't the bank rec tie?](record-to-report/02-why-wont-the-bank-rec-tie/) | Matches the bank's download to the books' ledger for any span of months: checks by number, card batches, outstanding items and their age, bank items not in the books, the entries that look wrong (wrong amount, digits swapped, sign reversed, entered twice, paid twice), and the reconciliation that proves it, with the entries and the client questions. | 2026-11-28 | 1.0.0 |

## Parked tools

Built and tested, not released. Each can be released later as it stands.

| Process | Folder | Tool | Why parked |
|---|---|---|---|
| Order-to-Cash | 01 | [Does the 1099-K tie?](order-to-cash/01-does-the-1099k-tie/) (14/14 cases, rebuilt from its prompt) | Too close to Agent 1's 1099 topic in the same week, and a narrower problem than the series should lead with. Candidate for a January tax-season release. |

## How to get any past build

Each release is recorded by its commit:

| Episode | Version | Commit |
|---|---|---|
| Record-to-Report 02, Why won't the bank rec tie? | 1.0.0 | `aa6f9ec84f9f5f23f1baf0b83b329509e47c26aa` |
| Record-to-Report 01, Did last year change? | 1.0.0 | `56f31c977a7c288989d9ac18d69bd822335be03a` |
| Order-to-Cash 02, What's really collectible? | 1.0.0 | `79f2bc17f10628e1640a0d771d34e4f021f20b14` |
| Acquire-to-Retire 01, What goes on the asset schedule? | 1.0.0 | `f15a03a1ccb7e9e298ba75486dd9c5e51a69b7dd` |
| Hire-to-Retire 01, Do the 941s match the W-3? | 1.0.0 | `92f777018c6e9c4627ab063f56aa2f4ce4e9a15f` |
| Procure-to-Pay 01, Who gets a 1099? | 1.1.0 | `a2f00b20007b931f654214c2783b4f2662e7406f` |
| Procure-to-Pay 01, Who gets a 1099? | 1.0.0 (before the series structure) | `e9c23172b253bc0f8c1a76bcf97f2d6d1040dfb2` |

```bash
git checkout a2f00b20007b931f654214c2783b4f2662e7406f
```

Then open the agent file in that folder, or rerun its tests as its README describes.
Version tags (`procure-to-pay/01-who-gets-a-1099/v1.1.0`) exist in the working copy but
could not be pushed from the build environment; they can be added on GitHub as releases
pointing at the commits above.

## Other files

- [SERIES.md](SERIES.md): the five processes, the value test, and the candidate episodes.
- [BACKLOG.md](BACKLOG.md): candidate problems by process, reader suggestions, killed ideas.
- [GROWTH.md](GROWTH.md): what drives reach and follows on LinkedIn, what the series changes because of it, and the numbers per post.
- `tools/`: the one library the tests need (`npm install` there before running tests).

No real client data is in this repository. Every company and person in the test files is invented.
