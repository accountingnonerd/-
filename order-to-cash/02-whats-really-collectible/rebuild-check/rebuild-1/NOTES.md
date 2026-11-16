# Rebuild check 1: notes

Built from REBUILD-PROMPT.md alone. I did not open `agent/`, `tests/make_cases.py`, `tests/answer-key.json`, the case files or any other tool. I read only `tests/run-tests.js`, to see how it drives the page.

## Result

- First run: **17/17 cases, 2066/2066 checks** (see `first-run.txt`, `RESULTS.md`).
- Fixes: none were needed, so there was no second or third run.

## Fixes made after the first run

None.

## Places where the prompt was silent or ambiguous

The test passed, so none of these changed the result. Each is a judgment call that another rebuild could make differently. Where a hidden case touches one of them, two builds could disagree.

1. **Duplicates: what the recurring-billing exception covers.** The prompt says: "a duplicate if (x.num == y.num, or x.amount == y.amount and x.amount >= 100 cents and |y.date - x.date| < 7 days), unless the job has 3 or more such invoices with x's amount (recurring billing)". It does not say whether "unless" also covers the same-number test. I applied it to both. The prompt also does not say whether two blank numbers count as "the same number".
2. **The vendor/supplier test.** The prompt says: "or the heading row has `vendor` or `supplier`". It does not say whether the cell must equal that word or only contain it. I matched the word anywhere in a cell.
3. **"First cell".** The prompt says: "First cell exactly `total` (any case)". It does not say whether this is column A or the first non-empty cell. I used column A, taken literally.
4. **Unread rows.** The prompt says: "otherwise, if the row has other content and a non-empty date cell, record it as unread". It does not define "other content": other than the first cell, or other than the date cell. I used any non-empty cell other than the date cell.
5. **Verdict count K.** The prompt says: "K items to post in the ledger first" but does not define K. I used exact matches + applyOldest + credit balances + duplicate pairs. The test does not check it.
6. **When the allowance is worked out.** The prompt says: "Every time she types something and presses a button ... run the whole review again ... with everything she has typed so far (... rates ...)". Read that way, rates she has typed would apply even when she presses Compare. But the report lists `allowance` only "when they apply". I worked out the allowance only once `#apply-rates` (or Enter in a rate box) has been pressed.
7. **Sort order "by name".** The prompt does not say whether this is code-point order or locale order. I used code-point order. It matters only for ties in the worklist and the order of jobs.
8. **Two-digit years.** The prompt says: "`M/D/YYYY` or `M/D/YY`" but does not give a century rule. I used 20YY.
9. **The signature.** The prompt says: "all the row's cells joined, plus the current Xero contact". It gives no separator. Without one, a joined row could collide with a different row. I used a control-character separator.
10. **Rounding the allowance.** The prompt says: "round-half-up(base * rate / 100) cents", while also saying "all arithmetic is in whole cents (integers), in code". It does not say how to handle decimal rates such as 2.5% without floating-point error. I scaled the rate to an integer, multiplying by 1e6, and rounded in integers.
11. **Where IDENTICAL_LINES and DUPLICATE_ROWS go.** The ordered exception list ("in this order, only when they apply") leaves out these two codes. I put DUPLICATE_ROWS after UNREAD_ROWS and IDENTICAL_LINES after CASH_BASIS.
12. **Fields of the NEEDS_DATE report.** The prompt does not list them. I gave it version, file, status, exceptions, layout, company, asOf, basis and rows.
13. **Typed as-of date versus the file's own date.** The prompt does not say which wins if both exist. The as-of box only appears when the file has no date, so I let the file's date win.
14. **CSV text read by FileReader.** The prompt says to read CSV with `{type:"string"}` but gives no encoding. I used `readAsText`, which defaults to UTF-8.
