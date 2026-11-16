#!/usr/bin/env python3
"""Builds the acceptance test for Order-to-Cash 02, "What's really collectible?".

Each case is one A/R aging detail report, as of October 31, 2026, in the layout of QuickBooks
Online, QuickBooks Desktop or Xero. The files are written from a model of open items (invoices,
unapplied payments, credit memos, journal entries) for three invented businesses, and the answer
key is worked out from the model with the rules below, never by reading the files back.
Money is held in integer cents.

The rules the key follows (version 2, after the accounting review and the cold-user check):
  days past due = as-of date - due date (0 or less is current); buckets: current, 1-30, 31-60,
    61-90, 91-180, 181-365, over 365.
  Clean-up, job by job ("Customer:Job" is its own job; jobs roll up to the customer for chasing):
    1. each credit (payment, credit memo, negative journal entry), oldest first, is matched to an
       open invoice (or refund check) of exactly the same amount, the oldest such;
    2. what remains of each credit is applied to the job's oldest open invoices;
    3. whatever credit is still left is owed to the customer: a credit balance, never chased.
  Duplicates, per job: two open invoices with the same number, or of the same amount (at least $1)
    dated less than 7 days apart; not when the job has three or more invoices of that amount
    (recurring billing). The later copy is not chased.
  Small balances: a part-paid invoice with less than $10.00 left, more than 60 days past due.
  Over a year: an invoice more than 365 days past due with a balance left.
  Write-off proposed: small balances plus over-a-year invoices.
  Chased: open invoices past due, not proposed for write-off, not the later copy of a duplicate,
    not journal entries. Worklist per customer, ranked by the amount over 60 days past due, then by
    the overdue amount, then by name; the step follows the oldest chased invoice.
  Allowance: the accountant's rates by bucket, on balances left after the clean-up and write-offs;
    with the allowance already on the books, the adjustment = required - (existing - write-offs).
  Concentration: a customer whose remaining balance is 20% or more of all remaining balances.
  Reconciliation: report total = owed by customers - owed to customers in credit.

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
def key_for(items, rates=None, typed=None, existing=None, asof_known=True):
    """What the tool should report, from the model, by the rules in the docstring (version 2, after review)."""
    rem = {id(i): i["open"] for i in items}
    parent = lambda i: i["customer"].split(":")[0].strip()
    jobs = sorted(set(i["customer"] for i in items))
    parents = sorted(set(parent(i) for i in items))
    target = lambda i: i["open"] > 0 and i["type"] in ("Invoice", "Refund")     # a credit can be applied to these
    matches, apply_oldest, credit_bal = [], [], []
    for j in jobs:
        mine = [i for i in items if i["customer"] == j]
        credits = sorted([i for i in mine if i["open"] < 0], key=lambda i: (i["date"], i["num"]))
        tg = sorted([i for i in mine if target(i)], key=lambda i: (i["date"], i["num"]))
        for cr in credits:                                  # 1. exact amount, oldest invoice first
            hit = [v for v in tg if rem[id(v)] == -rem[id(cr)] and rem[id(v)] == v["open"]]
            if hit:
                v = hit[0]
                matches.append({"customer": j, "credit": cr["num"] or cr["type"], "creditType": cr["type"], "invoice": v["num"], "amount": v["open"] / 100})
                rem[id(v)] = 0; rem[id(cr)] = 0
        for cr in credits:                                  # 2. the rest to the oldest invoices of the same job
            if rem[id(cr)] == 0: continue
            amt, used = -rem[id(cr)], []
            for v in tg:
                if amt == 0: break
                take = min(amt, rem[id(v)])
                if take: rem[id(v)] -= take; amt -= take; used.append(v["num"])
            if used: apply_oldest.append({"customer": j, "credit": cr["num"] or cr["type"], "amount": (-rem[id(cr)] - amt) / 100})
            rem[id(cr)] = -amt
        left = -sum(rem[id(cr)] for cr in credits)          # 3. what is still left is owed to the customer
        if left: credit_bal.append({"customer": j, "amount": left / 100})
    pos = [i for i in items if rem[id(i)] > 0]
    # a credit balance that equals another customer's untouched open invoice may have been posted to the wrong customer;
    # a job's credit balance may belong to the same customer's other jobs
    misp = []
    for cb in credit_bal:
        amt = round(cb["amount"] * 100)
        hits = [i for i in pos if parent(i) != cb["customer"].split(":")[0].strip() and i["type"] == "Invoice" and rem[id(i)] == amt and i["open"] == amt]
        if len(hits) == 1: misp.append({"customer": cb["customer"], "maybeFor": hits[0]["customer"], "invoice": hits[0]["num"]})
        twice = [m for m in matches if m["customer"] == cb["customer"] and round(m["amount"] * 100) == amt]
        cb["paidTwice"] = twice[0]["invoice"] if twice else None
        cb["otherJobs"] = any(parent(i) == cb["customer"].split(":")[0].strip() and i["customer"] != cb["customer"] for i in pos)
    # duplicates: per job, open invoices of the same amount within 6 days, or the same number twice; not recurring billing
    dups, second = [], set()
    for j in jobs:
        iv = sorted([i for i in items if i["customer"] == j and i["type"] == "Invoice" and i["open"] > 0], key=lambda i: (i["date"], i["num"]))
        for a in range(len(iv)):
            for b in range(a + 1, len(iv)):
                x, y = iv[a], iv[b]
                same_num = x["num"] == y["num"]
                recurring = sum(1 for z in iv if z["amount"] == x["amount"]) >= 3
                if (same_num or (x["amount"] == y["amount"] and x["amount"] >= 100 and abs((y["date"] - x["date"]).days) < 7)) and not recurring:
                    dups.append({"customer": j, "a": x["num"], "b": y["num"], "amount": x["amount"] / 100}); second.add(id(y))
    small = [i for i in pos if i["type"] == "Invoice" and rem[id(i)] < 1000 and i["open"] < i["amount"] and days(i) > 60]
    old = [i for i in pos if i["type"] == "Invoice" and days(i) > 365 and i not in small]
    wo = small + old
    chased = [i for i in pos if i["type"] == "Invoice" and days(i) > 0 and i not in wo and id(i) not in second]
    rep_buckets = {b: 0 for b in BUCKETS}
    for i in items: rep_buckets[bucket(days(i))] += i["open"]
    clean = {b: 0 for b in BUCKETS}
    for i in pos: clean[bucket(days(i))] += rem[id(i)]
    work = []
    for c in parents:
        mine = [i for i in chased if parent(i) == c]
        if not mine: continue
        oldest = max(days(i) for i in mine)
        step = ("Friendly reminder" if oldest <= 30 else "Second request and a call" if oldest <= 60 else "Call about the account" if oldest <= 90 else
                "Past-due notice" if oldest <= 180 else "Final request")
        work.append({"customer": c, "overdue": sum(rem[id(i)] for i in mine) / 100, "over60": sum(rem[id(i)] for i in mine if days(i) > 60) / 100,
                     "oldestDays": oldest, "step": step, "invoices": len(mine)})
    work.sort(key=lambda w: (-w["over60"], -w["overdue"], w["customer"]))
    total = sum(i["open"] for i in items)
    owed = sum(rem[id(i)] for i in pos)
    conc = []
    for c in parents:
        cr_ = sum(rem[id(i)] for i in pos if parent(i) == c)
        if owed and cr_ * 100 >= 20 * owed: conc.append({"customer": c, "share": round(cr_ * 1000 / owed) / 10})
    k = {"asOf": ASOF.isoformat() if asof_known else None, "rows": len(items), "total": total / 100, "customers": len(parents),
         "owed": owed / 100, "inCredit": sum(int(round(x["amount"] * 100)) for x in credit_bal) / 100,
         "buckets": {b: v / 100 for b, v in rep_buckets.items()}, "bucketsClean": {b: v / 100 for b, v in clean.items()},
         "matches": matches, "creditBalances": credit_bal, "applyOldest": apply_oldest, "duplicates": dups,
         "small": sorted(i["num"] for i in small), "old": sorted(i["num"] for i in old),
         "writeOff": sum(rem[id(i)] for i in wo) / 100, "worklist": work, "concentration": conc,
         "journalEntries": sum(1 for i in items if i["type"] == "Journal Entry"), "mispostings": misp}
    assert total == owed - sum(int(round(x["amount"] * 100)) for x in credit_bal), "the clean-up must reconcile to the report"
    if rates is not None:
        half_up = lambda x: int(x + 0.5)
        k["rates"] = rates
        need = sum(half_up(sum(rem[id(i)] for i in pos if bucket(days(i)) == b and i not in wo and i["type"] != "Refund") * rates[b] / 100) for b in BUCKETS)
        k["allowance"] = need / 100
        if existing is not None:
            wo_amt = sum(rem[id(i)] for i in wo)
            k["existingAllowance"] = existing / 100
            k["allowanceAdjustment"] = (need - (existing - wo_amt)) / 100     # Dr bad debt expense, Cr allowance (negative: a release)
    if typed is not None:
        k["typedAR"] = typed / 100; k["difference"] = (typed - total) / 100
    return k

# ------------------------------------------------------------------ writers
QBO_SECTIONS = [("current", "Current"), ("d1_30", "1 - 30 days past due"), ("d31_60", "31 - 60 days past due"), ("d61_90", "61 - 90 days past due"), ("91+", "91 or more days past due")]
def qsec(it):
    b = bucket(days(it))
    return b if b in ("current", "d1_30", "d31_60", "d61_90") else "91+"
def ds(d): return d.strftime("%m/%d/%Y")

def write_qbo(path, company, items, csv_out=False, paren=False, total_override=None, dup_rows=0, no_date=False):
    """QuickBooks Online: Reports > A/R Aging Detail > Export to Excel. Grouped by aging section."""
    rows = [[company], ["A/R Aging Detail"], [] if no_date else ["As of October 31, 2026"], [], ["", "Date", "Transaction Type", "Num", "Customer", "Due Date", "Amount", "Open Balance"]]
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
            ws.append(["", "Check" if i["type"] == "Refund" else i["type"], datetime(i["date"].year, i["date"].month, i["date"].day), i["num"], "", i["customer"],
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
for w_ in range(4):   # a customer billed the same $450.00 twice a week: recurring billing, not duplicates
    I4.append(inv("Willow Property Management", ASOF - timedelta(days=40 - 3 * w_), 45000, f"52{w_}0"))
write_qbo(P("04-planted-duplicate-invoice.xlsx"), "Lantern Signs & Graphics", I4)
case("04", "Planted: the same invoice entered twice; a twice-weekly flat bill that is not a duplicate", "planted", "04-planted-duplicate-invoice.xlsx", "COMPUTED", ["DUPLICATE_INVOICES"], key_for(I4), "qbo")

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
I7.append(credit(N7[3], "Credit Memo", D(2026, 9, 10), 30000, "CM-31"))
I7.append(dict(customer=N7[3], type="Refund", date=D(2026, 9, 24), due=D(2026, 9, 24), num="5531", amount=30000, open=30000, terms=0))
write_desktop(P("07-desktop-hollis-tate-ar-aging.xlsx"), I7)
k7 = key_for(I7); k7["asOf"] = None
case("07", "QuickBooks Desktop: no as-of date, days from the Aging column; a credit memo refunded by check", "ugly", "07-desktop-hollis-tate-ar-aging.xlsx", "COMPUTED", ["DATE_UNKNOWN", "UNAPPLIED_CREDITS"], k7, "desktop")

# ---- 08 invoices over a year old, and small leftover balances
N8, I8 = book(8)
I8.append(inv(N8[2], D(2025, 6, 12), 412500, "7701"))
I8.append(inv(N8[5], D(2025, 3, 2), 98000, "7702", open_=98000))
for k_, c in enumerate([N8[1], N8[4], N8[9]]):
    I8.append(inv(c, ASOF - timedelta(days=100 + k_ * 9), 230000 + k_ * 1000, f"78{k_}0", open_=[350, 75, 912][k_]))
I8.append(inv(N8[7], ASOF - timedelta(days=10), 240000, "7830", open_=640))   # a part-paid invoice not yet 60 days late: chased, not written off
write_qbo(P("08-old-and-small-balances.xlsx"), "Copperline Plumbing Supply", I8)
rates8 = {"current": 1, "d1_30": 2, "d31_60": 5, "d61_90": 10, "d91_180": 25, "d181_365": 50, "over365": 100}
case("08", "Invoices over a year old, small leftover balances; allowance rates and the allowance on the books", "ugly", "08-old-and-small-balances.xlsx", "COMPUTED",
     ["OVER_A_YEAR", "SMALL_BALANCES"], key_for(I8, rates=rates8, existing=1500000), "qbo")

# ---- 09 the QuickBooks Online report saved as CSV: dollar signs, parentheses, sub-customers
N9, I9 = book(9, n_customers=20)
for i in I9[::4]: i["customer"] = i["customer"] + ":Job " + str(int(i["num"]) % 7 + 1)
I9.append(credit(I9[3]["customer"].split(":")[0] + ":Job 2", "Credit Memo", ASOF - timedelta(days=20), 12000, "CM-9"))
write_qbo(P("09-qbo-csv-sub-customers.csv"), "Meadowbrook Catering Co.", I9, csv_out=True, paren=True)
k9 = key_for(I9)
case("09", "QuickBooks Online as CSV: dollar signs, parentheses, jobs under customers", "ugly", "09-qbo-csv-sub-customers.csv", "COMPUTED",
     (["UNAPPLIED_CREDITS"] if k9["matches"] or k9["applyOldest"] else []) + (["CREDIT_BALANCES"] if k9["creditBalances"] else []), k9, "qbo")

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

# ---- 15 two real payments of the same amount on the same day, with no number: identical lines, both kept
N15, I15 = book(15, n_customers=20)
I15.append(inv("Hawthorn Fitness", D(2026, 8, 20), 50000, "8801")); I15.append(inv("Hawthorn Fitness", D(2026, 9, 12), 50000, "8802"))
I15.append(credit("Hawthorn Fitness", "Payment", D(2026, 10, 20), 50000, "")); I15.append(credit("Hawthorn Fitness", "Payment", D(2026, 10, 20), 50000, ""))
write_qbo(P("15-two-identical-payments.xlsx"), "Orchard Valley Farms", I15)
case("15", "Two real payments of $500 on the same day, no number: identical lines, both kept", "ugly", "15-two-identical-payments.xlsx", "COMPUTED",
     ["IDENTICAL_LINES", "UNAPPLIED_CREDITS"], key_for(I15), "qbo")

# ---- 16 the report exported without its as-of line: the page must ask for the date
N16, I16 = book(16, n_customers=22)
write_qbo(P("16-no-as-of-date.xlsx"), "Prairie Glass Works", I16, no_date=True)
case("16", "No as-of date in the file: the page asks for it, then reviews", "ugly", "16-no-as-of-date.xlsx", "COMPUTED", [],
     {**key_for(I16), "typeAsOf": "10/31/2026"}, "qbo")

# ---- 17 planted: a check that pays two invoices in full, and a payment posted to the wrong customer
N17, I17 = book(17, n_customers=22)
I17.append(inv("Zenith Builders", D(2026, 8, 1), 50000, "9101")); I17.append(inv("Zenith Builders", D(2026, 8, 25), 30000, "9102"))
I17.append(credit("Zenith Builders", "Payment", D(2026, 10, 2), 80000, ""))
I17.append(inv("Indigo Storage", D(2026, 8, 14), 125000, "9150"))
I17.append(credit("Keystone Apartments", "Payment", D(2026, 9, 30), 125000, ""))
write_qbo(P("17-planted-netting-and-misposting.xlsx"), "Falcon Commercial Cleaning", I17)
k17 = key_for(I17)
case("17", "Planted: one check for two invoices; a payment posted to the wrong customer", "planted", "17-planted-netting-and-misposting.xlsx", "COMPUTED",
     ["UNAPPLIED_CREDITS", "CREDIT_BALANCES"] + (["CONCENTRATION"] if k17["concentration"] else []),
     k17, "qbo")
assert k17["mispostings"] == [{"customer": "Keystone Apartments", "maybeFor": "Indigo Storage", "invoice": "9150"}], k17["mispostings"]

with open(os.path.join(HERE, "answer-key.json"), "w") as f:
    json.dump(KEY, f, indent=1, default=str)
print(len(KEY), "cases")
for cid, e in KEY.items():
    print(cid, e["status"], e["exceptions"], "rows", e.get("rows"), "total", e.get("total"), "match", len(e.get("matches", [])), "credit", len(e.get("creditBalances", [])),
          "dups", len(e.get("duplicates", [])), "small", e.get("small"), "old", e.get("old"), "wo", e.get("writeOff"), "work", len(e.get("worklist", [])), "allow", e.get("allowance"))
