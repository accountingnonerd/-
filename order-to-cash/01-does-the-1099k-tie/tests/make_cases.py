#!/usr/bin/env python3
"""Builds the acceptance test for Order-to-Cash 01, "Does the 1099-K tie?".

Each case is one processor export (Square transactions, Stripe balance activity, or PayPal
activity) for a year. The files are written from a transaction model of three invented
businesses, and the answer key is worked out from the model and the problems planted in it,
never by reading the files back. Money is held in integer cents.

The rules the key follows (IRS Form 1099-K instructions, box 1a, and boxes 5a-5l):
  gross = card and app payments for goods and services, before refunds, fees, discounts,
          including sales tax, tips and shipping, on the date of the transaction.
  Not in gross: cash, the seller's own gift cards, other tenders, personal transfers, money
  moved in from the bank, refunds, chargebacks.

Run:  python3 make_cases.py      writes cases/* and answer-key.json
"""
import csv, json, os, random
from datetime import date, datetime, timedelta
from openpyxl import Workbook

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cases")
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))
Y = 2025

def rnd(x):  # half up, to cents
    return int(x + 0.5) if x >= 0 else -int(-x + 0.5)

def usd(c, dollar=True, paren=False):
    s = f"{abs(c) // 100:,}.{abs(c) % 100:02d}"
    if dollar: s = "$" + s
    if c < 0: return f"({s})" if paren else "-" + s
    return s

# ------------------------------------------------------------------ the model
# A transaction: dict(kind, id, dt (local datetime), card, cash, gift, other, tax, tip, fee, payout_date, ref, ...)
# kind: sale | refund | chargeback | chargeback_reversal | payout | transfer_in | personal | hold | hold_release | fee_only

def square_year(seed, per_day=(3, 7), months=range(1, 13), year=Y):
    """A café on Square: card, cash and gift-card tenders, 8.25% sales tax, card tips."""
    r = random.Random(seed)
    tx, n = [], 0
    d = date(year, 1, 1)
    while d.year == year:
        if d.month in months:
            for _ in range(r.randint(*per_day)):
                n += 1
                net_sales = r.randint(450, 4200)
                tax = rnd(net_sales * 0.0825)
                tender = r.random()
                tip = rnd(net_sales * r.choice([0, 0.10, 0.15, 0.18, 0.20])) if tender < 0.78 else 0
                total = net_sales + tax + tip
                card = cash = gift = 0
                if tender < 0.78: card = total
                elif tender < 0.95: cash = total
                else: gift = total
                fee = -(rnd(card * 0.026) + 15) if card else 0
                t = datetime(d.year, d.month, d.day, r.randint(7, 17), r.randint(0, 59), r.randint(0, 59))
                dep = d + timedelta(days=1 if d.weekday() < 4 else 7 - d.weekday())
                tx.append(dict(kind="sale", id=f"SQ{seed}{n:06d}", dt=t, net_sales=net_sales, tax=tax, tip=tip, card=card, cash=cash, gift=gift,
                               other=0, fee=fee, payout_date=dep if card else None))
        d += timedelta(days=1)
    return tx

def square_refund(sale, dt, amount=None, rid=None):
    """A refund of all or part of a card sale, as its own row (Square does not return the fee)."""
    amt = sale["card"] if amount is None else amount
    return dict(kind="refund", id=rid or sale["id"], dt=dt, net_sales=-amt, tax=0, tip=0, card=-amt, cash=0, gift=0, other=0, fee=0,
                payout_date=(dt + timedelta(days=1)).date(), refund_of=sale["id"])

def stripe_year(seed, months=range(1, 13), year=Y, per_week=(9, 16)):
    """An online shop on Stripe: card charges, weekly payouts, 2.9% + 30c."""
    r = random.Random(seed)
    tx, n = [], 0
    d = date(year, 1, 1)
    while d.year == year:
        if d.month in months:
            for _ in range(r.randint(*per_week) if d.weekday() == 0 else 0):
                n += 1
                day = d + timedelta(days=r.randint(0, 6))
                if day.year != year or day.month not in months: continue
                amt = r.randint(2400, 18900)
                t = datetime(day.year, day.month, day.day, r.randint(8, 21), r.randint(0, 59), r.randint(0, 59))
                tx.append(dict(kind="sale", id=f"txn_{seed}{n:05d}", ch=f"ch_{seed}{n:05d}", dt=t, card=amt, fee=-(rnd(amt * 0.029) + 30)))
        d += timedelta(days=1)
    tx.sort(key=lambda x: x["dt"])
    return tx

def stripe_payouts(tx, year=Y):
    """Every Tuesday, Stripe pays out the balance available (activity up to the previous Friday)."""
    out, bal_rows, d = [], sorted([t for t in tx if t["kind"] != "payout"], key=lambda t: t["dt"]), date(year, 1, 7)
    paid_upto = datetime(year, 1, 1)
    i = 0
    while d.year == year:
        if d.weekday() == 1:
            cutoff = datetime(d.year, d.month, d.day) - timedelta(days=4)
            amt = sum(net(t) for t in bal_rows if paid_upto <= t["dt"] < cutoff)
            if amt > 0:
                i += 1
                out.append(dict(kind="payout", id=f"txn_po{i:04d}", po=f"po_{i:04d}", dt=datetime(d.year, d.month, d.day, 2, 0, 0), card=0, fee=0, payout=-amt))
                paid_upto = cutoff
        d += timedelta(days=1)
    return out

def net(t):
    if t["kind"] == "payout": return t["payout"]
    return t.get("card", 0) + t.get("fee", 0)

def paypal_year(seed, year=Y):
    """A print seller on PayPal: goods-and-services payments, 3.49% + 49c, monthly withdrawals."""
    r = random.Random(seed)
    tx, n = [], 0
    d = date(year, 1, 1)
    while d.year == year:
        if r.random() < 0.55:
            n += 1
            amt = r.randint(1800, 14500)
            ship = r.choice([0, 0, 595, 895])
            tax = rnd(amt * 0.07) if r.random() < 0.3 else 0
            total = amt + ship + tax
            t = datetime(d.year, d.month, d.day, r.randint(6, 22), r.randint(0, 59), r.randint(0, 59))
            tx.append(dict(kind="sale", id=f"{seed}PP{n:06d}X", dt=t, card=total, ship=ship, tax=tax, fee=-(rnd(total * 0.0349) + 49),
                           ptype=r.choice(["Express Checkout Payment", "Website Payment", "Mobile Payment"]), name=r.choice(["J. Okafor", "L. Brandt", "M. Silva", "A. Novak", "R. Chen", "T. Haddad"])))
        d += timedelta(days=1)
    return tx

def paypal_withdrawals(tx, year=Y):
    """On the 3rd of each month, withdraw the whole balance to the bank."""
    out, bal, i = [], 0, 0
    events = sorted(tx, key=lambda t: t["dt"])
    for m in range(2, 14):
        yy, mm = (year, m) if m <= 12 else (year + 1, 1)
        when = datetime(yy, mm, 3, 9, 0, 0)
        bal = sum(paypal_net(t) for t in events if t["dt"] < when) + sum(o["card"] for o in out)
        if bal > 0 and yy == year:
            i += 1
            out.append(dict(kind="payout", id=f"WD{i:04d}PAYPAL", dt=when, card=-bal, fee=0))
    return out

def paypal_net(t):
    if t["kind"] in ("hold", "hold_release", "conversion_out", "conversion_in"): return t["card"]
    return t["card"] + t.get("fee", 0)

# ------------------------------------------------------------------ writers
SQ_COLS = ["Date", "Time", "Time Zone", "Gross Sales", "Discounts", "Service Charges", "Net Sales", "Gift Card Sales", "Tax", "Tip",
           "Partial Refunds", "Total Collected", "Source", "Card", "Card Entry Methods", "Cash", "Square Gift Card", "Other Tender",
           "Other Tender Type", "Tender Note", "Fees", "Net Total", "Transaction ID", "Payment ID", "Card Brand", "PAN Suffix",
           "Device Name", "Staff Name", "Staff ID", "Details", "Description", "Event Type", "Location", "Dining Option", "Customer ID",
           "Customer Name", "Customer Reference ID", "Device Nickname", "Third Party Fees", "Deposit ID", "Deposit Date", "Deposit Details",
           "Fee Percentage Rate", "Fee Fixed Rate", "Refund Reason", "Discount Name", "Transaction Status", "Cash App", "Order Reference ID",
           "Fulfillment Note", "Free Processing Applied", "Channel", "Unattributed Tips"]

def sq_row(t, iso=False, paren=False, location="Juniper Street"):
    m = lambda c: usd(c, True, paren)
    total = t["card"] + t["cash"] + t["gift"] + t["other"]
    gross_sales = t["net_sales"]
    ev = "Payment" if t["kind"] == "sale" else "Refund"
    dep = t.get("payout_date")
    depid = ("DEP" + dep.strftime("%Y%m%d")) if dep else ""
    row = {
        "Date": t["dt"].strftime("%Y-%m-%d") if iso else t["dt"].strftime("%m/%d/%Y"), "Time": t["dt"].strftime("%H:%M:%S"),
        "Time Zone": "Central Time (US & Canada)", "Gross Sales": m(gross_sales), "Discounts": m(0), "Service Charges": m(0),
        "Net Sales": m(gross_sales), "Gift Card Sales": m(0), "Tax": m(t["tax"]), "Tip": m(t["tip"]), "Partial Refunds": m(0),
        "Total Collected": m(total), "Source": "Square Point of Sale", "Card": m(t["card"]), "Card Entry Methods": "Contactless" if t["card"] else "",
        "Cash": m(t["cash"]), "Square Gift Card": m(t["gift"]), "Other Tender": m(t["other"]), "Other Tender Type": "Check" if t["other"] else "",
        "Tender Note": "", "Fees": m(t["fee"]), "Net Total": m(total + t["fee"]), "Transaction ID": t["id"], "Payment ID": "P" + t["id"][2:],
        "Card Brand": "Visa" if t["card"] else "", "PAN Suffix": "4242" if t["card"] else "", "Device Name": "Counter 1", "Staff Name": "",
        "Staff ID": "", "Details": "", "Description": "Custom Amount", "Event Type": ev, "Location": location, "Dining Option": "",
        "Customer ID": "", "Customer Name": "", "Customer Reference ID": "", "Device Nickname": "", "Third Party Fees": m(0),
        "Deposit ID": depid, "Deposit Date": (dep.strftime("%Y-%m-%d") if iso else dep.strftime("%m/%d/%Y")) if dep else "",
        "Deposit Details": "", "Fee Percentage Rate": "2.6" if t["card"] else "0", "Fee Fixed Rate": "$0.15" if t["card"] else "$0.00",
        "Refund Reason": "Returned goods" if ev == "Refund" else "", "Discount Name": "", "Transaction Status": t.get("status", "Complete"),
        "Cash App": m(0), "Order Reference ID": "", "Fulfillment Note": "", "Free Processing Applied": m(0), "Channel": location,
        "Unattributed Tips": "",
    }
    return [row[c] for c in SQ_COLS]

def write_square(path, txs, iso=False, paren=False, xlsx=False, extras=None, location="Juniper Street"):
    rows = [SQ_COLS] + [sq_row(t, iso, paren, location) for t in sorted(txs, key=lambda t: t["dt"])]
    if extras: rows = extras(rows)
    if xlsx:
        wb = Workbook(); ws = wb.active; ws.title = "Transactions"
        for r in rows: ws.append(r)
        wb.save(path); return
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

ST_COLS = ["balance_transaction_id", "created_utc", "created", "available_on_utc", "available_on", "currency", "gross", "fee", "net",
           "reporting_category", "source_id", "description", "customer_facing_amount", "customer_facing_currency", "automatic_payout_id",
           "automatic_payout_effective_at", "customer_id", "customer_email", "charge_id", "payment_intent_id", "card_brand", "card_country",
           "dispute_reason"]

def write_stripe(path, txs, local=True):
    """Stripe: Reports > Balance > Balance change from activity > Download (itemized). created_utc is UTC; created is
    in the report's time zone (America/Los_Angeles here) when chosen."""
    cols = ST_COLS if local else [c for c in ST_COLS if c not in ("created", "available_on")]
    rows = [cols]
    for t in sorted(txs, key=lambda t: t["dt"]):
        utc = t["dt"] + timedelta(hours=8)     # the model's times are Pacific
        cat = {"sale": "charge", "refund": "refund", "chargeback": "dispute", "chargeback_reversal": "dispute_reversal", "payout": "payout"}[t["kind"]]
        if t["kind"] == "payout": g, fe, ne = t["payout"], 0, t["payout"]
        else: g, fe, ne = t["card"], -t["fee"], t["card"] + t["fee"]
        r = {"balance_transaction_id": t["id"], "created_utc": utc.strftime("%Y-%m-%d %H:%M:%S"), "created": t["dt"].strftime("%Y-%m-%d %H:%M:%S"),
             "available_on_utc": (utc + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), "available_on": (t["dt"] + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
             "currency": "usd", "gross": f"{g / 100:.2f}", "fee": f"{fe / 100:.2f}", "net": f"{ne / 100:.2f}", "reporting_category": cat,
             "source_id": t.get("po") or t.get("ch") or t["id"].replace("txn_", "re_"), "description": t.get("desc", ""),
             "customer_facing_amount": f"{t.get('cf_amt', g) / 100:.2f}" if cat == "charge" else "", "customer_facing_currency": t.get("cf_cur", "usd") if cat == "charge" else "",
             "automatic_payout_id": "", "automatic_payout_effective_at": "", "customer_id": "", "customer_email": "", "charge_id": t.get("ch", ""),
             "payment_intent_id": "", "card_brand": "visa" if cat == "charge" else "", "card_country": "US" if cat == "charge" else "",
             "dispute_reason": "fraudulent" if cat.startswith("dispute") else ""}
        rows.append([r[c] for c in cols])
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

PP_COLS = ["Date", "Time", "TimeZone", "Name", "Type", "Status", "Currency", "Gross", "Fee", "Net", "From Email Address", "To Email Address",
           "Transaction ID", "Shipping Address", "Address Status", "Item Title", "Item ID", "Shipping and Handling Amount", "Insurance Amount",
           "Sales Tax", "Option 1 Name", "Option 1 Value", "Option 2 Name", "Option 2 Value", "Reference Txn ID", "Invoice Number",
           "Custom Number", "Quantity", "Receipt ID", "Balance", "Subject", "Note", "Country Code", "Balance Impact"]

SETTLED = ("Completed", "Complete", "Refunded", "Partially Refunded", "Reversed")
def write_paypal(path, txs):
    """PayPal: Activity > Statements > Activity download, all transactions, CSV."""
    rows = [PP_COLS]
    p = lambda c: f"{'-' if c < 0 else ''}{abs(c) // 100:,}.{abs(c) % 100:02d}"
    bal = 0
    for t in sorted(txs, key=lambda t: t["dt"]):
        k = t["kind"]
        typ = {"sale": t.get("ptype", "Express Checkout Payment"), "refund": "Payment Refund", "chargeback": "Chargeback",
               "chargeback_reversal": "Chargeback Reversal", "payout": "General Withdrawal", "transfer_in": "Bank Deposit to PP Account",
               "personal": "General Payment", "hold": "Hold on Balance for Dispute Investigation", "hold_release": "Reversal of General Account Hold",
               "fee_only": "Chargeback Fee", "conversion_out": "General Currency Conversion", "conversion_in": "General Currency Conversion",
               "vendor_refund": "Payment Refund", "purchase": "Express Checkout Payment"}[k]
        if k == "sale" and t.get("goods_general"): typ = "General Payment"
        cur = t.get("cur", "USD")
        g, fe = t["card"], t.get("fee", 0)
        ne = g + fe
        if cur == "USD" and t.get("status", "Completed") in SETTLED: bal += ne
        rows.append([t["dt"].strftime("%m/%d/%Y"), t["dt"].strftime("%H:%M:%S"), "PST", t.get("name", ""), typ, t.get("status", "Completed"), cur,
                     p(g), p(fe), p(ne), "buyer@example.com" if g > 0 else "seller@example.com", "seller@example.com" if g > 0 else "",
                     t["id"], "", "", "Print order" if k == "sale" else "", "", p(t.get("ship", 0)), "0.00", p(t.get("tax", 0)), "", "", "", "",
                     t.get("ref", ""), "", "", "1" if k == "sale" else "", "", p(bal), "", "", "US", "Credit" if ne > 0 else ("Debit" if ne < 0 else "Memo")])
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

# ------------------------------------------------------------------ the answer key, from the model
def key_for(txs, *, processor, year=Y, box1a=None, utc=False):
    """What the tool should report, from the model.
    sales: card/app money for goods and services in the year (gross for 1099-K box 1a)."""
    when = (lambda t: t["dt"] + timedelta(hours=8)) if utc else (lambda t: t["dt"])   # a UTC-only file dates everything in UTC
    inyear = lambda t: when(t).year == year
    sales = [dict(t) for t in txs if t["kind"] == "sale" and inyear(t) and t.get("status", "Completed") in SETTLED and t["card"] > 0]
    for t in sales:   # a sale in another currency counts in dollars at PayPal's own conversion rate (USD received / EUR converted)
        if t.get("cur", "USD") != "USD":
            eur_net = -sum(x["card"] for x in txs if x["kind"] == "conversion_out" and x.get("ref") == t["id"])
            usd = sum(x["card"] for x in txs if x["kind"] == "conversion_in" and x.get("ref") == t["id"])
            g = rnd(t["card"] * usd / eur_net)
            t["card"], t["fee"], t["usd_net"] = g, -(g - usd), usd
    gross = sum(t["card"] for t in sales)
    monthly = [sum(t["card"] for t in sales if when(t).month == m) for m in range(1, 13)]
    count = len(sales)
    ok = lambda t: inyear(t) and t.get("status", "Completed") in SETTLED and t.get("cur", "USD") == "USD"
    allsales = [t for t in txs if t["kind"] == "sale" and ok(t)]
    # sales tax and tips on every tender except the business's own gift cards (one tender per sale in this model)
    salestax = sum(t.get("tax", 0) for t in allsales if not t.get("gift"))
    tips = sum(t.get("tip", 0) for t in allsales if not t.get("gift"))
    refunds = -sum(t["card"] for t in txs if t["kind"] == "refund" and ok(t))
    cb = -sum(t["card"] for t in txs if t["kind"] == "chargeback" and ok(t)) - sum(t["card"] for t in txs if t["kind"] == "chargeback_reversal" and ok(t))
    fees = -sum(t.get("fee", 0) for t in txs if ok(t) and t["kind"] in ("refund", "chargeback", "chargeback_reversal", "fee_only")) - sum(t.get("fee", 0) for t in sales)
    fees += -sum(t["card"] for t in txs if ok(t) and t["kind"] == "fee_only")
    notcard = sum(t.get("cash", 0) + t.get("other", 0) for t in allsales)
    gift = sum(t.get("gift", 0) for t in allsales)
    other = sum(t["card"] for t in txs if t["kind"] in ("vendor_refund", "purchase") and ok(t))
    personal = sum(t["card"] for t in txs if t["kind"] == "personal" and ok(t))
    transfers_in = sum(t["card"] for t in txs if t["kind"] == "transfer_in" and ok(t))
    if processor == "square":
        payouts = sum(t["card"] + t["fee"] for t in txs if ok(t) and t.get("payout_date") and t["payout_date"].year == year and t["kind"] in ("sale", "refund"))
    else:
        payouts = -sum(t.get("payout", t["card"]) for t in txs if t["kind"] == "payout" and ok(t))
    gross_receipts = gross + notcard              # with sales tax and tips, as the 1099-K counts them
    returns = refunds + cb
    net_activity = gross - refunds - cb - fees
    held = net_activity + transfers_in + personal + other - payouts
    # the entry for books that recorded each payout as sales: after it, sales = the 1099-K gross
    lines = []
    def L(a, c):
        if c: lines.append({"account": a, "debit": c / 100 if c > 0 else 0, "credit": -c / 100 if c < 0 else 0})
    owner = transfers_in + personal
    sales_cr = fees + returns + held - owner - other
    assert payouts + sales_cr == gross
    L("Merchant fees", fees); L("Sales returns and allowances", returns); L("Due from processor", held)
    L("Owner contributions", -owner); L("Other activity to classify", -other); L("Sales", -sales_cr)
    k = {"year": year, "box1a": gross / 100, "box3": count, "monthly": [m / 100 for m in monthly],
         "bridge": {"gross": gross / 100, "salesTax": salestax / 100, "tips": tips / 100, "refunds": refunds / 100, "chargebacks": cb / 100,
                    "fees": fees / 100, "notOn1099K": notcard / 100, "giftRedeemed": gift / 100, "personal": personal / 100, "transfersIn": transfers_in / 100,
                    "other": other / 100, "grossReceipts": gross_receipts / 100, "grossReceiptsExcluding": (gross_receipts - salestax - tips) / 100,
                    "returns": returns / 100, "netActivity": net_activity / 100, "payouts": payouts / 100, "held": held / 100},
         "entry": lines}
    if box1a is not None:
        k["typedBox1a"] = box1a / 100
        k["difference"] = (box1a - gross) / 100
    return k

KEY = {}
def case(cid, title, kind, file, status, exceptions, extra=None, processor=None):
    e = {"title": title, "kind": kind, "file": file, "status": status, "exceptions": sorted(exceptions), "noOtherExceptions": True}
    if processor: e["processor"] = processor
    if extra: e.update(extra)
    KEY[cid] = e
P = lambda n: os.path.join(OUT, n)

# ---- 01 Square café, a full year: card, cash, gift cards, tips, sales tax; some December sales paid out in January
S1 = square_year(11)
write_square(P("01-square-juniper-street-2025.csv"), S1)
case("01", "Square café, full year: cash, gift cards, tips and sales tax", "clean", "01-square-juniper-street-2025.csv", "COMPUTED",
     ["SALES_TAX_IN_GROSS", "TIPS_IN_GROSS", "NOT_ON_1099K"], key_for(S1, processor="square"), "square")

# ---- 02 the same, with the 1099-K's box 1a typed in: it ties
k = key_for(S1, processor="square", box1a=sum(t["card"] for t in S1 if t["kind"] == "sale"))
case("02", "Square café with the 1099-K typed in: it ties", "clean", "01-square-juniper-street-2025.csv", "TIES",
     ["SALES_TAX_IN_GROSS", "TIPS_IN_GROSS", "NOT_ON_1099K"], k, "square")

# ---- 03 Stripe online shop: refunds, a lost dispute and a won dispute, a euro charge, UTC dates only
S3 = stripe_year(31)
r = random.Random(3)
sales3 = [t for t in S3 if t["kind"] == "sale"]
for i, s in enumerate(r.sample(sales3, 9)):
    amt = s["card"] if i % 3 else s["card"] // 2
    S3.append(dict(kind="refund", id=f"txn_rf3{i:03d}", dt=s["dt"] + timedelta(days=r.randint(1, 9)), card=-amt, fee=0))
d1, d2 = sales3[40], sales3[120]
S3.append(dict(kind="chargeback", id="txn_dp3001", dt=d1["dt"] + timedelta(days=20), card=-d1["card"], fee=-1500))
S3.append(dict(kind="chargeback", id="txn_dp3002", dt=d2["dt"] + timedelta(days=15), card=-d2["card"], fee=-1500))
S3.append(dict(kind="chargeback_reversal", id="txn_dr3002", dt=d2["dt"] + timedelta(days=50), card=d2["card"], fee=1500))
sales3[60]["cf_amt"], sales3[60]["cf_cur"] = 8800, "eur"
# a sale at 6:40 pm Pacific on December 31: in UTC it is already January 1
late = dict(kind="sale", id="txn_3late", ch="ch_3late", dt=datetime(Y, 12, 31, 18, 40, 0), card=12500, fee=-(rnd(12500 * 0.029) + 30)); S3.append(late)
S3 = [t for t in S3 if t["dt"].year == Y]
S3 += stripe_payouts(S3)
write_stripe(P("03-stripe-fernhill-ceramics-2025.csv"), S3, local=False)
# with UTC dates only, the 6:40 pm December 31 sale reads as January 1, 2026: outside the year in the file
k3x = key_for(S3, processor="stripe", utc=True)
def edge(yy):   # sales in the first 8 hours of January 1 of year yy, UTC
    e = [t for t in S3 if t["kind"] == "sale" and (t["dt"] + timedelta(hours=8)).date() == date(yy, 1, 1) and (t["dt"] + timedelta(hours=8)).hour < 8]
    return {"count": len(e), "amount": sum(t["card"] for t in e) / 100}
k3x["boundary"] = {"intoNextYear": edge(Y + 1), "fromPriorYear": edge(Y)}
case("03", "Stripe shop: refunds, disputes, a euro charge, dates in UTC only", "ugly", "03-stripe-fernhill-ceramics-2025.csv", "COMPUTED",
     ["UTC_DATES", "OUTSIDE_YEAR", "NO_TAX_DETAIL"], k3x, "stripe")

# ---- 04 PayPal print seller: refunds, two personal transfers, money moved in from the bank, a hold, a chargeback with fee, a euro sale
S4 = paypal_year(41)
r = random.Random(4)
sales4 = [t for t in S4 if t["kind"] == "sale"]
for i, s in enumerate(r.sample(sales4, 6)):
    S4.append(dict(kind="refund", id=f"4RF{i:05d}X", dt=s["dt"] + timedelta(days=3), card=-s["card"], fee=0, ref=s["id"], name=s["name"]))
    s["status"] = "Refunded"          # PayPal re-labels the original payment once it is refunded
S4.append(dict(kind="purchase", id="4PU00001X", dt=datetime(Y, 9, 9, 10, 0), card=-12000, fee=0, name="Inkwell Supply Co."))
S4.append(dict(kind="vendor_refund", id="4VR00001X", dt=datetime(Y, 9, 20, 10, 0), card=4500, fee=0, name="Inkwell Supply Co."))
S4.append(dict(kind="personal", id="4GP00001X", dt=datetime(Y, 3, 14, 12, 0), card=25000, fee=0, name="Dana Rivera"))
S4.append(dict(kind="personal", id="4GP00002X", dt=datetime(Y, 8, 2, 9, 30), card=6000, fee=0, name="Dana Rivera"))
S4.append(dict(kind="transfer_in", id="4BD00001X", dt=datetime(Y, 5, 20, 8, 0), card=50000, fee=0))
c = sales4[30]
S4.append(dict(kind="hold", id="4HD00001X", dt=c["dt"] + timedelta(days=10), card=-c["card"], fee=0, ref=c["id"]))
S4.append(dict(kind="chargeback", id="4CB00001X", dt=c["dt"] + timedelta(days=24), card=-c["card"], fee=0, ref=c["id"]))
S4.append(dict(kind="hold_release", id="4HR00001X", dt=c["dt"] + timedelta(days=24, minutes=1), card=c["card"], fee=0, ref=c["id"]))
S4.append(dict(kind="fee_only", id="4CF00001X", dt=c["dt"] + timedelta(days=24, minutes=2), card=-2000, fee=0, ref=c["id"]))
eur = dict(kind="sale", id="4EU00001X", dt=datetime(Y, 6, 11, 15, 0), card=7500, fee=-(rnd(7500 * 0.0349) + 39), cur="EUR", name="K. Weber")
S4.append(eur)
S4.append(dict(kind="conversion_out", id="4CV00001X", dt=eur["dt"] + timedelta(minutes=1), card=-(7500 - (rnd(7500 * 0.0349) + 39)), fee=0, cur="EUR", ref=eur["id"]))
S4.append(dict(kind="conversion_in", id="4CV00002X", dt=eur["dt"] + timedelta(minutes=1), card=7712, fee=0, ref=eur["id"]))
S4 += paypal_withdrawals([t for t in S4 if t.get("cur", "USD") == "USD"])
write_paypal(P("04-paypal-ridgeline-prints-2025.csv"), S4)
k4 = key_for(S4, processor="paypal")
k4["foreign"] = {"count": 1, "usd": rnd(7500 * 7712 / 7199) / 100}   # EUR 75.00 at PayPal's rate: USD 77.12 for EUR 71.99 net
case("04", "PayPal seller: refunds, personal transfers, a bank top-up, a hold, a chargeback, a euro sale, a purchase from the balance", "ugly", "04-paypal-ridgeline-prints-2025.csv", "COMPUTED",
     ["PERSONAL_TRANSFERS", "FOREIGN_CURRENCY", "SALES_TAX_IN_GROSS", "OTHER_ACTIVITY", "BELOW_THRESHOLD"], k4, "paypal")

# ---- 05 planted: two Square exports pasted together, June in both
S5 = square_year(52)
def dup_june(rows):
    june = [r for r in rows[1:] if r[0].startswith("06/")]
    return rows + june
write_square(P("05-square-two-exports-pasted.csv"), S5, extras=dup_june)
nd = sum(1 for t in S5 if t["dt"].month == 6)
case("05", "Planted: two exports pasted together, June counted twice", "planted", "05-square-two-exports-pasted.csv", "COMPUTED",
     ["DUPLICATE_ROWS", "SALES_TAX_IN_GROSS", "TIPS_IN_GROSS", "NOT_ON_1099K"], {**key_for(S5, processor="square"), "duplicates": nd}, "square")

# ---- 06 planted: a Stripe export with September missing
S6 = stripe_year(61, months=[m for m in range(1, 13) if m != 9])
S6 += stripe_payouts(S6)
write_stripe(P("06-stripe-september-missing.csv"), S6)
case("06", "Planted: a Stripe export with no September", "planted", "06-stripe-september-missing.csv", "COMPUTED",
     ["MISSING_MONTH", "NO_TAX_DETAIL"], {**key_for(S6, processor="stripe"), "missingMonths": [9]}, "stripe")

# ---- 07 a PayPal export that runs from December 2024 to January 2026
S7 = paypal_year(71)
S7 += [dict(kind="sale", id=f"7OUT{i}X", dt=datetime(Y - 1, 12, 20 + i, 11, 0), card=4100 + i * 100, fee=-(rnd((4100 + i * 100) * 0.0349) + 49), name="E. Park") for i in range(3)]
S7 += [dict(kind="sale", id=f"7NXT{i}X", dt=datetime(Y + 1, 1, 5 + i, 11, 0), card=5100 + i * 100, fee=-(rnd((5100 + i * 100) * 0.0349) + 49), name="E. Park") for i in range(2)]
S7 += paypal_withdrawals([t for t in S7 if t["dt"].year == Y])
write_paypal(P("07-paypal-dec-to-jan.csv"), S7)
case("07", "A PayPal export from December 2024 to January 2026", "ugly", "07-paypal-dec-to-jan.csv", "COMPUTED",
     ["OUTSIDE_YEAR", "SALES_TAX_IN_GROSS", "BELOW_THRESHOLD"], {**key_for(S7, processor="paypal"), "outside": {"count": 5}}, "paypal")

# ---- 08 planted: the 1099-K's box 1a is higher by another location's sales
S8 = square_year(81)
g8 = sum(t["card"] for t in S8 if t["kind"] == "sale")
k8 = key_for(S8, processor="square", box1a=g8 + 218400)
case("08", "Planted: the 1099-K includes a second location not in this export", "planted", "08-square-one-location.csv", "DIFFERS",
     ["SALES_TAX_IN_GROSS", "TIPS_IN_GROSS", "NOT_ON_1099K", "DIFFERS_FROM_1099K"], k8, "square")
write_square(P("08-square-one-location.csv"), S8)

# ---- 09 Square in Excel: dollar signs, parentheses, a totals row, blank lines, ISO dates
S9 = square_year(91, per_day=(2, 4))
def add_totals(rows):
    body = rows[1:]
    blank = [""] * len(SQ_COLS)
    tot = list(blank); tot[0] = "Totals"
    return [rows[0]] + body[:200] + [blank] + body[200:] + [blank, tot]
write_square(P("09-square-excel-with-totals.xlsx"), S9, iso=True, paren=True, xlsx=True, extras=add_totals)
case("09", "Square export in Excel with a totals row, blank lines, parentheses", "ugly", "09-square-excel-with-totals.xlsx", "COMPUTED",
     ["SALES_TAX_IN_GROSS", "TIPS_IN_GROSS", "NOT_ON_1099K"], key_for(S9, processor="square"), "square")

# ---- 10 not a processor export: a bank statement
with open(P("10-bank-statement.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Date", "Description", "Withdrawals", "Deposits", "Balance"])
    w.writerow(["01/02/2025", "SQUARE INC DEP", "", "1,204.55", "8,410.10"]); w.writerow(["01/03/2025", "RENT", "2,400.00", "", "6,010.10"])
case("10", "Not a processor export: a bank statement", "ugly", "10-bank-statement.csv", "NOT_RECOGNIZED", ["NOT_RECOGNIZED"])

# ---- 11 Square: a January refund of a December 2024 sale, and partial refunds
S11 = square_year(111, per_day=(2, 5))
r = random.Random(11)
ghost = dict(kind="sale", id="SQ111GHOST", dt=datetime(Y - 1, 12, 28, 10, 0), net_sales=0, tax=0, tip=0, card=6400, cash=0, gift=0, other=0, fee=0)
S11.append(square_refund(ghost, datetime(Y, 1, 4, 11, 0), rid="SQ111GHOST"))
cards11 = [t for t in S11 if t["kind"] == "sale" and t["card"] > 2000]
for i, s in enumerate(r.sample(cards11, 5)):
    S11.append(square_refund(s, s["dt"] + timedelta(days=2), amount=s["card"] // 3))
write_square(P("11-square-refund-of-last-years-sale.csv"), S11)
case("11", "Square: partial refunds, and a January refund of a December 2024 sale", "ugly", "11-square-refund-of-last-years-sale.csv", "COMPUTED",
     ["REFUND_WITHOUT_SALE", "SALES_TAX_IN_GROSS", "TIPS_IN_GROSS", "NOT_ON_1099K"], key_for(S11, processor="square"), "square")

# ---- 12 PayPal: pending and denied payments that never settled
S12 = paypal_year(121)
S12.append(dict(kind="sale", id="12PEND01X", dt=datetime(Y, 12, 30, 20, 0), card=9900, fee=-(rnd(9900 * 0.0349) + 49), status="Pending", name="G. Ito"))
S12.append(dict(kind="sale", id="12DENY01X", dt=datetime(Y, 4, 2, 10, 0), card=15000, fee=0, status="Denied", name="H. Moss"))
S12 += paypal_withdrawals([t for t in S12 if t.get("status", "Completed") == "Completed"])
write_paypal(P("12-paypal-pending-and-denied.csv"), S12)
case("12", "PayPal: a pending and a denied payment", "ugly", "12-paypal-pending-and-denied.csv", "COMPUTED",
     ["NOT_SETTLED", "SALES_TAX_IN_GROSS", "BELOW_THRESHOLD"], key_for(S12, processor="paypal"), "paypal")

# ---- 13 Stripe with local dates and the 1099-K typed in: it ties
S13 = stripe_year(131)
S13 += stripe_payouts(S13)
write_stripe(P("13-stripe-local-dates.csv"), S13, local=True)
g13 = sum(t["card"] for t in S13 if t["kind"] == "sale")
case("13", "Stripe with local dates and the 1099-K typed in: it ties", "clean", "13-stripe-local-dates.csv", "TIES",
     ["NO_TAX_DETAIL"], key_for(S13, processor="stripe", box1a=g13), "stripe")

# ---- 14 planted: a PayPal 1099-K typed in that is lower than the transactions (a refund-netted figure)
k14 = key_for(S7, processor="paypal")
refunds14 = 0
case("14", "Planted: the 1099-K typed in is lower than the year's payments", "planted", "07-paypal-dec-to-jan.csv", "DIFFERS",
     ["OUTSIDE_YEAR", "SALES_TAX_IN_GROSS", "DIFFERS_FROM_1099K", "BELOW_THRESHOLD"],
     {**key_for(S7, processor="paypal", box1a=sum(t["card"] for t in S7 if t["kind"] == "sale" and t["dt"].year == Y) - 41250), "outside": {"count": 5}}, "paypal")

with open(os.path.join(HERE, "answer-key.json"), "w") as f:
    json.dump(KEY, f, indent=1)
print(len(KEY), "cases")
for cid, e in KEY.items():
    b = e.get("bridge", {})
    print(cid, e["status"], e["exceptions"], "box1a", e.get("box1a"), "n", e.get("box3"), "fees", b.get("fees"), "payouts", b.get("payouts"), "held", b.get("held"))
