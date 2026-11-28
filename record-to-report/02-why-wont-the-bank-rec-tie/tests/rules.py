"""The rules of "Why won't the bank rec tie?", version 2 (after the CPA review and the first-time-user
review), as plain Python over the files' lines. make_cases.py uses them to work out the answer key.
Money is integer cents, positive = money into the account. "Old" means dated before the bank span.

0. Files and account.
   - The bank account in the books: the first account whose name contains "checking", else
     "operating", else "bank", else "savings", "money market" or "cash" (never "undeposited", "petty",
     "clearing"); the accountant can choose another. The account includes its sub-accounts.
   - An account whose name says credit card, card, visa, mastercard, amex, american express,
     discover, loan or line of credit is not reconciled by this version (stop).
   - Bank lines marked pending are left out. A bank file whose running balance does not follow its
     lines (checked day by day), a dated bank line with an amount that cannot be read, or a ledger
     account that does not add up stops the review: only that message is shown.
   - Book lines of zero (voided) are left out, except to explain a check the bank paid.
1. Dates. The bank span starts on the first bank line's date. It ends on the statement end date: the
   date in the file's "ending balance as of" line, else the one typed, else the last bank line's date.
   Book lines dated after the end are set aside.
2. Matching, bank lines in date order (ties: file order); one bank line to one book line unless said:
   a. Checks by number: a money-out bank line with a check number (its own column, or "check",
      "chk" or "ck" and 3 to 6 digits in the description) matches the unused money-out book line with
      the same number (leading zeros ignored) and the same amount. Same number, different amount:
      "check amount differs". Same number, book amount zero: "voided but paid". A second bank line
      for a check number already matched: "paid twice". None of these match.
   b. Same amount: the unused book line with exactly the same amount, from 60 days before (180 for a
      book check, one with a number of 3 to 6 digits) to 5 days after the bank line, and never an old
      non-check line dated more than 10 days before the span. A bank check with a number never
      matches a book check with another number. The nearest date wins, then the earlier book line.
   c. Several to one: a bank line still unmatched, and 2 to 6 unused book lines in the same direction
      dated from 5 days before to 1 day after it, adding up to it exactly (card batches, deposits of
      several checks, a batch of payments). Only the 12 nearest such book lines are tried, in date
      order, as sets in binary-counter order; the first set that adds up wins.
   d. One to several: a book line still unmatched, and 2 to 6 unmatched bank lines in the same
      direction dated from 1 day before to 5 days after it, adding up to it exactly (a deposit the
      bank split). Same search.
3. Near misses, among what is left (none of these match; each waits for the accountant):
   a. Transposed: same direction, dates at most 10 days apart, different amounts, the difference a
      multiple of 9 cents, the same digits in another order.
   b. Sign: the book amount is minus the bank amount, dates at most 10 days apart.
   c. Entered twice: an unmatched book line dated in the span with the same amount and the same name
      (not blank) as a matched book line dated in the span, at most 5 days apart.
   Undecided, a near miss counts as two separate items (outstanding and bank-only) and an entered-
   twice line as outstanding. Decided "same, books wrong": the book side is corrected by (bank amount
   - book amount), or by minus the duplicate. Decided "bank error" (check amount differs, paid twice,
   voided but paid): the bank side is corrected instead.
4. Before the bank span. R = (books' balance the day before the span) - (bank's beginning balance)
   - (old book lines matched or paired inside the span). R is what old book lines still outstanding
   must add up to. Only checks (a number of 3 to 6 digits, money out) and lines dated in the 10 days
   before the span can still be open; the other old lines cleared before the bank file starts.
   - R = 0: none is still outstanding. Their sum = R: all are.
   - Else, with 20 or fewer, the sets that add up to R (binary-counter order): exactly one, it is
     the one; two or more, ambiguous; none, not explained. More than 20: too many to search.
   - Ambiguous or too many: the accountant ticks the ones still outstanding (none until she does).
   - No old candidate lines at all (the books file starts with the bank span): the unmatched bank
     lines in the first 45 days whose set adds up to R are suggested as "recorded before the books
     file starts"; they count only when she ticks them.
   - Bank beginning balance unknown: nothing is still outstanding, and the proof cannot be made.
5. Outstanding at the end: unmatched book lines dated in the span (not near misses, not entered
   twice, not zero), plus the old ones from step 4, plus undecided near misses and duplicates. Bank
   only: unmatched bank lines (less ticked step 4 lines), plus undecided near misses. Kinds: fee
   (money out, the description says service charge, monthly fee, maintenance fee, account fee,
   wire fee, overdraft, analysis fee, atm fee or the word fee), interest (money in, the word
   interest), returned item (NSF, returned item, return item, chargeback, but not a fee), other.
6. The proof. Adjusted bank = bank ending balance + outstanding + bank-side corrections. Adjusted
   books = books' balance at the end date + bank-only + book-side corrections. Difference = adjusted
   bank - adjusted books. A stale check (step 7) the accountant reverses (decision o{i} = "reverse")
   stays listed with its decision, but leaves the outstanding total and adds its amount to the
   book-side corrections: the reversing entry puts it back in the books.
7. Age at the end date. A check outstanding more than 180 days is stale-dated (UCC 4-404); more than
   90 days, old. A non-check payment or a deposit not at the bank after 10 days is flagged. A stale
   check waits for the accountant: keep it outstanding or reverse it to a liability. It does not
   stop the tie.
"""
from datetime import date, timedelta
import re

CHECK_RE = re.compile(r"\b(?:check|chk|ck)\s*#?\s*(\d{3,6})\b", re.I)
FEE_RE = re.compile(r"service charge|monthly (?:service |maintenance )?fee|maintenance fee|account fee|wire (?:transfer )?fee|overdraft|analysis fee|atm fee|\bfee\b", re.I)
RET_RE = re.compile(r"\bnsf\b|returned item|return item|chargeback", re.I)

def norm_num(s):
    s = str(s or "").strip()
    return s.lstrip("0") if s.isdigit() else s
def is_check_num(s): return bool(re.fullmatch(r"\d{3,6}", str(s or "").strip()))
def check_no(b):
    if b.get("check"): return norm_num(b["check"])
    m = CHECK_RE.search(b.get("desc", ""))
    return norm_num(m.group(1)) if m else None
def digits_perm(a, b): return sorted(str(abs(a))) == sorted(str(abs(b)))
def bank_kind(b):
    if b["amount"] > 0 and re.search(r"\binterest\b", b["desc"], re.I) and not re.search(r"charge", b["desc"], re.I): return "interest"
    if RET_RE.search(b["desc"]) and not re.search(r"\bfee\b", b["desc"], re.I): return "returned"
    if b["amount"] < 0 and FEE_RE.search(b["desc"]): return "fee"
    return "other"

def sets_adding(items, target, minn=1, maxn=None, stop_at=1):
    """The sets of items adding up to target, in binary-counter order (set k holds item i when bit i of k is 1)."""
    am = [x["amount"] for x in items]; n = len(items); found = []
    for k in range(1, 1 << n):
        c = bin(k).count("1")
        if c < minn or (maxn and c > maxn): continue
        t = 0; j = 0; kk = k
        while kk:
            if kk & 1: t += am[j]
            kk >>= 1; j += 1
        if t == target:
            found.append([items[i] for i in range(n) if k >> i & 1])
            if len(found) >= stop_at: break
    return found

def reconcile(bank, books, opening, bank_begin=None, bank_end=None, stmt_end=None, decide=None, ticks=None):
    """bank, books: lists of dicts in file order. decide: {id: choice}; ticks: set of ('book'|'bank', index)."""
    decide = decide or {}; ticks = ticks or set()
    for i, b in enumerate(bank): b["i"] = i
    for i, k in enumerate(books): k["i"] = i
    start = min(b["date"] for b in bank)
    end = stmt_end or max(b["date"] for b in bank)
    after = [k for k in books if k["date"] > end]
    bk = [k for k in books if k["date"] <= end and k["amount"] != 0]
    zero = [k for k in books if k["date"] <= end and k["amount"] == 0]
    used = set(); match = {}; near = []; nb = set()
    order = sorted(bank, key=lambda b: (b["date"], b["i"]))
    dd = lambda k, b: (k["date"] - b["date"]).days
    done_checks = {}
    # a. checks by number
    for b in order:
        if b["amount"] >= 0: continue
        n = check_no(b)
        if not n: continue
        same = [k for k in bk if k["i"] not in used and k["amount"] < 0 and norm_num(k["num"]) == n]
        hit = next((k for k in same if k["amount"] == b["amount"]), None)
        if hit: used.add(hit["i"]); match[b["i"]] = [hit["i"]]; done_checks[n] = b["i"]
        elif same:
            k = same[0]; used.add(k["i"]); nb.add(b["i"]); near.append({"kind": "check amount differs", "bank": b["i"], "book": k["i"]}); done_checks[n] = b["i"]
        else:
            z = next((k for k in zero if norm_num(k["num"]) == n and ("z", k["i"]) not in used), None)
            if z: used.add(("z", z["i"])); nb.add(b["i"]); near.append({"kind": "voided but paid", "bank": b["i"], "book": None, "zero": z["i"]}); done_checks[n] = b["i"]
            elif n in done_checks: nb.add(b["i"]); near.append({"kind": "paid twice", "bank": b["i"], "book": None})
    # b. same amount
    for b in order:
        if b["i"] in match or b["i"] in nb: continue
        bn = check_no(b) if b["amount"] < 0 else None
        def ok(k):
            if k["i"] in used or k["amount"] != b["amount"]: return False
            ischk = is_check_num(k["num"]) and k["amount"] < 0
            lo = -180 if ischk else -60
            if not (lo <= dd(k, b) <= 5): return False
            if not ischk and (start - k["date"]).days > 10: return False
            if bn and ischk and norm_num(k["num"]) != bn: return False
            return True
        cands = [k for k in bk if ok(k)]
        if cands:
            k = min(cands, key=lambda k: (abs(dd(k, b)), k["i"])); used.add(k["i"]); match[b["i"]] = [k["i"]]
    # c. several book lines to one bank line
    for b in order:
        if b["i"] in match or b["i"] in nb: continue
        cands = [k for k in bk if k["i"] not in used and (k["amount"] > 0) == (b["amount"] > 0) and -5 <= dd(k, b) <= 1]
        cands = sorted(sorted(cands, key=lambda k: (abs(dd(k, b)), k["i"]))[:12], key=lambda k: (k["date"], k["i"]))
        s = sets_adding(cands, b["amount"], 2, 6)
        if s:
            for k in s[0]: used.add(k["i"])
            match[b["i"]] = [k["i"] for k in s[0]]
    # d. one book line to several bank lines
    split = {}
    for k in sorted(bk, key=lambda k: (k["date"], k["i"])):
        if k["i"] in used: continue
        cands = [b for b in order if b["i"] not in match and b["i"] not in nb and b["i"] not in split and (b["amount"] > 0) == (k["amount"] > 0) and -1 <= (b["date"] - k["date"]).days <= 5]
        cands = sorted(sorted(cands, key=lambda b: (abs((b["date"] - k["date"]).days), b["i"]))[:12], key=lambda b: (b["date"], b["i"]))
        s = sets_adding(cands, k["amount"], 2, 6)
        if s:
            used.add(k["i"])
            for b in s[0]: split[b["i"]] = k["i"]
    # 3. near misses
    ub = [b for b in order if b["i"] not in match and b["i"] not in nb and b["i"] not in split]
    for b in ub:
        c = [k for k in bk if k["i"] not in used and abs(dd(k, b)) <= 10 and k["amount"] != b["amount"] and (k["amount"] > 0) == (b["amount"] > 0)
             and (k["amount"] - b["amount"]) % 9 == 0 and digits_perm(k["amount"], b["amount"])]
        if c:
            k = min(c, key=lambda k: (abs(dd(k, b)), k["i"])); used.add(k["i"]); nb.add(b["i"]); near.append({"kind": "transposed", "bank": b["i"], "book": k["i"]}); continue
        c = [k for k in bk if k["i"] not in used and k["amount"] == -b["amount"] and abs(dd(k, b)) <= 10]
        if c:
            k = min(c, key=lambda k: (abs(dd(k, b)), k["i"])); used.add(k["i"]); nb.add(b["i"]); near.append({"kind": "sign", "bank": b["i"], "book": k["i"]})
    ub = [b for b in ub if b["i"] not in nb]
    matched_books = {i for v in match.values() for i in v} | set(split.values())
    dups = []
    for k in bk:
        if k["i"] in used or not k["name"] or k["date"] < start: continue
        twin = next((m for m in bk if m["i"] in matched_books and m["date"] >= start and m["amount"] == k["amount"] and m["name"].lower() == k["name"].lower()
                     and abs((m["date"] - k["date"]).days) <= 5), None)
        if twin: used.add(k["i"]); dups.append({"book": k["i"], "twin": twin["i"]})
    for j, n in enumerate(near): n["id"] = f"n{j}"; n["decision"] = decide.get(n["id"], "undecided")
    for j, d in enumerate(dups): d["id"] = f"u{j}"; d["decision"] = decide.get(d["id"], "undecided")
    # 4. before the bank span
    pre_bal = opening + sum(k["amount"] for k in bk if k["date"] < start)
    paired = matched_books | {n["book"] for n in near if n["book"] is not None}
    old_un = sorted([k for k in bk if k["date"] < start and k["i"] not in used], key=lambda k: (k["date"], k["i"]))
    old_paired = sum(k["amount"] for k in bk if k["date"] < start and k["i"] in paired)
    can = [k for k in old_un if (is_check_num(k["num"]) and k["amount"] < 0) or (start - k["date"]).days <= 10]
    still, suggest_bank, mode, R = [], [], None, None
    if bank_begin is not None:
        R = pre_bal - bank_begin - old_paired
        if can:
            if R == 0: mode = "none"
            elif sum(k["amount"] for k in can) == R: mode = "all"; still = list(can)
            elif len(can) <= 20:
                sets = sets_adding(can, R, stop_at=2)
                if len(sets) == 1: mode = "unique"; still = sets[0]
                elif len(sets) >= 2: mode = "ambiguous"
                else: mode = "not explained"
            else: mode = "too many"
            if mode in ("ambiguous", "too many"): still = [k for k in can if ("book", k["i"]) in ticks]
        else:
            if R == 0: mode = "none"
            else:
                early = sorted([b for b in ub if (b["date"] - start).days <= 45], key=lambda b: (b["date"], b["i"]))[:20]
                sets = sets_adding(early, R, stop_at=1)
                mode = "bank lines" if sets else "not explained"
                suggest_bank = sets[0] if sets else []
    else: mode = "unknown"
    still_ids = {k["i"] for k in still}
    ticked_bank = {b["i"] for b in suggest_bank if ("bank", b["i"]) in ticks}
    left = None if R is None else R - sum(k["amount"] for k in still) - sum(b["amount"] for b in suggest_bank if b["i"] in ticked_bank)
    # 5. outstanding and bank only
    near_books = {n["book"] for n in near if n["book"] is not None}; near_bank = {n["bank"] for n in near}
    dup_books = {d["book"] for d in dups}
    outstanding = [k for k in bk if k["i"] not in matched_books and k["i"] not in near_books and k["i"] not in dup_books and (k["date"] >= start or k["i"] in still_ids)]
    bank_only = [b for b in bank if b["i"] not in match and b["i"] not in split and b["i"] not in near_bank and b["i"] not in ticked_bank]
    BI = {b["i"]: b for b in bank}; KI = {k["i"]: k for k in books}
    book_corr = bank_corr = 0
    for n in near:
        b = BI[n["bank"]]; k = KI[n["book"]] if n["book"] is not None else None
        if n["decision"] == "fix": book_corr += b["amount"] - (k["amount"] if k else 0)
        elif n["decision"] == "bank": bank_corr += (k["amount"] if k else 0) - b["amount"]
        else:
            bank_only.append(b)
            if k: outstanding.append(k)
    for d in dups:
        if d["decision"] == "fix": book_corr -= KI[d["book"]]["amount"]
        else: outstanding.append(KI[d["book"]])
    # a stale check the accountant reverses: the entry puts it back in the books, so it leaves the outstanding list in the proof
    reversed_ = {k["i"] for k in outstanding if is_check_num(k["num"]) and k["amount"] < 0 and (end - k["date"]).days > 180 and decide.get(f"o{k['i']}") == "reverse"}
    book_corr -= sum(k["amount"] for k in outstanding if k["i"] in reversed_)
    outstanding.sort(key=lambda k: (k["date"], k["i"])); bank_only.sort(key=lambda b: (b["date"], b["i"]))
    book_end = opening + sum(k["amount"] for k in bk)
    if bank_end is None and bank_begin is not None: bank_end = bank_begin + sum(b["amount"] for b in bank)
    adj_bank = None if bank_end is None else bank_end + sum(k["amount"] for k in outstanding if k["i"] not in reversed_) + bank_corr
    adj_book = book_end + sum(b["amount"] for b in bank_only) + book_corr
    def age(k): return (end - k["date"]).days
    def is_chk(k): return is_check_num(k["num"]) and k["amount"] < 0
    stale = [k for k in outstanding if is_chk(k) and age(k) > 180]
    old = [k for k in outstanding if is_chk(k) and 90 < age(k) <= 180]
    late = [k for k in outstanding if not is_chk(k) and age(k) > 10]
    return {"start": start, "end": end, "match": match, "split": split, "near": near, "dups": dups, "outstanding": outstanding, "bank_only": bank_only,
            "after": after, "book_end": book_end, "bank_end": bank_end, "adj_bank": adj_bank, "adj_book": adj_book, "mode": mode, "R": R,
            "can": can, "still": still, "suggest_bank": suggest_bank, "left": left, "stale": stale, "old": old, "late": late,
            "book_corr": book_corr, "bank_corr": bank_corr, "pre_bal": pre_bal, "cleared_before": [k for k in old_un if k["i"] not in still_ids]}
