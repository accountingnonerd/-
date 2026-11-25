#!/usr/bin/env python3
"""Builds the acceptance test for Acquire-to-Retire 01, "What goes on the asset schedule?".

Each case is one general ledger report for the year 2026 (January 1 to December 31), in the layout
of QuickBooks Online (General Ledger), QuickBooks Desktop (General Ledger) or Xero (Account
Transactions), written from a model of accounts and ledger lines for invented businesses. The answer
key is worked out from the model with the rules below, never by reading the files back.
Money is held in integer cents, debit positive.

The rules the key follows (version 1):
  Account roles, from the account name (number prefixes like "15000 · " and codes like " (710)"
  removed, lower case), first match wins:
    accumulated depreciation: "accumulated depreciation", "accum depr", "accum. depr";
    depreciation expense: "depreciation";
    fixed asset (cost): equipment, furniture, fixture(s), vehicle(s), truck(s), trailer(s),
      machinery, computer(s), leasehold improvement(s), improvements, building(s), "land" as a word,
      "fixed asset(s)", "property and equipment", and none of: expense(s), rental, rent, repair(s),
      maintenance, small, supplies, lease, fuel, insurance, registration, software, internet, minor;
    review for capitalization: repair(s), maintenance, supplies, tools, computer, software,
      equipment, furniture, improvement(s), and none of: rental, rent, lease, fuel, insurance;
    anything else: other (read, checked, not reviewed).
  The accountant can change any account's role on screen; the review then runs again.
  Reversals: in a fixed asset account, a credit equal to an earlier-or-later unpaired debit of the
    same amount, same name, at most 31 days apart, is a reversal; neither line is an addition or
    disposal.
  Additions: the other debits to fixed asset accounts. Journal entries among them are flagged.
  Disposals: the other credits to fixed asset accounts.
  Capitalization candidates: in review accounts, the debit lines grouped by account, date, type,
    number and name (one bill); a group whose total is at least the threshold ($2,500.00 unless the
    accountant types another) is a candidate, unless the same account has a credit line of exactly
    that amount during the year (already reclassified or refunded: dropped), or its name has 3 or
    more groups at or above the threshold in that account during the year: then it is routine, like
    a service contract (listed, not proposed).
  Depreciation booked: the sum of the lines in depreciation expense accounts.
  Tax depreciation typed: adjustment = typed - booked (Dr Depreciation expense, Cr Accumulated
    depreciation; negative reverses).
  Last year's schedule typed (cost, accumulated depreciation): compared with the ledger's opening
    balances of fixed asset accounts (cost) and accumulated depreciation accounts (shown positive).
  The file adds up: for each account, opening + lines = the report's total and ending balance.

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
Y0, Y1 = date(2026, 1, 1), date(2026, 12, 31)
P = lambda n: os.path.join(OUT, n)
D = lambda m, d: date(2026, m, d)

def money(c, dollar=False, paren=False):
    s = f"{abs(c) // 100:,}.{abs(c) % 100:02d}"
    if dollar: s = "$" + s
    if c < 0: return f"({s})" if paren else "-" + s
    return s

# ------------------------------------------------------------------ the model
def acct(name, opening=0, num=None, code=None):
    return {"name": name, "opening": opening, "lines": [], "num": num, "code": code}

def line(a, d, typ, num, name, memo, amount):
    a["lines"].append({"date": d, "type": typ, "num": num, "name": name, "memo": memo, "amount": amount})

def book(seed, company):
    """A small business's ledger for 2026: fixed assets, depreciation, and ordinary expenses."""
    r = random.Random(seed)
    A = {}
    A["fe"] = acct("Furniture and Equipment", 4_812_550, 15000, 710)
    A["veh"] = acct("Vehicles", 6_245_000, 15100, 720)
    A["ad"] = acct("Accumulated Depreciation", -5_903_412, 17000, 711)
    A["dep"] = acct("Depreciation Expense", 0, 62400, 416)
    A["rm"] = acct("Repairs and Maintenance", 0, 64300, 473)
    A["sup"] = acct("Office Supplies & Software", 0, 64100, 461)
    A["tools"] = acct("Small Tools and Equipment", 0, 64200, 462)
    A["rent"] = acct("Equipment Rental", 0, 64500, 465)
    A["util"] = acct("Utilities", 0, 68600, 445)
    A["adv"] = acct("Advertising & Marketing", 0, 60000, 400)
    vendors = ["Harbor Supply Co", "Midline Hardware", "Office Depot Business", "Riverside Electric", "Apex Plumbing", "Summit Office Systems",
               "Greenfield Tools", "Metro Utilities", "Brightside Media", "Northline Rentals"]
    n = 1000
    for m in range(1, 13):               # ordinary monthly expenses, all under the threshold
        for key, vend, lo, hi in (("util", "Metro Utilities", 18000, 42000), ("adv", "Brightside Media", 25000, 90000), ("rent", "Northline Rentals", 30000, 120000)):
            n += 1; line(A[key], D(m, r.randint(3, 25)), "Bill", str(n), vend, "Monthly", r.randint(lo, hi))
        for _ in range(r.randint(1, 3)):
            n += 1; line(A["sup"], D(m, r.randint(1, 28)), "Expense", str(n), r.choice(["Office Depot Business", "Summit Office Systems"]), "Supplies", r.randint(2500, 60000))
        for _ in range(r.randint(0, 2)):
            n += 1; line(A["rm"], D(m, r.randint(1, 28)), "Bill", str(n), r.choice(["Riverside Electric", "Apex Plumbing", "Midline Hardware"]), "Repair call", r.randint(9000, 180000))
        if r.random() < 0.5:
            n += 1; line(A["tools"], D(m, r.randint(1, 28)), "Expense", str(n), "Greenfield Tools", "Hand tools", r.randint(3000, 95000))
    return A

def depreciate(A, total, monthly=True, months=12):
    """Depreciation as journal entries: Dr Depreciation expense, Cr Accumulated depreciation."""
    if monthly:
        per = total // months
        for m in range(1, months + 1):
            amt = per if m < months else total - per * (months - 1)
            line(A["dep"], D(m, 28), "Journal Entry", f"DEP-{m:02d}", "", "Monthly depreciation", amt)
            line(A["ad"], D(m, 28), "Journal Entry", f"DEP-{m:02d}", "", "Monthly depreciation", -amt)
    else:
        line(A["dep"], D(12, 31), "Journal Entry", "DEP-26", "", "Depreciation 2026", total)
        line(A["ad"], D(12, 31), "Journal Entry", "DEP-26", "", "Depreciation 2026", -total)

# ------------------------------------------------------------------ the rules
import re
NUMPFX = re.compile(r"^\s*\d[\d.\-]*\s*(·|-|–)?\s*")
def norm_name(s):
    s = re.sub(r"\s*\([0-9A-Za-z.\-]{1,10}\)\s*$", "", s.strip())
    s = NUMPFX.sub("", s)
    return s.strip()

FA_W = re.compile(r"equipment|furniture|fixtures?\b|vehicles?\b|trucks?\b|trailers?\b|machinery|computers?\b|leasehold improvements?|improvements\b|buildings?\b|\bland\b|fixed assets?|property and equipment")
NOT_FA = re.compile(r"expenses?\b|rental|\brent\b|repairs?\b|maintenance|small|supplies|lease|fuel|insurance|registration|software|internet|minor")
RV_W = re.compile(r"repairs?\b|maintenance|supplies|tools|computer|software|equipment|furniture|improvements?\b")
NOT_RV = re.compile(r"rental|\brent\b|lease|fuel|insurance")
def role_of(name):
    s = norm_name(name).lower()
    if re.search(r"accumulated depreciation|accum\.? depr", s): return "ad"
    if "depreciation" in s: return "dep"
    if FA_W.search(s) and not NOT_FA.search(s): return "fa"
    if RV_W.search(s) and not NOT_RV.search(s): return "review"
    return "other"

def key_for(A, threshold=250000, sched=None, tax_dep=None, roles=None, period=("2026-01-01", "2026-12-31")):
    accts = [a for a in A.values() if a["lines"] or a["opening"]]      # an account with no balance and no lines is not in the export
    role = {a["name"]: (roles or {}).get(a["name"], role_of(a["name"])) for a in accts}
    by = lambda r_: [a for a in accts if role[a["name"]] == r_]
    additions, disposals, reversals, rollforward = [], [], [], []
    for a in by("fa"):
        ls = sorted(enumerate(a["lines"]), key=lambda t: (t[1]["date"], t[0]))
        paired = set()
        for i, c in ls:
            if c["amount"] >= 0: continue
            for j, d in ls:
                if j in paired or d["amount"] != -c["amount"] or (d["name"] or "").lower() != (c["name"] or "").lower(): continue
                if abs((d["date"] - c["date"]).days) > 31: continue
                paired.add(i); paired.add(j)
                reversals.append({"account": a["name"], "amount": d["amount"] / 100, "name": d["name"]})
                break
        add = [x for k, x in ls if k not in paired and x["amount"] > 0]
        dis = [x for k, x in ls if k not in paired and x["amount"] < 0]
        for x in add: additions.append({"account": a["name"], "date": x["date"].isoformat(), "num": x["num"], "name": x["name"], "amount": x["amount"] / 100, "journal": "journal" in x["type"].lower()})
        for x in dis: disposals.append({"account": a["name"], "date": x["date"].isoformat(), "num": x["num"], "name": x["name"], "amount": -x["amount"] / 100})
        end = a["opening"] + sum(x["amount"] for x in a["lines"])
        rollforward.append({"account": a["name"], "opening": a["opening"] / 100, "additions": sum(x["amount"] for x in add) / 100,
                            "disposals": sum(x["amount"] for x in dis) / 100, "ending": end / 100})
    adroll = []
    for a in by("ad"):
        end = a["opening"] + sum(x["amount"] for x in a["lines"])
        adroll.append({"account": a["name"], "opening": a["opening"] / 100, "credits": sum(x["amount"] for x in a["lines"] if x["amount"] < 0) / 100,
                       "debits": sum(x["amount"] for x in a["lines"] if x["amount"] > 0) / 100, "ending": end / 100})
    candidates, routine = [], []
    for a in by("review"):
        groups = {}
        for x in a["lines"]:
            k = (x["date"], x["type"], x["num"], x["name"])
            groups.setdefault(k, []).append(x)
        big = {}
        for k in groups:
            t_ = sum(x["amount"] for x in groups[k])
            if k[3] and t_ >= threshold: big.setdefault(k[3].lower(), []).append(t_)
        counts = {n_: len(v) for n_, v in big.items()}
        seen_routine = {}
        for k in sorted(groups, key=lambda k: (k[0], k[2])):
            tot = sum(x["amount"] for x in groups[k])
            if tot < threshold: continue
            if any(x["amount"] == -tot for x in a["lines"]): continue      # already reclassified or refunded
            if k[3] and counts[k[3].lower()] >= 3:
                if k[3].lower() not in seen_routine:
                    seen_routine[k[3].lower()] = 1
                    routine.append({"account": a["name"], "name": k[3], "count": counts[k[3].lower()], "amount": sum(big[k[3].lower()]) / 100})
                continue
            candidates.append({"account": a["name"], "date": k[0].isoformat(), "num": k[2], "name": k[3], "amount": tot / 100, "lines": len(groups[k])})
    booked = sum(x["amount"] for a in by("dep") for x in a["lines"])
    cost_open = sum(a["opening"] for a in by("fa"))
    ad_open = -sum(a["opening"] for a in by("ad"))
    ex = []
    if not by("fa"): ex.append("NO_FIXED_ASSET_ACCOUNTS")
    if candidates: ex.append("CAPITALIZE_CANDIDATES")
    if routine: ex.append("ROUTINE_CHARGES")
    if disposals: ex.append("DISPOSALS")
    if disposals and not any(x["amount"] > 0 for a in by("ad") for x in a["lines"]): ex.append("AD_NOT_REMOVED")
    if reversals: ex.append("REVERSALS")
    if any(x["journal"] for x in additions): ex.append("JOURNAL_ENTRY_ADDITIONS")
    if booked == 0 and (cost_open > 0 or additions): ex.append("NO_DEPRECIATION_BOOKED")
    if not period: ex.append("PERIOD_UNKNOWN")
    k = {"period": {"from": period[0], "to": period[1]} if period else None,
         "accounts": {a["name"]: role[a["name"]] for a in accts},
         "rollforward": rollforward, "adRollforward": adroll,
         "additions": additions, "disposals": disposals, "reversals": reversals, "candidates": candidates, "routine": routine,
         "costOpening": cost_open / 100, "adOpening": ad_open / 100,
         "costEnding": sum(r_["ending"] for r_ in rollforward), "adEnding": -sum(r_["ending"] for r_ in adroll),
         "additionsTotal": sum(x["amount"] for x in additions), "candidatesTotal": sum(x["amount"] for x in candidates),
         "depreciationBooked": booked / 100, "threshold": threshold / 100}
    k["costEnding"] = round(k["costEnding"], 2); k["adEnding"] = round(k["adEnding"], 2)
    k["additionsTotal"] = round(k["additionsTotal"], 2); k["candidatesTotal"] = round(k["candidatesTotal"], 2)
    if tax_dep is not None:
        k["taxDepreciation"] = tax_dep / 100; k["depreciationAdjustment"] = (tax_dep - booked) / 100
        if tax_dep != booked: ex.append("DEPRECIATION_DIFFERS")
    if sched is not None:
        k["scheduleCost"] = sched[0] / 100; k["scheduleAD"] = sched[1] / 100
        k["openingDiffCost"] = (cost_open - sched[0]) / 100; k["openingDiffAD"] = (ad_open - sched[1]) / 100
        if cost_open != sched[0] or ad_open != sched[1]: ex.append("OPENING_DIFFERS")
    k["exceptions"] = sorted(ex)
    return k

# ------------------------------------------------------------------ writers
def ds(d): return d.strftime("%m/%d/%Y")

def write_qbo(path, company, A, csv_out=False, paren=False, period_text="January 1 - December 31, 2026", drop=None, footer=True):
    """QuickBooks Online: Reports > General Ledger > Export to Excel. Amount in the account's own sign
    (debit positive for assets and expenses), running Balance, a Total row per account."""
    rows = [[company], ["General Ledger"], [period_text], [], ["", "Date", "Transaction Type", "Num", "Name", "Memo/Description", "Split", "Amount", "Balance"]]
    for a in A.values():
        if not a["lines"] and not a["opening"]: continue
        rows.append([a["name"]])
        bal = a["opening"]
        rows.append(["", "Beginning Balance", "", "", "", "", "", "", bal / 100])
        tot = 0
        for i, x in enumerate(sorted(a["lines"], key=lambda x: x["date"])):
            bal += x["amount"]; tot += x["amount"]
            if drop and drop == (a["name"], i): continue
            rows.append(["", ds(x["date"]), x["type"], x["num"], x["name"], x["memo"], "-Split-", x["amount"] / 100, bal / 100])
        rows.append([f"Total for {a['name']}", "", "", "", "", "", "", tot / 100, ""])
    if footer: rows += [[], [], ["Accrual Basis Wednesday, January 20, 2027 09:12 AM GMT-05:00"]]
    if csv_out:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL)
            for r_ in rows: w.writerow([money(round(v * 100), True, paren) if isinstance(v, float) else ("" if v is None else v) for v in r_])
        return
    wb = Workbook(); ws = wb.active; ws.title = "General Ledger"
    for r_ in rows: ws.append(r_)
    wb.save(path)

def write_qbd(path, A):
    """QuickBooks Desktop: Reports > Accountant & Taxes > General Ledger > Excel. Account numbers as
    '15000 · Furniture and Equipment'; Debit and Credit columns; the title goes to the page header,
    so the cells carry no period."""
    wb = Workbook(); ws = wb.active; ws.title = "Sheet1"
    ws.append(["", "", "Type", "Date", "Num", "Name", "Memo", "Split", "Debit", "Credit", "Balance"])
    for a in A.values():
        if not a["lines"] and not a["opening"]: continue
        label = f"{a['num']} · {a['name']}"
        ws.append([label, "", "", "", "", "", "", "", None, None, a["opening"] / 100])
        bal, dr, cr = a["opening"], 0, 0
        for x in sorted(a["lines"], key=lambda x: x["date"]):
            bal += x["amount"]
            d_ = x["amount"] if x["amount"] > 0 else None; c_ = -x["amount"] if x["amount"] < 0 else None
            dr += d_ or 0; cr += c_ or 0
            ws.append(["", "", x["type"], datetime(x["date"].year, x["date"].month, x["date"].day), x["num"], x["name"], x["memo"], "-SPLIT-",
                       d_ / 100 if d_ else None, c_ / 100 if c_ else None, bal / 100])
        ws.append([f"Total {label}", "", "", "", "", "", "", "", dr / 100, cr / 100, bal / 100])
    ws.append(["TOTAL"])
    for row in ws.iter_rows(min_row=2):
        if isinstance(row[3].value, datetime): row[3].number_format = "mm/dd/yyyy"
    wb.save(path)

def write_xero(path, company, A):
    """Xero: Reports > Account Transactions > Export to Excel. Grouped by account, 'Opening Balance'
    and 'Closing Balance' rows, Debit and Credit columns, dates like '15 Mar 2026'."""
    wb = Workbook(); ws = wb.active; ws.title = "Account Transactions"
    for r_ in [["Account Transactions"], [company], ["For the period 1 January 2026 to 31 December 2026"], [],
               ["Date", "Source", "Contact", "Description", "Reference", "Debit", "Credit", "Running Balance"]]:
        ws.append(r_)
    src = {"Bill": "Payable Invoice", "Expense": "Spend Money", "Check": "Spend Money", "Journal Entry": "Manual Journal", "Deposit": "Receive Money"}
    for a in A.values():
        if not a["lines"] and not a["opening"]: continue
        ws.append([f"{a['name']} ({a['code']})"])
        ws.append(["Opening Balance", "", "", "", "", None, None, a["opening"] / 100])
        bal, dr, cr = a["opening"], 0, 0
        for x in sorted(a["lines"], key=lambda x: x["date"]):
            bal += x["amount"]
            d_ = x["amount"] if x["amount"] > 0 else None; c_ = -x["amount"] if x["amount"] < 0 else None
            dr += d_ or 0; cr += c_ or 0
            ws.append([x["date"].strftime("%d %b %Y"), src.get(x["type"], x["type"]), x["name"], x["memo"], x["num"], d_ / 100 if d_ else None, c_ / 100 if c_ else None, bal / 100])
        ws.append([f"Total {a['name']} ({a['code']})", "", "", "", "", dr / 100, cr / 100, None])
        ws.append(["Closing Balance", "", "", "", "", None, None, bal / 100])
    wb.save(path)

KEY = {}
def case(cid, title, kind, file, status, k, layout, extra=None):
    e = {"title": title, "kind": kind, "file": file, "status": status, "layout": layout}
    e.update(k)
    if extra: e.update(extra)
    KEY[cid] = e

# ---- 01 QuickBooks Online, a clean year: two purchases recorded as assets, depreciation booked monthly
A = book(1, "Northgate Electrical Supply")
line(A["fe"], D(3, 12), "Bill", "2207", "Summit Office Systems", "Conference room furniture", 684_000)
line(A["veh"], D(6, 3), "Check", "4418", "Carver Ford", "2026 Ford Transit van", 4_675_000)
depreciate(A, 1_386_400)
write_qbo(P("01-northgate-general-ledger.xlsx"), "Northgate Electrical Supply", A)
case("01", "QuickBooks Online, a clean year: purchases recorded as assets, depreciation booked", "clean", "01-northgate-general-ledger.xlsx", "COMPUTED", key_for(A), "qbo")
A1 = A

# ---- 02 the same, with last year's schedule and this year's tax depreciation typed in: both agree
case("02", "QuickBooks Online, last year's schedule and this year's depreciation typed in: both agree", "clean", "01-northgate-general-ledger.xlsx", "COMPUTED",
     key_for(A1, sched=(4_812_550 + 6_245_000, 5_903_412), tax_dep=1_386_400), "qbo",
     {"typed": {"scheduleCost": 110_575.50, "scheduleAD": 59_034.12, "taxDepreciation": 13_864.00}})

# ---- 03 planted: purchases buried in repairs, supplies and small tools; a monthly service contract that is routine
A = book(3, "Granite Facility Services")
line(A["rm"], D(4, 14), "Bill", "8812", "Coastal HVAC Contractors", "Replace rooftop HVAC unit, 5 ton", 1_148_000)
line(A["sup"], D(8, 21), "Expense", "3391", "Summit Office Systems", "Laptops (3) for field staff", 412_597)
line(A["tools"], D(9, 2), "Bill", "8840", "Greenfield Tools", "Pipe threading machine", 186_000)    # one bill, two lines: 1,860 + 975 = 2,835
line(A["tools"], D(9, 2), "Bill", "8840", "Greenfield Tools", "Threading dies set", 97_500)
for m in (2, 5, 8, 11):                                                                            # quarterly maintenance contract, routine
    line(A["rm"], D(m, 1), "Bill", f"PM-{m}", "Keystone Mechanical", "Quarterly maintenance contract", 285_000)
line(A["rm"], D(10, 9), "Bill", "8890", "Apex Plumbing", "Water heater repair", 248_000)              # under the threshold
line(A["rm"], D(11, 16), "Bill", "8921", "Ridge Roofing", "Replace shop roof section", 250_000)           # exactly the threshold: a candidate
depreciate(A, 1_402_100, monthly=False)
write_qbo(P("03-planted-purchases-in-expense.xlsx"), "Granite Facility Services", A)
case("03", "Planted: an HVAC unit, laptops and a machine expensed; a quarterly service contract that is routine", "planted", "03-planted-purchases-in-expense.xlsx", "COMPUTED", key_for(A), "qbo")

# ---- 04 planted: a truck sold, the proceeds credited to the Vehicles account, accumulated depreciation untouched
A = book(4, "Lantern Signs & Graphics")
line(A["veh"], D(7, 1), "Check", "5101", "Prairie Trailer Sales", "Utility trailer", 1_800_000)           # same amount as the sale, another name: not a reversal
line(A["veh"], D(7, 15), "Deposit", "", "Carver Auto Sales", "Sold 2019 F-150", -1_800_000)
line(A["veh"], D(7, 20), "Check", "5120", "Carver Ford", "2026 F-250", 5_412_500)
depreciate(A, 1_515_000)
write_qbo(P("04-planted-truck-sold.xlsx"), "Lantern Signs & Graphics", A)
case("04", "Planted: a truck sold with the proceeds credited to Vehicles; accumulated depreciation untouched", "planted", "04-planted-truck-sold.xlsx", "COMPUTED", key_for(A), "qbo")

# ---- 05 planted: no depreciation booked all year; this year's depreciation from the tax software typed in
A = book(5, "Copperline Plumbing Supply")
line(A["fe"], D(2, 9), "Bill", "1180", "Riverside Electric", "Shop compressor", 925_000)
write_qbo(P("05-planted-no-depreciation.xlsx"), "Copperline Plumbing Supply", A)
case("05", "Planted: no depreciation booked; the tax software's figure typed in", "planted", "05-planted-no-depreciation.xlsx", "COMPUTED",
     key_for(A, tax_dep=1_611_250), "qbo", {"typed": {"taxDepreciation": 16_112.50}})

# ---- 06 planted: the ledger's opening balances no longer agree with last year's schedule
A = book(6, "Falcon Landscape Group")
line(A["veh"], D(5, 1), "Check", "6610", "Prairie Trailer Sales", "Equipment trailer", 1_290_000)
depreciate(A, 1_244_000)
case("06", "Planted: opening cost and accumulated depreciation differ from last year's schedule", "planted", "06-planted-opening-differs.xlsx", "COMPUTED",
     key_for(A, sched=(4_812_550 + 6_245_000 + 352_000, 5_903_412 + 118_200), tax_dep=1_244_000), "qbo",
     {"typed": {"scheduleCost": 114_095.50, "scheduleAD": 60_216.12, "taxDepreciation": 12_440.00}})
write_qbo(P("06-planted-opening-differs.xlsx"), "Falcon Landscape Group", A)

# ---- 07 Xero Account Transactions, default account names
A = book(7, "Indigo Storage")
A["fe"]["name"] = "Office Equipment"; A["veh"]["name"] = "Computer Equipment"
A["ad"]["name"] = "Less Accumulated Depreciation on Office Equipment"; A["dep"]["name"] = "Depreciation"
A["sup"]["name"] = "Office Expenses"; A["tools"]["name"] = "General Expenses"
line(A["veh"], D(3, 30), "Bill", "INV-0412", "Summit Office Systems", "Server and switches", 1_064_000)
line(A["rm"], D(10, 2), "Bill", "INV-7781", "Riverside Electric", "New LED lighting, warehouse", 655_000)
line(A["rm"], D(11, 20), "Bill", "INV-7790", "Riverside Electric", "New LED lighting, office", 318_000)    # two big bills from one vendor: not routine
depreciate(A, 1_150_000)
write_xero(P("07-xero-account-transactions.xlsx"), "Indigo Storage", A)
case("07", "Xero Account Transactions: default account names; lighting expensed as a repair", "ugly", "07-xero-account-transactions.xlsx", "COMPUTED", key_for(A), "xero")

# ---- 08 QuickBooks Desktop General Ledger: account numbers, Debit and Credit, no period in the cells
A = book(8, "Kestrel Bakery")
A["fe"]["name"] = "Kitchen Equipment"
line(A["fe"], D(1, 20), "Bill", "B-201", "Harbor Supply Co", "Deck oven", 2_240_000)
line(A["fe"], D(11, 5), "Bill", "B-288", "Harbor Supply Co", "Walk-in cooler", 1_675_000)
line(A["rm"], D(6, 18), "Bill", "B-240", "Apex Plumbing", "Floor drain replacement", 386_500)
depreciate(A, 1_920_800)
write_qbd(P("08-quickbooks-desktop-gl.xlsx"), A)
case("08", "QuickBooks Desktop General Ledger: account numbers, Debit and Credit, no period", "ugly", "08-quickbooks-desktop-gl.xlsx", "COMPUTED", key_for(A, period=None), "qbd")

# ---- 09 QuickBooks Online as CSV: dollar signs and parentheses
A = book(9, "Yarrow Auto Body")
A["fe"]["name"] = "Shop Equipment"
line(A["fe"], D(4, 2), "Bill", "770", "Greenfield Tools", "Paint booth", 3_850_000)
line(A["fe"], D(9, 9), "Credit Card Credit", "", "Greenfield Tools", "Return: damaged lift arm", -82_500)
line(A["sup"], D(12, 15), "Expense", "812", "Summit Office Systems", "Diagnostic scanner", 299_900)
depreciate(A, 2_088_000)
write_qbo(P("09-quickbooks-online-csv.csv"), "Yarrow Auto Body", A, csv_out=True, paren=True)
case("09", "QuickBooks Online as CSV: dollar signs, parentheses; a returned part credited to the asset", "ugly", "09-quickbooks-online-csv.csv", "COMPUTED", key_for(A), "qbo")

# ---- 10 entered twice and reversed; an addition by journal entry
A = book(10, "Orchard Restaurants")
line(A["fe"], D(3, 3), "Bill", "3001", "Harbor Supply Co", "Dishwasher", 1_420_000)
line(A["fe"], D(3, 5), "Bill", "3001", "Harbor Supply Co", "Dishwasher (entered twice)", 1_420_000)
line(A["fe"], D(3, 19), "Bill Credit", "3001-V", "Harbor Supply Co", "Reverse duplicate", -1_420_000)
line(A["fe"], D(12, 31), "Journal Entry", "AJE-4", "", "Reclass hood system from repairs", 1_870_000)
line(A["rm"], D(12, 31), "Journal Entry", "AJE-4", "", "Reclass hood system to equipment", -1_870_000)
line(A["rm"], D(8, 14), "Bill", "3120", "Riverside Electric", "Hood system install", 1_870_000)
depreciate(A, 1_455_000)
write_qbo(P("10-reversal-and-journal-entry.xlsx"), "Orchard Restaurants", A)
case("10", "A bill entered twice and reversed; an addition by journal entry; the reclassed repair is not proposed again", "ugly", "10-reversal-and-journal-entry.xlsx", "COMPUTED", key_for(A), "qbo")

# ---- 11 the wrong report: a trial balance
wb = Workbook(); ws = wb.active
for r_ in [["Northgate Electrical Supply"], ["Trial Balance"], ["As of December 31, 2026"], [], ["", "Debit", "Credit"],
           ["Furniture and Equipment", 116_265.50, None], ["Vehicles", 62_450.00, None], ["Accumulated Depreciation", None, 72_898.12], ["TOTAL", 178_715.50, 72_898.12]]:
    ws.append(r_)
wb.save(P("11-trial-balance.xlsx"))
KEY["11"] = {"title": "The wrong report: a trial balance", "kind": "ugly", "file": "11-trial-balance.xlsx", "status": "NOT_RECOGNIZED", "exceptions": ["NOT_RECOGNIZED"], "layout": None}

# ---- 12 the wrong report: an A/R aging detail
wb = Workbook(); ws = wb.active
for r_ in [["Granite Facility Services"], ["A/R Aging Detail"], ["As of December 31, 2026"], [], ["", "Date", "Transaction Type", "Num", "Customer", "Due Date", "Amount", "Open Balance"],
           ["", "12/01/2026", "Invoice", "1001", "Alder Builders", "12/31/2026", 4200, 4200], ["TOTAL", "", "", "", "", "", "", 4200]]:
    ws.append(r_)
wb.save(P("12-ar-aging.xlsx"))
KEY["12"] = {"title": "The wrong report: an A/R aging", "kind": "ugly", "file": "12-ar-aging.xlsx", "status": "NOT_RECOGNIZED", "exceptions": ["NOT_RECOGNIZED"], "layout": None}

# ---- 13 planted: a line missing from the export, so an account does not add up
A = book(13, "Pioneer Fitness")
line(A["fe"], D(2, 14), "Bill", "4410", "Harbor Supply Co", "Treadmills (4)", 2_196_000)
line(A["fe"], D(5, 22), "Bill", "4480", "Harbor Supply Co", "Rowing machines (6)", 1_074_000)
depreciate(A, 1_610_000)
write_qbo(P("13-planted-line-missing.xlsx"), "Pioneer Fitness", A, drop=("Furniture and Equipment", 1))
k13 = key_for(A)
# the tool reads what is in the file; the key is what the file holds, and the stop
A["fe"]["lines"] = [x for i, x in enumerate(sorted(A["fe"]["lines"], key=lambda x: x["date"])) if i != 1]
k13 = key_for(A); k13["exceptions"] = sorted(k13["exceptions"] + ["FILE_DOES_NOT_ADD_UP"])
k13["rollforward"] = [r_ for r_ in k13["rollforward"]]
case("13", "Planted: a line missing from the export, so Furniture and Equipment does not add up", "planted", "13-planted-line-missing.xlsx", "COMPUTED", k13, "qbo",
     {"notAddUp": ["Furniture and Equipment"]})

# ---- 14 the client uses a $5,000 threshold (it has audited statements)
A = book(3, "Granite Facility Services")
line(A["rm"], D(4, 14), "Bill", "8812", "Coastal HVAC Contractors", "Replace rooftop HVAC unit, 5 ton", 1_148_000)
line(A["sup"], D(8, 21), "Expense", "3391", "Summit Office Systems", "Laptops (3) for field staff", 412_597)
line(A["tools"], D(9, 2), "Bill", "8840", "Greenfield Tools", "Pipe threading machine", 186_000)
line(A["tools"], D(9, 2), "Bill", "8840", "Greenfield Tools", "Threading dies set", 97_500)
depreciate(A, 1_402_100, monthly=False)
write_qbo(P("14-threshold-5000.xlsx"), "Granite Facility Services", A)
case("14", "The client has audited statements: a $5,000 threshold typed in", "ugly", "14-threshold-5000.xlsx", "COMPUTED", key_for(A, threshold=500_000), "qbo",
     {"typed": {"threshold": 5_000.00}})

# ---- 15 an asset account the page cannot recognize by name; the accountant marks it
A = book(15, "Beacon Property Management")
A["fe"]["name"] = "Shop Assets"; del A["veh"]
line(A["fe"], D(6, 6), "Bill", "9901", "Harbor Supply Co", "Floor scrubber", 714_000)
depreciate(A, 640_000)
write_qbo(P("15-unrecognized-asset-account.xlsx"), "Beacon Property Management", A)
case("15", "An asset account named 'Shop Assets': the page asks, the accountant marks it as a fixed asset", "ugly", "15-unrecognized-asset-account.xlsx", "COMPUTED",
     key_for(A, roles={"Shop Assets": "fa"}), "qbo", {"setRoles": {"Shop Assets": "fa"}, "firstExceptions": ["NO_FIXED_ASSET_ACCOUNTS"]})

# ---- 16 QuickBooks Online, a fiscal year ending June 30
A = book(16, "Meadow Dental Group")
line(A["fe"], D(4, 11), "Bill", "551", "Summit Office Systems", "Dental chair", 2_475_000)
depreciate(A, 1_320_000)
write_qbo(P("16-fiscal-year.xlsx"), "Meadow Dental Group", A, period_text="July 1, 2025 - June 30, 2026")
case("16", "QuickBooks Online, a fiscal year ending June 30 (still twelve months)", "ugly", "16-fiscal-year.xlsx", "COMPUTED",
     key_for(A, period=("2025-07-01", "2026-06-30")), "qbo")

# ---- 17 a sale booked properly: cost and accumulated depreciation removed, gain recorded
A = book(17, "Summit Landscaping")
A["gain"] = acct("Gain on Sale of Assets", 0, 80100, 260)
line(A["veh"], D(9, 10), "Journal Entry", "AJE-9", "", "Sale of 2017 dump truck: remove cost", -3_250_000)
line(A["ad"], D(9, 10), "Journal Entry", "AJE-9", "", "Sale of 2017 dump truck: remove depreciation", 2_910_000)
line(A["gain"], D(9, 10), "Journal Entry", "AJE-9", "", "Sale of 2017 dump truck: gain", -860_000)
line(A["veh"], D(9, 22), "Check", "7004", "Carver Ford", "2026 dump truck", 6_890_000)
depreciate(A, 1_710_000)
write_qbo(P("17-sale-booked-properly.xlsx"), "Summit Landscaping", A)
case("17", "A sale booked properly: cost and accumulated depreciation removed, gain recorded", "clean", "17-sale-booked-properly.xlsx", "COMPUTED", key_for(A), "qbo")

json.dump(KEY, open(os.path.join(HERE, "answer-key.json"), "w"), indent=1, default=str)
print(len(KEY), "cases written")
for c, k in KEY.items(): print(c, k["status"], k.get("exceptions"))
