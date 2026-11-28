"""The rules of "Why won't the bank rec tie?", version 1, as plain Python over the model. make_cases.py
uses them to work out the answer key. Money is integer cents, positive = money into the account.

Inputs: the bank's lines (date, description, check number or None, amount) with the bank's beginning
and ending balances when known; the books' lines for the account (date, type, num, name, memo, amount)
with the account's opening balance at the start of the books file.

0. The account. If the books' file has several accounts, the bank account is the first whose name
   contains "checking", else "operating", else "bank", else "savings", "money market" or "cash"
   (never "undeposited", "petty" or "clearing"); the accountant can choose another.
   A file that does not add up (the bank's running balance jumps, or a ledger account does not add up
   to its own totals) stops the review: only that message is shown.
1. Span. The bank span is the first to the last bank line date. Book lines dated after the span's
   last day are set aside ("after the statement").
2. Matching, one bank line to one book line unless said otherwise, bank lines taken in date order
   (ties: file order):
   a. Checks by number: a money-out bank line with a check number (its own column, or "check",
      "chk" or "ck" followed by 3 to 6 digits in the description) matches the unused book line with
      the same number (leading zeros ignored) and the same amount. Same number, different amount:
      a "check amount differs" pair; neither is matched.
   b. Same amount: the unused book line with exactly the same amount dated from 60 days before to
      5 days after the bank line; the nearest date wins, then the earlier book line.
   c. Batches: a money-in bank line still unmatched, and 2 to 6 unused money-in book lines dated from
      5 days before to 1 day after it whose amounts add up to it exactly. Only the 12 nearest such
      book lines are tried, in date order, as sets in binary-counter order; the first set that adds
      up wins.
3. Near misses, among what is left (each line used once; these do not match, they explain):
   a. Transposed: same direction, dates at most 10 days apart, the amounts differ, the difference is
      a multiple of 9 cents, and both amounts have the same digits in another order.
   b. Sign: the book amount is minus the bank amount, dates at most 10 days apart.
   c. Duplicate in the books: an unmatched book line with the same amount and the same name (not
      blank) as a matched book line dated at most 5 days apart.
4. Before the bank lines. O = (books' balance on the day before the bank span starts) - (bank's
   beginning balance) is what was outstanding then. Of it, the book lines dated before the span that
   were matched (or paired as a near miss) inside the span account for some. The rest, R = O - their sum, must be book lines
   dated before the span that are still unmatched (still outstanding at the end). Electronic payments
   and deposits clear within days, so only checks (a number of 3 to 6 digits) and lines dated in the
   10 days before the span can still be open; every other unmatched old line cleared before the bank
   file starts. Among the possible ones (if there are 20 or fewer, in date order) find the first set,
   in binary-counter order, that adds up to R; the rest cleared before the bank file starts. If there are no such book lines,
   look instead among the unmatched bank lines in the first 45 days of the span for a set adding up
   to R: those cleared items the books recorded before the books file starts. If no set adds up,
   or the bank's beginning balance is unknown, every unmatched old book line is taken as cleared
   before the bank file starts, and the difference shows what is unexplained.
5. Outstanding at the end: unmatched book lines dated in the span, plus the old ones from step 4
   (not near misses or duplicates). Checks and payments (money out) and deposits in transit (money
   in), each with its age in days at the span's end. Bank only: unmatched bank lines (less step 4's,
   not near misses).
6. The proof. Adjusted bank = bank ending balance + all outstanding (signed). Adjusted books = books'
   balance at the span's end + all bank-only lines (signed) + for each near miss (bank amount - book
   amount) - each duplicate's amount. Difference = adjusted bank - adjusted books; zero means it ties.
7. Old items: a check or payment outstanding more than 180 days is stale (a bank need not pay a check
   over six months old, UCC 4-404; an uncashed check is unclaimed property, so it is reversed to a
   liability, not income); more than 90 days is old. A deposit in transit more than 10 days old is
   flagged.
8. The bank file adds up: with a balance column, each line's balance = the one before + its amount
   (in date order), and beginning + lines = ending.
"""
from datetime import date, timedelta
import re

CHECK_RE = re.compile(r"\b(?:check|chk|ck)\s*#?\s*(\d{3,6})\b", re.I)

def norm_num(s):
    s = str(s or "").strip()
    return s.lstrip("0") if s.isdigit() else s

def check_no(b):
    if b.get("check"): return norm_num(b["check"])
    m = CHECK_RE.search(b.get("desc", ""))
    return norm_num(m.group(1)) if m else None

def digits_perm(a, b):
    return sorted(str(abs(a))) == sorted(str(abs(b)))

def subsets_binary(items, target, minn=1, maxn=None, limit=20):
    """The first set, counting k = 1, 2, 3 ... where the set holds item i when bit i of k is 1."""
    items = items[:limit]; am = [x["amount"] for x in items]; n = len(items)
    for k in range(1, 1 << n):
        c = bin(k).count("1")
        if c < minn or (maxn and c > maxn): continue
        t = 0; j = 0; kk = k
        while kk:
            if kk & 1: t += am[j]
            kk >>= 1; j += 1
        if t == target: return [items[i] for i in range(n) if k >> i & 1]
    return None

def reconcile(bank, books, opening, bank_begin=None, bank_end=None):
    """bank, books: lists of dicts in file order (each gets 'i'). Returns the answer-key dict."""
    for i, b in enumerate(bank): b["i"] = i
    for i, k in enumerate(books): k["i"] = i
    start = min(b["date"] for b in bank); end = max(b["date"] for b in bank)
    after = [k for k in books if k["date"] > end]
    bk = [k for k in books if k["date"] <= end]
    used = set(); match = {}          # bank i -> list of book i
    order = sorted(bank, key=lambda b: (b["date"], b["i"]))
    near = []
    # a. checks by number
    for b in order:
        if b["amount"] >= 0: continue
        n = check_no(b)
        if not n: continue
        same = [k for k in bk if k["i"] not in used and norm_num(k["num"]) == n]
        hit = next((k for k in same if k["amount"] == b["amount"]), None)
        if hit: used.add(hit["i"]); match[b["i"]] = [hit["i"]]
        elif same:
            k = same[0]; used.add(k["i"]); near.append({"kind": "check amount differs", "bank": b["i"], "book": k["i"]})
    nb = {x["bank"] for x in near}
    # b. same amount
    for b in order:
        if b["i"] in match or b["i"] in nb: continue
        cands = [k for k in bk if k["i"] not in used and k["amount"] == b["amount"] and -60 <= (k["date"] - b["date"]).days <= 5]
        if cands:
            k = min(cands, key=lambda k: (abs((k["date"] - b["date"]).days), k["i"]))
            used.add(k["i"]); match[b["i"]] = [k["i"]]
    # c. batches
    for b in order:
        if b["i"] in match or b["i"] in nb or b["amount"] <= 0: continue
        cands = [k for k in bk if k["i"] not in used and k["amount"] > 0 and -5 <= (k["date"] - b["date"]).days <= 1]
        cands = sorted(cands, key=lambda k: (abs((k["date"] - b["date"]).days), k["i"]))[:12]
        cands = sorted(cands, key=lambda k: (k["date"], k["i"]))
        sub = subsets_binary(cands, b["amount"], minn=2, maxn=6, limit=12)
        if sub:
            for k in sub: used.add(k["i"])
            match[b["i"]] = [k["i"] for k in sub]
    # 3. near misses
    ub = [b for b in order if b["i"] not in match and b["i"] not in nb]
    for b in ub:
        cands = [k for k in bk if k["i"] not in used and abs((k["date"] - b["date"]).days) <= 10 and k["amount"] != b["amount"]
                 and (k["amount"] > 0) == (b["amount"] > 0) and (k["amount"] - b["amount"]) % 9 == 0 and digits_perm(k["amount"], b["amount"])]
        if cands:
            k = min(cands, key=lambda k: (abs((k["date"] - b["date"]).days), k["i"])); used.add(k["i"]); nb.add(b["i"])
            near.append({"kind": "transposed", "bank": b["i"], "book": k["i"]}); continue
        cands = [k for k in bk if k["i"] not in used and k["amount"] == -b["amount"] and abs((k["date"] - b["date"]).days) <= 10]
        if cands:
            k = min(cands, key=lambda k: (abs((k["date"] - b["date"]).days), k["i"])); used.add(k["i"]); nb.add(b["i"])
            near.append({"kind": "sign", "bank": b["i"], "book": k["i"]})
    matched_books = {i for v in match.values() for i in v}
    dups = []
    for k in bk:
        if k["i"] in used or not k["name"]: continue
        twin = next((m for m in bk if m["i"] in matched_books and m["amount"] == k["amount"] and m["name"].lower() == k["name"].lower()
                     and abs((m["date"] - k["date"]).days) <= 5), None)
        if twin: used.add(k["i"]); dups.append({"book": k["i"], "twin": twin["i"]})
    # 4. before the bank lines
    pre_bal = opening + sum(k["amount"] for k in bk if k["date"] < start)
    old_unmatched = sorted([k for k in bk if k["date"] < start and k["i"] not in used], key=lambda k: (k["date"], k["i"]))
    paired = matched_books | {n["book"] for n in near}       # cleared inside the span (exactly, or with a near miss)
    old_matched = sum(k["amount"] for k in bk if k["date"] < start and k["i"] in paired)
    cleared_before, from_before = [], []
    still_old = list(old_unmatched)
    start_explained = None
    if bank_begin is not None:
        O = pre_bal - bank_begin; R = O - old_matched
        if old_unmatched:
            can = [k for k in old_unmatched if re.fullmatch(r"\d{3,6}", str(k["num"] or "").strip()) or (start - k["date"]).days <= 10]
            if R == 0: sub = []
            elif len(can) <= 20: sub = subsets_binary(can, R, limit=20)
            else: sub = None
            if sub is not None:
                ids = {k["i"] for k in sub}
                cleared_before = [k for k in old_unmatched if k["i"] not in ids]; still_old = sub; start_explained = True
            else:
                start_explained = False; cleared_before = list(old_unmatched)
        else:
            early = sorted([b for b in ub if b["i"] not in nb and (b["date"] - start).days <= 45], key=lambda b: (b["date"], b["i"]))
            sub = [] if R == 0 else subsets_binary(early, R, limit=20)
            if sub is not None: from_before = sub; start_explained = True
            else: start_explained = False
    if bank_begin is None: cleared_before = list(old_unmatched)
    fb = {b["i"] for b in from_before}; cb = {k["i"] for k in cleared_before}
    near_books = {n["book"] for n in near}; near_bank = {n["bank"] for n in near}
    # 5. outstanding and bank only
    outstanding = [k for k in bk if k["i"] not in matched_books and k["i"] not in cb and k["i"] not in near_books and not any(d["book"] == k["i"] for d in dups)]
    bank_only = [b for b in bank if b["i"] not in match and b["i"] not in fb and b["i"] not in near_bank]
    BI = {b["i"]: b for b in bank}; KI = {k["i"]: k for k in books}
    corrections = sum(BI[n["bank"]]["amount"] - KI[n["book"]]["amount"] for n in near) - sum(KI[d["book"]]["amount"] for d in dups)
    book_end = opening + sum(k["amount"] for k in bk)
    if bank_end is None and bank_begin is not None: bank_end = bank_begin + sum(b["amount"] for b in bank)
    adj_bank = bank_end + sum(k["amount"] for k in outstanding) if bank_end is not None else None
    adj_book = book_end + sum(b["amount"] for b in bank_only) + corrections
    def age(k): return (end - k["date"]).days
    stale = [k for k in outstanding if k["amount"] < 0 and age(k) > 180]
    old = [k for k in outstanding if k["amount"] < 0 and 90 < age(k) <= 180]
    old_dit = [k for k in outstanding if k["amount"] > 0 and age(k) > 10]
    return {"start": start, "end": end, "match": match, "near": near, "dups": dups, "outstanding": outstanding, "bank_only": bank_only,
            "cleared_before": cleared_before, "from_before": from_before, "after": after, "book_end": book_end, "bank_end": bank_end,
            "adj_bank": adj_bank, "adj_book": adj_book, "start_explained": start_explained, "stale": stale, "old": old, "old_dit": old_dit,
            "pre_bal": pre_bal, "corrections": corrections}
