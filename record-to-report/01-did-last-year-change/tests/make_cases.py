#!/usr/bin/env python3
"""Builds the acceptance test for Record-to-Report 01, "Did last year change?".

Every case is two trial balances for the same date, December 31, 2025:
  final  - last year's final trial balance, as the accountant kept it in her file
  today  - the same date, exported from the client's books today

The files are written from a ledger model (four invented companies). The answer key is worked
out from the model and from the change that was planted in it, never by reading the files back.
Amounts are held in cents, as integers, so no figure in the key depends on floating point.

Run:  python3 make_cases.py      writes cases/*.xlsx|csv and answer-key.json
"""
import csv, json, os
from openpyxl import Workbook

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cases")
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))

# ---------------------------------------------------------------- the four invented companies
# Each account: (number or None, name, kind, balance in cents, debit positive)
# kind: BS (balance sheet), RE (retained earnings), PL (income statement)

def acct(num, name, kind, cents):
    return {"num": num, "name": name, "kind": kind, "cents": cents}

def balance_re(accts):
    """Retained earnings is whatever makes the trial balance balance (it holds all earlier years)."""
    re = [a for a in accts if a["kind"] == "RE"][0]
    re["cents"] = 0
    re["cents"] = -sum(a["cents"] for a in accts)
    assert re["cents"] < 0, "retained earnings should be a credit"
    return accts

def whole(c):  # round cents to whole dollars, half away from zero, result in cents
    s = -1 if c < 0 else 1
    return s * ((abs(c) + 50) // 100) * 100

# Harbor Light Bakery LLC: QuickBooks Online, 4-digit account numbers, accrual basis
def harbor():
    a = [
        acct("1000", "Checking", "BS", 4821537), acct("1010", "Savings", "BS", 2500000),
        acct("1200", "Accounts Receivable", "BS", 641280), acct("1300", "Inventory", "BS", 987015),
        acct("1400", "Prepaid Insurance", "BS", 185000), acct("1500", "Equipment", "BS", 8640000),
        acct("1590", "Accumulated Depreciation", "BS", -3156000),
        acct("2000", "Accounts Payable", "BS", -732241), acct("2100", "Credit Card", "BS", -311862),
        acct("2200", "Payroll Liabilities", "BS", -428690), acct("2300", "Sales Tax Payable", "BS", -210733),
        acct("2500", "Equipment Loan", "BS", -3890000), acct("3000", "Common Stock", "BS", -100000),
        acct("3100", "Shareholder Distributions", "BS", 6000000), acct("3900", "Retained Earnings", "RE", 0),
        acct("4000", "Bakery Sales", "PL", -51264025), acct("4100", "Wholesale Sales", "PL", -8821500),
        acct("5000", "Cost of Goods Sold", "PL", 19633042), acct("6000", "Advertising", "PL", 741500),
        acct("6100", "Bank Fees", "PL", 122618), acct("6200", "Depreciation Expense", "PL", 1578000),
        acct("6300", "Insurance", "PL", 912000), acct("6400", "Office Supplies", "PL", 231866),
        acct("6450", "Meals", "PL", 124430), acct("6500", "Rent", "PL", 5400000),
        acct("6550", "Repairs and Maintenance", "PL", 681355), acct("6600", "Wages", "PL", 18240000),
        acct("6610", "Officer Wages", "PL", 6000000), acct("6700", "Payroll Taxes", "PL", 1872204),
        acct("6810", "Utilities:Electric", "PL", 948821), acct("6820", "Utilities:Water", "PL", 211477),
        acct("7000", "Interest Income", "PL", -31244), acct("8000", "Interest Expense", "PL", 256000),
    ]
    balance_re(a)
    # Make the whole-dollar version balance too, as a real workpaper would: nudge Bank Fees' cents.
    fees = [x for x in a if x["name"] == "Bank Fees"][0]
    for cents in range(122600, 122700):
        fees["cents"] = cents
        balance_re(a)
        if sum(whole(x["cents"]) for x in a) == 0:
            break
    assert sum(whole(x["cents"]) for x in a) == 0
    return a

# Ridgeview Dental Lab, Inc.: QuickBooks Desktop, 5-digit numbers shown as "10100 · Checking"
def ridgeview():
    a = [
        acct("10100", "Checking", "BS", 3377410), acct("10300", "Petty Cash", "BS", 25000),
        acct("11000", "Accounts Receivable", "BS", 4128855), acct("12000", "Undeposited Funds", "BS", 186000),
        acct("12100", "Inventory Asset", "BS", 1554320), acct("15000", "Furniture and Equipment", "BS", 12278000),
        acct("17000", "Accumulated Depreciation", "BS", -6871200), acct("20000", "Accounts Payable", "BS", -1196577),
        acct("24000", "Payroll Liabilities", "BS", -880214), acct("26000", "Line of Credit", "BS", -2500000),
        acct("30100", "Capital Stock", "BS", -500000), acct("32000", "Retained Earnings", "RE", 0),
        acct("40100", "Lab Fees:Crowns and Bridges", "PL", -61244380), acct("40200", "Lab Fees:Dentures", "PL", -21877050),
        acct("50100", "Cost of Goods Sold:Materials", "PL", 17766215), acct("60000", "Advertising and Promotion", "PL", 384000),
        acct("60400", "Bank Service Charges", "PL", 92655), acct("62400", "Depreciation Expense", "PL", 2140000),
        acct("63300", "Insurance Expense", "PL", 1462580), acct("64300", "Meals and Entertainment", "PL", 211940),
        acct("64900", "Office Supplies", "PL", 588123), acct("66500", "Payroll Expenses:Wages", "PL", 39118000),
        acct("66700", "Payroll Expenses:Payroll Taxes", "PL", 3080791), acct("67100", "Rent Expense", "PL", 7200000),
        acct("67200", "Repairs and Maintenance", "PL", 948366), acct("68600", "Utilities", "PL", 1066402),
        acct("70100", "Interest Income", "PL", -18733), acct("80100", "Interest Expense", "PL", 187400),
    ]
    return balance_re(a)

# Pine & Proof Landscaping LLC: Xero, codes shown as "Sales (200)", sections, YTD columns
def pineproof():
    a = [
        acct("200", "Sales", "PL", -38411650), acct("260", "Other Revenue", "PL", -412000),
        acct("310", "Cost of Goods Sold", "PL", 9926315), acct("400", "Advertising", "PL", 518800),
        acct("404", "Bank Fees", "PL", 61210), acct("412", "Consulting & Accounting", "PL", 650000),
        acct("420", "Entertainment", "PL", 98045), acct("429", "General Expenses", "PL", 233719),
        acct("433", "Insurance", "PL", 1184400), acct("449", "Motor Vehicle Expenses", "PL", 2216644),
        acct("469", "Rent", "PL", 2400000), acct("473", "Repairs and Maintenance", "PL", 1385122),
        acct("477", "Wages and Salaries", "PL", 14411500), acct("478", "Payroll Tax Expense", "PL", 1183225),
        acct("489", "Telephone & Internet", "PL", 214080),
        acct("090", "Business Bank Account", "BS", 2911463), acct("610", "Accounts Receivable", "BS", 1877500),
        acct("710", "Office Equipment", "BS", 640000), acct("711", "Less Accumulated Depreciation on Office Equipment", "BS", -280000),
        acct("720", "Vehicles and Mowers", "BS", 9850000), acct("721", "Less Accumulated Depreciation on Vehicles and Mowers", "BS", -4105000),
        acct("800", "Accounts Payable", "BS", -614390), acct("820", "Sales Tax", "BS", -96214),
        acct("825", "Payroll Liabilities", "BS", -390477), acct("900", "Loan", "BS", -2200000),
        acct("960", "Retained Earnings", "RE", 0), acct("970", "Owner A Funds Introduced", "BS", -1000000),
        acct("980", "Owner A Drawings", "BS", 4500000),
    ]
    return balance_re(a)
XERO_SECTION = {"200": "Revenue", "260": "Revenue", "310": "Direct Costs"}

def xero_section(a):
    if a["num"] in XERO_SECTION: return XERO_SECTION[a["num"]]
    n = int(a["num"])
    if 400 <= n < 500: return "Expenses"
    if n < 800: return "Assets"
    if n < 960: return "Liabilities"
    return "Equity"

# Copper Kettle Catering: QuickBooks Online, no account numbers, accrual basis
def copper():
    a = [
        acct(None, "Checking", "BS", 1877240), acct(None, "Savings", "BS", 1200000),
        acct(None, "Accounts Receivable (A/R)", "BS", 942615), acct(None, "Undeposited Funds", "BS", 64000),
        acct(None, "Prepaid Expenses", "BS", 120000), acct(None, "Kitchen Equipment", "BS", 4366000),
        acct(None, "Vehicles", "BS", 5150000), acct(None, "Accumulated Depreciation", "BS", -3842200),
        acct(None, "Accounts Payable (A/P)", "BS", -508833), acct(None, "Visa Card", "BS", -277419),
        acct(None, "Payroll Liabilities:Federal Taxes", "BS", -186240), acct(None, "Sales Tax Payable", "BS", -133375),
        acct(None, "Vehicle Loan", "BS", -2244100), acct(None, "Owner's Draw", "BS", 5200000),
        acct(None, "Owner's Investment", "BS", -1000000), acct(None, "Retained Earnings", "RE", 0),
        acct(None, "Catering Sales", "PL", -42290550), acct(None, "Event Rentals", "PL", -3311000),
        acct(None, "Cost of Goods Sold:Food and Beverage", "PL", 14402233), acct(None, "Advertising & Marketing", "PL", 288000),
        acct(None, "Bank Charges & Fees", "PL", 41620), acct(None, "Car & Truck", "PL", 905517),
        acct(None, "Depreciation", "PL", 1210000), acct(None, "Insurance", "PL", 744000),
        acct(None, "Meals", "PL", 93520), acct(None, "Office Expenses", "PL", 167744),
        acct(None, "Office Supplies", "PL", 116305), acct(None, "Rent & Lease", "PL", 3600000),
        acct(None, "Repairs & Maintenance", "PL", 412650), acct(None, "Wages", "PL", 15377000),
        acct(None, "Payroll Taxes", "PL", 1268110), acct(None, "Utilities", "PL", 522090),
        acct(None, "Interest Earned", "PL", -8814), acct(None, "Interest Paid", "PL", 160000),
    ]
    return balance_re(a)

def clone(accts):
    return [dict(a) for a in accts]

def find(accts, name):
    return [a for a in accts if a["name"] == name][0]

def change(accts, name, delta):
    find(accts, name)["cents"] += delta

# ---------------------------------------------------------------- writers (one per layout)

def money(c):  # 123456 -> "1,234.56"
    s = "-" if c < 0 else ""
    c = abs(c)
    return f"{s}{c // 100:,}.{c % 100:02d}"

def qbo_label(a, numbered):
    return f"{a['num']} {a['name']}" if numbered and a["num"] else a["name"]

def write_qbo(path, company, asof, accts, basis="Accrual", stamp="Thursday, March 12, 2026 09:41 AM GMT-05:00", numbered=True, csv_out=False):
    """QuickBooks Online: Reports > Trial Balance > Export. Zero balances are left out, as QBO does."""
    rows = [[company, None, None], ["Trial Balance", None, None], [asof, None, None], [None, None, None], [None, "Debit", "Credit"]]
    td = tc = 0
    for a in accts:
        c = a["cents"]
        if c == 0: continue
        if c > 0: rows.append([qbo_label(a, numbered), c / 100, None]); td += c
        else: rows.append([qbo_label(a, numbered), None, -c / 100]); tc += -c
    rows.append(["TOTAL", td / 100, tc / 100])
    rows += [[None, None, None], [None, None, None], [f"{basis} Basis {stamp}", None, None]]
    if csv_out:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL)
            for r in rows:
                out = []
                for i, v in enumerate(r):
                    if isinstance(v, float):
                        c = round(v * 100)
                        out.append(("$" if r[0] == "TOTAL" else "") + money(c))
                    else:
                        out.append("" if v is None else v)
                w.writerow(out)
        return
    wb = Workbook(); ws = wb.active; ws.title = "Trial Balance"
    for r in rows: ws.append(r)
    for row in ws.iter_rows(min_row=6):
        for cell in row[1:]:
            if isinstance(cell.value, float): cell.number_format = '"$"#,##0.00' if row[0].value == "TOTAL" else '#,##0.00'
    wb.save(path)

def write_qbd(path, accts, colhead="Dec 31, 25", extra_debit=None):
    """QuickBooks Desktop: Reports > Accountant & Taxes > Trial Balance > Excel. The report title,
    date and basis go to Excel's page header, not into the cells, so only the column date shows."""
    wb = Workbook(); ws = wb.active; ws.title = "Sheet1"
    ws.append([None, None, colhead, None]); ws.append([None, None, "Debit", "Credit"])
    td = tc = 0
    for a in accts:
        c = a["cents"]
        if extra_debit and a["name"] == extra_debit[0]: c += extra_debit[1]
        if c == 0: continue
        parts = a["name"].split(":")
        if len(parts) == 2:  # parent:child, Desktop prints the parent's number too
            pnum = a["num"][:2] + "000"
            label = f"{pnum} · {parts[0]}:{a['num']} · {parts[1]}"
        else:
            label = f"{a['num']} · {a['name']}"
        if c > 0: ws.append([None, label, c / 100, None]); td += c
        else: ws.append([None, label, None, -c / 100]); tc += -c
    ws.append(["TOTAL", None, td / 100, tc / 100])
    for row in ws.iter_rows(min_row=3):
        for cell in row[2:]:
            if isinstance(cell.value, float): cell.number_format = '#,##0.00'
    wb.save(path)

def write_xero(path, company, accts, asof="As at 31 December 2025", rename=None):
    """Xero: Accounting > Reports > Trial Balance > Export to Excel. Debit and Credit are the month's
    movement; YTD Debit and YTD Credit are the balances. Sections with their own totals."""
    wb = Workbook(); ws = wb.active; ws.title = "Trial Balance"
    for r in [["Trial Balance"], [company], [asof], [], ["Account", "Debit", "Credit", "YTD Debit", "YTD Credit"]]:
        ws.append(r)
    # month movement: a twelfth of each income-statement balance, and the bank account takes the rest
    month = {}
    for a in accts:
        if a["kind"] == "PL": month[a["num"]] = int(a["cents"] / 12)
    bank_m = -sum(month.values())
    month["090"] = bank_m
    gd = gc = md = mc = 0
    for sec in ["Revenue", "Direct Costs", "Expenses", "Assets", "Liabilities", "Equity"]:
        members = [a for a in accts if xero_section(a) == sec and a["cents"] != 0]
        if not members: continue
        ws.append([sec])
        sd = sc = smd = smc = 0
        for a in members:
            c = a["cents"]; m = month.get(a["num"], 0)
            name = rename.get(a["num"], a["name"]) if rename else a["name"]
            ws.append([f"{name} ({a['num']})", m / 100 if m > 0 else None, -m / 100 if m < 0 else None,
                       c / 100 if c > 0 else None, -c / 100 if c < 0 else None])
            if c > 0: sd += c
            else: sc += -c
            if m > 0: smd += m
            else: smc += -m
        ws.append([f"Total {sec}", smd / 100, smc / 100, sd / 100, sc / 100])
        gd += sd; gc += sc; md += smd; mc += smc
    ws.append(["Total", md / 100, mc / 100, gd / 100, gc / 100])
    for row in ws.iter_rows(min_row=6):
        for cell in row[1:]:
            if isinstance(cell.value, (int, float)): cell.number_format = '#,##0.00'
    wb.save(path)

def write_workpaper(path, company, accts, unadj, aje, title="Trial balance, final, December 31, 2025"):
    """The accountant's own trial balance workpaper: books, her adjustments, final. Whole dollars,
    negatives in parentheses, a net income line under the total."""
    wb = Workbook(); ws = wb.active; ws.title = "TB"
    for r in [[company], [title], ["Workpaper TB-1"], [], ["Acct", "Account", "Per books 12/31/25", "Adjustments", "Final 12/31/25", "Return line"]]:
        ws.append(r)
    tb = ta = tf = 0
    for a in accts:
        u = whole(unadj[a["name"]]); j = aje.get(a["name"], 0); f = u + j
        if u == 0 and j == 0: continue
        line = "Sch L" if a["kind"] != "PL" else "p.1"
        ws.append([int(a["num"]), a["name"], u // 100, j // 100 if j else None, f // 100, line])
        tb += u; ta += j; tf += f
    ws.append([None, "Total", tb // 100, ta // 100, tf // 100, None])
    ws.append([])
    ni = -sum(whole(unadj[a["name"]]) + aje.get(a["name"], 0) for a in accts if a["kind"] == "PL")
    ws.append([None, "Net income per return", None, None, ni // 100, None])
    fmt = '#,##0;(#,##0);"-"'
    for row in ws.iter_rows(min_row=6):
        for cell in row[2:5]:
            cell.number_format = fmt
    wb.save(path)

def write_postclosing(path, company, accts):
    """A post-closing trial balance from the accountant's file: income and expenses already closed
    into retained earnings, so only balance sheet accounts remain."""
    wb = Workbook(); ws = wb.active; ws.title = "Post-closing"
    for r in [[company], ["Post-closing trial balance"], ["December 31, 2025"], [], ["Account", "Debit", "Credit"]]:
        ws.append(r)
    ni = sum(a["cents"] for a in accts if a["kind"] == "PL")
    td = tc = 0
    for a in accts:
        if a["kind"] == "PL": continue
        c = a["cents"] + (ni if a["kind"] == "RE" else 0)
        if c > 0: ws.append([a["name"], c / 100, None]); td += c
        else: ws.append([a["name"], None, -c / 100]); tc += -c
    ws.append(["Total", td / 100, tc / 100])
    for row in ws.iter_rows(min_row=6):
        for cell in row[1:]:
            if isinstance(cell.value, float): cell.number_format = '#,##0.00'
    wb.save(path)

def write_generic_csv(path, accts, bad_total=None):
    """A trial balance saved as CSV from an older tool: no title, no date, dollar signs, commas,
    a negative shown in parentheses, blank lines, and a total typed in by hand."""
    lines = [["Account", "Debit", "Credit"]]
    td = tc = 0
    for i, a in enumerate(accts):
        c = a["cents"]
        if c == 0: continue
        if a["name"] == "Accumulated Depreciation":  # shown as a negative debit
            lines.append([a["name"], f"(${money(-c)})", ""]); td += c
        elif c > 0: lines.append([a["name"], f"${money(c)}", ""]); td += c
        else: lines.append([a["name"], "", f"${money(-c)}"]); tc += -c
        if i in (6, 15): lines.append(["", "", ""])
    tot_d = bad_total if bad_total is not None else td
    lines.append(["Total", f"${money(tot_d)}", f"${money(tc)}"])
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(lines)

def write_balance_sheet(path, company, accts):
    """The wrong report: a QuickBooks Online Balance Sheet, not a trial balance."""
    wb = Workbook(); ws = wb.active; ws.title = "Balance Sheet"
    for r in [[company], ["Balance Sheet"], ["As of December 31, 2025"], [], [None, "Total"], ["ASSETS"], ["   Current Assets"]]:
        ws.append(r)
    ta = 0
    for a in accts:
        if a["kind"] == "BS" and a["cents"] > 0 and a["name"] not in ("Shareholder Distributions",):
            ws.append([f"      {a['name']}", a["cents"] / 100]); ta += a["cents"]
    ws.append(["TOTAL ASSETS", ta / 100])
    ws.append(["LIABILITIES AND EQUITY"])
    for a in accts:
        if a["kind"] in ("BS", "RE") and (a["cents"] < 0 or a["name"] == "Shareholder Distributions"):
            ws.append([f"      {a['name']}", -a["cents"] / 100])
    ni = -sum(a["cents"] for a in accts if a["kind"] == "PL")
    ws.append(["      Net Income", ni / 100])
    ws.append(["TOTAL LIABILITIES AND EQUITY", ta / 100])
    ws.append([]); ws.append(["Accrual Basis Friday, November 13, 2026 10:05 AM GMT-05:00"])
    wb.save(path)

# ---------------------------------------------------------------- the answer key, from the model

def key_for(final, today, *, rounding_ok=False, aje=None, post_closing=False, renames=None, merges=None, out_of_balance=False):
    """Works out what the tool should report, from the model.
    final, today: lists of accounts (the same accounts; renames/merges given separately).
    Returns differences, net income change, retained earnings change and the entry."""
    aje = aje or {}
    by_f = {a["name"]: a for a in final}
    by_t = {a["name"]: a for a in today}
    names = list(dict.fromkeys([a["name"] for a in final] + [a["name"] for a in today]))
    if post_closing:  # compare on a closed basis: close today's income statement into retained earnings
        ni_t = sum(a["cents"] for a in today if a["kind"] == "PL")
        ni_f = sum(a["cents"] for a in final if a["kind"] == "PL")
    diffs, rounding = [], 0
    for n in names:
        f = by_f.get(n); t = by_t.get(n)
        kind = (f or t)["kind"]
        if post_closing and kind == "PL": continue
        fc = f["cents"] if f else 0
        tc = t["cents"] if t else 0
        if post_closing and kind == "RE": fc += ni_f; tc += ni_t
        if rounding_ok and n in by_f: fc = whole(fc)
        if n in aje: fc = whole(by_f[n]["cents"]) + aje[n] if rounding_ok else fc
        d = tc - fc
        if d == 0: continue
        if n in aje and abs(d + aje[n]) < 100:
            diffs.append({"account": n, "kind": kind, "final": fc / 100, "today": tc / 100, "diff": d / 100, "aje": True, "ajeAmount": aje[n] / 100})
            continue
        if rounding_ok and abs(d) < 100:
            rounding += d; continue
        diffs.append({"account": n, "kind": kind, "final": fc / 100, "today": tc / 100, "diff": d / 100})
    # merges and guessed renames: the pair is explained, not a change
    explained = set()
    for (gone, into) in (merges or []):
        explained.add(gone); explained.add(into)
    for (old, new) in (renames or []):
        explained.add(old); explained.add(new)
    real = [d for d in diffs if d["account"] not in explained]
    pl_f = sum((whole(a["cents"]) if rounding_ok else a["cents"]) + aje.get(a["name"], 0) for a in final if a["kind"] == "PL")
    pl_t = sum(a["cents"] for a in today if a["kind"] == "PL")
    ni_change = None if post_closing else (-(pl_t) - -(pl_f)) / 100
    re_f = sum((whole(a["cents"]) if rounding_ok else a["cents"]) + aje.get(a["name"], 0) for a in final if a["kind"] == "RE")
    re_t = sum(a["cents"] for a in today if a["kind"] == "RE")
    re_change = None if post_closing else (-(re_t) - -(re_f)) / 100   # positive: retained earnings higher today
    # the entry, dated the first day of the new year: put every balance sheet account back to final
    lines = []
    if not out_of_balance:
        for d in real:
            if d["kind"] != "BS": continue
            # final minus today; for an adjustment never posted, the adjustment itself (no rounding cents)
            amt = round(d["ajeAmount"] * 100) if d.get("aje") else round(-d["diff"] * 100)
            lines.append({"account": d["account"], "debit": amt / 100 if amt > 0 else 0, "credit": -amt / 100 if amt < 0 else 0})
        if lines:
            off = -sum(round(l["debit"] * 100) - round(l["credit"] * 100) for l in lines)
            re_name = [a["name"] for a in final if a["kind"] == "RE"][0]
            lines.append({"account": re_name, "debit": off / 100 if off > 0 else 0, "credit": -off / 100 if off < 0 else 0})
    return {"differences": real, "netIncomeChange": ni_change, "retainedEarningsChange": re_change,
            "rounding": rounding / 100, "entry": lines or None}

KEY = {}

def n(accts, closed=False):
    """How many account lines the file shows: accounts with a balance (exports leave out zero balances)."""
    return sum(1 for a in accts if a["cents"] != 0 and not (closed and a["kind"] == "PL"))

def case(cid, title, kind, final_file, today_file, status, exceptions, extra=None, **k):
    entry = {"title": title, "kind": kind, "files": {"final": final_file, "today": today_file},
             "status": status, "exceptions": sorted(exceptions), "noOtherExceptions": True}
    if extra: entry.update(extra)
    KEY[cid] = entry

def P(name): return os.path.join(OUT, name)

STAMP_LAST = "Thursday, March 12, 2026 09:41 AM GMT-05:00"
STAMP_NOW = "Friday, November 13, 2026 10:05 AM GMT-05:00"
AS_OF = "As of December 31, 2025"

# ---- 01 nothing changed (QuickBooks Online, numbered)
H = harbor()
write_qbo(P("01-final.xlsx"), "Harbor Light Bakery LLC", AS_OF, H, stamp=STAMP_LAST)
write_qbo(P("01-today.xlsx"), "Harbor Light Bakery LLC", AS_OF, H, stamp=STAMP_NOW)
k = key_for(H, H)
case("01", "Nothing changed (QuickBooks Online)", "clean", "01-final.xlsx", "01-today.xlsx", "AGREES", [],
     {**k, "asOf": "2025-12-31", "rows": {"final": n(H), "today": n(H)}})

# ---- 02 planted: a 2025 deposit deleted after the return was filed
T = clone(H); change(T, "Bakery Sales", 425000); change(T, "Checking", -425000)
write_qbo(P("02-final.xlsx"), "Harbor Light Bakery LLC", AS_OF, H, stamp=STAMP_LAST)
write_qbo(P("02-today.xlsx"), "Harbor Light Bakery LLC", AS_OF, T, stamp=STAMP_NOW)
k = key_for(H, T)
case("02", "Planted: a December deposit deleted after filing", "planted", "02-final.xlsx", "02-today.xlsx", "CHANGED",
     ["CHANGED_PL", "CHANGED_BS"], {**k, "asOf": "2025-12-31", "rows": {"final": n(H), "today": n(T)}})

# ---- 03 planted: a backdated bill, and a reclassification between two expenses (no account numbers)
C = copper()
T = clone(C); change(T, "Accounts Payable (A/P)", -186000); change(T, "Repairs & Maintenance", 186000)
change(T, "Office Supplies", -64000); change(T, "Meals", 64000)
write_qbo(P("03-final.xlsx"), "Copper Kettle Catering", AS_OF, C, numbered=False, stamp=STAMP_LAST)
write_qbo(P("03-today.xlsx"), "Copper Kettle Catering", AS_OF, T, numbered=False, stamp=STAMP_NOW)
k = key_for(C, T)
case("03", "Planted: a backdated bill, and office supplies moved to meals", "planted", "03-final.xlsx", "03-today.xlsx", "CHANGED",
     ["CHANGED_PL", "CHANGED_BS"], {**k, "asOf": "2025-12-31", "rows": {"final": n(C), "today": n(T)}})

# ---- 04 planted: an earlier year changed (QuickBooks Desktop layout)
R = ridgeview()
T = clone(R); change(T, "Furniture and Equipment", -240000); change(T, "Retained Earnings", 240000)
write_qbd(P("04-final.xlsx"), R); write_qbd(P("04-today.xlsx"), T)
k = key_for(R, T)
case("04", "Planted: a 2024 equipment purchase re-entered as an expense (Desktop)", "planted", "04-final.xlsx", "04-today.xlsx", "CHANGED",
     ["PRIOR_YEARS_CHANGED", "CHANGED_BS"], {**k, "asOf": "2025-12-31", "rows": {"final": n(R), "today": n(T)}})

# ---- 05 her adjusting entries never posted; her workpaper is in whole dollars
H5 = harbor()
unadj = {a["name"]: a["cents"] for a in H5}
aje = {"Depreciation Expense": 800000, "Accumulated Depreciation": -800000,
       "Wages": 315000, "Accrued Wages": -315000,
       "Officer Wages": 480000, "Insurance": -480000}
H5w = clone(H5)
H5w.insert(12, acct("2150", "Accrued Wages", "BS", 0))
unadj["Accrued Wages"] = 0
write_workpaper(P("05-final-workpaper.xlsx"), "Harbor Light Bakery LLC", H5w, unadj, aje)
T = clone(H5)   # the client posted the officer health insurance entry only
change(T, "Officer Wages", 480000); change(T, "Insurance", -480000)
write_qbo(P("05-today.xlsx"), "Harbor Light Bakery LLC", AS_OF, T, stamp=STAMP_NOW)
finalmodel = clone(H5w)
k = key_for(finalmodel, T + [], rounding_ok=True, aje=aje)
# Accrued Wages is not in today's export (zero balance): it is an adjustment not posted
case("05", "Her adjusting entries never posted; workpaper in whole dollars", "ugly", "05-final-workpaper.xlsx", "05-today.xlsx", "CHANGED",
     ["AJE_NOT_POSTED", "ROUNDING"], {**k, "asOf": "2025-12-31", "rows": {"final": n(H5w) + 1, "today": n(T)}})

# ---- 06 Xero, an account renamed, nothing else changed
X = pineproof()
write_xero(P("06-final.xlsx"), "Pine & Proof Landscaping LLC", X)
write_xero(P("06-today.xlsx"), "Pine & Proof Landscaping LLC", X, rename={"429": "Office & General"})
k = key_for(X, X)
case("06", "Xero: one account renamed, nothing else changed", "ugly", "06-final.xlsx", "06-today.xlsx", "AGREES",
     ["RENAMED"], {**k, "asOf": "2025-12-31", "rows": {"final": n(X), "today": n(X)}})

# ---- 07 two accounts merged (no numbers)
C7 = copper(); T = clone(C7)
supplies = find(T, "Office Supplies")["cents"]; change(T, "Office Expenses", supplies); T = [a for a in T if a["name"] != "Office Supplies"]
write_qbo(P("07-final.xlsx"), "Copper Kettle Catering", AS_OF, C7, numbered=False, stamp=STAMP_LAST)
write_qbo(P("07-today.xlsx"), "Copper Kettle Catering", AS_OF, T, numbered=False, stamp=STAMP_NOW)
k = key_for(C7, T, merges=[("Office Supplies", "Office Expenses")])
case("07", "Office Supplies merged into Office Expenses", "ugly", "07-final.xlsx", "07-today.xlsx", "AGREES",
     ["MERGED_GUESS"], {**k, "asOf": "2025-12-31", "rows": {"final": n(C7), "today": n(T)}})

# ---- 08 the wrong date: today's report run for December 31, 2026
H8 = harbor(); T = clone(H8); change(T, "Checking", 1033300); change(T, "Bakery Sales", -1033300)
write_qbo(P("08-final.xlsx"), "Harbor Light Bakery LLC", AS_OF, H8, stamp=STAMP_LAST)
write_qbo(P("08-today.xlsx"), "Harbor Light Bakery LLC", "As of December 31, 2026", T, stamp=STAMP_NOW)
case("08", "Today's report run for the wrong year", "ugly", "08-final.xlsx", "08-today.xlsx", "NOT_COMPARABLE", ["DATE_MISMATCH"])

# ---- 09 cash basis against accrual basis
C9 = copper(); T = clone(C9)
change(T, "Accounts Receivable (A/R)", -942615); change(T, "Catering Sales", 942615)
change(T, "Accounts Payable (A/P)", 508833); change(T, "Cost of Goods Sold:Food and Beverage", -508833)
write_qbo(P("09-final.xlsx"), "Copper Kettle Catering", AS_OF, C9, numbered=False, stamp=STAMP_LAST)
write_qbo(P("09-today.xlsx"), "Copper Kettle Catering", AS_OF, T, numbered=False, basis="Cash", stamp=STAMP_NOW)
case("09", "Today's report on cash basis, last year's on accrual", "ugly", "09-final.xlsx", "09-today.xlsx", "NOT_COMPARABLE", ["BASIS_MISMATCH"])

# ---- 10 planted: a 2025 check voided after filing; last year's file is a hand-kept CSV with a mistyped total
C10 = copper(); T = clone(C10); change(T, "Checking", 97500); change(T, "Advertising & Marketing", -97500)
td = sum(a["cents"] for a in C10 if a["cents"] > 0 or a["name"] == "Accumulated Depreciation")
write_generic_csv(P("10-final.csv"), C10, bad_total=td + 9000)
write_qbo(P("10-today.xlsx"), "Copper Kettle Catering", AS_OF, T, numbered=False, stamp=STAMP_NOW)
k = key_for(C10, T)
case("10", "Planted: a 2025 check voided; last year's CSV has a mistyped total and no date", "planted", "10-final.csv", "10-today.xlsx", "CHANGED",
     ["CHANGED_PL", "CHANGED_BS", "TOTAL_MISMATCH", "DATE_UNKNOWN"], {**k, "rows": {"final": n(C10), "today": n(T)}})

# ---- 11 last year's file is a post-closing trial balance
X11 = pineproof()
write_postclosing(P("11-final-postclosing.xlsx"), "Pine & Proof Landscaping LLC", X11)
write_xero(P("11-today.xlsx"), "Pine & Proof Landscaping LLC", X11)
k = key_for(X11, X11, post_closing=True)
case("11", "Last year's file is a post-closing trial balance", "ugly", "11-final-postclosing.xlsx", "11-today.xlsx", "AGREES",
     ["POST_CLOSING"], {**k, "asOf": "2025-12-31", "rows": {"final": n(X11, closed=True), "today": n(X11)}})

# ---- 12 account numbers turned off since last year, and one account renamed
H12 = harbor(); T = clone(H12); find(T, "Insurance")["name"] = "Insurance - General Liability"
write_qbo(P("12-final.xlsx"), "Harbor Light Bakery LLC", AS_OF, H12, stamp=STAMP_LAST)
write_qbo(P("12-today.xlsx"), "Harbor Light Bakery LLC", AS_OF, T, numbered=False, stamp=STAMP_NOW)
k = key_for(H12, H12)
case("12", "Account numbers turned off since last year; one account renamed", "ugly", "12-final.xlsx", "12-today.xlsx", "AGREES",
     ["RENAMED_GUESS"], {**k, "asOf": "2025-12-31", "rows": {"final": n(H12), "today": n(T)}})

# ---- 13 planted: today's file does not balance (damaged Desktop file)
R13 = ridgeview(); T = clone(R13); change(T, "Undeposited Funds", 12500)
write_qbd(P("13-final.xlsx"), R13); write_qbd(P("13-today.xlsx"), T)
k = key_for(R13, T, out_of_balance=True)
case("13", "Planted: the client's books do not balance (Desktop)", "planted", "13-final.xlsx", "13-today.xlsx", "CHANGED",
     ["OUT_OF_BALANCE", "CHANGED_BS"], {**k, "asOf": "2025-12-31", "rows": {"final": n(R13), "today": n(T)}})

# ---- 14 the wrong report: a balance sheet instead of a trial balance
H14 = harbor()
write_qbo(P("14-final.xlsx"), "Harbor Light Bakery LLC", AS_OF, H14, stamp=STAMP_LAST)
write_balance_sheet(P("14-today-balance-sheet.xlsx"), "Harbor Light Bakery LLC", H14)
case("14", "The wrong report: a balance sheet in place of a trial balance", "ugly", "14-final.xlsx", "14-today-balance-sheet.xlsx", "NOT_COMPARABLE", ["NOT_A_TB"])

# ---- 15 the same file in both places
X15 = pineproof()
write_xero(P("15-same.xlsx"), "Pine & Proof Landscaping LLC", X15)
case("15", "The same file given twice", "ugly", "15-same.xlsx", "15-same.xlsx", "NOT_COMPARABLE", ["SAME_FILE"])

# ---- 16 files in the wrong boxes: her workpaper given as today's file
H16 = harbor()
unadj = {a["name"]: a["cents"] for a in H16}
aje16 = {"Officer Wages": 480000, "Insurance": -480000}
write_workpaper(P("16-workpaper.xlsx"), "Harbor Light Bakery LLC", H16, unadj, aje16)
T = clone(H16); change(T, "Officer Wages", 480000); change(T, "Insurance", -480000)
write_qbo(P("16-books.xlsx"), "Harbor Light Bakery LLC", AS_OF, T, stamp=STAMP_NOW)
k = key_for(H16, T, rounding_ok=True, aje=aje16)
case("16", "Files put in the wrong boxes (workpaper given as today's)", "ugly", "16-books.xlsx", "16-workpaper.xlsx", "AGREES",
     ["SWAPPED", "ROUNDING"], {**k, "asOf": "2025-12-31", "rows": {"final": n(H16), "today": n(T)}})

with open(os.path.join(HERE, "answer-key.json"), "w") as f:
    json.dump(KEY, f, indent=1)
print(f"{len(KEY)} cases written to {OUT}")
for cid, e in KEY.items():
    print(cid, e["status"], e["exceptions"], "NI", e.get("netIncomeChange"), "RE", e.get("retainedEarningsChange"),
          "entry", None if not e.get("entry") else [(l["account"], l["debit"], l["credit"]) for l in e["entry"]])
