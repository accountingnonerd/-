#!/usr/bin/env python3
"""
Builds the acceptance-test inputs and the answer key for agent 01, "Who gets a 1099?".

HOW THE ANSWER KEY STAYS INDEPENDENT OF THE AGENT
-------------------------------------------------
Every payment line below is written out by hand and tagged with the TRUE vendor and the
TRUE payment method (b = check/ACH/Zelle/cash, c = card, n = PayPal/Venmo-type network).
Those tags never go into the test file. The expected answer for each vendor (bucket and
dollar amount) is ALSO written by hand, from the IRS rules, before the agent existed.

This script then adds up the tagged lines with plain Python and refuses to write the key
if a hand-worked amount disagrees with the tagged lines. It shares no code with the agent
(the agent is JavaScript in one HTML file) and never parses the files it writes.

All companies and people are invented. No client data.

Run:  python3 make_cases.py      (writes cases/*.csv, cases/*.xlsx, answer-key.json)
"""
import csv, io, json, os, sys
from datetime import date
from decimal import Decimal as D
from openpyxl import Workbook

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, "cases")
os.makedirs(CASES, exist_ok=True)

KEY = {}


def money(x):
    return float(D(str(x)).quantize(D("0.01")))


class Case:
    """Collects tagged lines and hand-worked expectations for one test file."""

    def __init__(self, cid, filename, title, kind, payer):
        self.cid, self.filename, self.title, self.kind, self.payer = cid, filename, title, kind, payer
        self.lines = []      # dicts with truth tags
        self.expect = []     # hand-worked vendor answers
        self.meta = {}

    def pay(self, truth, d, amount, method="b", name=None, year_ok=True, **cols):
        """One payment line. `truth` = real vendor; `method` = real payment method."""
        self.lines.append(dict(truth=truth, date=d, amount=D(str(amount)), method=method,
                               name=name or truth, year_ok=year_ok, cols=cols))

    def want(self, truth, bucket, reportable, spellings=None, rows=None, total=None):
        """Hand-worked answer: bucket and the check/transfer dollars that count."""
        e = dict(vendor=truth, bucket=bucket, reportable=money(reportable))
        if spellings:
            e["spellings"] = spellings
        if rows:
            e["rows"] = rows
        if total is not None:
            e["total"] = money(total)
        self.expect.append(e)

    def finish(self, tax_year, threshold, exceptions, hand_total, file_total=None,
               file_total_ties=None, unreadable=0, no_other_exceptions=True, notes=""):
        # ---- independent cross-check of the hand-worked numbers against the tagged lines
        by = {}
        for ln in self.lines:
            v = by.setdefault(ln["truth"], dict(b=D(0), c=D(0), n=D(0), out=D(0)))
            if ln["year_ok"]:
                v[ln["method"]] += ln["amount"]
            else:
                v["out"] += ln["amount"]
        for e in self.expect:
            tagged = by[e["vendor"]]["b"]
            assert money(tagged) == e["reportable"], (
                f"{self.cid}: hand answer for {e['vendor']} is {e['reportable']} "
                f"but tagged lines add to {tagged}")
        missing = set(by) - {e["vendor"] for e in self.expect}
        assert not missing, f"{self.cid}: no hand answer for {missing}"
        tot = sum(ln["amount"] for ln in self.lines)
        assert money(tot) == money(hand_total), f"{self.cid}: hand total {hand_total} vs lines {tot}"
        bank = sum(v["b"] for v in by.values())
        card = sum(v["c"] for v in by.values())
        net = sum(v["n"] for v in by.values())
        out = sum(v["out"] for v in by.values())
        KEY[self.cid] = dict(
            file=self.filename, title=self.title, kind=self.kind, payer=self.payer,
            taxYear=tax_year, threshold=threshold,
            controls=dict(
                linesRead=len(self.lines), totalPayments=money(tot),
                byMethod=dict(bank=money(bank), card=money(card), network=money(net)),
                outsideYearTotal=money(out),
                outsideYearLines=sum(1 for ln in self.lines if not ln["year_ok"]),
                unreadableLines=unreadable, ties=True,
                fileTotal=None if file_total is None else money(file_total),
                fileTotalTies=file_total_ties),
            exceptions=sorted(exceptions), noOtherExceptions=no_other_exceptions,
            vendors=self.expect, notes=notes)


def us(d):
    return f"{d.month}/{d.day}/{d.year}"


def write_csv(filename, rows, bom=False):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\r\n")
    for r in rows:
        w.writerow(r)
    with open(os.path.join(CASES, filename), "w", encoding="utf-8-sig" if bom else "utf-8", newline="") as f:
        f.write(buf.getvalue())


def write_xlsx(filename, rows, date_cols=(), money_cols=()):
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    for r in rows:
        ws.append(r)
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, date):
                c.number_format = "mm/dd/yyyy"
            elif isinstance(c.value, float):
                c.number_format = "#,##0.00"
    wb.save(os.path.join(CASES, filename))


def flat_rows(case, header, order):
    """Standard flat layout: one header row, one line per payment."""
    rows = [header]
    for ln in case.lines:
        c = ln["cols"]
        rec = dict(Date=us(ln["date"]), Name=ln["name"], Amount=f"{ln['amount']:.2f}", **c)
        rows.append([rec.get(h, "") for h in order])
    return rows


# =====================================================================================
# CASE 01 - clean, flat CSV. Nothing wrong with it. The agent must not invent problems.
# =====================================================================================
c = Case("01", "01-clean-check-register.csv", "Clean file, one line per payment", "clean", "Harbor Print Shop")
H = ["Date", "Transaction Type", "Num", "Name", "Paid From", "Category", "Memo", "Amount"]
CHK = dict(**{"Transaction Type": "Check", "Paid From": "Operating Checking 4410"})
ACH = dict(**{"Transaction Type": "Bill Payment (Check)", "Paid From": "Operating Checking 4410", "Num": "ACH"})
for d, n, a in [(date(2026, 2, 3), "1041", 900), (date(2026, 5, 19), "1077", 750), (date(2026, 9, 8), "1123", 600)]:
    c.pay("Rivera Plumbing", d, a, Num=n, Category="Repairs & Maintenance", Memo="press room drain", **CHK)
for d, n, a in [(date(2026, 3, 2), "1050", 1200), (date(2026, 7, 15), "1101", 1300)]:
    c.pay("Dana Whitfield", d, a, Num=n, Category="Contract Labor", Memo="freelance layout", **CHK)
c.pay("Office Depot", date(2026, 4, 1), 2400, Num="1060", Category="Office Supplies", Memo="paper stock", **CHK)
for m in range(1, 13):
    c.pay("Pacific Gas & Electric", date(2026, m, 12), "310.25", Category="Utilities", Memo="", **ACH)
c.pay("Lin & Park LLP", date(2026, 6, 10), 3000, Num="1088", Category="Legal Fees", Memo="lease dispute", **CHK)
for m in (3, 6, 9, 11):
    c.pay("Greenleaf Landscaping", date(2026, m, 20), 300, Num=str(1200 + m), Category="Landscaping", Memo="", **CHK)
for m in range(1, 13):
    c.pay("Summit Realty Holdings LLC", date(2026, m, 1), 1500, Num=str(1300 + m), Category="Rent", Memo="shop rent", **CHK)
c.pay("Coastal Sign Co", date(2026, 10, 5), 1750, Num="1130", Category="Advertising", Memo="storefront sign install", **CHK)
c.lines.sort(key=lambda l: l["date"])
write_csv(c.filename, flat_rows(c, H, H))
# Hand-worked answers (2026 payments: $2,000 limit; close-call list starts at $1,500)
c.want("Rivera Plumbing", "NEC", 2250)             # 900+750+600, repairs = services
c.want("Dana Whitfield", "NEC", 2500)              # 1,200+1,300 contract labor
c.want("Office Depot", "NOT_REPORTABLE", 2400)     # merchandise
c.want("Pacific Gas & Electric", "NOT_REPORTABLE", "3723.00")  # 12 x 310.25 utilities
c.want("Lin & Park LLP", "NEC", 3000)              # attorney fees, 1099-NEC box 1a on the 2026 form
c.want("Greenleaf Landscaping", "NOT_REPORTABLE", 1200)  # under the limit and under $1,500
c.want("Summit Realty Holdings LLC", "MISC_RENT", 18000)
c.want("Coastal Sign Co", "CLOSE", 1750)           # service, 1,500 <= 1,750 < 2,000
c.finish(2026, 2000, [], hand_total="34823.00")

# =====================================================================================
# CASE 02 - payment method decides. Card and PayPal are excluded; Zelle is not.
# =====================================================================================
c = Case("02", "02-card-check-paypal-zelle.csv", "Same vendor paid by check and by card; PayPal, Venmo, Zelle", "rules", "Juniper Yoga Studio LLC")
CK = {"Transaction Type": "Check", "Paid From": "Checking 8841"}
AMEX = {"Transaction Type": "Credit Card Expense", "Paid From": "Amex Business 1009"}
VISA = {"Transaction Type": "Credit Card Expense", "Paid From": "Visa 4432"}
c.pay("Bright Web Design", date(2026, 1, 20), 800, Num="2001", Category="Advertising & Marketing", Memo="site refresh deposit", **CK)
c.pay("Bright Web Design", date(2026, 4, 11), 1500, "c", Category="Advertising & Marketing", Memo="site refresh balance", **AMEX)
c.pay("Tomas Ortega", date(2026, 2, 9), 1500, Num="2010", Category="Contract Labor", Memo="workshop teaching", **CK)
c.pay("Tomas Ortega", date(2026, 8, 3), 900, "c", Category="Contract Labor", Memo="workshop teaching", **VISA)
c.pay("Keystone Consulting Group", date(2026, 3, 16), 2000, Num="ACH", Category="Professional Fees", Memo="pricing study",
      **{"Transaction Type": "Bill Payment (Check)", "Paid From": "Checking 8841"})
c.pay("Paloma Reyes", date(2026, 5, 4), "1999.99", Num="2022", Category="Contract Labor", Memo="substitute teaching", **CK)
for d in (date(2026, 6, 6), date(2026, 10, 17)):
    c.pay("Nadia Brooks Photography", d, 1300, "n", Category="Advertising & Marketing", Memo="studio photo shoot",
          **{"Transaction Type": "Expense", "Paid From": "PayPal"})
for d in (date(2026, 7, 1), date(2026, 12, 1)):
    c.pay("Marcus Lee", d, 1200, Num="Zelle", Category="Contract Labor", Memo="Zelle payment - retreat teaching",
          **{"Transaction Type": "Expense", "Paid From": "Checking 8841"})
c.pay("Studio Supply Warehouse", date(2026, 9, 14), 640, "c", Num="Debit Card", Category="Supplies", Memo="mats and blocks",
      **{"Transaction Type": "Expense", "Paid From": "Checking 8841"})
c.pay("Elena Park", date(2026, 3, 30), 1000, Num="2015", Category="Contract Labor", Memo="sub teaching", **CK)
c.pay("Elena Park", date(2026, 11, 9), 1100, "n", Category="Contract Labor", Memo="Venmo - sub teaching",
      **{"Transaction Type": "Expense", "Paid From": "Checking 8841"})
for m in range(1, 13):
    c.pay("Sparkle Cleaning Services", date(2026, m, 25), 250, "c", Category="Janitorial", Memo="monthly cleaning", **VISA)
c.pay("Lotus Flow Music", date(2026, 8, 20), 180, Num="2031", Category="Music Royalties", Memo="class playlist licence - royalty", **CK)
c.lines.sort(key=lambda l: l["date"])
write_csv(c.filename, flat_rows(c, H, H))
c.want("Lotus Flow Music", "REVIEW", 180)                        # royalties have a $10 limit (1099-MISC box 2), not $2,000
c.want("Bright Web Design", "NOT_REPORTABLE", 800, total=2300)   # $2,300 in all, only $800 by check
c.want("Tomas Ortega", "CLOSE", 1500, total=2400)                # $1,500 by check: on the close-call list
c.want("Keystone Consulting Group", "NEC", 2000)                 # "at least $2,000": exactly at the limit counts
c.want("Paloma Reyes", "CLOSE", "1999.99")                       # one cent short
c.want("Nadia Brooks Photography", "REVIEW", 0, total=2600)      # all PayPal: excluded only if a business payment
c.want("Marcus Lee", "NEC", 2400)                                # Zelle is a bank transfer, it counts
c.want("Studio Supply Warehouse", "NOT_REPORTABLE", 0)           # goods, and paid by debit card
c.want("Elena Park", "REVIEW", 1000, total=2100)                 # under only because $1,100 went by Venmo
c.want("Sparkle Cleaning Services", "NOT_REPORTABLE", 0, total=3000)  # all on a credit card
c.finish(2026, 2000, [], hand_total="19619.99")

# =====================================================================================
# CASE 03 - realistic size. QuickBooks-style report grouped by vendor, Excel, 300+ lines.
# =====================================================================================
c = Case("03", "03-quickbooks-style-by-vendor.xlsx", "Full year, grouped by vendor with subtotal rows (Excel)", "ugly", "Northwind Auto Repair Inc")
BK = "Checking 2207"
CC = "Visa Business 9120"


def g(truth, d, amt, typ, num, memo, acct, split, method="b"):
    c.pay(truth, d, amt, method, **{"Transaction Type": typ, "Num": num, "Memo/Description": memo, "Account": acct, "Split": split})


for i, d in enumerate([date(2026, 4, 14), date(2026, 8, 21)]):
    g("Harlan HVAC Service", d, 1300, "Check", str(5100 + i), "shop heater and bay AC service", BK, "Repairs & Maintenance")
g("Harlan HVAC Service", date(2026, 8, 21), 400, "Check", "5102", "filters and refrigerant", BK, "Shop Supplies")
for i, d in enumerate([date(2026, 3, 3), date(2026, 9, 9)]):
    g("Miller Hardware & Repair", d, 950, "Check", str(5200 + i), "fasteners, hoses, stock", BK, "Shop Supplies")
g("Miller Hardware & Repair", date(2026, 6, 18), 300, "Check", "5202", "compressor repair", BK, "Repairs & Maintenance")
for i in range(26):
    d = date.fromordinal(date(2026, 1, 9).toordinal() + 14 * i)
    g("Ines Calderon", d, 480, "Check", str(5300 + i), "front desk - contract", BK, "Contract Labor")
for i, (m, a) in enumerate([(1, 350), (3, 425), (5, 275), (7, 510), (9, 390), (11, 460)]):
    g("Tri-County Towing LLC", date(2026, m, 22), a, "Check", str(5400 + i), "customer tows", BK, "Subcontractors")
for m in range(1, 13):
    g("Whitaker Properties LLC", date(2026, m, 1), 3200, "Check", str(5500 + m), "shop rent", BK, "Rent")
for i, m in enumerate([2, 5, 8, 11]):
    g("Apex Diagnostics Inc", date(2026, m, 6), 875, "Check", str(5600 + i), "ECU programming", BK, "Outside Services")
g("Ortiz Mobile Detailing", date(2026, 5, 15), 1100, "Check", "5700", "detailing - customer cars", BK, "Subcontractors")
g("Ortiz Mobile Detailing", date(2026, 10, 2), 1400, "Credit Card Expense", "", "detailing - customer cars", CC, "Subcontractors", "c")
for i, m in enumerate([3, 6, 9, 12]):
    g("Priya Nair CPA", date(2026, m, 28), 450, "Check", str(5800 + i), "quarterly bookkeeping review", BK, "Accounting")
# ---- everyday vendors that should all drop out
for i in range(52):
    d = date.fromordinal(date(2026, 1, 5).toordinal() + 7 * i)
    g("NAPA Auto Parts", d, D("412.18") + D((i * 37) % 90), "Credit Card Expense", "", "parts", CC, "Parts Inventory", "c")
for i in range(40):
    d = date.fromordinal(date(2026, 1, 7).toordinal() + 9 * i)
    g("AutoZone", d, D("96.40") + D((i * 13) % 55), "Credit Card Expense", "", "parts", CC, "Parts Inventory", "c")
for m in range(1, 13):
    g("City Water & Sewer", date(2026, m, 15), D("188.07") + m, "Bill Payment (Check)", "ACH", "", BK, "Utilities")
    g("Verizon Wireless", date(2026, m, 18), D("214.36"), "Credit Card Expense", "", "", CC, "Telephone", "c")
    g("State Farm", date(2026, m, 3), D("1260.00"), "Bill Payment (Check)", "ACH", "garage liability", BK, "Insurance")
    g("Waste Management", date(2026, m, 20), D("145.00"), "Bill Payment (Check)", "ACH", "oil and scrap pickup", BK, "Utilities")
    g("United States Treasury", date(2026, m, 15), D("3890.00") + 10 * m, "Check", "EFTPS", "941 deposit", BK, "Payroll Taxes")
for i, m in enumerate([1, 3, 5, 7, 9, 11]):
    g("Snap-on Tools", date(2026, m, 27), D("640.00") + 25 * i, "Check", str(5900 + i), "tool truck", BK, "Tools & Equipment")
for i in range(24):
    d = date.fromordinal(date(2026, 1, 10).toordinal() + 15 * i)
    g("Shell Fleet", d, D("88.15") + D((i * 7) % 30), "Credit Card Expense", "", "shop truck", CC, "Fuel", "c")
for i in range(26):
    d = date.fromordinal(date(2026, 1, 2).toordinal() + 14 * i)
    g("Gusto", d, D("7450.00") + D((i * 111) % 400), "Bill Payment (Check)", "ACH", "payroll", BK, "Payroll")

order03 = ["Harlan HVAC Service", "Miller Hardware & Repair", "Ines Calderon", "Tri-County Towing LLC", "Whitaker Properties LLC",
           "Apex Diagnostics Inc", "Ortiz Mobile Detailing", "Priya Nair CPA", "NAPA Auto Parts", "AutoZone", "City Water & Sewer",
           "Verizon Wireless", "State Farm", "Waste Management", "United States Treasury", "Snap-on Tools", "Shell Fleet", "Gusto"]
order03 = sorted(order03, key=str.lower)


def grouped_rows(case, order, header, bad_subtotal=None):
    """QuickBooks-style: title rows, vendor name row, lines, 'Total for' row, grand TOTAL."""
    rows = [[case.payer], ["Transaction List by Vendor"], ["January - December 2026"], [], [""] + header]
    grand = D(0)
    for v in order:
        rows.append([v])
        sub = D(0)
        for ln in sorted([l for l in case.lines if l["truth"] == v], key=lambda l: l["date"]):
            rec = dict(Date=ln["date"], Amount=float(ln["amount"]), **ln["cols"])
            rows.append([""] + [rec.get(h, "") for h in header])
            sub += ln["amount"]
        shown = sub if not (bad_subtotal and v in bad_subtotal) else bad_subtotal[v]
        rows.append([f"Total for {v}"] + [""] * (len(header) - 1) + [float(shown)])
        grand += shown
    rows.append(["TOTAL"] + [""] * (len(header) - 1) + [float(grand)])
    return rows, grand


GH = ["Date", "Transaction Type", "Num", "Memo/Description", "Account", "Split", "Amount"]
rows, grand03 = grouped_rows(c, order03, GH)
write_xlsx(c.filename, rows)
c.want("Harlan HVAC Service", "NEC", 3000)          # service with incidental parts: the whole $3,000 is reportable
c.want("Miller Hardware & Repair", "REVIEW", 2200)  # $300 service + $1,900 goods: judgment call
c.want("Ines Calderon", "NEC", 12480)               # 26 x 480
c.want("Tri-County Towing LLC", "NEC", 2410)        # 350+425+275+510+390+460
c.want("Whitaker Properties LLC", "MISC_RENT", 38400)
c.want("Apex Diagnostics Inc", "CONFIRM_CORP", 3500)  # "Inc": corporations are generally exempt; a W-9 settles it
c.want("Ortiz Mobile Detailing", "NOT_REPORTABLE", 1100, total=2500)  # $1,400 was on the card
c.want("Priya Nair CPA", "CLOSE", 1800)             # 4 x 450
for v in ["NAPA Auto Parts", "AutoZone", "Verizon Wireless", "Shell Fleet"]:
    c.want(v, "NOT_REPORTABLE", 0)                  # card purchases of goods
c.want("City Water & Sewer", "NOT_REPORTABLE", sum(D("188.07") + m for m in range(1, 13)))
c.want("State Farm", "NOT_REPORTABLE", 12 * D("1260.00"))
c.want("Waste Management", "NOT_REPORTABLE", 12 * D("145.00"))
c.want("United States Treasury", "NOT_REPORTABLE", sum(D("3890.00") + 10 * m for m in range(1, 13)))
c.want("Snap-on Tools", "NOT_REPORTABLE", sum(D("640.00") + 25 * i for i in range(6)))
c.want("Gusto", "NOT_REPORTABLE", sum(D("7450.00") + D((i * 111) % 400) for i in range(26)))
c.finish(2026, 2000, [], hand_total=grand03, file_total=grand03, file_total_ties=True,
         notes="Filler vendors' amounts are generated by formula; their expected totals are the same formulas summed in Python.")

# =====================================================================================
# CASE 04 - one vendor, several spellings.
# =====================================================================================
c = Case("04", "04-vendor-name-variants.csv", "Same vendor typed three ways; look-alike vendors", "ugly", "Larkspur Cafe")
CK = {"Transaction Type": "Check", "Paid From": "Checking 1150"}
c.pay("Rivera Plumbing", date(2026, 1, 14), 700, name="Rivera Plumbing LLC", Num="3001", Category="Repairs & Maintenance", Memo="grease trap", **CK)
c.pay("Rivera Plumbing", date(2026, 4, 22), 800, name="RIVERA PLUMBING", Num="3015", Category="Repairs & Maintenance", Memo="dish line", **CK)
c.pay("Rivera Plumbing", date(2026, 10, 6), 900, name="Rivera Plumbing, L.L.C.", Num="3040", Category="Repairs & Maintenance", Memo="water heater", **CK)
c.pay("Mike Chen", date(2026, 2, 11), 1100, Num="3004", Category="Contract Labor", Memo="patio wiring", **CK)
c.pay("Mike Chen Electric", date(2026, 7, 8), 1200, Num="3027", Category="Repairs & Maintenance", Memo="panel upgrade", **CK)
c.pay("Delgado Janitorial", date(2026, 3, 5), 1000, Num="3009", Category="Janitorial", Memo="deep clean", **CK)
c.pay("Delgado Janitoral", date(2026, 9, 17), 1300, Num="3036", Category="Janitorial", Memo="deep clean", **CK)
c.pay("Smith Electric", date(2026, 5, 13), 1200, Num="3020", Category="Repairs & Maintenance", Memo="hood fan", **CK)
c.pay("Smith Roofing", date(2026, 6, 24), 1200, Num="3024", Category="Repairs & Maintenance", Memo="patch over kitchen", **CK)
for m in (1, 3, 6, 9, 12):
    c.pay("Sysco", date(2026, m, 28), 2000, Num=str(3100 + m), Category="Food Purchases", Memo="", **CK)
c.pay("Sysco", date(2026, 8, 12), 500, name="Sysco Corporation", Num="3033", Category="Food Purchases", Memo="", **CK)
c.lines.sort(key=lambda l: l["date"])
write_csv(c.filename, flat_rows(c, H, H))
c.want("Rivera Plumbing", "NEC", 2400, spellings=3)        # 700+800+900: only over once the three are combined
c.want("Mike Chen", "REVIEW", 1100)                        # with "Mike Chen Electric" = $2,300
c.want("Mike Chen Electric", "REVIEW", 1200)
c.want("Delgado Janitorial", "REVIEW", 1000)               # typo twin, combined $2,300
c.want("Delgado Janitoral", "REVIEW", 1300)
c.want("Smith Electric", "NOT_REPORTABLE", 1200)           # different businesses: must NOT be combined
c.want("Smith Roofing", "NOT_REPORTABLE", 1200)
c.want("Sysco", "NOT_REPORTABLE", 10500, spellings=2)      # food purchases
c.finish(2026, 2000, ["SAME_VENDOR"], hand_total=19900)

# =====================================================================================
# CASE 05 - attorneys, medical, corporations, and things that are not vendors at all.
# =====================================================================================
c = Case("05", "05-attorneys-medical-corporations.xlsx", "Attorneys, medical, 'Inc.' vendors, payroll, taxes, owner draws (Excel)", "rules", "Cedar Ridge Builders LLC")
H5 = ["Date", "Type", "Num", "Payee", "Bank Account", "Expense Account", "Memo", "Amount"]
BKA = "First National Checking 0091"


def f5(truth, d, amt, num, acct, memo, typ="Check"):
    c.pay(truth, d, amt, **{"Type": typ, "Num": num, "Bank Account": BKA, "Expense Account": acct, "Memo": memo})


f5("Hartwell & Dunn, P.C.", date(2026, 2, 17), 2500, "7003", "Legal & Professional Fees", "contract review")
f5("Hartwell & Dunn, P.C.", date(2026, 9, 1), 2000, "7061", "Legal & Professional Fees", "lien filing")
f5("Law Offices of Maria Santos, Inc.", date(2026, 5, 20), 4500, "7030", "Legal & Professional Fees", "permit appeal")
f5("Lakeside Occupational Health Inc", date(2026, 3, 9), 1400, "7010", "Employee Medical Exams", "crew physicals")
f5("Lakeside Occupational Health Inc", date(2026, 10, 12), 1400, "7070", "Employee Medical Exams", "crew physicals")
for i, m in enumerate([4, 7, 11]):
    f5("Apex Staffing Inc", date(2026, m, 15), 3000, str(7020 + i), "Contract Labor", "temp laborers")
for m in range(1, 13):
    f5("Northgate Properties Inc", date(2026, m, 1), 2000, str(7100 + m), "Rent", "yard and office")
f5("Jordan Avery", date(2026, 6, 26), 3200, "7041", "Uncategorized Expense", "")
f5("Blue Ridge Insurance Co", date(2026, 1, 20), 5000, "ACH", "Insurance", "general liability", "Bill Payment")
f5("State Department of Revenue", date(2026, 4, 20), 6400, "ACH", "Taxes & Licenses", "sales and use tax", "Bill Payment")
for m in range(1, 13):
    f5("Gusto", date(2026, m, 28), 4000, "ACH", "Payroll", "net pay and taxes", "Bill Payment")
for m in range(1, 13):
    f5("Chase Card Services", date(2026, m, 10), 2500, "ACH", "Credit Card Payment", "card balance", "Transfer")
f5("Ferguson Supply", date(2026, 8, 4), "14250.75", "7055", "Materials", "framing lumber")
for m in (3, 6, 9, 12):
    f5("Sam Cedar", date(2026, m, 30), 5000, str(7200 + m), "Owner's Draw", "")
for i, (m, a) in enumerate([(2, 4000), (5, 5500), (8, 6000)]):
    f5("Oakline Drywall", date(2026, m, 24), a, str(7300 + i), "Subcontractors", "hang and finish")
f5("Brannock Law Group", date(2026, 3, 19), 1200, "7012", "Legal & Professional Fees", "demand letter")
f5("Delmar Equipment Leasing", date(2026, 5, 5), 1800, "7028", "Equipment Rental", "skid steer, 2 weeks")
f5("Delmar Equipment Leasing", date(2026, 5, 22), 900, "7031", "Repairs & Maintenance", "operator and repair call")
f5("Summit Health & Safety Supply", date(2026, 7, 14), 2600, "7048", "Safety Supplies", "harnesses, hard hats")
c.lines.sort(key=lambda l: l["date"])
rows = [H5]
for ln in c.lines:
    rec = dict(Date=ln["date"], Payee=ln["name"], Amount=float(ln["amount"]), **ln["cols"])
    rows.append([rec.get(h, "") for h in H5])
write_xlsx(c.filename, rows)
c.want("Hartwell & Dunn, P.C.", "REVIEW", 4500)             # "P.C." + a legal account: could be a law firm, which is NOT exempt
c.want("Law Offices of Maria Santos, Inc.", "NEC", 4500)    # attorneys get a 1099 even when incorporated
c.want("Lakeside Occupational Health Inc", "MISC_MEDICAL", 2800)  # medical: reportable even when incorporated (tax-exempt hospitals aside)
c.want("Apex Staffing Inc", "CONFIRM_CORP", 9000)
c.want("Northgate Properties Inc", "CONFIRM_CORP", 24000)
c.want("Jordan Avery", "REVIEW", 3200)                      # no way to tell what the payment was for
c.want("Blue Ridge Insurance Co", "NOT_REPORTABLE", 5000)
c.want("State Department of Revenue", "NOT_REPORTABLE", 6400)
c.want("Gusto", "NOT_REPORTABLE", 48000)
c.want("Chase Card Services", "NOT_REPORTABLE", 30000)
c.want("Ferguson Supply", "NOT_REPORTABLE", "14250.75")
c.want("Sam Cedar", "NOT_REPORTABLE", 20000)
c.want("Oakline Drywall", "NEC", 15500)
c.want("Summit Health & Safety Supply", "REVIEW", 2600)     # name says health care, books say supplies: flag, do not guess
c.want("Brannock Law Group", "REVIEW", 1200)                # fees under $2,000 need no 1099, but attorney settlement money is reportable from $600
c.want("Delmar Equipment Leasing", "REVIEW", 2700)          # $1,800 rent + $900 service: two different forms, neither over the limit alone
c.finish(2026, 2000, [], hand_total="193650.75")

# =====================================================================================
# CASE 06 - messy CSV: title lines, $ signs, parentheses, trailing minus, mixed dates,
#           quoted names, blank lines, a refund, an unreadable amount, a TOTAL line.
# =====================================================================================
c = Case("06", "06-messy-export.csv", "Messy export: mixed date and number formats, a refund, an unreadable line", "ugly", "Fernhill Veterinary Clinic PLLC")
raw = [
    ["Fernhill Veterinary Clinic PLLC"], ["Check Detail"], ["Jan 1 - Dec 31, 2026"], [],
    ["Date", "Num", "Name", "Memo", "Category", "Amount"],
]


def m6(truth, dtxt, d, num, name, memo, cat, amt_txt, amt):
    c.pay(truth, d, amt, name=name)
    raw.append([dtxt, num, name, memo, cat, amt_txt])


m6("Whitfield, Dana", "1/5/26", date(2026, 1, 5), "5501", "Whitfield, Dana", "relief vet, 3 days", "Contract Labor", "$1,200.00", 1200)
m6("Okafor Kennel Cleaning", "01/19/2026", date(2026, 1, 19), "5504", "Okafor Kennel Cleaning", "", "Janitorial", "1,300.00", 1300)
m6("Whitfield, Dana", "2026-02-14", date(2026, 2, 14), "5509", "Whitfield, Dana", "relief vet", "Contract Labor", "$1,100.00", 1100)
raw.append([])
m6("Whitfield, Dana", "Mar 3, 2026", date(2026, 3, 3), "DEP", "Whitfield, Dana", "refund of overpayment", "Contract Labor", "(450.00)", -450)
m6("Pet Meds Direct", "3/18/2026", date(2026, 3, 18), "5513", "Pet Meds Direct", "vaccines", "Medical Supplies", "$3,150.40", "3150.40")
m6("Marsh Lab Courier", "4/2/2026", date(2026, 4, 2), "5517", "Marsh Lab Courier", "sample runs", "Outside Services", "400.00", 400)
raw.append(["4/22/2026", "5521", "Marsh Lab Courier", "sample runs", "Outside Services", "see note"])   # unreadable amount
m6("Tidewater Shredding", "5/11/2026", date(2026, 5, 11), "5526", "Tidewater Shredding", "records purge", "Outside Services", "900.00", 900)
m6("Idexx Labs", "6/30/2026", date(2026, 6, 30), "DEP", "Idexx Labs", "credit for returned kits", "Lab Supplies", "(125.00)", -125)
raw.append([])
m6("Okafor Kennel Cleaning", "07/20/2026", date(2026, 7, 20), "5540", "Okafor Kennel Cleaning", "", "Janitorial", " 1,300.00 ", 1300)
m6("Tidewater Shredding", "8/14/2026", date(2026, 8, 14), "5547", "Tidewater Shredding", "records purge", "Outside Services", "900.00", 900)
m6("Marsh Lab Courier", "Sep 9, 2026", date(2026, 9, 9), "5552", "Marsh Lab Courier", "sample runs", "Outside Services", "500.00", 500)
m6("(no name)", "10/2/2026", date(2026, 10, 2), "5560", "", "cash - weekend helper", "Contract Labor", "350.00", 350)
m6("Tidewater Shredding", "2026-12-04", date(2026, 12, 4), "CR", "Tidewater Shredding", "credit memo applied", "Outside Services", "300.00-", -300)
raw.append(["TOTAL", "", "", "", "", "$10,225.40"])
write_csv(c.filename, raw, bom=True)
c.want("Whitfield, Dana", "REVIEW", 1850, rows=[6, 8, 10])      # 1,200 + 1,100 - 450: under the limit ONLY because of the refund
c.want("Okafor Kennel Cleaning", "NEC", 2600, rows=[7, 17])
c.want("Pet Meds Direct", "NOT_REPORTABLE", "3150.40")           # supplies
c.want("Marsh Lab Courier", "REVIEW", 900)                       # one of its lines has no readable amount: total unknown
c.want("Tidewater Shredding", "CLOSE", 1500)                     # 900 + 900 - 300 credit; even without the credit, 1,800 is under
c.want("Idexx Labs", "NOT_REPORTABLE", -125)                     # a credit only
c.want("(no name)", "REVIEW", 350)                               # a payment with no payee cannot be left in a "no 1099" pile
c.finish(2026, 2000, ["REFUND", "UNREADABLE_LINES"], hand_total="10225.40", file_total="10225.40",
         file_total_ties=True, unreadable=1)

# =====================================================================================
# CASE 07 - bank-style export: payments are NEGATIVE numbers, payee is in "Description".
# =====================================================================================
c = Case("07", "07-bank-style-negative-amounts.csv", "Bank-style export: payments are negative numbers, no category column", "ugly", "Bluebird Bookshop")
H7 = ["Date", "Description", "Check Number", "Amount"]
rows = [H7]


def b7(truth, d, amt, num):
    c.pay(truth, d, amt)
    rows.append([us(d), truth, num, f"{-D(str(amt)):.2f}"])


for i, m in enumerate([1, 4, 7, 10]):
    b7("Hollis Bookkeeping", date(2026, m, 8), 550, str(810 + i))
b7("Quill Shelving & Carpentry", date(2026, 2, 19), 1250, "822")
b7("Quill Shelving & Carpentry", date(2026, 6, 4), 1100, "841")
for i, m in enumerate([3, 8, 11]):
    b7("Ingram Book Distributors", date(2026, m, 12), 4000, str(830 + i))
b7("Ingram Book Distributors", date(2026, 9, 2), -600, "")       # +600.00 in the file: a returns credit
for i, m in enumerate([5, 9, 12]):
    b7("Rosa Mendez", date(2026, m, 16), 500, str(850 + i))
for m in (1, 3, 5, 7, 9, 11):
    b7("Lumen Electric Utility", date(2026, m, 21), 210, "")
b7("Petal & Vine Florist", date(2026, 12, 9), 300, "861")
b7("Teodoro Vance", date(2026, 10, 27), 2600, "858")
rows[1:] = sorted(rows[1:], key=lambda r: (int(r[0].split("/")[0]), int(r[0].split("/")[1])))
write_csv(c.filename, rows)
# With no category column the agent has only the name to go on.
c.want("Hollis Bookkeeping", "NEC", 2200)                     # "bookkeeping" is a service
c.want("Quill Shelving & Carpentry", "NEC", 2350)             # "carpentry" is a service
c.want("Ingram Book Distributors", "NOT_REPORTABLE", 11400)   # 12,000 less the 600 credit; a distributor sells goods
c.want("Rosa Mendez", "CLOSE", 1500)                          # purpose unknown, but worth watching at $1,500
c.want("Lumen Electric Utility", "NOT_REPORTABLE", 1260)      # under the limit whatever it is
c.want("Petal & Vine Florist", "NOT_REPORTABLE", 300)
c.want("Teodoro Vance", "REVIEW", 2600)                       # over the limit, and nothing says what for: must ask, not guess
c.finish(2026, 2000, ["REFUND"], hand_total=21610)

# =====================================================================================
# CASE 08 - ledger-style export with Debit and Credit columns; the paying account is in
#           "Split", the expense account is in "Account".
# =====================================================================================
c = Case("08", "08-ledger-debit-credit-columns.csv", "Ledger export with Debit/Credit columns and a Split column", "ugly", "Granite Peak Brewing Co")
H8 = ["Date", "Type", "Num", "Name", "Memo", "Account", "Split", "Debit", "Credit"]
raw = [["Granite Peak Brewing Co"], ["Transaction Detail by Account"], ["January through December 2026"], [], H8]
CHK8, VISA8 = "1000 · Operating Checking", "2050 · Visa 7781"
lines8 = []


def l8(truth, d, amt, typ, num, memo, acct, split, method="b"):
    c.pay(truth, d, amt, method)
    a = D(str(amt))
    lines8.append((d, [us(d), typ, num, truth, memo, acct, split, f"{a:,.2f}" if a > 0 else "", f"{-a:,.2f}" if a < 0 else ""]))


for i, (m, a) in enumerate([(2, 800), (6, 700), (10, 650)]):
    l8("Hopline Draft Services", date(2026, m, 5), a, "Check", str(9100 + i), "line cleaning and repair", "6400 · Repairs & Maintenance", CHK8)
for i, m in enumerate([1, 4, 6, 9, 12]):
    l8("Yakima Hop Farms", date(2026, m, 14), 2300, "Check", str(9200 + i), "hops", "5000 · Cost of Goods Sold", CHK8)
for i, m in enumerate([2, 4, 6, 8, 10]):
    l8("Tessa Malloy", date(2026, m, 23), 400, "Check", str(9300 + i), "taproom music", "6100 · Contract Labor", CHK8)
l8("Tessa Malloy", date(2026, 12, 19), 400, "Credit Card Charge", "", "taproom music", "6100 · Contract Labor", VISA8, "c")
for m in (3, 7, 11):
    l8("Cascade Label Printing", date(2026, m, 9), 900, "Credit Card Charge", "", "can labels", "5100 · Packaging Supplies", VISA8, "c")
l8("Ridgeline Refrigeration", date(2026, 5, 27), 2900, "Check", "9400", "glycol chiller repair", "6400 · Repairs & Maintenance", CHK8)
l8("Ridgeline Refrigeration", date(2026, 7, 2), -1000, "Deposit", "", "refund - warranty covered part", "6400 · Repairs & Maintenance", CHK8)
for _, r in sorted(lines8, key=lambda t: t[0]):
    raw.append(r)
write_csv(c.filename, raw)
c.want("Hopline Draft Services", "NEC", 2150)
c.want("Yakima Hop Farms", "NOT_REPORTABLE", 11500)
c.want("Tessa Malloy", "NEC", 2000, total=2400)        # 5 checks x 400 = exactly $2,000; the sixth was on the card
c.want("Cascade Label Printing", "NOT_REPORTABLE", 0)
c.want("Ridgeline Refrigeration", "REVIEW", 1900)      # 2,900 less 1,000: under the limit ONLY because of the refund
c.finish(2026, 2000, ["REFUND"], hand_total=20650)

# =====================================================================================
# CASE 09 - PLANTED ERROR: the same check appears twice.
# =====================================================================================
c = Case("09", "09-planted-duplicate-checks.csv", "PLANTED ERROR: duplicated check lines", "planted", "Sable Interiors")
CK = {"Transaction Type": "Check", "Paid From": "Checking 3306"}
c.pay("Olsen Carpentry", date(2026, 3, 12), 1200, Num="4102", Category="Subcontractors", Memo="built-in shelving", **CK)
c.pay("Olsen Carpentry", date(2026, 3, 12), 1200, Num="4102", Category="Subcontractors", Memo="built-in shelving", **CK)   # duplicate
c.pay("Paige Turner Bookkeeping", date(2026, 1, 30), 1500, Num="4110", Category="Accounting", Memo="Q4 books", **CK)
c.pay("Paige Turner Bookkeeping", date(2026, 7, 31), 1500, Num="4150", Category="Accounting", Memo="Q2 books", **CK)
c.pay("Paige Turner Bookkeeping", date(2026, 7, 31), 1500, Num="4150", Category="Accounting", Memo="Q2 books", **CK)       # duplicate
c.pay("Vargas Upholstery", date(2026, 5, 6), 1050, Num="4201", Category="Subcontractors", Memo="sofa - Henley job", **CK)
c.pay("Vargas Upholstery", date(2026, 5, 6), 1050, Num="4202", Category="Subcontractors", Memo="chairs - Henley job", **CK)  # NOT a duplicate
c.pay("Fabric Depot", date(2026, 12, 11), 3300, Num="4260", Category="Materials", Memo="", **CK)
c.lines.sort(key=lambda l: l["date"])
write_csv(c.filename, flat_rows(c, H, H))
c.want("Olsen Carpentry", "REVIEW", 2400)              # over the limit ONLY because of the duplicate
c.want("Paige Turner Bookkeeping", "NEC", 4500)        # over either way; amount shown is what the file says, with a warning
c.want("Vargas Upholstery", "NEC", 2100)               # two different check numbers: real payments
c.want("Fabric Depot", "NOT_REPORTABLE", 3300)
c.finish(2026, 2000, ["DUPLICATE"], hand_total=12300,
         notes="The agent must flag both duplicate pairs and must not flag the Vargas checks.")
KEY["09"]["duplicateGroups"] = 2

# =====================================================================================
# CASE 10 - PLANTED ERROR: the report's own totals do not match its lines.
# =====================================================================================
c = Case("10", "10-planted-totals-do-not-tie.xlsx", "PLANTED ERROR: subtotal and grand total do not match the lines", "planted", "Alder Creek Farm Supply")
BK = "Checking 6672"
for i, (m, a) in enumerate([(3, 1000), (6, 1100), (10, 1000)]):
    g("Benton Fence Repair", date(2026, m, 7), a, "Check", str(2300 + i), "paddock fence", BK, "Repairs & Maintenance")
for i, m in enumerate([1, 12]):
    g("Kira Sato", date(2026, m, 18), 1250, "Check", str(2310 + i), "seasonal counter help", BK, "Contract Labor")
for i, m in enumerate([2, 5, 8, 11]):
    g("Farmers Co-op", date(2026, m, 25), 1500, "Check", str(2320 + i), "feed", BK, "Feed Purchases")
rows, grand10 = grouped_rows(c, ["Benton Fence Repair", "Farmers Co-op", "Kira Sato"], GH,
                             bad_subtotal={"Benton Fence Repair": D(4300)})   # lines add to 3,100
write_xlsx(c.filename, rows)
c.want("Benton Fence Repair", "NEC", 3100)   # what the lines add to; the file's own subtotal says 4,300
c.want("Kira Sato", "NEC", 2500)
c.want("Farmers Co-op", "NOT_REPORTABLE", 6000)
c.finish(2026, 2000, ["SUBTOTAL_MISMATCH", "TOTAL_MISMATCH"], hand_total=11600, file_total=12800, file_total_ties=False,
         notes="A $1,200 line is missing from the export. The agent must say the totals do not tie, prominently.")

# =====================================================================================
# CASE 11 - wrong period: last year's December is in the file and the year stops in September.
# =====================================================================================
c = Case("11", "11-wrong-period.csv", "PLANTED ERROR: prior-year lines mixed in and the year is incomplete", "planted", "Pinecrest Tutoring LLC")
CK = {"Transaction Type": "Check", "Paid From": "Checking 5518"}
c.pay("Amira Haddad", date(2025, 12, 15), 900, year_ok=False, Num="601", Category="Contract Labor", Memo="tutoring", **CK)
c.pay("Brightpath Curriculum", date(2025, 12, 20), 400, year_ok=False, Num="602", Category="Supplies", Memo="workbooks", **CK)
c.pay("Brightpath Curriculum", date(2025, 12, 28), 250, year_ok=False, Num="603", Category="Supplies", Memo="workbooks", **CK)
c.pay("Amira Haddad", date(2026, 1, 16), 600, Num="610", Category="Contract Labor", Memo="tutoring", **CK)
c.pay("Leo Grant", date(2026, 2, 13), 1000, Num="615", Category="Contract Labor", Memo="test prep", **CK)
c.pay("Amira Haddad", date(2026, 4, 17), 700, Num="622", Category="Contract Labor", Memo="tutoring", **CK)
c.pay("Brightpath Curriculum", date(2026, 6, 5), 1000, Num="630", Category="Supplies", Memo="workbooks", **CK)
c.pay("Leo Grant", date(2026, 9, 28), 1100, Num="641", Category="Contract Labor", Memo="test prep", **CK)
write_csv(c.filename, flat_rows(c, H, H))
c.want("Amira Haddad", "NOT_REPORTABLE", 1300)     # the $900 from December 2025 belongs to last year (and was over 2025's $600 limit: the agent should say so)
c.want("Leo Grant", "NEC", 2100)
c.want("Brightpath Curriculum", "NOT_REPORTABLE", 1000)
c.finish(2026, 2000, ["OUTSIDE_YEAR", "PARTIAL_YEAR"], hand_total=5950)

# =====================================================================================
# CASE 12 - a 2025 file. The old $600 limit applies to 2025 payments.
# =====================================================================================
c = Case("12", "12-prior-year-600-limit.csv", "A 2025 check register with Payment and Deposit columns: the old $600 limit must apply", "rules", "Old Mill Antiques")
CK = {"Transaction Type": "Check", "Paid From": "Checking 7090"}
c.pay("Gabe Linden", date(2025, 1, 22), 650, Num="300", Category="Contract Labor", Memo="furniture repair", **CK)
c.pay("Nora Fitch", date(2025, 5, 9), 500, Num="318", Category="Contract Labor", Memo="appraisals", **CK)
for m in (2, 5, 8, 11):
    c.pay("Wren Cleaning", date(2025, m, 3), 100, Num=str(330 + m), Category="Janitorial", Memo="", **CK)
for m in range(1, 13):
    c.pay("Old Mill Plaza LLC", date(2025, m, 1), 900, Num=str(350 + m), Category="Rent", Memo="booth rent", **CK)
c.pay("Hall family estate sale", date(2025, 6, 14), -3000, Num="", Category="Sales", Memo="consignment proceeds")   # money IN
c.lines.sort(key=lambda l: l["date"])
H12 = ["Date", "Check No", "Payee", "Payment", "Deposit", "Category"]
rows = [H12]
for ln in c.lines:
    a_ = ln["amount"]
    rows.append([us(ln["date"]), ln["cols"].get("Num", ""), ln["name"], f"{a_:.2f}" if a_ > 0 else "", f"{-a_:.2f}" if a_ < 0 else "", ln["cols"]["Category"]])
write_csv(c.filename, rows)
c.want("Hall family estate sale", "NOT_REPORTABLE", -3000)   # a deposit, not a payment; and not a "refund" either
c.want("Gabe Linden", "NEC", 650)           # $650 >= $600
c.want("Nora Fitch", "CLOSE", 500)          # $450 <= 500 < $600
c.want("Wren Cleaning", "NOT_REPORTABLE", 400)
c.want("Old Mill Plaza LLC", "MISC_RENT", 10800)
c.finish(2025, 600, [], hand_total=9350)

# =====================================================================================
# CASE 13 - a 2027 file. The agent does not know the 2027 limit and must say so.
# CASE 14 - not a payments file at all.
# =====================================================================================
rows = [H]
for m in range(1, 13):
    rows.append([f"{m}/15/2027", "Check", str(100 + m), "Leo Grant", "Checking 5518", "Contract Labor", "", "400.00"])
write_csv("13-future-year.csv", rows)
KEY["13"] = dict(file="13-future-year.csv", title="A 2027 file: rules not built in, must refuse", kind="planted",
                 payer="Pinecrest Tutoring LLC", fatal="UNSUPPORTED_YEAR")
write_csv("14-not-a-payments-file.csv", [
    ["Vendor", "Contact", "Phone", "Email", "City"],
    ["Rivera Plumbing", "Luis Rivera", "555-0142", "luis@example.com", "Dayton"],
    ["Dana Whitfield", "Dana Whitfield", "555-0177", "dana@example.com", "Dayton"],
    ["Office Depot", "", "555-0100", "", "Kettering"],
])
KEY["14"] = dict(file="14-not-a-payments-file.csv", title="A vendor contact list, not payments: must refuse", kind="planted",
                 payer="-", fatal="NO_COLUMNS")

# =====================================================================================
# CASE 15 - a vendor report that lists BILLS as well as the payments of those bills.
#           Counting both would double every vendor. Bill payments are negative, as
#           QuickBooks-style vendor reports show them. One bill is still unpaid at year end.
# =====================================================================================
c = Case("15", "15-bills-and-bill-payments.xlsx", "Report lists bills AND their payments: only payments may count", "ugly", "Harrow & Finch Cabinetry")
BK, CC = "Checking 4471", "Visa 0338"
raw15 = {}   # vendor -> list of rows exactly as written in the file


def w15(v, d, typ, num, memo, acct, split, written, paid=None, method="b"):
    """`written` is the number in the file. `paid` is the true cash paid (None = not a payment)."""
    raw15.setdefault(v, []).append([d, typ, num, memo, acct, split, float(written)])
    if paid is not None:
        c.pay(v, d, paid, method)


K = "Kestrel Fabrication"
w15(K, date(2026, 1, 10), "Bill", "INV-88", "drawer boxes", "Accounts Payable", "Subcontractors", 1500)
w15(K, date(2026, 1, 25), "Bill Payment (Check)", "6001", "", BK, "Accounts Payable", -1500, paid=1500)
w15(K, date(2026, 6, 3), "Bill", "INV-131", "drawer boxes", "Accounts Payable", "Subcontractors", 1400)
w15(K, date(2026, 6, 20), "Bill Payment (Check)", "6040", "", BK, "Accounts Payable", -1400, paid=1400)
P = "Pine Hollow Graphics"
w15(P, date(2026, 2, 2), "Bill", "2211", "showroom signs", "Accounts Payable", "Advertising", 1200)
w15(P, date(2026, 2, 20), "Bill Payment (Check)", "6010", "", BK, "Accounts Payable", -1200, paid=1200)
w15(P, date(2026, 3, 1), "Vendor Credit", "CM-4", "reprint credit", "Accounts Payable", "Advertising", -300)
w15(P, date(2026, 12, 15), "Bill", "2390", "holiday mailer - unpaid at year end", "Accounts Payable", "Advertising", 900)
M = "Marlow Finishing"
w15(M, date(2026, 4, 4), "Check", "6022", "lacquer work", BK, "Subcontractors", 1000, paid=1000)
w15(M, date(2026, 9, 9), "Check", "6071", "lacquer work", BK, "Subcontractors", 1100, paid=1100)
B = "Baxter Lumber"
w15(B, date(2026, 3, 12), "Bill", "77102", "maple and birch", "Accounts Payable", "Materials", 5000)
w15(B, date(2026, 3, 30), "Bill Payment (Check)", "6018", "", BK, "Accounts Payable", -5000, paid=5000)
w15(B, date(2026, 8, 5), "Expense", "", "hardware", CC, "Materials", 300, paid=300, method="c")
w15(B, date(2026, 11, 14), "Bill", "80455", "walnut", "Accounts Payable", "Materials", 5000)
w15(B, date(2026, 12, 8), "Bill Payment (Check)", "6090", "", BK, "Accounts Payable", -5000, paid=5000)
O = "Odell Pruitt"
w15(O, date(2026, 7, 7), "Bill", "OP-3", "install crew, Henley kitchen", "Accounts Payable", "Contract Labor", 2500)
w15(O, date(2026, 7, 21), "Bill Payment (Credit Card)", "", "", CC, "Accounts Payable", -2500, paid=2500, method="c")
rows = [[c.payer], ["Transaction List by Vendor"], ["January - December 2026"], [], [""] + GH]
grand = 0.0
for v in sorted(raw15):
    rows.append([v])
    sub = 0.0
    for r in raw15[v]:
        rows.append([""] + r)
        sub += r[-1]
    rows.append([f"Total for {v}"] + [""] * (len(GH) - 1) + [sub])
    grand += sub
rows.append(["TOTAL"] + [""] * (len(GH) - 1) + [grand])
write_xlsx(c.filename, rows)
c.want("Kestrel Fabrication", "NEC", 2900)                 # paid 1,500 + 1,400. Bills + payments would wrongly give 5,800
c.want("Pine Hollow Graphics", "NOT_REPORTABLE", 1200)     # paid 1,200. The unpaid 900 bill and the 300 credit are not cash
c.want("Marlow Finishing", "NEC", 2100)                    # plain checks
c.want("Baxter Lumber", "NOT_REPORTABLE", 10000, total=10300)
c.want("Odell Pruitt", "NOT_REPORTABLE", 0, total=2500)    # the bill was paid by credit card
c.finish(2026, 2000, ["NOT_PAYMENTS"], hand_total=19000, file_total=3000, file_total_ties=True,
         notes="The file's own total (3,000) is the net of bills and payments as written; it must tie to the lines as written.")
KEY["15"]["controls"]["notPaymentLines"] = 8

with open(os.path.join(HERE, "answer-key.json"), "w") as f:
    json.dump(KEY, f, indent=1)
print("wrote", len(KEY), "cases;", sum(v.get("controls", {}).get("linesRead", 0) for v in KEY.values()), "payment lines")
