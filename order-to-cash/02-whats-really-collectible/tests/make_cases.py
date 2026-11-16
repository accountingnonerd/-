#!/usr/bin/env python3
"""Builds the acceptance test for Order-to-Cash 02, "What's really collectible?".

Each case is one A/R aging detail report, as of October 31, 2026, in the layout of QuickBooks
Online, QuickBooks Desktop or Xero. The files are written from a model of open items (invoices,
unapplied payments, credit memos, journal entries) for three invented businesses, and the answer
key is worked out from the model with the rules below, never by reading the files back.
Money is held in integer cents.

The rules the key follows:
  days past due = as-of date - due date (0 or less is current); buckets: current, 1-30, 31-60,
    61-90, 91-180, 181-365, over 365.
  Clean-up, customer by customer:
    1. each credit (payment, credit memo, negative journal entry), oldest first, is matched to an
       open invoice of exactly the same amount (the oldest such invoice);
    2. if the customer's open items add up to zero or less, the customer is owed a refund or must
       confirm: listed as a credit balance, and not chased;
    3. otherwise each remaining credit is applied to the customer's oldest invoices.
  Duplicates: two open invoices of one customer with the same amount (at least $1), dated within
    7 days of each other, with different numbers.
  Small balances: an invoice whose remaining balance is above zero and below $10.00.
  Over a year: an invoice more than 365 days past due with a remaining balance.
  Write-off proposed: small balances plus over-a-year invoices, after the clean-up.
  Worklist: customers with an overdue remaining balance, ranked by the amount over 60 days past due,
    then by the overdue amount, then by name; the step follows the oldest overdue invoice.
  Allowance: the accountant's rates by bucket, applied to remaining balances not proposed for
    write-off.
  Concentration: a customer whose remaining balance is 20% or more of all remaining balances.

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
ASOF = date(2026, 10, 31)
BUCKETS = ["current", "d1_30", "d31_60", "d61_90", "d91_180", "d181_365", "over365"]

def days(it):
    return (ASOF - it["due"]).days

def bucket(d):
    if d <= 0: return "current"
    if d <= 30: return "d1_30"
    if d <= 60: return "d31_60"
    if d <= 90: return "d61_90"
    if d <= 180: return "d91_180"
    if d <= 365: return "d181_365"
    return "over365"

def money(c, dollar=False, paren=False):
    s = f"{abs(c) // 100:,}.{abs(c) % 100:02d}"
    if dollar: s = "$" + s
    if c < 0: return f"({s})" if paren else "-" + s
    return s

# ------------------------------------------------------------------ the model
FIRST = ["Alder", "Birch", "Cedar", "Delta", "Ember", "Falcon", "Granite", "Harbor", "Iron", "Juniper", "Keystone", "Lantern", "Maple", "Nimbus",
         "Orchard", "Pioneer", "Quarry", "Ridge", "Summit", "Timber", "Union", "Valley", "Willow", "Yarrow", "Zenith", "Beacon", "Copper", "Driftwood",
         "Evergreen", "Foxglove", "Garnet", "Hawthorn", "Indigo", "Jasper", "Kestrel", "Linden", "Meadow", "Northwind", "Oakridge", "Prairie"]
LAST = ["Builders", "Contracting", "Property Management", "Electric", "Restaurants", "Dental Group", "Schools", "Apartments", "Hotel", "Fitness",
        "Hardware", "Mechanical", "Roofing", "Landscaping", "Medical Center", "Storage", "Brewing", "Logistics", "Bakery", "Auto Body"]

def book(seed, n_customers=36, per=(1, 7), start=1000):
    """Open invoices as of October 31, 2026: mostly recent, a tail of older ones, some part-paid."""
    r = random.Random(seed)
    names = []
    while len(names) < n_customers:
        nm = f"{r.choice(FIRST)} {r.choice(LAST)}"
        if nm not in names: names.append(nm)
    items, num = [], start
    for c in names:
        for _ in range(r.randint(*per)):
            num += 1
            age = int(r.choices([r.randint(1, 30), r.randint(31, 60), r.randint(61, 95), r.randint(96, 200), r.randint(201, 330)], [52, 22, 12, 9, 5])[0])
            d = ASOF - timedelta(days=age)
            terms = r.choice([30, 30, 30, 15, 45])
            amt = r.randint(15000, 980000)
            open_ = amt if r.random() < 0.85 else amt - r.randint(1, (amt * 3 // 4) // 100) * 100   # part-paid: at least a quarter still open
            items.append(dict(customer=c, type="Invoice", date=d, due=d + timedelta(days=terms), num=str(num), amount=amt, open=open_, terms=terms))
    return names, items

def credit(customer, kind, d, amt, num=""):
    return dict(customer=customer, type=kind, date=d, due=d, num=num, amount=-amt, open=-amt, terms=0)

def inv(customer, d, amt, num, terms=30, open_=None):
    return dict(customer=customer, type="Invoice", date=d, due=d + timedelta(days=terms), num=num, amount=amt, open=amt if open_ is None else open_, terms=terms)

# ------------------------------------------------------------------ the answer key, from the model
def key_for(items, rates=None, typed=None):
    """What the tool should report, from the model, by the rules in the docstring."""
    rem = {id(i): i["open"] for i in items}
    custs = sorted(set(i["customer"] for i in items))
    matches, credit_bal, apply_oldest = [], [], []
    for c in custs:
        mine = [i for i in items if i["customer"] == c]
        credits = sorted([i for i in mine if i["open"] < 0], key=lambda i: (i["date"], i["num"]))
        invs = sorted([i for i in mine if i["open"] > 0], key=lambda i: (i["date"], i["num"]))
        for cr in credits:
            hit = [v for v in invs if rem[id(v)] == -rem[id(cr)] and rem[id(v)] == v["open"]]
            if hit:
                v = hit[0]
                matches.append({"customer": c, "credit": cr["num"] or cr["type"], "creditType": cr["type"], "invoice": v["num"], "amount": v["open"] / 100})
                rem[id(v)] = 0; rem[id(cr)] = 0
        net = sum(rem[id(i)] for i in mine)
        left = [cr for cr in credits if rem[id(cr)] < 0]
        if net <= 0 and (left or net < 0):
            if net < 0: credit_bal.append({"customer": c, "amount": -net / 100})
            for i in mine: rem[id(i)] = 0
            continue
        for cr in left:
            amt = -rem[id(cr)]
            apply_oldest.append({"customer": c, "credit": cr["num"] or cr["type"], "amount": amt / 100})
            for v in invs:
                if amt == 0: break
                take = min(amt, rem[id(v)])
                rem[id(v)] -= take; amt -= take
            rem[id(cr)] = 0
    pos = [i for i in items if rem[id(i)] > 0]
    small = [i for i in pos if rem[id(i)] < 1000 and i["type"] == "Invoice"]
    old = [i for i in pos if days(i) > 365 and i["type"] == "Invoice" and i not in small]
    wo = small + old
    # duplicates among open invoices as reported
    dups = []
    for c in custs:
        iv = sorted([i for i in items if i["customer"] == c and i["type"] == "Invoice" and i["open"] > 0], key=lambda i: (i["date"], i["num"]))
        for a in range(len(iv)):
            for b in range(a + 1, len(iv)):
                x, y = iv[a], iv[b]
                if x["amount"] == y["amount"] and x["amount"] >= 100 and abs((y["date"] - x["date"]).days) <= 7 and x["num"] != y["num"]:
                    dups.append({"customer": c, "a": x["num"], "b": y["num"], "amount": x["amount"] / 100})
    rep_buckets = {b: 0 for b in BUCKETS}
    for i in items: rep_buckets[bucket(days(i))] += i["open"]
    clean = {b: 0 for b in BUCKETS}
    for i in pos: clean[bucket(days(i))] += rem[id(i)]
    # worklist
    work = []
    for c in custs:
        mine = [i for i in pos if i["customer"] == c and days(i) > 0]
        if not mine: continue
        over60 = sum(rem[id(i)] for i in mine if days(i) > 60)
        overdue = sum(rem[id(i)] for i in mine)
        oldest = max(days(i) for i in mine)
        step = ("Friendly reminder" if oldest <= 30 else "Second reminder and a call" if oldest <= 60 else "Call; hold new orders" if oldest <= 90 else
                "Final notice" if oldest <= 180 else "Collection agency or payment plan" if oldest <= 365 else "Consider writing off")
        work.append({"customer": c, "overdue": overdue / 100, "over60": over60 / 100, "oldestDays": oldest, "step": step, "invoices": len(mine)})
    work.sort(key=lambda w: (-w["over60"], -w["overdue"], w["customer"]))
    total = sum(i["open"] for i in items)
    all_rem = sum(rem[id(i)] for i in pos)
    conc = []
    for c in custs:
        cr_ = sum(rem[id(i)] for i in pos if i["customer"] == c)
        if all_rem and cr_ * 100 >= 20 * all_rem: conc.append({"customer": c, "share": round(cr_ * 100 / all_rem, 1)})
    k = {"asOf": ASOF.isoformat(), "rows": len(items), "total": total / 100, "customers": len(custs),
         "buckets": {b: v / 100 for b, v in rep_buckets.items()}, "bucketsClean": {b: v / 100 for b, v in clean.items()},
         "matches": matches, "creditBalances": credit_bal, "applyOldest": apply_oldest, "duplicates": dups,
         "small": sorted(i["num"] for i in small), "old": sorted(i["num"] for i in old),
         "writeOff": sum(rem[id(i)] for i in wo) / 100, "worklist": work, "concentration": conc,
         "journalEntries": sum(1 for i in items if i["type"] == "Journal Entry")}
    if rates is not None:
        k["rates"] = rates
        half_up = lambda x: int(x + 0.5)
        k["allowance"] = sum(half_up(sum(rem[id(i)] for i in pos if bucket(days(i)) == b and i not in wo) * rates[b] / 100) for b in BUCKETS) / 100
    if typed is not None:
        k["typedAR"] = typed / 100; k["difference"] = (typed - total) / 100
    return k

# ------------------------------------------------------------------ writers
QBO_SECTIONS = [("current", "Current"), ("d1_30", "1 - 30 days past due"), ("d31_60", "31 - 60 days past due"), ("d61_90", "61 - 90 days past due"), ("91+", "91 or more days past due")]
def qsec(it):
    b = bucket(days(it))
    return b if b in ("current", "d1_30", "d31_60", "d61_90") else "91+"
def ds(d): return d.strftime("%m/%d/%Y")

def write_qbo(path, company, items, csv_out=False, paren=False, total_override=None, dup_rows=0):
    """QuickBooks Online: Reports > A/R Aging Detail > Export to Excel. Grouped by aging section."""
    rows = [[company], ["A/R Aging Detail"], ["As of October 31, 2026"], [], ["", "Date", "Transaction Type", "Num", "Customer", "Due Date", "Amount", "Open Balance"]]
    grand = 0
    for key, label in QBO_SECTIONS:
        sec = sorted([i for i in items if qsec(i) == key], key=lambda i: (i["date"], i["num"]))
        if not sec: continue
        rows.append([label])
        st = 0
        for i in sec:
            rows.append(["", ds(i["date"]), i["type"], i["num"], i["customer"], ds(i["due"]), i["amount"] / 100, i["open"] / 100])
            st += i["open"]
        if dup_rows and key == "d1_30":
            rows += [list(x) for x in rows[-dup_rows:]]
        rows.append([f"Total for {label}", "", "", "", "", "", "", st / 100])
        grand += st
    rows.append(["TOTAL", "", "", "", "", "", "", (total_override if total_override is not None else grand) / 100])
    rows += [[], [], ["Accrual Basis Monday, November 2, 2026 09:12 AM GMT-05:00"]]
    if csv_out:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL)
            for r in rows:
                w.writerow([money(round(v * 100), True, paren) if isinstance(v, float) else ("" if v is None else v) for v in r])
        return
    wb = Workbook(); ws = wb.active; ws.title = "AR Aging Detail"
    for r in rows: ws.append(r)
    wb.save(path)

DESK_SECTIONS = [("current", "Current"), ("d1_30", "1 - 30"), ("d31_60", "31 - 60"), ("d61_90", "61 - 90"), ("91+", "> 90")]
def write_desktop(path, items):
    """QuickBooks Desktop: Reports > Customers & Receivables > A/R Aging Detail > Excel. Title and date go to the
    Excel page header, so the cells carry no as-of date; the Aging column gives days past due."""
    wb = Workbook(); ws = wb.active; ws.title = "Sheet1"
    ws.append(["", "Type", "Date", "Num", "P. O. #", "Name", "Terms", "Due Date", "Class", "Aging", "Open Balance"])
    grand = 0
    for key, label in DESK_SECTIONS:
        sec = sorted([i for i in items if qsec(i) == key], key=lambda i: (i["date"], i["num"]))
        if not sec: continue
        ws.append([label])
        st = 0
        for i in sec:
            d = days(i)
            ws.append(["", i["type"], datetime(i["date"].year, i["date"].month, i["date"].day), i["num"], "", i["customer"],
                       f"Net {i['terms']}" if i["type"] == "Invoice" else "", datetime(i["due"].year, i["due"].month, i["due"].day), "",
                       d if d > 0 else None, i["open"] / 100])
            st += i["open"]
        ws.append([f"Total {label}", "", "", "", "", "", "", "", "", "", st / 100])
        grand += st
    ws.append(["TOTAL", "", "", "", "", "", "", "", "", "", grand / 100])
    for row in ws.iter_rows(min_row=2):
        for cell in (row[2], row[7]):
            if isinstance(cell.value, datetime): cell.number_format = "mm/dd/yyyy"
    wb.save(path)

XERO_COLS = ["Current", "1 Month", "2 Months", "3 Months", "Older"]
def xcol(it):
    d = days(it)
    return "Current" if d <= 0 else "1 Month" if d <= 30 else "2 Months" if d <= 60 else "3 Months" if d <= 90 else "Older"
def write_xero(path, company, items):
    """Xero: Reports > Aged Receivables Detail > Export to Excel. Grouped by contact; the amount sits in its
    ageing column and in Total. Credit notes and overpayments are negative."""
    wb = Workbook(); ws = wb.active; ws.title = "Aged Receivables Detail"
    for r in [["Aged Receivables Detail"], [company], ["As at 31 October 2026"], ["Ageing by due date"], [],
              ["Invoice Date", "Invoice Number", "Reference", "Due Date"] + XERO_COLS + ["Total"]]:
        ws.append(r)
    grand = 0
    for c in sorted(set(i["customer"] for i in items)):
        ws.append([c])
        st = 0
        for i in sorted([i for i in items if i["customer"] == c], key=lambda i: (i["date"], i["num"])):
            ref = {"Invoice": "", "Payment": "Overpayment", "Credit Memo": "Credit Note", "Journal Entry": "Manual journal"}[i["type"]]
            cells = [i["open"] / 100 if xcol(i) == col else None for col in XERO_COLS]
            ws.append([i["date"].strftime("%d %b %Y"), i["num"], ref, i["due"].strftime("%d %b %Y")] + cells + [i["open"] / 100])
            st += i["open"]
        ws.append([f"Total {c}"] + [""] * 8 + [st / 100])
        grand += st
    ws.append(["Total"] + [""] * 8 + [grand / 100])
    wb.save(path)

KEY = {}
def case(cid, title, kind, file, status, exceptions, extra=None, layout=None):
    e = {"title": title, "kind": kind, "file": file, "status": status, "exceptions": sorted(exceptions), "noOtherExceptions": True}
    if layout: e["layout"] = layout
    if extra: e.update(extra)
    KEY[cid] = e
P = lambda n: os.path.join(OUT, n)
D = lambda y, m, d: date(y, m, d)

# ---- 01 QuickBooks Online, a clean book: nothing to clean, just the worklist
N1, I1 = book(1)
write_qbo(P("01-northgate-ar-aging-detail.xlsx"), "Northgate Electrical Supply", I1)
case("01", "QuickBooks Online, a clean book", "clean", "01-northgate-ar-aging-detail.xlsx", "COMPUTED", [], key_for(I1), "qbo")

# ---- 02 the same, with A/R from the balance sheet typed in: it ties
case("02", "QuickBooks Online, A/R from the balance sheet typed in: it ties", "clean", "01-northgate-ar-aging-detail.xlsx", "TIES", [],
     key_for(I1, typed=sum(i["open"] for i in I1)), "qbo")

# ---- 03 planted: unapplied payments, a credit memo, a customer in credit
N3, I3 = book(3)
r = random.Random(33)
targets = r.sample([i for i in I3 if i["open"] == i["amount"] and days(i) > 20], 3)
for k_, t in enumerate(targets):        # three payments received but never applied to their invoice
    I3.append(credit(t["customer"], "Payment", t["date"] + timedelta(days=25 + k_), t["open"], ""))
c4 = [i for i in I3 if i["type"] == "Invoice" and i["open"] > 200000][0]          # a partial payment left unapplied
I3.append(credit(c4["customer"], "Payment", ASOF - timedelta(days=12), 100000, ""))
cm = [i for i in I3 if i["type"] == "Invoice" and i["customer"] != c4["customer"] and i not in targets][5]   # a credit memo for part of an invoice
I3.append(credit(cm["customer"], "Credit Memo", ASOF - timedelta(days=40), 25000, "CM-104"))
I3.append(inv("Quarry Hotel", D(2026, 8, 3), 84000, "9001"))                    # a customer who paid twice: net credit
I3.append(credit("Quarry Hotel", "Payment", D(2026, 9, 1), 84000, ""))
I3.append(credit("Quarry Hotel", "Payment", D(2026, 9, 4), 84000, ""))
write_qbo(P("03-planted-unapplied-credits.xlsx"), "Granite Facility Services", I3)
case("03", "Planted: unapplied payments, a credit memo, a customer who paid twice", "planted", "03-planted-unapplied-credits.xlsx", "COMPUTED",
     ["UNAPPLIED_CREDITS", "CREDIT_BALANCES"], key_for(I3), "qbo")

# ---- 04 planted: an invoice entered twice
N4, I4 = book(4)
dsrc = [i for i in I4 if i["type"] == "Invoice" and 10 < days(i) < 50][0]
I4.append(inv(dsrc["customer"], dsrc["date"] + timedelta(days=2), dsrc["amount"], str(int(dsrc["num"]) + 5000), dsrc["terms"]))
write_qbo(P("04-planted-duplicate-invoice.xlsx"), "Lantern Signs & Graphics", I4)
case("04", "Planted: the same invoice entered twice", "planted", "04-planted-duplicate-invoice.xlsx", "COMPUTED", ["DUPLICATE_INVOICES"], key_for(I4), "qbo")

# ---- 05 planted: A/R on the balance sheet does not agree with the aging
k5 = key_for(I1, typed=sum(i["open"] for i in I1) + 315000)
case("05", "Planted: the balance sheet's A/R is $3,150.00 more than the aging", "planted", "01-northgate-ar-aging-detail.xlsx", "DIFFERS",
     ["DIFFERS_FROM_BALANCE_SHEET"], k5, "qbo")

# ---- 06 Xero: credit notes and an overpayment
N6, I6 = book(6, n_customers=24)
x = [i for i in I6 if i["type"] == "Invoice"][3]
I6.append(credit(x["customer"], "Credit Memo", x["date"] + timedelta(days=5), x["open"], "CN-0031"))
y = [i for i in I6 if i["type"] == "Invoice" and i["customer"] != x["customer"]][7]
I6.append(credit(y["customer"], "Payment", ASOF - timedelta(days=3), 50000, "OP-0007"))
write_xero(P("06-xero-bellwether-aged-receivables.xlsx"), "Bellwether Design Studio", I6)
case("06", "Xero: a credit note and an overpayment", "ugly", "06-xero-bellwether-aged-receivables.xlsx", "COMPUTED", ["UNAPPLIED_CREDITS"], key_for(I6), "xero")

# ---- 07 QuickBooks Desktop: no as-of date in the cells, days from the Aging column, real Excel dates
N7, I7 = book(7)
write_desktop(P("07-desktop-hollis-tate-ar-aging.xlsx"), I7)
k7 = key_for(I7); k7["asOf"] = None
case("07", "QuickBooks Desktop: no as-of date, days from the Aging column", "ugly", "07-desktop-hollis-tate-ar-aging.xlsx", "COMPUTED", ["DATE_UNKNOWN"], k7, "desktop")

# ---- 08 invoices over a year old, and small leftover balances
N8, I8 = book(8)
I8.append(inv(N8[2], D(2025, 6, 12), 412500, "7701"))
I8.append(inv(N8[5], D(2025, 3, 2), 98000, "7702", open_=98000))
for k_, c in enumerate([N8[1], N8[4], N8[9]]):
    I8.append(inv(c, ASOF - timedelta(days=50 + k_ * 9), 230000 + k_ * 1000, f"78{k_}0", open_=[350, 75, 912][k_]))
write_qbo(P("08-old-and-small-balances.xlsx"), "Copperline Plumbing Supply", I8)
case("08", "Invoices over a year old, and small leftover balances", "ugly", "08-old-and-small-balances.xlsx", "COMPUTED", ["OVER_A_YEAR", "SMALL_BALANCES"], key_for(I8), "qbo")

# ---- 09 the QuickBooks Online report saved as CSV: dollar signs, parentheses, sub-customers
N9, I9 = book(9, n_customers=20)
for i in I9[::4]: i["customer"] = i["customer"] + ":Job " + str(int(i["num"]) % 7 + 1)
I9.append(credit(I9[3]["customer"].split(":")[0] + ":Job 2", "Credit Memo", ASOF - timedelta(days=20), 12000, "CM-9"))
write_qbo(P("09-qbo-csv-sub-customers.csv"), "Meadowbrook Catering Co.", I9, csv_out=True, paren=True)
# sub-customers ("Customer:Job") are reviewed as their parent customer
for i in I9: i["customer"] = i["customer"].split(":")[0]
case("09", "QuickBooks Online as CSV: dollar signs, parentheses, jobs under customers", "ugly", "09-qbo-csv-sub-customers.csv", "COMPUTED", ["UNAPPLIED_CREDITS"], key_for(I9), "qbo")

# ---- 10 the wrong report: A/P aging detail
with open(P("10-ap-aging-detail.csv"), "w", newline="") as f:
    w = csv.writer(f)
    for row in [["Northgate Electrical Supply"], ["A/P Aging Detail"], ["As of October 31, 2026"], [], ["", "Date", "Transaction Type", "Num", "Vendor", "Due Date", "Amount", "Open Balance"],
                ["Current"], ["", "10/12/2026", "Bill", "4471", "Cedar Wire Co.", "11/11/2026", "1,240.00", "1,240.00"], ["TOTAL", "", "", "", "", "", "", "1,240.00"]]:
        w.writerow(row)
case("10", "The wrong report: A/P aging detail", "ugly", "10-ap-aging-detail.csv", "NOT_RECOGNIZED", ["NOT_RECOGNIZED"])

# ---- 11 the summary report, with no invoices in it
with open(P("11-ar-aging-summary.csv"), "w", newline="") as f:
    w = csv.writer(f)
    for row in [["Northgate Electrical Supply"], ["A/R Aging Summary"], ["As of October 31, 2026"], [], ["", "Current", "1 - 30", "31 - 60", "61 - 90", "91 and over", "Total"],
                ["Alder Builders", "1,200.00", "", "", "", "", "1,200.00"], ["TOTAL", "1,200.00", "", "", "", "", "1,200.00"]]:
        w.writerow(row)
case("11", "The summary report, with no invoices in it", "ugly", "11-ar-aging-summary.csv", "NOT_RECOGNIZED", ["SUMMARY_ONLY"])

# ---- 12 planted: the report's total line was typed over
N12, I12 = book(12)
write_qbo(P("12-planted-total-typed-over.xlsx"), "Ridgeway Pest Control", I12, total_override=sum(i["open"] for i in I12) + 90000)
case("12", "Planted: the report's total line does not agree with its lines", "planted", "12-planted-total-typed-over.xlsx", "COMPUTED", ["TOTAL_MISMATCH"], key_for(I12), "qbo")

# ---- 13 planted: rows pasted twice
N13, I13 = book(13)
write_qbo(P("13-planted-rows-pasted-twice.xlsx"), "Summit Office Interiors", I13, dup_rows=3)
case("13", "Planted: three lines pasted in twice", "planted", "13-planted-rows-pasted-twice.xlsx", "COMPUTED", ["DUPLICATE_ROWS"], {**key_for(I13), "duplicates_removed": 3}, "qbo")

# ---- 14 the accountant's allowance rates, a journal entry posted to A/R, and one customer with a third of the balance
N14, I14 = book(14, n_customers=18)
I14.append(dict(customer=N14[0], type="Journal Entry", date=D(2026, 9, 30), due=D(2026, 9, 30), num="JE-88", amount=1250000, open=1250000, terms=0))
I14.append(inv(N14[1], D(2026, 7, 14), 9400000, "6001"))      # one large customer
rates14 = {"current": 1, "d1_30": 2, "d31_60": 5, "d61_90": 10, "d91_180": 25, "d181_365": 50, "over365": 100}
write_qbo(P("14-allowance-rates-journal-entry.xlsx"), "Kestrel Staffing Partners", I14)
k14 = key_for(I14, rates=rates14)
assert len(k14["concentration"]) == 1, k14["concentration"]
case("14", "Allowance rates typed in; a journal entry in A/R; one customer holds a large share", "ugly", "14-allowance-rates-journal-entry.xlsx", "COMPUTED",
     ["JOURNAL_ENTRIES", "CONCENTRATION"], k14, "qbo")

with open(os.path.join(HERE, "answer-key.json"), "w") as f:
    json.dump(KEY, f, indent=1, default=str)
print(len(KEY), "cases")
for cid, e in KEY.items():
    print(cid, e["status"], e["exceptions"], "rows", e.get("rows"), "total", e.get("total"), "match", len(e.get("matches", [])), "credit", len(e.get("creditBalances", [])),
          "dups", len(e.get("duplicates", [])), "small", e.get("small"), "old", e.get("old"), "wo", e.get("writeOff"), "work", len(e.get("worklist", [])), "allow", e.get("allowance"))
