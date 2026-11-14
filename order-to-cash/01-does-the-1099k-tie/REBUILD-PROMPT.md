# Rebuild prompt

Paste everything between the two lines into a fresh AI coding session. The result is "the same
agent" if it passes the same acceptance test: `node tests/run-tests.js path/to/your-build.html`.

---

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
