# Rebuild 1: notes

## First run (main measure)

21 of 22 cases, 712 of 714 checks (see first-run.txt). The only failure was case 22:

    x produces a report: expected "a report", got "nothing"
    x runs without errors: got "TimeoutError: locator.fill: Timeout 30000ms exceeded."

## Fix 1: case 22, the sold truck's figures (prompt version mismatch, not a reading error)

The test was waiting for `input.disp` nth(2), a third box for the first sale. My build had two boxes per sale because
the PROMPT.txt I read at the start said:

> G. For each "proceeds" credit she can type the asset's original cost and its depreciation to date (from the schedule).
> 3c ... two boxes <input class="disp"> (first the original cost, then the depreciation to date; in the order of the credits)

tests/run-tests.js, answer-key.json, cases/ and make_cases.py were rewritten at 18:07 to 18:09 UTC, during my build.
PROMPT.txt was rewritten at 18:11 UTC, after my first run. The current prompt says:

> G. For each "proceeds" credit she types three figures: the asset's original cost and its accumulated depreciation at
> the end of last year ..., and its depreciation this year up to the sale ... Depreciation to date = the last two added.
> 3c ... three boxes <input class="disp" data-id="SALE ID" data-f="cost|ad|ady">

So the first run tested a build from the old prompt against the new test. Neither unclear nor misread: the prompt changed.
For fix 1, I re-read the current PROMPT.txt and brought the whole build in line with it, not only case 22: three sale
boxes worked out when she leaves the sale; rule H (target and reason selects); rule I (costAfter and adAfter); faAccounts;
the AJE journal table id="entries"; the finished form of the verdict; the "You are looking at step N of 4" line; Workpaper
ref.; the print title and print confirmation; the compact step bar on a phone; the new start-screen text.

Disclosure: to find which fill timed out, I loaded case 22 into my own page and ran a copy of run-tests.js (in the
scratchpad) that only logged the step name, the number of boxes on the page and Playwright's call log. It printed no
answer-key values. I did not open the answer key, make_cases.py or agent/.

Result after fix 1: 22 of 22 cases, 758 of 758 checks (final-run.txt, RESULTS.md). No second fix was needed.
