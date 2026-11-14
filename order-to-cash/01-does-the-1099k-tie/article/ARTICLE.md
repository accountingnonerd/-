<!--
DRAFT FOR APPROVAL. Not published.
Series: One Painful Problem, Series 1, Agent 4 (Order-to-Cash).
For the LinkedIn newsletter edition and the repository. Images are slides from the carousel (carousel/slides/).
-->

# Series 1 · Agent 4: The 1099-K says one number. The bank says another.

![The 1099-K says $39,907.56. The deposits say $38,492.25. The return should say neither.](carousel/slides/01.png)

A café owner drops off the tax papers in February. On top is a Form 1099-K from Square: $39,907.56. The books, built from the bank feed, show card sales of $38,492.25. Neither number is what goes on line 1 of the return.

That café, Juniper Street Coffee, is invented; it is one of our test files. The form is not. Every business that takes cards gets a 1099-K from its processor "no matter how many payments you got or how much they were for" ([IRS](https://www.irs.gov/businesses/understanding-your-form-1099-k)), and the 2026 forms arrive by January 31, 2027. This is Series 1, Agent 4: a free tool that turns a client's year of Square, Stripe or PayPal transactions into what the 1099-K should say, and ties it to the return and to the bank.

## Why the numbers never match

The 1099-K counts gross. The IRS instructions define box 1a as the total of card and app payments "without regard to any adjustments for credits, cash equivalents, discount amounts, fees, refunded amounts, shipping amounts, or any other amounts" ([IRS](https://www.irs.gov/instructions/i1099k)). The bank sees what is left after the processor takes its fees and holds back late-December sales until January.

So books built from deposits come in low. Intuit's own help page for preparers warns that "the client may receive an IRS notice if the gross receipts don't reflect amounts from the 1099-K" ([Intuit](https://accountants.intuit.com/support/en-us/help-article/form-1099-k/entering-form-1099-k-transactions-proconnect-tax/L1sbeU13g_US_en_US)). A preparer on the Intuit community put the everyday version plainly: "The 1099K shows more than what the deposits in the bank are... Do I gross up sales that were recorded as net deposits?" ([thread](https://accountants.intuit.com/community/proconnect-tax-discussions/discussion/1099-for-s-corp/00/229306)).

![Some sales aren't in it. Some of it may not be sales.](carousel/slides/04.png)

And the 1099-K is not gross receipts either:
- cash sales are income, but never on it;
- payments with the business's own gift cards are left off it, and should not be added back, because the gift card was income when it was sold;
- sales tax and tips are inside it. Whether they belong on line 1 depends on the state and on who keeps the tips. A preparer asking about "$176K in a 1099" with over $13,000 of sales tax inside it got two different answers in the same thread ([thread](https://accountants.intuit.com/community/proseries-tax-discussions/discussion/accounting-treatment-for-1099-k-that-includes-sales-tax/00/283709)).

## What the tool does

![The bridge to line 1](carousel/slides/05.png)

You drop in one export, the one the client can download in two minutes: Square's transactions CSV, Stripe's itemized balance activity, or PayPal's activity download. Type box 1a from the client's 1099-K if you have it. The page returns a workpaper with:
- what the 1099-K should say: box 1a, box 3, and each month, 5a to 5l;
- whether it ties, and if not, by how much and the likely cause;
- the bridge to the return: gross receipts, returns and allowances, merchant fees, with sales tax and tips included as the 1099-K includes them, and a box to leave them out where the law allows;
- the tie to the bank deposits, top to bottom;
- the year-end entry for books that recorded deposits as sales, with proof that sales afterwards equal the 1099-K gross;
- the questions for the client.

It runs in the browser and uploads nothing. The arithmetic is ordinary code, in whole cents.

![What comes back](carousel/slides/07.png)

## What it catches

In the test files: a 1099-K $2,184 higher than the export, because a second location reports on the same tax ID. Friends-and-family transfers through PayPal with no fee, which may be customers dodging the fee or may be personal. A December 31 sale that Stripe's UTC export dates January 1. Two exports pasted together, so June counts twice. A payment PayPal marks "Refunded" that still belongs in gross.

## We tried to break it

![Tested before it was built](carousel/slides/09.png)

We wrote the test first: 14 cases from three invented businesses, a café on Square, an online shop on Stripe and a print seller on PayPal. The final version passes all 660 checks. We then broke it on purpose 17 ways; the tests caught every one.

The first run passed 8 of 14. Box 3, the count of payments, included cash-only sales, which never reach a 1099-K.

A separate AI session, told to review the tool as a skeptical CPA, found sixteen problems. The worst: gift cards were counted twice, once when sold and again when redeemed. Sales tax and tips were taken out of gross receipts by default, which is wrong in California and in states whose tax falls on the seller, and wrong for an owner who keeps the tips; that would also put line 1 below the 1099-K, the very mismatch the tool exists to prevent. Gross receipts now include them, and leaving them out is the accountant's tick, with the warning printed.

Another session, playing a 60-year-old partner who had never seen the tool, footed the bank bridge and found the bold total was not the sum of the lines above it. It now foots top to bottom.

The last check was the rebuild prompt at the end of this article. We gave it to a fresh AI session with nothing else, then ran what it built through the same tests. The first rebuild got every figure right but passed 12 of 14 cases: the prompt never said how to report duplicate lines, or where to show a refusal. With those two lines added, the second rebuild passed all 660 checks.

By hand, we estimate about 50 minutes for a clean client and over an hour and a half when something is wrong, before any call to the client. That is an estimate, not a measurement.

## What it won't do

It does not read the 1099-K itself; you type box 1a and check the payee's tax ID, box 4 and the state boxes, which the page lists. It reads Square, Stripe and PayPal, not Shopify, Venmo or the marketplaces. It does not decide sales tax or tips for you. Our layouts were built from the processors' published column names, not from a real client's export, and it does not see what Square takes from deposits outside the transactions export.

## The series

Agent 1 found the 1099 vendors your software misses. Agent 2 checked the 941s against the W-3. Agent 3 checked whether last year's books still match what you filed. This is agent 4; agent 5 covers fixed assets. Every agent comes with its test files, its results and one prompt that rebuilds it. The prompt is below; everything else is at [github.com/accountingnonerd/-](https://github.com/accountingnonerd/-).

## Your turn

Which tax-season reconciliation still eats your evenings? Tell me the task, the document it starts from, and how long it takes.

---

## Appendix: the rebuild prompt, in full

````text
Build a single self-contained HTML file called `does-the-1099k-tie.html`. It is a tool for a US accountant who prepares small-business returns, is expert in tax, impatient with software, and works on a desktop. She drops in a client's year of card or payment-app transactions exported from Square, Stripe or PayPal. She gets back what the client's Form 1099-K should say, the figures for the return, how they tie to the bank deposits, and a year-end entry. Everything runs in the browser; nothing is uploaded. All money is integer cents; all arithmetic in code.

The rule (IRS instructions for Form 1099-K, box 1a): "gross amount" is the total of payment transactions "without regard to any adjustments for credits, cash equivalents, discount amounts, fees, refunded amounts, shipping amounts, or any other amounts", dated on the date of the transaction. Box 3 counts payment transactions, not refunds. Boxes 5a to 5l are the gross for each month. A payment with the merchant's own gift card is excluded.

## Screen
- Load SheetJS 0.18.5: `<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>`.
- Start screen: title "Does the 1099-K tie?", one sentence saying what it does; an optional field `<input id="box1a-start">` labelled "Have the client's 1099-K? Type box 1a first (optional)"; one large drop area wrapping `<input type="file" id="file" accept=".csv,.txt,.xlsx,.xls,.xlsm">` ("Drop the processor's export for the year here"); short notes on which export to get from each processor (Square: Transactions, Export, Transactions CSV; Stripe: Reports, Balance, itemized balance change from activity; PayPal: Activity download, CSV); why it matters (the 1099-K reports gross, the bank sees payouts, gross receipts below the 1099-K may bring an IRS notice); a "See it work on a made-up sample" link; "Where your data goes: nowhere"; "You stay in charge". Footer "Version 1.0.0."
- Refusals are shown in `<div id="problem" role="alert">` directly under the drop area, staying on the start screen. A PDF, or anything other than xlsx/xlsm/xls/csv/txt, is refused there with a plain message. A file that is not one of the three exports is refused the same way, with status NOT_RECOGNIZED (set `window.__report` with that status and the exception).
- Read CSV/TXT with `XLSX.read(text, {type:"string", raw:true})`; other files with `{type:"array"}`. Use the sheet with the most rows (`sheet_to_json(ws, {header:1, raw:true, defval:null, blankrows:true})`).
- After reading, replace the start screen with the workpaper. Above it: one main button "Print or save as PDF" and a "Start over" link. In the workpaper: `<input id="box1a">` and `<button id="compare">` ("Check it ties"); pressing the button (or Enter) compares and re-renders. If `#box1a-start` held a number when the file was dropped, compare at once. Large type, plain words, print styles. Set `window.__report` (the report object without internal fields) after every render.

## Recognizing the export
Look in the first 15 rows for a heading row (lower-cased, trimmed cells) that contains all of:
- Square: `transaction id`, `event type`, `total collected`, `card`, `net total`;
- Stripe: `reporting_category`, `gross`, `fee`, `net`, and `created_utc` or `created`;
- PayPal: `type`, `status`, `currency`, `gross`, `fee`, `net`, `transaction id`.
Amounts: numbers, or text such as `$1,234.56`, `-$1.23`, `(1.23)`, `1,234.56-`; blank is 0. Dates: `MM/DD/YYYY` or `YYYY-MM-DD`, optionally with a time (`HH:MM`), or a separate Time column; keep year, month, day and hour.

## Each line becomes an event
Skip blank rows. A row whose date cannot be read is "unread" (Square: a row whose first cell is `Total`/`Totals` is skipped silently). A row exactly identical to an earlier row (every cell) is a duplicate: count it, note its month, and skip it.
- **Square.** If Transaction Status does not start with "Complete": unsettled. card = Card + Cash App; cashOther = Cash + Other Tender; gift = Square Gift Card; total = Total Collected; a share of x for tender t = round(x × t / total). depositNet = Net Total − cashOther − gift; depositWhen = Deposit Date; fee = −Fees.
  - Event Type "Payment": a sale with card, tax = share(Tax, card), tip = share(Tip, card), cashOther, cashOtherTax = share(Tax, cashOther), cashOtherTip = share(Tip, cashOther), gift; giftSold = Gift Card Sales.
  - Event Type "Refund": a refund of card amount −card (a positive number), cash refund −cashOther, and the tax refunded.
  - Anything else: other activity, amount depositNet.
- **Stripe.** Date = `created` if that column has a value, else `created_utc` (and then the file is "UTC only"). gross, fee, net as given. reporting_category: `charge` → sale (card = gross, fee = fee); `refund`, `refund_failure`, `partial_capture_reversal` → refund (amount −gross, fee); `dispute`, `dispute_reversal` → chargeback (amount −gross, fee; a reversal is negative, so the two net); `payout`, `payout_reversal` → payout of −net; `fee`, `network_cost`, `tax` → fee of −net; anything else → other activity of net, labelled with its category.
- **PayPal.** A status of Completed, Refunded, Partially Refunded, Reversed or Cleared counts as paid (PayPal re-labels a refunded payment, but it was paid); any other status is unsettled, except hold lines. Type, lower-cased, decides, in this order:
  1. contains "hold" or "authorization": a hold (ignored);
  2. currency other than USD: a foreign sale if it is a payment with positive gross (not a refund), a foreign conversion if it is a currency conversion, otherwise foreign other;
  3. "currency conversion" in USD: money in (conversion in) if positive, else other;
  4. contains "refund": a refund (−gross) if gross is negative; if positive, it is a supplier's refund to the client: other activity, labelled "Refunds received (money in)";
  5. "chargeback fee" or "dispute fee": a fee of −gross − fee;
  6. "chargeback" or "dispute" (including reversals): chargeback of −gross, fee −fee;
  7. "withdraw": payout of −(gross + fee);
  8. "bank deposit", "add funds", "credit card deposit", "transfer from": money moved in, gross + fee;
  9. "general payment" with positive gross and zero fee: a personal transfer (friends and family);
  10. any other type containing "payment" with positive gross: a sale (card = gross, fee = −fee, tax = Sales Tax);
  11. anything else: other activity of gross + fee, labelled with the type and "(money in)" or "(money out)".
  A foreign sale is converted at PayPal's own rate: find the foreign conversion lines and the USD conversion-in lines whose Reference Txn ID is the sale's Transaction ID; rate = USD received ÷ foreign amount converted; card = round(foreign gross × rate); fee = card − USD received. It becomes a sale, and its USD conversion lines are absorbed (not counted again). A foreign sale with no conversion lines is reported, not counted.

## The year and the figures
- Year Y = the year with the most sale events (ties: the later year). Everything dated outside Y is left out and reported.
- Sales = sale events in Y with card > 0. gross = Σ card; box 3 = their count; month m = Σ card of sales in month m.
- salesTax = Σ (tax + cashOtherTax) and tips = Σ (tip + cashOtherTip) over all sale events in Y. cashOther = Σ cashOther; giftRedeemed = Σ gift.
- refunds = Σ refund amounts (card); chargebacks = Σ chargeback amounts; fees = Σ fee of every event in Y; personal, transfersIn = Σ their amounts; other = Σ other activity + unabsorbed conversions in.
- payouts: Square, Σ depositNet of sales and refunds whose Deposit Date is in Y; others, Σ payouts.
- netActivity = gross − refunds − chargebacks − fees. held = netActivity + transfersIn + personal + other − payouts (for Square, the sales paid out after the year end; for the others, the change in the balance held during the year).
- grossReceipts = gross + cashOther (sales tax and tips included, as the 1099-K includes them). grossReceiptsExcluding = grossReceipts − salesTax − tips. returns = refunds + cash refunds + chargebacks.
- The entry (for books that recorded each payout as sales), dated December 31 of Y. owner = transfersIn + personal; salesCredit = fees + refunds + chargebacks + held − owner − other. Lines, each with a nonzero amount as debit if positive, credit if negative: "Merchant fees" (fees), "Sales returns and allowances" (refunds + chargebacks), "Due from processor" (held), "Owner contributions" (−owner), "Other activity to classify" (−other), "Sales" (−salesCredit). Report the total debit and credit, salesBooked = payouts and salesAfter = payouts + salesCredit (which equals gross).

## Warnings: code, level (stop, care or info), and a plain-English message
- UNREAD_ROWS (stop); DUPLICATE_ROWS (stop; the count and months in the message; set `duplicates` to the count, a plain number).
- MISSING_MONTH (care): months of Y with no card sales, when some months have them; set `missingMonths`.
- OUTSIDE_YEAR (info): lines dated outside Y; set `outside = {count, sales, amount}`.
- UTC_DATES (care) when the Stripe file is UTC only: report sales dated January 1 of Y+1 before 8:00 (they may be December 31 sales in the US) and January 1 of Y before 8:00, separately, as `boundary = {intoNextYear:{count, amount}, fromPriorYear:{count, amount}}`, with box 1a both ways.
- NO_TAX_DETAIL (info) for every Stripe file.
- SALES_TAX_IN_GROSS (care) if salesTax > 0; TIPS_IN_GROSS (care) if tips > 0: say they are included, as the 1099-K includes them, where they may be left out, and that line 1 is then below the 1099-K.
- NOT_ON_1099K (info) if cashOther > 0 or giftRedeemed > 0. GIFT_CARD_SALES (info) if gift cards were sold.
- PERSONAL_TRANSFERS (care), naming each; FOREIGN_CURRENCY (care), setting `foreign = {count, usd}` (usd = Σ converted card); FOREIGN_NOT_CONVERTED (care); NOT_SETTLED (info); OTHER_ACTIVITY (care) listing each label and total; REFUND_WITHOUT_SALE (info, Square: refunds whose Transaction ID matches no sale); NO_DEPOSIT_DATES (stop, Square without a Deposit Date column).
- BELOW_THRESHOLD (info) for PayPal when gross ≤ $20,000 or there are ≤ 200 sales: PayPal need not issue a federal 1099-K; states may; the income is reportable either way.
- When box 1a is typed: d = typed − gross. d = 0: status TIES. Otherwise status DIFFERS and DIFFERS_FROM_1099K (stop, first in the list) with the likely causes (another location or account, the UTC edge, missing months, personal transfers; or, if typed is lower, a different account or year, or a figure net of refunds). Set `typedBox1a` and `difference` (= d).
Status without a typed figure: COMPUTED.

## The workpaper, in order
- Heading with the layout, year and file; lines for Client, EIN, Prepared by, Date, Reviewed by, Date.
- `<div id="verdict">`: COMPUTED "If a 1099-K is issued for Y, box 1a should be $X."; TIES "The 1099-K ties: box 1a is $X, exactly the year's card and app sales."; DIFFERS "The 1099-K does not tie: box 1a is $D more/less than this export's sales."; NOT_RECOGNIZED "I cannot read this file."
- `<div id="stop-banner">`, visible with the messages only when a stop-level warning exists.
- What the 1099-K should say: box 1a, box 3, the typed-figure field, and the twelve months 5a to 5l in a grid that wraps on a phone.
- Check these first: the other warnings, care before info.
- From the 1099-K to the return: box 1a; add cash and other-tender sales; gross receipts; returns and allowances (Schedule C line 2; Forms 1120-S and 1065 line 1b); merchant fees (Schedule C line 10; Form 1120-S line 19; Form 1065 line 21). Two checkboxes, shown only when there is tax or tips, to leave sales tax or tips out of gross receipts; when ticked, show the reduced figure and that line 1 is now below the 1099-K. When DIFFERS, say "Not for the return yet" above it and above the entry.
- From the 1099-K to the bank: gross, less refunds, chargebacks and fees, add money moved in, personal transfers and other, less held, equals payouts. It must foot from top to bottom.
- The entry, with what it starts from (salesBooked) and the proof (salesAfter), and notes for sales tax and tips.
- To ask the client; the checks to make on the 1099-K itself (payee TIN, box 4 backup withholding, state boxes, one form per account, months against 5a to 5l); month by month (open when DIFFERS); what was read; footer (data stays here, cents, the accountant is responsible).

## The report object (window.__report), amounts in dollars
```
{ version:"1.0.0", file, status, processor:"square"|"stripe"|"paypal", layout, year, rowsRead,
  box1a, box3, monthly:[12],
  bridge:{ gross, salesTax, tips, notOn1099K, giftRedeemed, grossReceipts, grossReceiptsExcluding, refunds, chargebacks, returns,
           refundTax, fees, personal, transfersIn, other, netActivity, payouts, held },
  entry:{ date, lines:[{account, debit, credit}], salesBooked, salesAfter, totalDebit, totalCredit },
  exceptions:[{code, level, message}], typedBox1a, difference, boundary, duplicates (a number), missingMonths (an array of month numbers), outside, foreign, months:[...] }
```
Use exactly these account names in the entry.

## The made-up sample
Behind the sample link, a built-in Square year for a small café: card and cash sales with 8.25% sales tax, card tips, and one refund.
````
