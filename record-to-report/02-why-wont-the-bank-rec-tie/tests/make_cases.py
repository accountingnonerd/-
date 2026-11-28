#!/usr/bin/env python3
"""Builds the acceptance test for Record-to-Report 02, "Why won't the bank rec tie?".

Each case is a pair of files for one bank account: the bank's own transaction download (CSV or Excel,
in the shapes banks commonly use) and the books' ledger detail for the account (QuickBooks Online,
QuickBooks Desktop or Xero). They are written from a model of real events: each event is recorded in
the books, clears the bank, or both, with its own dates. The answer key is worked out from the files'
lines with the rules in rules.py, never by reading the files back; the model is also used to check
that the rules find what was planted. Money is integer cents, positive = money into the account.

Run:  python3 make_cases.py      writes cases/* and answer-key.json
"""
import csv, json, os, random
from datetime import date, datetime, timedelta
from openpyxl import Workbook
from rules import reconcile, check_no, CHECK_RE

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cases"); os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
P = lambda n: os.path.join(OUT, n)
D = date
def ds(d): return d.strftime("%m/%d/%Y")
def money(c, dollar=False, paren=False):
    s = f"{abs(c) // 100:,}.{abs(c) % 100:02d}"
    if dollar: s = "$" + s
    return (f"({s})" if paren else "-" + s) if c < 0 else s

# ------------------------------------------------------------------ the model of events
VENDORS = ["Harbor Supply Co", "Metro Utilities", "Brightside Media", "Northline Rentals", "Apex Plumbing", "Summit Office Systems", "Greenfield Tools",
           "Riverside Electric", "Coastal Insurance", "Valley Fuel"]
CUSTOMERS = ["Alder Builders", "Birch Dental Group", "Cedar Apartments", "Delta Fitness", "Ember Hotel", "Falcon Contracting", "Granite Schools",
             "Harbor Restaurants", "Indigo Storage", "Juniper Bakery"]

class World:
    def __init__(self, seed, opening=4_825_000, book_from=D(2025, 10, 1), start=D(2026, 1, 1), end=D(2026, 3, 31), check0=1001):
        self.r = random.Random(seed); self.opening = opening; self.book_from = book_from; self.start = start; self.end = end
        self.events = []; self.check = check0
    def ev(self, d, amount, typ, name="", memo="", num="", lag=2, bank_desc=None, book=True, bank=True, bank_amount=None, bank_check=None):
        e = dict(date=d, amount=amount, type=typ, name=name, memo=memo, num=num, lag=lag, book=book, bank=bank,
                 bank_desc=bank_desc, bank_amount=amount if bank_amount is None else bank_amount, bank_check=bank_check)
        self.events.append(e); return e
    def cheque(self, d, amount, name, memo="", lag=None):
        n = str(self.check); self.check += 1
        lag = None if lag == "never" else self.r.randint(3, 16) if lag is None else lag
        return self.ev(d, -amount, "Check", name, memo, n, lag, bank_desc=f"CHECK {n}", bank_check=n)
    def normal(self, d0, d1, n_dep=14, n_chk=10, n_ach=8):
        r = self.r; days = (d1 - d0).days
        for _ in range(n_dep):
            d = d0 + timedelta(days=r.randint(0, days)); c = r.choice(CUSTOMERS)
            self.ev(d, r.randint(40_000, 900_000), "Deposit", c, "Customer payment", lag=r.randint(0, 2), bank_desc=f"DEPOSIT ID {r.randint(100000, 999999)}")
        for _ in range(n_chk):
            d = d0 + timedelta(days=r.randint(0, days)); self.cheque(d, r.randint(15_000, 480_000), r.choice(VENDORS), "Bill payment")
        for _ in range(n_ach):
            d = d0 + timedelta(days=r.randint(0, days)); v = r.choice(VENDORS)
            self.ev(d, -r.randint(8_000, 260_000), "Expense", v, "Online payment", lag=r.randint(0, 2), bank_desc=f"ACH DEBIT {v.upper()}")
    def lines(self):
        """The books' lines (book_from .. end + 20 days) and the bank's lines (start .. end), in date order."""
        books, bank = [], []
        for e in sorted(self.events, key=lambda e: e["date"]):
            if e["book"] and self.book_from <= e["date"] <= self.end + timedelta(days=20):
                books.append(dict(date=e["date"], type=e["type"], num=e["num"], name=e["name"], memo=e["memo"], amount=e["amount"], ev=e))
            bd = e["date"] + timedelta(days=e["lag"]) if e["lag"] is not None else None
            if e["bank"] and bd and self.start <= bd <= self.end:
                bank.append(dict(date=bd, desc=e["bank_desc"] or e["name"].upper(), check=e["bank_check"], amount=e["bank_amount"], ev=e))
        bank.sort(key=lambda b: b["date"]); books.sort(key=lambda k: k["date"])
        # the bank's beginning balance: the books' opening plus everything that cleared before the span
        cleared_before = sum(e["bank_amount"] for e in self.events if e["bank"] and e["lag"] is not None and e["date"] + timedelta(days=e["lag"]) < self.start
                             and e["date"] >= self.book_from)
        begin = self.opening + cleared_before + getattr(self, "bank_extra_begin", 0)
        return books, bank, begin

# ------------------------------------------------------------------ writers: the bank's download
def bank_generic(path, bank, begin):
    """Date, Description, Amount, Balance; oldest first."""
    bal = begin
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Date", "Description", "Amount", "Balance"])
        for b in bank:
            bal += b["amount"]; w.writerow([ds(b["date"]), b["desc"], money(b["amount"]), money(bal)])
def bank_newest_first(path, bank, begin):
    """Details, Posting Date, Description, Amount, Type, Balance, Check or Slip #; newest first."""
    rows, bal = [], begin
    for b in bank:
        bal += b["amount"]
        typ = "CHECK_PAID" if b["check"] else ("ACH_DEBIT" if b["amount"] < 0 else "DEPOSIT")
        rows.append(["CHECK" if b["check"] else ("DEBIT" if b["amount"] < 0 else "CREDIT"), ds(b["date"]), b["desc"], f"{b['amount'] / 100:.2f}", typ, f"{bal / 100:.2f}", b["check"] or ""])
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Details", "Posting Date", "Description", "Amount", "Type", "Balance", "Check or Slip #"])
        for r_ in reversed(rows): w.writerow(r_)
def bank_summary_top(path, bank, begin, start, end):
    """A summary block on top (beginning balance, totals, ending balance), then Date, Description, Amount, Running Bal."""
    endbal = begin + sum(b["amount"] for b in bank)
    cr = sum(b["amount"] for b in bank if b["amount"] > 0); dr = sum(b["amount"] for b in bank if b["amount"] < 0)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Description", "", "Summary Amt."])
        w.writerow([f"Beginning balance as of {ds(start)}", "", money(begin)])
        w.writerow([f"Total credits", "", money(cr)]); w.writerow([f"Total debits", "", money(dr)])
        w.writerow([f"Ending balance as of {ds(end)}", "", money(endbal)]); w.writerow([])
        w.writerow(["Date", "Description", "Amount", "Running Bal."])
        w.writerow([ds(start), f"Beginning balance as of {ds(start)}", "", money(begin)])
        bal = begin
        for b in bank:
            bal += b["amount"]; w.writerow([ds(b["date"]), b["desc"], money(b["amount"]), money(bal)])
def bank_headerless(path, bank):
    """No heading row: date, amount, "*", check number, description."""
    with open(path, "w", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        for b in bank: w.writerow([ds(b["date"]), f"{b['amount'] / 100:.2f}", "*", b["check"] or "", b["desc"]])
def bank_debit_credit(path, bank, begin, drop=None):
    """Excel: Date, Transaction, Check No., Withdrawals, Deposits, Balance (withdrawals as positive numbers)."""
    wb = Workbook(); ws = wb.active; ws.title = "Transactions"
    ws.append(["Account activity"]); ws.append([])
    ws.append(["Date", "Transaction", "Check No.", "Withdrawals", "Deposits", "Balance"])
    bal = begin
    for i, b in enumerate(bank):
        bal += b["amount"]
        if drop is not None and i == drop: continue
        ws.append([datetime(b["date"].year, b["date"].month, b["date"].day), b["desc"], b["check"] or None,
                   -b["amount"] / 100 if b["amount"] < 0 else None, b["amount"] / 100 if b["amount"] > 0 else None, bal / 100])
    for row in ws.iter_rows(min_row=4):
        if isinstance(row[0].value, datetime): row[0].number_format = "mm/dd/yyyy"
    wb.save(path)

# ------------------------------------------------------------------ writers: the books' ledger detail
def books_qbo(path, company, accounts, period_text):
    """QuickBooks Online: General Ledger (or Transaction Detail by Account) > Export to Excel. accounts: [(name, opening, lines)]."""
    rows = [[company], ["General Ledger"], [period_text], [], ["", "Date", "Transaction Type", "Num", "Name", "Memo/Description", "Split", "Amount", "Balance"]]
    for name, opening, ls in accounts:
        rows.append([name]); rows.append(["", "Beginning Balance", "", "", "", "", "", "", opening / 100])
        bal, tot = opening, 0
        for k in ls:
            bal += k["amount"]; tot += k["amount"]
            rows.append(["", ds(k["date"]), k["type"], k["num"], k["name"], k["memo"], "-Split-", k["amount"] / 100, bal / 100])
        rows.append([f"Total for {name}", "", "", "", "", "", "", tot / 100, ""])
    rows += [[], [], ["Accrual Basis Monday, April 20, 2026 09:12 AM GMT-04:00"]]
    wb = Workbook(); ws = wb.active; ws.title = "General Ledger"
    for r_ in rows: ws.append(r_)
    wb.save(path)
def books_qbd(path, accounts):
    wb = Workbook(); ws = wb.active; ws.title = "Sheet1"
    ws.append(["", "", "Type", "Date", "Num", "Name", "Memo", "Split", "Debit", "Credit", "Balance"])
    for n_, (name, opening, ls) in enumerate(accounts):
        label = f"{10100 + n_ * 100} · {name}"
        ws.append([label, "", "", "", "", "", "", "", None, None, opening / 100])
        bal, dr, cr = opening, 0, 0
        for k in ls:
            bal += k["amount"]; d_ = k["amount"] if k["amount"] > 0 else None; c_ = -k["amount"] if k["amount"] < 0 else None
            dr += d_ or 0; cr += c_ or 0
            ws.append(["", "", k["type"], datetime(k["date"].year, k["date"].month, k["date"].day), k["num"], k["name"], k["memo"], "-SPLIT-",
                       d_ / 100 if d_ else None, c_ / 100 if c_ else None, bal / 100])
        ws.append([f"Total {label}", "", "", "", "", "", "", "", dr / 100, cr / 100, bal / 100])
    ws.append(["TOTAL"])
    for row in ws.iter_rows(min_row=2):
        if isinstance(row[3].value, datetime): row[3].number_format = "mm/dd/yyyy"
    wb.save(path)
def books_xero(path, company, accounts, period_text):
    wb = Workbook(); ws = wb.active; ws.title = "Account Transactions"
    for r_ in [["Account Transactions"], [company], [period_text], [], ["Date", "Source", "Contact", "Description", "Reference", "Debit", "Credit", "Running Balance"]]: ws.append(r_)
    src = {"Check": "Spend Money", "Expense": "Spend Money", "Deposit": "Receive Money", "Payment": "Receive Money", "Journal Entry": "Manual Journal", "Transfer": "Bank Transfer"}
    for n_, (name, opening, ls) in enumerate(accounts):
        ws.append([f"{name} ({90 + n_})"]); ws.append(["Opening Balance", "", "", "", "", None, None, opening / 100])
        bal, dr, cr = opening, 0, 0
        for k in ls:
            bal += k["amount"]; d_ = k["amount"] if k["amount"] > 0 else None; c_ = -k["amount"] if k["amount"] < 0 else None
            dr += d_ or 0; cr += c_ or 0
            ws.append([k["date"].strftime("%d %b %Y"), src.get(k["type"], k["type"]), k["name"], k["memo"], k["num"], d_ / 100 if d_ else None, c_ / 100 if c_ else None, bal / 100])
        ws.append([f"Total {name} ({90 + n_})", "", "", "", "", dr / 100, cr / 100, None]); ws.append(["Closing Balance", "", "", "", "", None, None, bal / 100])
    wb.save(path)

# ------------------------------------------------------------------ the key
KEY = {}
def bank_kind(b):
    d = b["desc"].lower()
    if b["amount"] < 0 and any(w in d for w in ("fee", "service charge", "maintenance", "overdraft", "nsf")): return "fee"
    if b["amount"] > 0 and "interest" in d: return "interest"
    return "other"
def key_for(bank, books, opening, begin, end_bal, account, accounts, bank_layout, books_layout, period=None, known=(True, True)):
    """bank, books as written to the files (book lines only for the account reconciled)."""
    bb = begin if known[0] else None
    be = end_bal if known[1] else None
    if bb is None and be is not None: pass
    r = reconcile([dict(x) for x in bank], [dict(x) for x in books], opening, bb, be)
    BK = {i: k for i, k in enumerate(books)}; BN = {i: b for i, b in enumerate(bank)}
    ex = []
    near = [{"kind": n["kind"], "bankDate": BN[n["bank"]]["date"].isoformat(), "bankAmount": BN[n["bank"]]["amount"] / 100,
             "bookDate": BK[n["book"]]["date"].isoformat(), "bookAmount": BK[n["book"]]["amount"] / 100, "num": BK[n["book"]]["num"]} for n in r["near"]]
    batches = [{"bankDate": BN[bi]["date"].isoformat(), "amount": BN[bi]["amount"] / 100, "count": len(v)} for bi, v in r["match"].items() if len(v) > 1]
    end = r["end"]
    out = [{"date": k["date"].isoformat(), "num": k["num"], "name": k["name"], "amount": k["amount"] / 100, "age": (end - k["date"]).days} for k in r["outstanding"]]
    bo = [{"date": b["date"].isoformat(), "desc": b["desc"], "amount": b["amount"] / 100, "kind": bank_kind(b)} for b in r["bank_only"]]
    k = {"account": account, "accounts": accounts, "bankLayout": bank_layout, "booksLayout": books_layout,
         "bankStart": r["start"].isoformat(), "bankEnd": r["end"].isoformat(), "bankLines": len(bank),
         "bankBegin": None if bb is None else bb / 100, "bankEnding": None if r["bank_end"] is None else r["bank_end"] / 100,
         "booksEnding": r["book_end"] / 100, "matched": len(r["match"]), "matchedChecks": sum(1 for bi, v in r["match"].items() if len(v) == 1 and BN[bi]["amount"] < 0 and check_no(BN[bi]) and BK[v[0]]["num"]),
         "batches": batches, "near": near, "duplicates": [{"date": BK[d["book"]]["date"].isoformat(), "amount": BK[d["book"]]["amount"] / 100, "name": BK[d["book"]]["name"]} for d in r["dups"]],
         "outstanding": out, "bankOnly": bo, "clearedBefore": len(r["cleared_before"]), "fromBefore": [{"date": b["date"].isoformat(), "amount": b["amount"] / 100} for b in r["from_before"]],
         "afterStatement": len(r["after"]), "corrections": r["corrections"] / 100, "adjustedBank": None if r["adj_bank"] is None else r["adj_bank"] / 100, "adjustedBooks": r["adj_book"] / 100,
         "difference": None if r["adj_bank"] is None else (r["adj_bank"] - r["adj_book"]) / 100,
         "stale": len(r["stale"]), "oldOutstanding": len(r["old"]), "oldDeposits": len(r["old_dit"])}
    if len(accounts) > 1: ex.append("ACCOUNT_CHOSEN")
    if bb is None or be is None: ex.append("NEED_BALANCES")
    if k["difference"] not in (None, 0): ex.append("DOES_NOT_TIE")
    if r["start_explained"] is False: ex.append("START_NOT_EXPLAINED")
    if any(n["kind"] == "check amount differs" for n in r["near"]): ex.append("CHECK_AMOUNT_DIFFERS")
    if any(n["kind"] == "transposed" for n in r["near"]): ex.append("TRANSPOSED")
    if any(n["kind"] == "sign" for n in r["near"]): ex.append("SIGN_ERROR")
    if r["dups"]: ex.append("BOOK_DUPLICATES")
    if r["bank_only"]: ex.append("BANK_ONLY")
    if r["stale"]: ex.append("STALE_CHECKS")
    if r["old"]: ex.append("OLD_OUTSTANDING")
    if r["old_dit"]: ex.append("OLD_DEPOSITS_IN_TRANSIT")
    if batches: ex.append("BATCHES")
    if r["from_before"]: ex.append("FROM_BEFORE")
    if r["after"]: ex.append("AFTER_STATEMENT")
    k["exceptions"] = sorted(ex); k["status"] = "COMPUTED"
    return k, r
def case(cid, title, kind, bank_file, books_file, k, extra=None):
    e = {"title": title, "kind": kind, "bankFile": bank_file, "booksFile": books_file}; e.update(k)
    if extra: e.update(extra)
    KEY[cid] = e

def strip(lines): return [{k_: v for k_, v in x.items() if k_ != "ev"} for x in lines]
PERIOD = "October 1, 2025 - April 20, 2026"

def standard(seed, opening=4_825_000):
    w = World(seed, opening=opening)
    w.normal(D(2025, 10, 1), D(2025, 12, 31), 16, 12, 10)          # last quarter: most cleared in 2025
    for d, a, n in ((D(2025, 12, 22), 186_450, "Riverside Electric"), (D(2025, 12, 29), 74_210, "Valley Fuel")):  # outstanding at Dec 31
        w.cheque(d, a, n, "Bill payment", lag=12)
    w.normal(D(2026, 1, 1), D(2026, 3, 24), 22, 16, 12)
    w.cheque(D(2026, 3, 26), 142_300, "Harbor Supply Co", "Bill payment", lag=14)                 # outstanding at Mar 31
    w.cheque(D(2026, 3, 30), 56_875, "Apex Plumbing", "Bill payment", lag=9)
    w.ev(D(2026, 3, 31), 318_640, "Deposit", "Granite Schools", "Customer payment", lag=2, bank_desc="DEPOSIT ID 774120")   # in transit
    w.ev(D(2026, 1, 31), -2_500, "Expense", "", "", lag=0, bank_desc="MONTHLY SERVICE FEE", book=False)                      # bank only
    w.ev(D(2026, 2, 28), -2_500, "Expense", "", "", lag=0, bank_desc="MONTHLY SERVICE FEE", book=False)
    w.ev(D(2026, 3, 31), -2_500, "Expense", "", "", lag=0, bank_desc="MONTHLY SERVICE FEE", book=False)
    w.ev(D(2026, 3, 31), 1_842, "Deposit", "", "", lag=0, bank_desc="INTEREST PAYMENT", book=False)
    w.ev(D(2026, 4, 6), -88_000, "Check", "Metro Utilities", "Bill payment", num="9999", lag=None)   # after the statement
    return w

# ---- 01 a normal quarter, generic bank CSV, QuickBooks Online ledger with the checking account only
w = standard(1); books, bank, begin = w.lines()
bank_generic(P("01-bank.csv"), bank, begin)
books_qbo(P("01-books-general-ledger.xlsx"), "Northgate Electrical Supply", [("Checking", w.opening, books)], PERIOD)
k, r = key_for(strip(bank), strip(books), w.opening, begin, begin + sum(b["amount"] for b in bank), "Checking", ["Checking"], "generic", "qbo")
assert k["difference"] == 0 and len(r["bank_only"]) == 4, k
case("01", "A normal quarter: generic bank CSV, QuickBooks Online ledger; checks outstanding, a deposit in transit, fees and interest not in the books", "clean",
     "01-bank.csv", "01-books-general-ledger.xlsx", k)

# ---- 02 the bank's download newest first, with a check-number column and a Type column
w = standard(2); books, bank, begin = w.lines()
bank_newest_first(P("02-bank-newest-first.csv"), bank, begin)
books_qbo(P("02-books-general-ledger.xlsx"), "Lantern Signs & Graphics", [("Business Checking", w.opening, books)], PERIOD)
k, r = key_for(strip(bank), strip(books), w.opening, begin, begin + sum(b["amount"] for b in bank), "Business Checking", ["Business Checking"], "newest-first", "qbo")
assert k["difference"] == 0
case("02", "The bank's download newest first, with a check-number column", "ugly", "02-bank-newest-first.csv", "02-books-general-ledger.xlsx", k)

# ---- 03 a summary block above the lines; Xero ledger with three accounts, the checking one chosen
w = standard(3); books, bank, begin = w.lines()
bank_summary_top(P("03-bank-with-summary.csv"), bank, begin, w.start, w.end)
other1 = [dict(date=D(2026, 1, 15), type="Transfer", num="", name="", memo="Transfer from checking", amount=500_000), dict(date=D(2026, 3, 2), type="Deposit", num="", name="", memo="Interest", amount=1_210)]
other2 = [dict(date=D(2026, 2, 5), type="Expense", num="", name="Valley Fuel", memo="Fuel", amount=48_800)]
books_xero(P("03-books-xero.xlsx"), "Indigo Storage", [("Savings Account", 2_000_000, other1), ("Business Checking", w.opening, books), ("Fuel", 0, other2)], "For the period 1 October 2025 to 20 April 2026")
k, r = key_for(strip(bank), strip(books), w.opening, begin, begin + sum(b["amount"] for b in bank), "Business Checking", ["Savings Account", "Business Checking", "Fuel"], "summary", "xero")
case("03", "A summary block above the bank's lines; a Xero ledger with three accounts, the checking account chosen", "ugly", "03-bank-with-summary.csv", "03-books-xero.xlsx", k)

# ---- 04 no heading row and no balance column: the accountant types the statement's balances
w = standard(4); books, bank, begin = w.lines()
bank_headerless(P("04-bank-no-headings.csv"), bank)
books_qbd(P("04-books-desktop.xlsx"), [("Operating Account", w.opening, books)])
endb = begin + sum(b["amount"] for b in bank)
k, r = key_for(strip(bank), strip(books), w.opening, begin, endb, "Operating Account", ["Operating Account"], "headerless", "qbd")
case("04", "No heading row, no balance column (the accountant types the statement's beginning and ending balances); QuickBooks Desktop ledger", "ugly",
     "04-bank-no-headings.csv", "04-books-desktop.xlsx", k, {"typed": {"bankBegin": begin / 100, "bankEnd": endb / 100}})

# ---- 05 planted: a check entered with its digits swapped, a deposit entered twice, a check entered for the wrong amount
w = standard(5)
e = w.cheque(D(2026, 2, 3), 45_210, "Coastal Insurance", "Bill payment", lag=6); e["amount"] = -42_510      # books 425.10, bank 452.10, same number
e2 = w.cheque(D(2026, 2, 17), 83_400, "Greenfield Tools", "Bill payment", lag=5); e2["amount"] = -84_300    # books 843.00, bank 834.00: number differs? same number
twin = w.ev(D(2026, 1, 20), 276_500, "Deposit", "Ember Hotel", "Customer payment", lag=1, bank_desc="DEPOSIT ID 551201")
w.ev(D(2026, 1, 22), 276_500, "Deposit", "Ember Hotel", "Customer payment", lag=None, bank=False)            # the same payment entered again
ach = w.ev(D(2026, 3, 9), -61_750, "Expense", "Coastal Insurance", "Online payment", lag=1, bank_desc="ACH DEBIT COASTAL INSURANCE"); ach["amount"] = -67_150   # no number: transposed
books, bank, begin = w.lines()
bank_generic(P("05-planted-bank.csv"), bank, begin)
books_qbo(P("05-planted-books.xlsx"), "Granite Facility Services", [("Checking", w.opening, books)], PERIOD)
k, r = key_for(strip(bank), strip(books), w.opening, begin, begin + sum(b["amount"] for b in bank), "Checking", ["Checking"], "generic", "qbo")
kinds = sorted(n["kind"] for n in k["near"]); assert kinds == ["check amount differs", "check amount differs", "transposed"], kinds
assert len(k["duplicates"]) == 1
case("05", "Planted: two checks entered for the wrong amount, an online payment with its digits swapped, a customer payment entered twice", "planted",
     "05-planted-bank.csv", "05-planted-books.xlsx", k)

# ---- 06 planted: card batches that land as one deposit, and a refund entered as a deposit
w = standard(6)
for day in (D(2026, 1, 12), D(2026, 2, 9), D(2026, 3, 16)):
    sales = [w.r.randint(9_000, 64_000) for _ in range(w.r.randint(3, 5))]
    for j, a in enumerate(sales): w.ev(day - timedelta(days=j % 3), a, "Sales Receipt", "Card sales", "Card batch", lag=None, bank=False)
    w.ev(day, sum(sales), "Deposit", "", "", lag=0, bank_desc="MERCHANT BANKCARD DEPOSIT", book=False)
ref = w.ev(D(2026, 2, 20), -31_250, "Refund", "Delta Fitness", "Refund", lag=1, bank_desc="ACH DEBIT REFUND DELTA FITNESS"); ref["amount"] = 31_250   # entered as money in
books, bank, begin = w.lines()
bank_debit_credit(P("06-planted-bank.xlsx"), bank, begin)
books_qbo(P("06-planted-books.xlsx"), "Juniper Bakery", [("Checking", w.opening, books)], PERIOD)
k, r = key_for(strip(bank), strip(books), w.opening, begin, begin + sum(b["amount"] for b in bank), "Checking", ["Checking"], "debit-credit", "qbo")
assert len(k["batches"]) == 3 and any(n["kind"] == "sign" for n in k["near"]), (k["batches"], k["near"])
case("06", "Planted: card sales recorded one by one that land as one deposit; a refund paid out entered as money in; withdrawals and deposits columns", "planted",
     "06-planted-bank.xlsx", "06-planted-books.xlsx", k)

# ---- 07 planted: stale checks and an old deposit in transit, from before the bank file
w = standard(7)
w.book_from = D(2025, 6, 1)
w.cheque(D(2025, 7, 14), 38_900, "Summit Office Systems", "Bill payment", lag="never")   # never cleared: stale
w.cheque(D(2025, 9, 2), 12_450, "Apex Plumbing", "Bill payment", lag="never")            # never cleared: stale
w.cheque(D(2025, 11, 20), 27_300, "Brightside Media", "Bill payment", lag="never")       # never cleared: old (90-180)
w.ev(D(2026, 3, 12), 145_000, "Deposit", "Cedar Apartments", "Customer payment", lag=None, bank=False)   # recorded, never deposited
books, bank, begin = w.lines()
bank_generic(P("07-planted-bank.csv"), bank, begin)
books_qbo(P("07-planted-books.xlsx"), "Copperline Plumbing Supply", [("Checking", w.opening, books)], "June 1, 2025 - April 20, 2026")
k, r = key_for(strip(bank), strip(books), w.opening, begin, begin + sum(b["amount"] for b in bank), "Checking", ["Checking"], "generic", "qbo")
assert k["stale"] == 2 and k["oldOutstanding"] == 1 and k["oldDeposits"] == 1 and k["difference"] == 0, k
case("07", "Planted: two checks over six months old, one over 90 days, and a deposit recorded but never made", "planted", "07-planted-bank.csv", "07-planted-books.xlsx", k)

# ---- 08 the books file starts the same day as the bank's: items recorded earlier clear in January
w = standard(8)
books, bank, begin = w.lines()
cut = [k_ for k_ in books if k_["date"] >= w.start]
opening8 = w.opening + sum(k_["amount"] for k_ in books if k_["date"] < w.start)
bank_generic(P("08-bank.csv"), bank, begin)
books_qbo(P("08-books-from-january.xlsx"), "Kestrel Bakery", [("Checking", opening8, cut)], "January 1 - April 20, 2026")
k, r = key_for(strip(bank), strip(cut), opening8, begin, begin + sum(b["amount"] for b in bank), "Checking", ["Checking"], "generic", "qbo")
truth = sorted(round(e["bank_amount"] / 100, 2) for e in w.events if e["bank"] and e["lag"] is not None and e["date"] < w.start <= e["date"] + timedelta(days=e["lag"]))
assert sorted(x["amount"] for x in k["fromBefore"]) == truth and k["difference"] == 0, (k["fromBefore"], truth)
case("08", "The books file starts on the bank file's first day: two checks written in December clear in January and are recognized as recorded before", "ugly",
     "08-bank.csv", "08-books-from-january.xlsx", k)

# ---- 09 planted: a line missing from the bank's download
w = standard(9); books, bank, begin = w.lines()
bank_debit_credit(P("09-planted-bank-line-missing.xlsx"), bank, begin, drop=17)
books_qbo(P("09-books.xlsx"), "Pioneer Fitness", [("Checking", w.opening, books)], PERIOD)
KEY["09"] = {"title": "Planted: a line missing from the bank's download, so its running balance jumps", "kind": "planted", "bankFile": "09-planted-bank-line-missing.xlsx",
             "booksFile": "09-books.xlsx", "status": "COMPUTED", "stopOnly": True, "exceptions": ["BANK_FILE_GAPS"]}

# ---- 10 the wrong files: a trial balance for the books, and the books' ledger given as the bank file
wb = Workbook(); ws = wb.active
for r_ in [["Northgate Electrical Supply"], ["Trial Balance"], ["As of March 31, 2026"], [], ["", "Debit", "Credit"], ["Checking", 128_089.98, None], ["TOTAL", 128_089.98, None]]: ws.append(r_)
wb.save(P("10-trial-balance.xlsx"))
KEY["10"] = {"title": "The wrong books file: a trial balance", "kind": "ugly", "bankFile": "01-bank.csv", "booksFile": "10-trial-balance.xlsx", "status": "NOT_RECOGNIZED", "exceptions": ["NOT_RECOGNIZED"]}
KEY["11"] = {"title": "The wrong bank file: the books' ledger dropped as the bank's download", "kind": "ugly", "bankFile": "01-books-general-ledger.xlsx", "booksFile": "01-books-general-ledger.xlsx",
             "status": "NOT_RECOGNIZED", "exceptions": ["NOT_RECOGNIZED"]}

# ---- 12 the starting balances do not explain the old items: the bank's beginning balance is off
w = standard(12); w.bank_extra_begin = 10_000
books, bank, begin = w.lines()
bank_generic(P("12-bank.csv"), bank, begin)
books_qbo(P("12-books.xlsx"), "Orchard Restaurants", [("Checking", w.opening, books)], PERIOD)
k, r = key_for(strip(bank), strip(books), w.opening, begin, begin + sum(b["amount"] for b in bank), "Checking", ["Checking"], "generic", "qbo")
assert "START_NOT_EXPLAINED" in k["exceptions"] and k["difference"] == 100.0, (k["exceptions"], k["difference"])
case("12", "Planted: $100.00 that no transaction explains (the bank's beginning balance does not fit the books), so it does not tie", "planted", "12-bank.csv", "12-books.xlsx", k)

# ---- 13 CSV ledger with dollar signs and parentheses; savings account chosen by the accountant
w = standard(13); books, bank, begin = w.lines()
bank_generic(P("13-bank-savings.csv"), bank, begin)
chk = [dict(date=D(2026, 1, 6), type="Check", num="2001", name="Valley Fuel", memo="", amount=-12_000)]
rows = [["Meadow Dental Group"], ["General Ledger"], [PERIOD], [], ["", "Date", "Transaction Type", "Num", "Name", "Memo/Description", "Split", "Amount", "Balance"]]
for name, op, ls in (("Operating Checking", 1_500_000, chk), ("Reserve Account", w.opening, books)):
    rows.append([name]); rows.append(["", "Beginning Balance", "", "", "", "", "", "", money(op, True, True)]); bal, tot = op, 0
    for x in ls:
        bal += x["amount"]; tot += x["amount"]
        rows.append(["", ds(x["date"]), x["type"], x["num"], x["name"], x["memo"], "-Split-", money(x["amount"], True, True), money(bal, True, True)])
    rows.append([f"Total for {name}", "", "", "", "", "", "", money(tot, True, True), ""])
with open(P("13-books.csv"), "w", newline="") as f:
    wr = csv.writer(f, quoting=csv.QUOTE_ALL)
    for r_ in rows: wr.writerow(r_)
k, r = key_for(strip(bank), strip(books), w.opening, begin, begin + sum(b["amount"] for b in bank), "Reserve Account", ["Operating Checking", "Reserve Account"], "generic", "qbo")
case("13", "The ledger as CSV with dollar signs and parentheses; two bank accounts, the accountant chooses the second", "ugly", "13-bank-savings.csv", "13-books.csv", k,
     {"chooseAccount": "Reserve Account"})

# ---- 14 no balances in the bank file and none typed: it cannot prove the tie, and says so
w = standard(14); books, bank, begin = w.lines()
bank_headerless(P("14-bank-no-headings.csv"), bank)
books_qbo(P("14-books.xlsx"), "Summit Landscaping", [("Checking", w.opening, books)], PERIOD)
k, r = key_for(strip(bank), strip(books), w.opening, begin, None, "Checking", ["Checking"], "headerless", "qbo", known=(False, False))
case("14", "No balances anywhere: the page matches, lists, and asks for the statement's balances before it can prove the tie", "ugly", "14-bank-no-headings.csv", "14-books.xlsx", k)

json.dump(KEY, open(os.path.join(HERE, "answer-key.json"), "w"), indent=1, default=str)
print(len(KEY), "cases;", {c: (v["exceptions"], v.get("difference")) for c, v in KEY.items()})
