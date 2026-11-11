# One Painful Problem

A series of small accounting agents. Each one does a single job that practicing
accountants do by hand, and does it completely, ugly cases included.

Every agent in this repository:
- is one screen with one obvious first action;
- does its arithmetic in code and shows control totals that tie to the source file;
- lists exceptions first and flags what it is unsure of, with the reason;
- says on screen where the data goes;
- ships with its acceptance test, the answer key, the test results, and a prompt that
  rebuilds it from nothing.

## Agents

| No. | Agent | What it does | Date | Version |
|---|---|---|---|---|
| 01 | [Who gets a 1099?](01-who-gets-a-1099/) | Takes a client's payments for the year and produces the 1099 worksheet: who needs a 1099, who needs a W-9, and why, tied to the file total. | 2026-11-11 | 1.0.0 |

## How to get any past build

Each release is tagged `NN-short-name/vX.Y.Z`. For example:

```bash
git checkout 01-who-gets-a-1099/v1.0.0
```

Then open the agent file in that folder, or rerun its tests as its README describes.

## Other files

- [BACKLOG.md](BACKLOG.md): candidate problems and reader suggestions.
- `tools/`: the one library the tests need (`npm install` there before running tests).

No real client data is in this repository. Every company and person in the test files is invented.
