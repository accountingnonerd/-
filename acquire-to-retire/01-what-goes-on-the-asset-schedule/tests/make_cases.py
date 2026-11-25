#!/usr/bin/env python3
"""Builds the acceptance test for Acquire-to-Retire 01, "What goes on the asset schedule?".

Each case is one general ledger report for the year 2026 (January 1 to December 31), in the layout
of QuickBooks Online (General Ledger), QuickBooks Desktop (General Ledger) or Xero (Account
Transactions), written from a model of accounts and ledger lines for invented businesses. The answer
key is worked out from the model with the rules below, never by reading the files back.
Money is held in integer cents, debit positive.

The rules the key follows (version 2, after the CPA review and the first-time-user review):
  Account roles, from the name (number prefixes like "15000 · " and codes like " (710)" removed,
  lower case). A sub-account "Parent:Child" takes its role from the child, except: a child
  containing "depreciation" under a fixed asset parent is accumulated depreciation; a child with no role under a fixed asset parent is
  a fixed asset. For one name, first match wins:
    other: "accumulated amortization", or "amortization" without "depreciation";
    accumulated depreciation: "accumulated depreciation", "accum depr", "accum. depr";
    depreciation expense: "depreciation";
    fixed asset (cost): equipment, furniture, fixture(s), vehicle(s), truck(s), trailer(s),
      machinery, computer(s), leasehold improvement(s), improvements, building(s), "land" as a word,
      "fixed asset(s)", "property and equipment"; and none of: expense(s), rental, rent, repair(s),
      maintenance, small, supplies, lease, fuel, insurance, registration, software, internet, minor,
      loan(s), note(s), payable, interest, gain, loss, sale, income, revenue, inventory, payment(s);
    review for capitalization: repair(s), maintenance, supplies, tools, computer, software,
      equipment, furniture, improvement(s), auto, vehicle(s), truck(s); and none of: rental, rent,
      lease, fuel, insurance, loan(s), payable, interest, gain, income, revenue;
    anything else: other. The accountant can change any role on screen.
  Fixed asset lines, in this order:
    1. transfers: a credit in one fixed asset account and a debit of the same amount in another,
       same number (not blank) and date: neither is an addition or a disposal;
    2. reversals: a credit and a debit of the same amount in one account, same name, at most 31
       days apart;
    3. payments: 3 or more debits of the same amount from the same name in one account (likely loan
       payments): not additions;
    4. additions: the other debits; flagged journal entry, trade-in (memo has "trade", "allowance"
       or "net of"), land (account named land, not land improvements: not depreciated);
    5. the other credits: "return" (type has "credit" or "refund", not a journal entry: reduces a
       purchase's cost); "recorded" (a numbered entry that, same number and date, debits accumulated
       depreciation or posts to an account named gain, loss, sale or disposal: booked as a sale,
       check it); otherwise "proceeds" (a sale or write-off whose proceeds were credited to the
       asset: the accountant types its cost and depreciation to date, the page works out the entry).
  Purchases in review accounts: lines grouped into bills (same date, type, number and name, across
    review accounts when the number is not blank; within one account when it is). Bills with a net
    credit are applied first, oldest first: a credit whose number and date also debit a fixed asset
    account is a reclass and removes the bill (or the set of bills, over the threshold, in the same
    account) of exactly its amount; any other credit with a name reduces the latest earlier bill from
    that name in that account. A bill whose remaining amount is more than the threshold ($2,500.00
    unless typed) is a candidate, undecided until the accountant chooses. It is routine (labelled,
    still listed) when its name has 3 or more candidates in that account that are all the same amount
    or whose memos say contract, maintenance, service, subscription, monthly, quarterly or annual.
  Possible sales elsewhere: credits in other accounts whose memo or name says sold, sale of,
    trade-in or insurance proceeds (not part of a recorded disposal).
  Mid-quarter: more than 40% of the year's depreciable additions dated in the last three months.
  Depreciation booked: the sum of the lines in depreciation expense accounts. Tax or book
    depreciation typed: adjustment = typed - booked.
  Last year's schedule typed (cost, accumulated depreciation): compared with the opening balances.
  The file adds up: for each account (with its sub-accounts), opening + lines = the report's total
  and ending balance.

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
def clean_part(s):
    s = re.sub(r"\s*\([0-9A-Za-z.\-]{1,10}\)\s*$", "", s.strip())
    s = re.sub(r"^\s*\d[\d.\-]*\s*(·|-|–)?\s*", "", s)
    return s.strip()
def norm_name(s): return ":".join(clean_part(p) for p in s.split(":"))

FA_W = re.compile(r"equipment|furniture|fixtures?\b|vehicles?\b|trucks?\b|trailers?\b|machinery|computers?\b|leasehold improvements?|improvements\b|buildings?\b|\bland\b|fixed assets?|property and equipment")
NOT_FA = re.compile(r"expenses?\b|rental|\brent\b|repairs?\b|maintenance|small|supplies|lease|fuel|insurance|registration|software|internet|minor|\bloans?\b|\bnotes?\b|payable|interest|\bgain|\bloss|\bsale|income|revenue|inventory|payments?\b")
RV_W = re.compile(r"repairs?\b|maintenance|supplies|tools|computer|software|equipment|furniture|improvements?\b|\bauto\b|vehicles?\b|trucks?\b")
NOT_RV = re.compile(r"rental|\brent\b|lease|fuel|insurance|\bloans?\b|payable|interest|\bgain|income|revenue")
def base_role(s):
    s = s.lower()
    if re.search(r"accumulated amortization|accum\.? amort", s): return "other"
    if re.search(r"accumulated depreciation|accum\.? depr", s): return "ad"
    if "depreciation" in s: return "dep"
    if "amortization" in s: return "other"
    if FA_W.search(s) and not NOT_FA.search(s): return "fa"
    if RV_W.search(s) and not NOT_RV.search(s): return "review"
    return "other"
def role_of(name):
    parts = norm_name(name).split(":")
    if len(parts) == 1: return base_role(parts[0])
    last, parent = parts[-1].lower(), ":".join(parts[:-1])
    rp = role_of(parent)
    if "depreciation" in last and rp == "fa": return "ad"
    r_ = base_role(last)
    if r_ == "other" and rp == "fa": return "fa"
    return r_
def is_land(name): s = norm_name(name).lower(); return bool(re.search(r"\bland\b", s)) and "improvement" not in s

def key_for(A, threshold=250000, sched=None, tax_dep=None, roles=None, period=("2026-01-01", "2026-12-31")):
    accts = [a for a in A.values() if a["lines"] or a["opening"]]      # an account with no balance and no lines is not in the export
    role = {a["name"]: (roles or {}).get(a["name"], role_of(a["name"])) for a in accts}
    by = lambda r_: [a for a in accts if role[a["name"]] == r_]
    ex = []
    # every line, with its account, in file order (accounts in order, lines by date)
    L = []
    for a in accts:
        for i, x in enumerate(sorted(a["lines"], key=lambda x: x["date"])):
            L.append(dict(x, acct=a["name"], role=role[a["name"]], seq=len(L)))
    fa_lines = [x for x in L if x["role"] == "fa"]
    used = set()
    # 1. transfers between fixed asset accounts: same number and date, same amount, opposite sides
    transfers = []
    for c in fa_lines:
        if c["amount"] >= 0 or not c["num"] or c["seq"] in used: continue
        d = next((y for y in fa_lines if y["seq"] not in used and y["amount"] == -c["amount"] and y["acct"] != c["acct"] and y["num"] == c["num"] and y["date"] == c["date"]), None)
        if d:
            used |= {c["seq"], d["seq"]}
            transfers.append({"from": c["acct"], "to": d["acct"], "date": c["date"].isoformat(), "amount": d["amount"] / 100})
    # 2. reversals within one account: same name, at most 31 days apart
    reversals = []
    for c in fa_lines:
        if c["amount"] >= 0 or c["seq"] in used: continue
        d = next((y for y in fa_lines if y["seq"] not in used and y["acct"] == c["acct"] and y["amount"] == -c["amount"] and y["name"].lower() == c["name"].lower() and abs((y["date"] - c["date"]).days) <= 31), None)
        if d:
            used |= {c["seq"], d["seq"]}
            reversals.append({"account": c["acct"], "amount": d["amount"] / 100, "name": d["name"]})
    # 3. payments: 3 or more equal debits from the same name in one account
    payments = []
    for a in by("fa"):
        cnt = {}
        for y in fa_lines:
            if y["acct"] == a["name"] and y["seq"] not in used and y["amount"] > 0 and y["name"]: cnt.setdefault((y["name"].lower(), y["amount"]), []).append(y)
        for (nm, am), ys in cnt.items():
            if len(ys) >= 3:
                used |= {y["seq"] for y in ys}
                payments.append({"account": a["name"], "name": ys[0]["name"], "count": len(ys), "amount": am / 100})
    # 4. additions and 5. credits
    additions, disposals = [], []
    for y in fa_lines:
        if y["seq"] in used: continue
        if y["amount"] > 0:
            additions.append({"account": y["acct"], "date": y["date"].isoformat(), "num": y["num"], "name": y["name"], "amount": y["amount"] / 100,
                              "journal": "journal" in y["type"].lower(), "tradeIn": bool(re.search(r"trade|allowance|net of", y["memo"], re.I)), "land": is_land(y["acct"])})
        elif y["amount"] < 0:
            if re.search(r"credit|refund", y["type"], re.I) and "journal" not in y["type"].lower(): kind = "return"
            elif y["num"] and any(z["num"] == y["num"] and z["date"] == y["date"] and ((z["role"] == "ad" and z["amount"] > 0) or re.search(r"gain|loss|sale|disposal", z["acct"], re.I)) for z in L): kind = "recorded"
            else: kind = "proceeds"
            disposals.append({"account": y["acct"], "date": y["date"].isoformat(), "num": y["num"], "name": y["name"], "amount": -y["amount"] / 100, "kind": kind})
    rollforward = []
    for a in by("fa"):
        mine = [y for y in fa_lines if y["acct"] == a["name"]]
        rollforward.append({"account": a["name"], "opening": a["opening"] / 100, "debits": sum(y["amount"] for y in mine if y["amount"] > 0) / 100,
                            "credits": sum(y["amount"] for y in mine if y["amount"] < 0) / 100, "ending": (a["opening"] + sum(y["amount"] for y in mine)) / 100})
    adroll = []
    for a in by("ad"):
        end = a["opening"] + sum(x["amount"] for x in a["lines"])
        adroll.append({"account": a["name"], "opening": a["opening"] / 100, "credits": sum(x["amount"] for x in a["lines"] if x["amount"] < 0) / 100,
                       "debits": sum(x["amount"] for x in a["lines"] if x["amount"] > 0) / 100, "ending": end / 100})
    # review accounts: one bill = same date, type, number and name (across review accounts when it has a number)
    groups, order = {}, []
    for y in L:
        if y["role"] != "review": continue
        k = ("n", y["date"], y["type"], y["num"], y["name"]) if y["num"] else ("a", y["acct"], y["date"], y["type"], y["name"])
        if k not in groups: groups[k] = []; order.append(k)
        groups[k].append(y)
    G = [{"k": k, "lines": groups[k], "total": sum(y["amount"] for y in groups[k]), "date": groups[k][0]["date"], "num": groups[k][0]["num"],
          "name": groups[k][0]["name"], "accts": list(dict.fromkeys(y["acct"] for y in groups[k])), "first": groups[k][0]["seq"]} for k in order]
    pos = sorted([g for g in G if g["total"] > 0], key=lambda g: (g["date"], g["first"]))
    for c in sorted([g for g in G if g["total"] < 0], key=lambda g: (g["date"], g["first"])):
        R = -c["total"]
        reclass = c["num"] and any(z["role"] == "fa" and z["amount"] > 0 and z["num"] == c["num"] and z["date"] == c["date"] for z in L)
        if reclass:
            pool = [g for g in pos if g["total"] > threshold and set(g["accts"]) & set(c["accts"]) and g["total"] > 0]
            hit = next((g for g in pool if g["total"] == R), None)
            chosen = [hit] if hit else None
            if not chosen and len(pool) <= 14:
                for mask in range(1, 1 << len(pool)):
                    sub = [pool[i] for i in range(len(pool)) if mask >> i & 1]
                    if sum(g["total"] for g in sub) == R: chosen = sub; break
            for g in chosen or []: g["total"] = 0
        elif c["name"]:
            prev = [g for g in pos if g["name"].lower() == c["name"].lower() and set(g["accts"]) & set(c["accts"]) and g["date"] <= c["date"] and g["total"] > 0]
            if prev: prev[-1]["total"] -= R
    cands = [g for g in pos if g["total"] > threshold]
    candidates = []
    for g in cands:
        same = [h for h in cands if h["name"] and h["name"].lower() == g["name"].lower() and h["accts"][0] == g["accts"][0]]
        memos = " ".join(y["memo"] for h in same for y in h["lines"])
        routine = bool(g["name"]) and len(same) >= 3 and (len({h["total"] for h in same}) == 1 or bool(re.search(r"contract|maintenance|service|subscription|monthly|quarterly|annual", memos, re.I)))
        candidates.append({"account": g["accts"][0], "date": g["date"].isoformat(), "num": g["num"], "name": g["name"], "amount": g["total"] / 100, "lines": len(g["lines"]), "routine": routine})
    # sales elsewhere
    rec_nums = {(d["num"], d["date"]) for d in disposals if d["kind"] == "recorded"}
    possible_sales = [{"account": y["acct"], "date": y["date"].isoformat(), "amount": -y["amount"] / 100} for y in L
                      if y["role"] == "other" and y["amount"] < 0 and re.search(r"\bsold\b|sale of|trade-?in|insurance proceeds", y["memo"] + " " + y["name"], re.I)
                      and (y["num"], y["date"].isoformat()) not in rec_nums]
    booked = sum(x["amount"] for a in by("dep") for x in a["lines"])
    cost_open = sum(a["opening"] for a in by("fa"))
    ad_open = -sum(a["opening"] for a in by("ad"))
    dep_adds = [x for x in additions if not x["land"]]
    if not by("fa"): ex.append("NO_FIXED_ASSET_ACCOUNTS")
    if any(a["opening"] < 0 or a["opening"] + sum(x["amount"] for x in a["lines"]) < 0 for a in by("fa")): ex.append("FA_CREDIT_BALANCE")
    if candidates: ex.append("CAPITALIZE_CANDIDATES")
    if any(c["routine"] for c in candidates): ex.append("ROUTINE_CHARGES")
    kinds = {d["kind"] for d in disposals}
    if "proceeds" in kinds: ex.append("DISPOSALS")
    if "proceeds" in kinds and not any(x["amount"] > 0 for a in by("ad") for x in a["lines"]): ex.append("AD_NOT_REMOVED")
    if "recorded" in kinds: ex.append("DISPOSALS_RECORDED")
    if "return" in kinds: ex.append("RETURNS")
    if transfers: ex.append("TRANSFERS")
    if reversals: ex.append("REVERSALS")
    if payments: ex.append("LIKELY_LOAN_PAYMENTS")
    if any(x["tradeIn"] for x in additions): ex.append("TRADE_IN")
    if any(x["land"] for x in additions): ex.append("LAND")
    if any(x["journal"] for x in additions): ex.append("JOURNAL_ENTRY_ADDITIONS")
    if possible_sales: ex.append("POSSIBLE_SALES")
    if any("amortization" in norm_name(a["name"]).lower() for a in by("dep")): ex.append("AMORTIZATION")
    if booked == 0 and (cost_open > 0 or additions): ex.append("NO_DEPRECIATION_BOOKED")
    if not period: ex.append("PERIOD_UNKNOWN")
    end = date.fromisoformat(period[1]) if period else max(y["date"] for y in L)
    if not period: end = date(end.year, 12, 31)
    q4 = date(end.year if end.month > 2 else end.year - 1, (end.month - 3) % 12 + 1, 1)
    tot = sum(x["amount"] for x in dep_adds)
    if tot > 0 and sum(x["amount"] for x in dep_adds if date.fromisoformat(x["date"]) >= q4) * 10 > tot * 4: ex.append("MID_QUARTER")
    k = {"period": {"from": period[0], "to": period[1]} if period else None,
         "accounts": {a["name"]: role[a["name"]] for a in accts},
         "rollforward": rollforward, "adRollforward": adroll,
         "additions": additions, "disposals": disposals, "reversals": reversals, "transfers": transfers, "payments": payments,
         "candidates": candidates, "possibleSales": possible_sales,
         "costOpening": cost_open / 100, "adOpening": ad_open / 100,
         "costEnding": round(sum(r_["ending"] for r_ in rollforward), 2), "adEnding": round(-sum(r_["ending"] for r_ in adroll), 2),
         "additionsTotal": round(sum(x["amount"] for x in additions), 2), "scheduleAdditions": round(tot, 2),
         "candidatesTotal": round(sum(x["amount"] for x in candidates), 2),
         "depreciationBooked": booked / 100, "threshold": threshold / 100}
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

def write_qbo_nested(path, company, A, period_text="January 1 - December 31, 2026"):
    """QuickBooks Online General Ledger with sub-accounts shown nested: a header row for the parent,
    its children inside it, and a 'Total for' row closing each level (the parent's total covers its
    children). Account names in the model are full paths, 'Fixed Assets:Truck:Original cost'."""
    rows = [[company], ["General Ledger"], [period_text], [], ["", "Date", "Transaction Type", "Num", "Name", "Memo/Description", "Split", "Amount", "Balance"]]
    accts = [a for a in A.values() if a["lines"] or a["opening"]]
    def subtree(prefix): return [a for a in accts if a["name"] == prefix or a["name"].startswith(prefix + ":")]
    def emit(prefix, label):
        rows.append([label])
        own = next((a for a in accts if a["name"] == prefix), None)
        if own:
            bal = own["opening"]
            rows.append(["", "Beginning Balance", "", "", "", "", "", "", bal / 100])
            for x in sorted(own["lines"], key=lambda x: x["date"]):
                bal += x["amount"]
                rows.append(["", ds(x["date"]), x["type"], x["num"], x["name"], x["memo"], "-Split-", x["amount"] / 100, bal / 100])
        kids = []
        for a in subtree(prefix):
            rest = a["name"][len(prefix) + 1:] if a["name"] != prefix else ""
            if rest and rest.split(":")[0] not in kids: kids.append(rest.split(":")[0])
        for kid in kids: emit(prefix + ":" + kid, kid)
        rows.append([f"Total for {label}", "", "", "", "", "", "", sum(x["amount"] for a in subtree(prefix) for x in a["lines"]) / 100, ""])
    tops = []
    for a in accts:
        t = a["name"].split(":")[0]
        if t not in tops: tops.append(t)
    for t in tops: emit(t, t)
    rows += [[], [], ["Accrual Basis Wednesday, January 20, 2027 09:12 AM GMT-05:00"]]
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
for a_ in A.values():                       # the same months, moved into a July-June year
    for x in a_["lines"]: x["date"] = date(2025, x["date"].month + 6, x["date"].day) if x["date"].month <= 6 else date(2026, x["date"].month - 6, x["date"].day)
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

# ---- 18 QuickBooks Online fixed asset tracking: sub-accounts "Original cost" and "Depreciation", nested, with parent totals
A = book(18, "Ridge Roofing")
del A["fe"], A["veh"], A["ad"]
A2 = {}
A2["truck_c"] = acct("Fixed Assets:Truck:Original cost", 4_200_000)
A2["truck_d"] = acct("Fixed Assets:Truck:Depreciation", -1_800_000)
A2["eq_c"] = acct("Fixed Assets:Equipment:Original cost", 2_650_000)
A2["eq_d"] = acct("Fixed Assets:Equipment:Depreciation", -1_120_000)
A2.update(A); A = A2
line(A["truck_c"], D(4, 8), "Bill", "6120", "Summit Upfitters", "Ladder rack and toolboxes on truck", 680_000)
for m in (6, 12):
    line(A["dep"], D(m, 30 if m == 6 else 31), "Journal Entry", f"DEP-{m}", "", "Depreciation", 420_000 + 175_000)
    line(A["truck_d"], D(m, 30 if m == 6 else 31), "Journal Entry", f"DEP-{m}", "", "Depreciation", -420_000)
    line(A["eq_d"], D(m, 30 if m == 6 else 31), "Journal Entry", f"DEP-{m}", "", "Depreciation", -175_000)
write_qbo_nested(P("18-fixed-asset-tracking-subaccounts.xlsx"), "Ridge Roofing", A)
case("18", "QuickBooks Online fixed asset tracking: 'Original cost' and 'Depreciation' sub-accounts, nested, with parent totals", "ugly",
     "18-fixed-asset-tracking-subaccounts.xlsx", "COMPUTED", key_for(A), "qbo")

# ---- 19 names that look like assets but are not: a truck loan, a note payable, a gain account; amortization; a down payment in auto expense
A = book(19, "Delta Mechanical")
A["loan"] = acct("Truck Loan", -3_000_000, 25000, 900)
A["note"] = acct("Equipment Note Payable", -1_450_000, 25100, 901)
A["gain"] = acct("Gain on Sale of Equipment", 0, 80100, 260)
A["auto"] = acct("Auto and Truck Expense", 0, 60200, 449)
A["dep"]["name"] = "Depreciation and Amortization"
line(A["loan"], D(2, 1), "Deposit", "", "Ally Financial", "Loan proceeds, 2026 Ram", -4_000_000)
for m in range(3, 13): line(A["loan"], D(m, 1), "Check", f"L{m}", "Ally Financial", "Truck loan payment", 61_000)
for m in range(1, 13): line(A["note"], D(m, 15), "Check", f"N{m}", "Kubota Credit", "Note payment", 45_000)
line(A["gain"], D(8, 3), "Deposit", "", "Prairie Equipment", "Sold old mower", -350_000)
line(A["auto"], D(2, 1), "Check", "2211", "Carver Ram", "Down payment, 2026 Ram 2500", 1_200_000)
for m in range(1, 13): line(A["auto"], D(m, 20), "Expense", f"F{m}", "Metro Fuel Card", "Fuel", 41_000 + m * 900)
depreciate(A, 1_300_000 + 220_000)
write_qbo(P("19-loans-gains-and-amortization.xlsx"), "Delta Mechanical", A)
case("19", "Accounts named after assets that are not assets (a truck loan, a note payable, a gain); amortization; a down payment in auto expense", "planted",
     "19-loans-gains-and-amortization.xlsx", "COMPUTED", key_for(A), "qbo")

# ---- 20 a trade-in recorded net, loan payments posted to the asset account, land and a building bought late in the year
A = book(20, "Prairie Grain Supply")
A["land"] = acct("Land", 0, 15500, 730)
A["bldg"] = acct("Buildings", 0, 15600, 731)
line(A["veh"], D(3, 18), "Check", "8101", "Carver Ram", "2026 Ram 3500, net of trade-in ($22,000 allowance for 2019 F-150)", 3_300_000)
for m in range(4, 10): line(A["veh"], D(m, 18), "Check", f"P{m}", "Ally Financial", "Truck payment", 91_240)
line(A["land"], D(11, 30), "Journal Entry", "CL-1", "", "Purchase of 410 Mill Road: land", 6_500_000)
line(A["bldg"], D(11, 30), "Journal Entry", "CL-1", "", "Purchase of 410 Mill Road: building", 24_000_000)
depreciate(A, 1_610_000)
write_qbo(P("20-trade-in-payments-land.xlsx"), "Prairie Grain Supply", A)
case("20", "A truck bought net of a trade-in, loan payments posted to Vehicles, land and a building bought in November", "planted",
     "20-trade-in-payments-land.xlsx", "COMPUTED", key_for(A), "qbo")

# ---- 21 already reclassed, refunded, split across accounts, moved between asset accounts, returned; equipment that is not routine
A = book(21, "Yarrow Fabrication")
line(A["rm"], D(2, 3), "Bill", "4401", "Northline Equipment", "Forklift, used", 800_000)
line(A["rm"], D(2, 17), "Bill", "4415", "Harbor Supply Co", "Pallet racking", 420_000)
line(A["fe"], D(3, 31), "Journal Entry", "AJE-2", "", "Reclass forklift and racking from repairs", 1_220_000)
line(A["rm"], D(3, 31), "Journal Entry", "AJE-2", "", "Reclass forklift and racking to equipment", -1_220_000)
line(A["rm"], D(5, 9), "Bill", "4470", "Coastal HVAC Contractors", "HVAC compressor replacement", 350_000)
line(A["rm"], D(5, 23), "Credit Card Credit", "", "Coastal HVAC Contractors", "Refund, warranty part", -120_000)
line(A["rm"], D(6, 12), "Bill", "77", "Metro Glass", "Storefront glass, front", 180_000)
line(A["sup"], D(6, 12), "Bill", "77", "Metro Glass", "Storefront door hardware", 160_000)
line(A["tools"], D(4, 4), "Bill", "G-11", "Greenfield Tools", "Plasma cutter", 480_000)
line(A["tools"], D(7, 9), "Bill", "G-19", "Greenfield Tools", "MIG welder", 390_000)
line(A["tools"], D(9, 21), "Bill", "G-27", "Greenfield Tools", "Air compressor, 80 gal", 290_000)
line(A["fe"], D(8, 1), "Journal Entry", "TR-1", "", "Move service truck to Vehicles", -1_500_000)
line(A["veh"], D(8, 1), "Journal Entry", "TR-1", "", "Move service truck to Vehicles", 1_500_000)
line(A["fe"], D(9, 2), "Bill", "4520", "Harbor Supply Co", "Welding table", 410_000)
line(A["fe"], D(9, 20), "Bill Credit", "4520-C", "Harbor Supply Co", "Returned clamps", -30_000)
line(A["tools"], D(10, 6), "Bill", "N-301", "Northline Equipment", "Pressure washer, hot water", 300_000)   # two equal bills: still not routine
line(A["tools"], D(11, 9), "Bill", "N-322", "Northline Equipment", "Pressure washer, cold water", 300_000)
A["loss"] = acct("Loss on Disposal of Assets", 0, 80200, 261)
line(A["veh"], D(11, 30), "Journal Entry", "AJE-7", "", "Scrap old utility trailer", -200_000)           # a write-off with a loss, no depreciation removed
line(A["loss"], D(11, 30), "Journal Entry", "AJE-7", "", "Scrap old utility trailer", 200_000)
line(A["fe"], D(11, 30), "Bill", "4600", "Harbor Supply Co", "Parts washer", 200_000)                     # same day and amount, another entry: not a transfer
line(A["veh"], D(12, 4), "Check", "5610", "Valley Kubota", "Kubota RTV, less $8,000 allowance for old unit", 1_250_000)
depreciate(A, 1_480_000)
write_qbo(P("21-reclass-refund-split-transfer.xlsx"), "Yarrow Fabrication", A)
case("21", "Purchases already reclassed, a part refund, a bill split over two accounts, a transfer between asset accounts, a return; three tools that are not routine", "planted",
     "21-reclass-refund-split-transfer.xlsx", "COMPUTED", key_for(A), "qbo")

# ---- 22 the sample for readers: Ridgeline Landscaping (also in ../sample/), with the decisions a reader makes
A = {}
A["eq"] = acct("Equipment", 8_640_000); A["veh"] = acct("Vehicles", 12_450_000); A["ad"] = acct("Accumulated Depreciation", -9_735_000)
A["dep"] = acct("Depreciation Expense", 0); A["rm"] = acct("Repairs and Maintenance", 0); A["sup"] = acct("Office Supplies & Software", 0)
A["tools"] = acct("Small Tools and Equipment", 0); A["fuel"] = acct("Fuel", 0); A["util"] = acct("Utilities", 0); A["rentx"] = acct("Rent", 0)
r = random.Random(22); n = 2000
for m in range(1, 13):
    n += 1; line(A["fuel"], D(m, 8), "Expense", str(n), "Metro Fuel Card", "Fuel", r.randint(90_000, 160_000))
    n += 1; line(A["util"], D(m, 15), "Bill", str(n), "Metro Utilities", "Utilities", r.randint(21_000, 38_000))
    n += 1; line(A["rentx"], D(m, 1), "Check", str(n), "Oakridge Properties", "Yard rent", 280_000)
    n += 1; line(A["sup"], D(m, r.randint(3, 26)), "Expense", str(n), "Office Depot Business", "Office supplies", r.randint(4_000, 31_000))
    if m % 2: n += 1; line(A["rm"], D(m, r.randint(3, 26)), "Bill", str(n), "Midline Hardware", "Mower blades and parts", r.randint(18_000, 95_000))
    if m % 3 == 0: n += 1; line(A["tools"], D(m, r.randint(3, 26)), "Expense", str(n), "Greenfield Tools", "Hand tools", r.randint(6_000, 48_000))
line(A["eq"], D(3, 9), "Bill", "3104", "Valley Kubota", "Zero-turn mower, 72 in.", 1_480_000)
line(A["veh"], D(5, 20), "Check", "3187", "Carver Ford", "2026 F-350 with dump body", 6_125_000)
line(A["veh"], D(6, 3), "Deposit", "", "Jones Turf Services", "Sold 2017 F-250", -1_600_000)
line(A["rm"], D(8, 14), "Bill", "3290", "Coastal Door Co", "Replace shop overhead door", 690_000)
line(A["sup"], D(2, 2), "Bill", "3021", "Summit Office Systems", "Laptops (2) and docking station", 348_000)
line(A["tools"], D(4, 22), "Bill", "3140", "Greenfield Tools", "Trailer-mounted sprayer, 200 gal", 560_000)
for m in (2, 5, 8, 11): line(A["rm"], D(m, 1), "Bill", f"IRR-{m}", "Clearwater Irrigation", "Quarterly irrigation maintenance contract", 275_000)
depreciate(A, 1_680_000)
write_qbo(P("22-sample-ridgeline-landscaping.xlsx"), "Ridgeline Landscaping LLC", A)
k22 = key_for(A, sched=(21_090_000, 9_735_000), tax_dep=2_461_000)
k22["decide"] = [["Coastal Door Co", 6900.00, "cap"], ["Greenfield Tools", 5600.00, "cap"], ["Summit Office Systems", 3480.00, "exp"]] + [["Clearwater Irrigation", 2750.00, "exp"]] * 4
k22["capitalizeTotal"] = 12_500.00
k22["disp"] = [[42_000.00, 36_750.00, 2_625.00]]; k22["gains"] = [13_375.00]
case("22", "The readers' sample: Ridgeline Landscaping, with the reader's decisions, last year's schedule, this year's depreciation and the sold truck's figures typed", "planted",
     "22-sample-ridgeline-landscaping.xlsx", "COMPUTED", k22, "qbo", {"typed": {"scheduleCost": 210_900.00, "scheduleAD": 97_350.00, "taxDepreciation": 24_610.00}})
import shutil
SAMPLE = os.path.join(HERE, "..", "sample"); os.makedirs(SAMPLE, exist_ok=True)
shutil.copy(P("22-sample-ridgeline-landscaping.xlsx"), os.path.join(SAMPLE, "ridgeline-general-ledger-2026.xlsx"))
with open(os.path.join(SAMPLE, "ridgeline-depreciation-schedule-2025.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Asset", "Class", "Placed in service", "Cost", "Accumulated depreciation at 12/31/2025"])
    sched = [("2017 Ford F-250", "Vehicles", "04/10/2017", 42_000_00, 36_750_00), ("2021 Ford F-350", "Vehicles", "03/02/2021", 58_500_00, 39_200_00),
             ("2023 Enclosed trailer", "Vehicles", "06/15/2023", 24_000_00, 6_900_00), ("2019 Skid steer", "Equipment", "05/01/2019", 51_200_00, 9_600_00),
             ("2022 Aerator and seeder", "Equipment", "04/04/2022", 21_900_00, 3_400_00), ("2024 Stand-on mowers (2)", "Equipment", "03/18/2024", 13_300_00, 1_500_00)]
    for a_ in sched: w.writerow([a_[0], a_[1], a_[2], f"{a_[3] / 100:.2f}", f"{a_[4] / 100:.2f}"])
    w.writerow(["Total", "", "", f"{sum(a_[3] for a_ in sched) / 100:.2f}", f"{sum(a_[4] for a_ in sched) / 100:.2f}"])
    assert sum(a_[3] for a_ in sched) == 21_090_000 and sum(a_[4] for a_ in sched) == 9_735_000, (sum(a_[3] for a_ in sched), sum(a_[4] for a_ in sched))
with open(os.path.join(SAMPLE, "ridgeline-depreciation-2026-from-tax-software.csv"), "w", newline="") as f:
    w = csv.writer(f)          # this year's depreciation report, before the bills found in expense accounts are added
    w.writerow(["Asset", "Placed in service", "Disposed", "Cost", "Depreciation 2026"])
    dep26 = [("2017 Ford F-250", "04/10/2017", "06/03/2026", 42_000_00, 2_625_00), ("2021 Ford F-350", "03/02/2021", "", 58_500_00, 5_850_00),
             ("2023 Enclosed trailer", "06/15/2023", "", 24_000_00, 2_400_00), ("2019 Skid steer", "05/01/2019", "", 51_200_00, 5_120_00),
             ("2022 Aerator and seeder", "04/04/2022", "", 21_900_00, 2_190_00), ("2024 Stand-on mowers (2)", "03/18/2024", "", 13_300_00, 1_330_00),
             ("Zero-turn mower, 72 in.", "03/09/2026", "", 14_800_00, 1_850_00), ("2026 F-350 with dump body", "05/20/2026", "", 61_250_00, 3_245_00)]
    for a_ in dep26: w.writerow([a_[0], a_[1], a_[2], f"{a_[3] / 100:.2f}", f"{a_[4] / 100:.2f}"])
    w.writerow(["Total", "", "", "", f"{sum(a_[4] for a_ in dep26) / 100:.2f}"])
    assert sum(a_[4] for a_ in dep26) == 2_461_000

json.dump(KEY, open(os.path.join(HERE, "answer-key.json"), "w"), indent=1, default=str)
print(len(KEY), "cases written")
for c, k in KEY.items(): print(c, k["status"], k.get("exceptions"))
