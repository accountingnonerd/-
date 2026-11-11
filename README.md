# One Painful Problem

A series of small tools for accountants who do client work, and one article per tool.

The series follows the five processes accountants run for clients. Each episode takes
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

| Series | Process | Episode | Tool | What it does | Date | Version |
|---|---|---|---|---|---|---|
| 1 | [Procure-to-Pay](procure-to-pay/) | 01 | [Who gets a 1099?](procure-to-pay/01-who-gets-a-1099/) | Reads a client's year of payments and produces the 1099 worksheet: who to file, whose W-9 to check, and why, including vendors the software's 1099 report misses because nobody flagged them. | 2026-11-11 | 1.1.0 |
| 2 | Hire-to-Retire (payroll) | | next, January 2027 | | | |
| 3 | Record-to-Report (close) | | February 2027 | | | |
| 4 | Order-to-Cash | | March 2027 | | | |
| 5 | Acquire-to-Retire (fixed assets) | | April 2027 | | | |

## How to get any past build

Each release is tagged `<process>/<episode>/v<version>`. For example:

```bash
git checkout procure-to-pay/01-who-gets-a-1099/v1.1.0
```

Version 1.0.0 of episode 01 predates the series structure and is tagged `01-who-gets-a-1099/v1.0.0`.

## Other files

- [SERIES.md](SERIES.md): the five processes, the value test, and the candidate episodes.
- [BACKLOG.md](BACKLOG.md): candidate problems by process, reader suggestions, killed ideas.
- `tools/`: the one library the tests need (`npm install` there before running tests).

No real client data is in this repository. Every company and person in the test files is invented.
