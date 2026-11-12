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
| 3 | Record-to-Report (close) | | February 2027 | | | |
| 4 | Order-to-Cash | | March 2027 | | | |
| 5 | Acquire-to-Retire (fixed assets) | | April 2027 | | | |

## How to get any past build

Each release is recorded by its commit:

| Episode | Version | Commit |
|---|---|---|
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
- `tools/`: the one library the tests need (`npm install` there before running tests).

No real client data is in this repository. Every company and person in the test files is invented.
