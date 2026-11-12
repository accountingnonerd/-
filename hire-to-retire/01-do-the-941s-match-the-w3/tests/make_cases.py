#!/usr/bin/env python3
"""
Builds the acceptance-test files and the answer key for "Do the 941s match the W-3?"
(Hire-to-Retire, episode 01).

HOW THE ANSWER KEY STAYS INDEPENDENT OF THE TOOL
-------------------------------------------------
Each case starts from a small staff list (invented people, invented employers). Python works
out every paycheck-quarter: wages, 401(k) deferrals, tips, the social security wage base,
Additional Medicare Tax, federal withholding, and the employee and employer FICA rounded per
person per quarter. From those it computes each 941 line and each W-3 box the way a payroll
provider would. Errors are then planted on purpose, field by field, and written down.

The key records what the tool should report: the four quarters' figures it should read,
the W-3 boxes, the differences, and which exceptions it must raise. All of it comes from the
data model below, never from reading the PDFs back, and nothing here is shared with the
tool (which is JavaScript in one HTML file).

The PDFs are written four ways, because that is how they reach an accountant:
  fillable  - the official IRS PDF with its form fields filled in (values live in the fields)
  printed   - the official IRS page with the values printed onto it and the fields removed
  provider  - a payroll provider's own "filed copy" layout, drawn from scratch
  scan      - a picture of a printed form, with no text at all
Official blank forms are in ./forms (IRS forms are public). All names and EINs are invented.

Run:  python3 make_cases.py      (needs pypdf, reportlab, pdftocairo)
"""
import copy, io, json, os, subprocess, tempfile
from decimal import Decimal as D, ROUND_HALF_UP
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

HERE = os.path.dirname(os.path.abspath(__file__))
FORMS = os.path.join(HERE, "forms")
CASES = os.path.join(HERE, "cases")
os.makedirs(CASES, exist_ok=True)
for f in os.listdir(CASES):
    os.remove(os.path.join(CASES, f))

C = D("0.01")
def r2(x): return D(x).quantize(C, rounding=ROUND_HALF_UP)
def money(x): return float(r2(x))
SS_BASE = {2025: D(176100), 2026: D(184500)}
ADDL_THRESHOLD = D(200000)

# =====================================================================================
# 1. The payroll model
# =====================================================================================
def payroll_year(staff, year=2026):
    """staff: list of dicts {name, pay:[q1,q2,q3,q4] gross wages, k401:[..], tips:[..], fit_rate}
    Returns per-quarter 941 lines and the W-3 boxes."""
    base = SS_BASE[year]
    q = [dict(emps=0, l2=D(0), l3=D(0), ss_w=D(0), ss_t=D(0), med=D(0), addl_w=D(0),
              emp_ss=D(0), emp_med=D(0), emp_addl=D(0), unc=D(0), tp_fit=D(0), tp_fica=D(0)) for _ in range(4)]
    w3 = dict(b1=D(0), b2=D(0), b3=D(0), b4=D(0), b5=D(0), b6=D(0), b7=D(0), b14=D(0), c=0)
    for e in staff:
        cum_ss = D(0); cum_med = D(0); paid = False
        e_b = dict(b1=D(0), b2=D(0), b3=D(0), b4=D(0), b5=D(0), b6=D(0), b7=D(0))
        for i in range(4):
            gross = r2(D(str(e["pay"][i]))); k = r2(D(str(e.get("k401", [0] * 4)[i]))); tips = r2(D(str(e.get("tips", [0] * 4)[i])))
            if gross == 0 and tips == 0:
                continue
            paid = True
            tp = e.get("third_party", {}).get(i)          # (income tax withheld by the insurer, sick pay wages)
            sick = r2(D(str(tp[1]))) if tp else D(0)
            gross += sick
            box1 = gross + tips - k
            fit = r2((box1 - sick) * D(str(e["fit_rate"])))  # withheld by the employer; the insurer withholds on the sick pay
            room = max(D(0), base - cum_ss)
            ss_w = min(gross, room); ss_t = min(tips, max(D(0), room - ss_w))
            cum_ss += ss_w + ss_t
            med = gross + tips
            over_before = max(D(0), cum_med - ADDL_THRESHOLD)
            cum_med += med
            over_after = max(D(0), cum_med - ADDL_THRESHOLD)
            addl_w = over_after - over_before
            emp_ss = r2((ss_w + ss_t) * D("0.062")); emp_med = r2(med * D("0.0145")); emp_addl = r2(addl_w * D("0.009"))
            # uncollected employee tax on tips (941 line 9; W-2 box 12 codes A and B; not in boxes 4 and 6)
            unc_ss, unc_med = [D(str(x)) for x in e.get("uncollected", {}).get(i, (0, 0))]
            emp_ss -= unc_ss; emp_med -= unc_med
            # third-party sick pay: the insurer withholds income tax and the employee's FICA (941 line 8; W-3 box 14)
            tp_fit = r2(D(str(tp[0]))) if tp else D(0)
            tp_fica = (r2(sick * D("0.062")) + r2(sick * D("0.0145"))) if tp else D(0)   # employee FICA the insurer withheld (in boxes 4 and 6)
            Q = q[i]
            Q["emps"] += 1; Q["l2"] += box1; Q["l3"] += fit; Q["ss_w"] += ss_w; Q["ss_t"] += ss_t; Q["med"] += med
            Q["addl_w"] += addl_w; Q["emp_ss"] += emp_ss; Q["emp_med"] += emp_med; Q["emp_addl"] += emp_addl
            Q["unc"] += unc_ss + unc_med; Q["tp_fit"] += tp_fit; Q["tp_fica"] += tp_fica

            w3["b14"] += tp_fit
            e_b["b1"] += box1; e_b["b2"] += fit + tp_fit; e_b["b3"] += ss_w; e_b["b7"] += ss_t; e_b["b4"] += emp_ss
            e_b["b5"] += med; e_b["b6"] += emp_med + emp_addl
        if paid:
            w3["c"] += 1
            for k_ in e_b: w3[k_] += e_b[k_]
    quarters = []
    for i, Q in enumerate(q):
        L = {}
        L["1"] = Q["emps"]; L["2"] = Q["l2"]; L["3"] = Q["l3"]
        L["5a1"] = Q["ss_w"]; L["5a2"] = r2(Q["ss_w"] * D("0.124"))
        L["5b1"] = Q["ss_t"]; L["5b2"] = r2(Q["ss_t"] * D("0.124"))
        L["5c1"] = Q["med"]; L["5c2"] = r2(Q["med"] * D("0.029"))
        L["5d1"] = Q["addl_w"]; L["5d2"] = r2(Q["addl_w"] * D("0.009"))
        L["5e"] = L["5a2"] + L["5b2"] + L["5c2"] + L["5d2"]; L["5f"] = D(0)
        L["6"] = L["3"] + L["5e"] + L["5f"]
        L["9"] = -Q["unc"]                                               # uncollected employee tax on tips
        L["8"] = -Q["tp_fica"]                                           # employee FICA withheld by the third-party payer
        # Line 7, as the 941 instructions describe it: the employer's share is the rate times the
        # quarter's totals; the employee's share is what was actually withheld, paycheck by paycheck.
        employer = r2((Q["ss_w"] + Q["ss_t"]) * D("0.062")) + r2(Q["med"] * D("0.0145"))
        employee = Q["emp_ss"] + Q["emp_med"] + Q["emp_addl"] + Q["unc"]   # all employee FICA owed, incl. the insurer's part
        L["7"] = (employer + employee) - L["5e"]                         # fractions of cents
        L["10"] = L["6"] + L["7"] + L["8"] + L["9"]; L["11"] = D(0); L["12"] = L["10"] - L["11"]
        L["13"] = L["12"]; L["14"] = D(0)
        quarters.append(L)
    return quarters, w3


AMOUNT_LINES = ["2", "3", "5a1", "5a2", "5b1", "5b2", "5c1", "5c2", "5d1", "5d2", "5e", "5f", "6", "7", "8", "9", "10", "11", "12", "13", "14"]
RECON = [("b1", "2"), ("b2", "3"), ("b3", "5a1"), ("b5", "5c1"), ("b7", "5b1")]   # box 2 is compared net of box 14

# =====================================================================================
# 2. Writers
# =====================================================================================
F941 = {"ein1": "f1_1[0]", "ein2": "f1_2[0]", "name": "f1_3[0]", "1": "f1_12[0]",
        "2": ("f1_13[0]", "f1_14[0]"), "3": ("f1_15[0]", "f1_16[0]"),
        "5a1": ("f1_17[0]", "f1_18[0]"), "5a2": ("f1_19[0]", "f1_20[0]"), "5b1": ("f1_21[0]", "f1_22[0]"), "5b2": ("f1_23[0]", "f1_24[0]"),
        "5c1": ("f1_25[0]", "f1_26[0]"), "5c2": ("f1_27[0]", "f1_28[0]"), "5d1": ("f1_29[0]", "f1_30[0]"), "5d2": ("f1_31[0]", "f1_32[0]"),
        "5e": ("f1_33[0]", "f1_34[0]"), "5f": ("f1_35[0]", "f1_36[0]"), "6": ("f1_37[0]", "f1_38[0]"), "7": ("f1_39[0]", "f1_40[0]"),
        "8": ("f1_41[0]", "f1_42[0]"), "9": ("f1_43[0]", "f1_44[0]"), "10": ("f1_45[0]", "f1_46[0]"), "11": ("f1_47[0]", "f1_48[0]"),
        "12": ("f1_49[0]", "f1_50[0]"), "13": ("f1_51[0]", "f1_52[0]"), "14": ("f1_53[0]", "f1_54[0]")}
FW3 = {"c": "f1_02[0]", "ein": "f1_04[0]", "name": "f1_05[0]", "addr": "f1_06[0]", "h": "f1_07[0]",
       "b1": "f1_08[0]", "b2": "f1_09[0]", "b3": "f1_10[0]", "b4": "f1_11[0]", "b5": "f1_12[0]", "b6": "f1_13[0]", "b7": "f1_14[0]"}


def split_amount(v, commas):
    v = r2(v); neg = v < 0; v = abs(v)
    dollars = int(v); cents = int((v - dollars) * 100)
    ds = f"{dollars:,}" if commas else str(dollars)
    return ("-" if neg else "") + ds, f"{cents:02d}"


def widgets(page):
    out = {}
    for a in page.get("/Annots", []) or []:
        a = a.get_object()
        if a.get("/Subtype") != "/Widget": continue
        t = a.get("/T") or (a.get("/Parent") and a["/Parent"].get_object().get("/T"))
        out.setdefault(str(t), []).append(a)
    return out


def set_text(w, name, value):
    a = w[name][0]
    target = a if a.get("/T") is not None else a["/Parent"].get_object()
    target[NameObject("/V")] = TextStringObject(value)


def set_check(w, name, index=0):
    a = w[name][index]
    on = [k for k in a["/AP"]["/N"].keys() if k != "/Off"][0]
    a[NameObject("/AS")] = NameObject(on)
    target = a if a.get("/T") is not None else a["/Parent"].get_object()
    target[NameObject("/V")] = NameObject(on)


def fill_941_fields(template, L, ein, name, quarter, commas=False):
    r = PdfReader(os.path.join(FORMS, template)); wr = PdfWriter(clone_from=r)
    w = widgets(wr.pages[0])
    a, b = ein.split("-")
    set_text(w, F941["ein1"], a); set_text(w, F941["ein2"], b); set_text(w, F941["name"], name)
    set_text(w, F941["1"], str(L["1"]))
    for k in AMOUNT_LINES:
        if k in L and L[k] != 0:
            d_, c_ = split_amount(L[k], commas)
            set_text(w, F941[k][0], d_); set_text(w, F941[k][1], c_)
    set_check(w, f"c1_1[{quarter - 1}]")
    wr.set_need_appearances_writer(True)
    return wr


def overlay_page(template, page_index, draws):
    """Print text onto an official blank page and drop its form fields (a 'printed' copy)."""
    r = PdfReader(os.path.join(FORMS, template))
    page = r.pages[page_index]
    buf = io.BytesIO(); cv = canvas.Canvas(buf, pagesize=(float(page.mediabox.width), float(page.mediabox.height)))
    for x, y, text, align, size in draws:
        cv.setFont("Helvetica", size)
        (cv.drawRightString if align == "r" else cv.drawString)(x, y, text)
    cv.save(); buf.seek(0)
    page.merge_page(PdfReader(buf).pages[0])
    if "/Annots" in page: del page[NameObject("/Annots")]
    return page


def rects(template, page_index):
    r = PdfReader(os.path.join(FORMS, template)); out = {}
    for name, ws in widgets(r.pages[page_index]).items():
        out[name] = [[float(v) for v in a["/Rect"]] for a in ws]
    return out


def printed_941(template, L, ein, name, quarter):
    R = rects(template, 0); draws = []
    def put(fname, text, align="l", idx=0):
        x0, y0, x1, y1 = R[fname][idx]
        draws.append(((x1 - 3) if align == "r" else (x0 + 2), y0 + 3.5, text, align, 9))
    a, b = ein.split("-"); put(F941["ein1"], a); put(F941["ein2"], b); put(F941["name"], name)
    put(F941["1"], str(L["1"]), "r")
    for k in AMOUNT_LINES:
        if k in L and L[k] != 0:
            d_, c_ = split_amount(L[k], True); put(F941[k][0], d_, "r"); put(F941[k][1], c_)
    x0, y0, x1, y1 = R["c1_1[%d]" % (quarter - 1)][0]
    draws.append((x0 + 1.5, y0 + 1.5, "X", "l", 9))
    return [overlay_page(template, 0, draws), PdfReader(os.path.join(FORMS, template)).pages[1], PdfReader(os.path.join(FORMS, template)).pages[2]]


def fill_w3_fields(W, ein, name, other_ein="", year=2026, commas=False):
    r = PdfReader(os.path.join(FORMS, "fw3-%d.pdf" % year)); wr = PdfWriter(clone_from=r)
    w = widgets(wr.pages[1])
    set_text(w, FW3["c"], str(W["c"])); set_text(w, FW3["ein"], ein); set_text(w, FW3["name"], name)
    if other_ein: set_text(w, FW3["h"], other_ein)
    for b in ["b1", "b2", "b3", "b4", "b5", "b6", "b7"]:
        if W[b] != 0:
            v = r2(W[b]); set_text(w, FW3[b], f"{v:,.2f}" if commas else f"{v:.2f}")
    set_check(w, "c1_1[0]", 0)
    wr.set_need_appearances_writer(True)
    return wr


def printed_w3(W, ein, name, other_ein="", year=2026):
    tpl = "fw3-%d.pdf" % year; R = rects(tpl, 1); draws = []
    def put(fname, text, align="l"):
        x0, y0, x1, y1 = R[fname][0]
        draws.append(((x1 - 4) if align == "r" else (x0 + 3), y0 + 2.5, text, align, 9))
    put(FW3["c"], str(W["c"])); put(FW3["ein"], ein); put(FW3["name"], name)
    if other_ein: put(FW3["h"], other_ein)
    for b in ["b1", "b2", "b3", "b4", "b5", "b6", "b7"]:
        if W[b] != 0: put(FW3[b], f"{r2(W[b]):,.2f}", "r")
    x0, y0, x1, y1 = R["c1_1[0]"][0]
    draws.append((x0 + 1.5, y0 + 1.5, "X", "l", 9))
    return [overlay_page(tpl, 1, draws)]


LABELS = [("1", "Number of employees who received wages, tips, or other compensation"),
          ("2", "Wages, tips, and other compensation"),
          ("3", "Federal income tax withheld from wages, tips, and other compensation"),
          ("5a", "Taxable social security wages"), ("5b", "Taxable social security tips"),
          ("5c", "Taxable Medicare wages & tips"), ("5d", "Taxable wages & tips subject to Additional Medicare Tax withholding"),
          ("5e", "Total social security and Medicare taxes"), ("5f", "Section 3121(q) Notice and Demand"),
          ("6", "Total taxes before adjustments"), ("7", "Current quarter's adjustment for fractions of cents"),
          ("8", "Current quarter's adjustment for sick pay"), ("9", "Current quarter's adjustments for tips and group-term life insurance"),
          ("10", "Total taxes after adjustments"), ("11", "Qualified small business payroll tax credit for increasing research activities"),
          ("12", "Total taxes after adjustments and nonrefundable credits"), ("13", "Total deposits for this quarter"),
          ("14", "Balance due")]
QNAMES = {1: "January, February, March", 2: "April, May, June", 3: "July, August, September", 4: "October, November, December"}


def provider_941(L, ein, name, quarter, year=2026, provider="Ledgerline Payroll"):
    """A payroll provider's own 'filed copy' layout: same IRS line wording, different page."""
    buf = io.BytesIO(); cv = canvas.Canvas(buf, pagesize=letter)
    y = 742
    cv.setFont("Helvetica-Bold", 14); cv.drawString(48, y, f"Form 941 for {year}: Employer's QUARTERLY Federal Tax Return"); y -= 18
    cv.setFont("Helvetica", 9); cv.drawString(48, y, f"Filed copy for your records. Prepared and e-filed by {provider}."); y -= 26
    cv.setFont("Helvetica", 10)
    for lab, val in [("Employer identification number (EIN):", ein), ("Name:", name), ("Report for this Quarter:", f"Quarter {quarter} ({QNAMES[quarter]}) {year}")]:
        cv.drawString(48, y, lab); cv.drawString(250, y, val); y -= 15
    y -= 12
    cv.setFont("Helvetica-Bold", 10); cv.drawString(48, y, "Part 1"); cv.drawRightString(430, y, "Column 1"); cv.drawRightString(560, y, "Column 2"); y -= 18
    cv.setFont("Helvetica", 9)
    fmt = lambda v: f"{r2(v):,.2f}"
    for lid, lab in LABELS:
        cv.drawString(48, y, lid); cv.drawString(72, y, lab)
        if lid in ("5a", "5b", "5c", "5d"):
            cv.drawRightString(430, y, fmt(L[lid + "1"])); cv.drawRightString(560, y, fmt(L[lid + "2"]))
        elif lid == "1":
            cv.drawRightString(560, y, str(L["1"]))
        else:
            cv.drawRightString(560, y, fmt(L.get(lid, D(0))))
        y -= 17
    cv.setFont("Helvetica", 8); cv.drawString(48, 60, f"{provider} · Accepted by the IRS · Copy for employer records")
    cv.save(); buf.seek(0)
    return PdfReader(buf).pages


def provider_w3(W, ein, name, year=2026, provider="Ledgerline Payroll", other_ein=""):
    buf = io.BytesIO(); cv = canvas.Canvas(buf, pagesize=letter)
    y = 742
    cv.setFont("Helvetica-Bold", 14); cv.drawString(48, y, f"Form W-3 Transmittal of Wage and Tax Statements {year}"); y -= 18
    cv.setFont("Helvetica", 9); cv.drawString(48, y, f"Employer copy. Prepared and filed with the SSA by {provider}."); y -= 28
    cv.setFont("Helvetica", 10)
    rows = [("c Total number of Forms W-2", str(W["c"])), ("e Employer identification number (EIN)", ein), ("f Employer's name", name),
            ("h Other EIN used this year", other_ein),
            ("1 Wages, tips, other compensation", W["b1"]), ("2 Federal income tax withheld", W["b2"]),
            ("3 Social security wages", W["b3"]), ("4 Social security tax withheld", W["b4"]),
            ("5 Medicare wages and tips", W["b5"]), ("6 Medicare tax withheld", W["b6"]), ("7 Social security tips", W["b7"])]
    for lab, v in rows:
        cv.drawString(48, y, lab)
        cv.drawRightString(560, y, v if isinstance(v, str) else f"{r2(v):,.2f}")
        y -= 17
    cv.save(); buf.seek(0)
    return PdfReader(buf).pages


def scan_of(pages):
    """Render pages to images and wrap each image in a PDF page: no text, no fields."""
    out = []
    with tempfile.TemporaryDirectory() as td:
        wr = PdfWriter()
        for p in pages: wr.add_page(p)
        src = os.path.join(td, "src.pdf"); wr.write(src)
        subprocess.run(["pdftocairo", "-png", "-r", "110", src, os.path.join(td, "img")], check=True)
        for fn in sorted(f for f in os.listdir(td) if f.endswith(".png")):
            buf = io.BytesIO(); cv = canvas.Canvas(buf, pagesize=letter)
            cv.drawImage(os.path.join(td, fn), 0, 0, width=612, height=792); cv.save(); buf.seek(0)
            out.append(PdfReader(buf).pages[0])
    return out


def write_pages(fname, pages):
    wr = PdfWriter()
    for p in pages: wr.add_page(p)
    with open(os.path.join(CASES, fname), "wb") as f: wr.write(f)


def write_writer(fname, wr):
    with open(os.path.join(CASES, fname), "wb") as f: wr.write(f)


def pages_of(wr):
    b = io.BytesIO(); wr.write(b); b.seek(0); return list(PdfReader(b).pages)

# =====================================================================================
# 3. The answer key
# =====================================================================================
KEY = {}


def key_for(cid, title, kind, files, year, quarters_read, w3=None, ein=None, exceptions=(), status=None,
            fatal=None, notes="", dup_quarter=None):
    """quarters_read: {q: lines} exactly as printed on the forms the tool should use."""
    k = dict(title=title, kind=kind, files=files, notes=notes)
    if fatal:
        k["fatal"] = fatal; KEY[cid] = k; return
    k.update(year=year, ein=ein, exceptions=sorted(set(exceptions)), quartersFound=sorted(quarters_read))
    k["quarters"] = {str(qn): {ln: money(v) for ln, v in L.items() if ln in ("2", "3", "5a1", "5a2", "5b1", "5b2", "5c1", "5c2", "5d1", "5d2", "5e", "7", "8", "9")}
                     for qn, L in quarters_read.items()}
    if w3 is not None and dup_quarter is None:
        rows = {}
        for b, ln in RECON:
            tot = sum((quarters_read[qn][ln] for qn in quarters_read), D(0))
            w = w3[b] - (w3.get("b14", D(0)) if b == "b2" else 0)
            rows[b] = dict(line=ln, total941=money(tot), w3=money(w), diff=money(w - tot), agrees=r2(w - tot) == 0)
        # Line 8 stays out: the insurer's withholding of the employee's FICA is in W-3 boxes 4 and 6 but taken off the 941 on line 8.
        # Line 9 stays in: uncollected employee tax on tips is in neither W-3 box 4 nor box 6.
        tax941 = sum((quarters_read[qn]["5e"] + quarters_read[qn]["7"] + quarters_read[qn]["9"] for qn in quarters_read), D(0))
        expect = w3["b4"] + w3["b6"] + r2((w3["b3"] + w3["b7"]) * D("0.062")) + r2(w3["b5"] * D("0.0145"))
        tol = D("1.00") + D("0.02") * w3["c"]
        rows["tax"] = dict(total941=money(tax941), w3=money(expect), diff=money(expect - tax941), agrees=abs(expect - tax941) <= tol)
        k["recon"] = rows
        k["w3"] = {b: money(w3[b]) for b in ["b1", "b2", "b3", "b4", "b5", "b6", "b7"]}
    else:
        k["recon"] = None
    k["status"] = status
    KEY[cid] = k

# =====================================================================================
# 4. The cases
# =====================================================================================
def staff_office():
    return [dict(name="A", pay=[18000, 18000, 18000, 18000], k401=[900] * 4, fit_rate="0.12"),
            dict(name="B", pay=[14250, 14250, 14250, 15750], k401=[0] * 4, fit_rate="0.10"),
            dict(name="C", pay=[11400.5, 11400.5, 11400.5, 11400.5], k401=[570.03] * 4, fit_rate="0.09"),
            dict(name="D", pay=[0, 6200, 9300, 9300], fit_rate="0.08"),
            dict(name="E", pay=[8333.33, 8333.33, 8333.34, 0], fit_rate="0.11")]


def staff_restaurant():
    s = []
    for i, (p, t) in enumerate([(9100, 6450.25), (8800, 5980.4), (8650, 6120.15), (9900, 0), (7400.5, 4310.6), (6350, 3990.35), (12500, 0)]):
        s.append(dict(name=f"R{i}", pay=[p, round(p * 1.05, 2), round(p * 1.1, 2), p], tips=[t, round(t * 1.08, 2), round(t * 1.15, 2), round(t * 1.2, 2)], fit_rate="0.07"))
    s[1]["uncollected"] = {3: (85.10, 19.90)}
    return s


def staff_firm():  # one partner over the wage base and over $200,000
    return [dict(name="P", pay=[78000, 78000, 78000, 92000], k401=[6125] * 4, fit_rate="0.24"),
            dict(name="Q", pay=[24500.17, 24500.17, 24500.17, 24500.17], k401=[1225.01] * 4, fit_rate="0.15"),
            dict(name="S", pay=[13333.33, 13333.33, 13333.34, 13333.33], fit_rate="0.11"),
            dict(name="T", pay=[9750.55, 9750.55, 9750.55, 9750.55], fit_rate="0.09")]


year = 2026
# ---- 01 clean, four separate fillable IRS 941s and a fillable W-3
qs, w3 = payroll_year(staff_office()); EIN, NAME = "84-2716053", "Brightwater Dental Group LLC"
for i in range(4): write_writer(f"01-q{i+1}-941.pdf", fill_941_fields("f941-2026.pdf", qs[i], EIN, NAME, i + 1))
write_writer("01-w3.pdf", fill_w3_fields(w3, EIN, NAME))
key_for("01", "Clean year: four filled-in IRS 941s and a W-3", "clean",
        [f"01-q{i}-941.pdf" for i in range(1, 5)] + ["01-w3.pdf"], year, {i + 1: qs[i] for i in range(4)}, w3, EIN, status="AGREES")

# ---- 02 restaurant with tips, one combined year-end packet, printed copies, extra pages
qs, w3 = payroll_year(staff_restaurant()); EIN, NAME = "47-1903382", "Calle Ocho Kitchen Inc"
pages = []
for i in range(4): pages += printed_941("f941-2026.pdf", qs[i], EIN, NAME, i + 1)
pages += [PdfReader(os.path.join(FORMS, "fw3-2026.pdf")).pages[0]] + printed_w3(w3, EIN, NAME)
write_pages("02-year-end-packet.pdf", pages)
key_for("02", "Year-end packet, printed copies, tips, uncollected tip tax, extra pages to ignore", "ugly", ["02-year-end-packet.pdf"],
        year, {i + 1: qs[i] for i in range(4)}, w3, EIN, exceptions=["UNCOLLECTED_TAX"], status="AGREES")

# ---- 03 a firm with one partner over the wage base and over $200,000: Additional Medicare, fractions of cents
qs, w3 = payroll_year(staff_firm()); EIN, NAME = "61-5520147", "Okafor & Lindqvist CPAs PLLC"
for i in range(4): write_writer(f"03-q{i+1}-941.pdf", fill_941_fields("f941-2026.pdf", qs[i], EIN, NAME, i + 1, commas=True))
write_writer("03-w3.pdf", fill_w3_fields(w3, EIN, NAME, commas=True))
assert any(q["7"] != 0 for q in qs) and qs[3]["5d1"] > 0, "case 03 must exercise lines 5d and 7"
key_for("03", "Wage base, Additional Medicare Tax and fractions of cents: must still agree", "rules",
        [f"03-q{i}-941.pdf" for i in range(1, 5)] + ["03-w3.pdf"], year, {i + 1: qs[i] for i in range(4)}, w3, EIN, status="AGREES")

# ---- 04 PLANTED: provider switch. Q1-Q2 old provider (IRS forms), Q3-Q4 new provider (its own layout).
#      The new provider's W-3 only covers the wages it paid.
staff = staff_office(); qs, w3_full = payroll_year(staff); EIN, NAME = "36-7741209", "Harbor Freight Forwarding LLC"
h2 = [dict(s, pay=[0, 0] + s["pay"][2:], k401=[0, 0] + s.get("k401", [0] * 4)[2:]) for s in staff]
_, w3_h2 = payroll_year(h2)
for i in range(2): write_writer(f"04-q{i+1}-941-old-provider.pdf", fill_941_fields("f941-2026.pdf", qs[i], EIN, NAME, i + 1))
for i in range(2, 4): write_pages(f"04-q{i+1}-941-ledgerline.pdf", provider_941(qs[i], EIN, NAME, i + 1))
write_pages("04-w3-ledgerline.pdf", provider_w3(w3_h2, EIN, NAME))
key_for("04", "PLANTED: switched providers mid-year; the new W-3 leaves out January to June", "planted",
        ["04-q1-941-old-provider.pdf", "04-q2-941-old-provider.pdf", "04-q3-941-ledgerline.pdf", "04-q4-941-ledgerline.pdf", "04-w3-ledgerline.pdf"],
        year, {i + 1: qs[i] for i in range(4)}, w3_h2, EIN, exceptions=["MISMATCH"], status="DOES_NOT_AGREE",
        notes="Every wage difference equals Q1 + Q2 exactly; the tool should say so and ask for the old provider's W-3.")
KEY["04"]["patternQuarters"] = [1, 2]

# ---- 05 two different Forms 941 for the second quarter
qs, w3 = payroll_year(staff_office()); EIN, NAME = "36-7741209", "Harbor Freight Forwarding LLC"
q2b = dict(qs[1]); q2b["2"] = qs[1]["2"] - D("6200.00"); q2b["5a1"] = qs[1]["5a1"] - D("6200.00"); q2b["5c1"] = qs[1]["5c1"] - D("6200.00")
q2b["5a2"] = r2(q2b["5a1"] * D("0.124")); q2b["5c2"] = r2(q2b["5c1"] * D("0.029")); q2b["5e"] = q2b["5a2"] + q2b["5b2"] + q2b["5c2"] + q2b["5d2"]
q2b["3"] = qs[1]["3"] - D("496.00"); q2b["6"] = q2b["3"] + q2b["5e"]; q2b["10"] = q2b["6"] + q2b["7"]; q2b["12"] = q2b["10"]; q2b["13"] = q2b["12"]
for i in range(4): write_writer(f"05-q{i+1}-941.pdf", fill_941_fields("f941-2026.pdf", qs[i], EIN, NAME, i + 1))
write_pages("05-q2-941-second-copy.pdf", provider_941(q2b, EIN, NAME, 2))
write_writer("05-w3.pdf", fill_w3_fields(w3, EIN, NAME))
key_for("05", "Two different 941s for the second quarter: must refuse to pick one", "ugly",
        [f"05-q{i}-941.pdf" for i in range(1, 5)] + ["05-q2-941-second-copy.pdf", "05-w3.pdf"], year,
        {1: qs[0], 2: qs[1], 3: qs[2], 4: qs[3]}, w3, EIN, exceptions=["DUPLICATE_QUARTER"], status="NOT_RECONCILED", dup_quarter=2)
KEY["05"]["dupQuarter"] = 2

# ---- 06 the fourth quarter is missing
qs, w3 = payroll_year(staff_office()); EIN, NAME = "84-2716053", "Brightwater Dental Group LLC"
for i in range(3): write_writer(f"06-q{i+1}-941.pdf", fill_941_fields("f941-2026.pdf", qs[i], EIN, NAME, i + 1))
write_writer("06-w3.pdf", fill_w3_fields(w3, EIN, NAME))
key_for("06", "Only three quarters dropped in: must say the fourth is missing", "ugly",
        [f"06-q{i}-941.pdf" for i in range(1, 4)] + ["06-w3.pdf"], year, {i + 1: qs[i] for i in range(3)}, w3, EIN,
        exceptions=["MISSING_QUARTER", "MISMATCH"], status="INCOMPLETE")

# ---- 07 PLANTED: arithmetic error inside the Q3 941 (line 5c column 2 typed wrong, carried into 5e)
qs, w3 = payroll_year(staff_restaurant()); EIN, NAME = "47-1903382", "Calle Ocho Kitchen Inc"
bad = dict(qs[2]); bad["5c2"] = qs[2]["5c2"] + D("90.00"); bad["5e"] = bad["5a2"] + bad["5b2"] + bad["5c2"] + bad["5d2"]
bad["6"] = bad["3"] + bad["5e"]; bad["10"] = bad["6"] + bad["7"]; bad["12"] = bad["10"]; bad["13"] = bad["12"]
quarters_printed = [qs[0], qs[1], bad, qs[3]]
for i in range(4): write_writer(f"07-q{i+1}-941.pdf", fill_941_fields("f941-2026.pdf", quarters_printed[i], EIN, NAME, i + 1))
write_writer("07-w3.pdf", fill_w3_fields(w3, EIN, NAME))
key_for("07", "PLANTED: a third-quarter 941 whose Medicare tax is not 2.9% of its wages", "planted",
        [f"07-q{i}-941.pdf" for i in range(1, 5)] + ["07-w3.pdf"], year, {i + 1: quarters_printed[i] for i in range(4)}, w3, EIN,
        exceptions=["ARITHMETIC", "MISMATCH", "UNCOLLECTED_TAX"], status="DOES_NOT_AGREE")
KEY["07"]["arithmeticQuarter"] = 3

# ---- 08 PLANTED: W-3 box 3 digits transposed
qs, w3 = payroll_year(staff_firm()); EIN, NAME = "61-5520147", "Okafor & Lindqvist CPAs PLLC"
w3_bad = dict(w3); s = f"{r2(w3['b3']):.2f}"; t = s[0] + s[2] + s[1] + s[3:]; w3_bad["b3"] = D(t)
assert w3_bad["b3"] != w3["b3"]
pages = []
for i in range(4): pages += printed_941("f941-2026.pdf", qs[i], EIN, NAME, i + 1)[:1]
write_pages("08-941s-2026.pdf", pages)
write_pages("08-w3.pdf", printed_w3(w3_bad, EIN, NAME))
key_for("08", "PLANTED: two digits swapped in W-3 box 3", "planted", ["08-941s-2026.pdf", "08-w3.pdf"], year,
        {i + 1: qs[i] for i in range(4)}, w3_bad, EIN, exceptions=["MISMATCH", "W3_INTERNAL"], status="DOES_NOT_AGREE")

# ---- 09 the second quarter is a scan
qs, w3 = payroll_year(staff_office()); EIN, NAME = "84-2716053", "Brightwater Dental Group LLC"
for i in (0, 2, 3): write_writer(f"09-q{i+1}-941.pdf", fill_941_fields("f941-2026.pdf", qs[i], EIN, NAME, i + 1))
write_pages("09-q2-941-scanned.pdf", scan_of(printed_941("f941-2026.pdf", qs[1], EIN, NAME, 2)[:1]))
write_writer("09-w3.pdf", fill_w3_fields(w3, EIN, NAME))
key_for("09", "The second quarter is a scan with no text: must say it cannot read it", "ugly",
        ["09-q1-941.pdf", "09-q2-941-scanned.pdf", "09-q3-941.pdf", "09-q4-941.pdf", "09-w3.pdf"], year,
        {1: qs[0], 3: qs[2], 4: qs[3]}, w3, EIN, exceptions=["SCANNED", "MISSING_QUARTER", "MISMATCH"], status="INCOMPLETE")

# ---- 10 last year's fourth quarter dropped in by mistake
qs, w3 = payroll_year(staff_office()); EIN, NAME = "84-2716053", "Brightwater Dental Group LLC"
qs25, _ = payroll_year(staff_office(), year=2025)
for i in range(3): write_writer(f"10-q{i+1}-941.pdf", fill_941_fields("f941-2026.pdf", qs[i], EIN, NAME, i + 1))
write_pages("10-q4-941.pdf", provider_941(qs25[3], EIN, NAME, 4, year=2025))
write_writer("10-w3.pdf", fill_w3_fields(w3, EIN, NAME))
key_for("10", "A 2025 fourth quarter instead of 2026: must leave it out and say why", "ugly",
        [f"10-q{i}-941.pdf" for i in range(1, 5)] + ["10-w3.pdf"], year, {i + 1: qs[i] for i in range(3)}, w3, EIN,
        exceptions=["WRONG_YEAR", "MISSING_QUARTER", "MISMATCH"], status="INCOMPLETE")

# ---- 11 one quarter filed under another EIN, and W-3 box h left blank
qs, w3 = payroll_year(staff_office()); EIN, NAME = "84-2716053", "Brightwater Dental Group LLC"
OLD = "84-0039417"
write_writer("11-q1-941.pdf", fill_941_fields("f941-2026.pdf", qs[0], OLD, "Brightwater Dental PC", 1))
for i in range(1, 4): write_writer(f"11-q{i+1}-941.pdf", fill_941_fields("f941-2026.pdf", qs[i], EIN, NAME, i + 1))
write_writer("11-w3.pdf", fill_w3_fields(w3, EIN, NAME))
key_for("11", "First quarter filed under an old EIN; W-3 box h is blank", "rules",
        [f"11-q{i}-941.pdf" for i in range(1, 5)] + ["11-w3.pdf"], year, {i + 1: qs[i] for i in range(4)}, w3, EIN,
        exceptions=["EIN_MISMATCH"], status="DOES_NOT_AGREE",
        notes="The totals agree only when both EINs are combined. The IRS matches by EIN, so this draws a letter unless box h shows the other EIN.")

# ---- 12 a filled-in 941-X correcting the 2026 second quarter (a $2,500 bonus left off); the W-3 includes it
qs, w3 = payroll_year(staff_office()); EIN, NAME = "36-7741209", "Harbor Freight Forwarding LLC"
bonus = D("2500.00"); fitb = r2(bonus * D("0.22"))
w3x = dict(w3); w3x["b1"] += bonus; w3x["b2"] += fitb; w3x["b3"] += bonus; w3x["b5"] += bonus
w3x["b4"] += r2(bonus * D("0.062")); w3x["b6"] += r2(bonus * D("0.0145"))
for i in range(4): write_writer(f"12-q{i+1}-941.pdf", fill_941_fields("f941-2026.pdf", qs[i], EIN, NAME, i + 1))
xr = PdfReader(os.path.join(FORMS, "f941x.pdf")); xw = PdfWriter(clone_from=xr)
w1 = widgets(xw.pages[0]); w2 = widgets(xw.pages[1])
set_text(w1, "f1_1[0]", EIN.split("-")[0]); set_text(w1, "f1_2[0]", EIN.split("-")[1]); set_text(w1, "f1_3[0]", NAME); set_text(w1, "f1_12[0]", "2026")
set_text(w2, "f2_1[0]", "2")
if "f1_12[0]" in w2: set_text(w2, "f1_12[0]", "2026")
X941 = {"2": ["f2_2[0]", "f2_3[0]", "f2_4[0]", "f2_5[0]", "f2_6[0]", "f2_7[0]", None, None],
        "3": ["f2_8[0]", "f2_9[0]", "f2_10[0]", "f2_11[0]", "f2_12[0]", "f2_13[0]", "f2_14[0]", "f2_15[0]"],
        "5a": ["f2_16[0]", "f2_17[0]", "f2_18[0]", "f2_19[0]", "f2_20[0]", "f2_21[0]", "f2_22[0]", "f2_23[0]"],
        "5c": ["f2_48[0]", "f2_49[0]", "f2_50[0]", "f2_51[0]", "f2_52[0]", "f2_53[0]", "f2_54[0]", "f2_55[0]"]}
orig = qs[1]
for ln, corr, was, tax in [("2", orig["2"] + bonus, orig["2"], None), ("3", orig["3"] + fitb, orig["3"], fitb),
                           ("5a", orig["5a1"] + bonus, orig["5a1"], r2(bonus * D("0.124"))), ("5c", orig["5c1"] + bonus, orig["5c1"], r2(bonus * D("0.029")))]:
    f = X941[ln]
    for (fd, fc), v in [((f[0], f[1]), corr), ((f[2], f[3]), was), ((f[4], f[5]), corr - was)] + ([((f[6], f[7]), tax)] if tax is not None else []):
        d_, c_ = split_amount(v, True); set_text(w2, fd, d_); set_text(w2, fc, c_)
xw.set_need_appearances_writer(True)
write_writer("12-q2-941-x.pdf", xw)
write_writer("12-w3.pdf", fill_w3_fields(w3x, EIN, NAME))
q2x = dict(qs[1]); q2x["2"] += bonus; q2x["3"] += fitb; q2x["5a1"] += bonus; q2x["5c1"] += bonus
q2x["5a2"] += r2(bonus * D("0.124")); q2x["5c2"] += r2(bonus * D("0.029")); q2x["5e"] += r2(bonus * D("0.124")) + r2(bonus * D("0.029"))
key_for("12", "A filled-in 2026 941-X for the second quarter: must add it in, and then agree", "rules",
        [f"12-q{i}-941.pdf" for i in range(1, 5)] + ["12-q2-941-x.pdf", "12-w3.pdf"], year, {1: qs[0], 2: q2x, 3: qs[2], 4: qs[3]}, w3x, EIN,
        exceptions=["AMENDED_INCLUDED"], status="AGREES")

# ---- 13 an annual Form 944 filer: out of scope
write_pages("13-form-944.pdf", PdfReader(os.path.join(FORMS, "f944.pdf")).pages[:2])
key_for("13", "A Form 944 (annual filer): must say this tool is for quarterly 941 filers", "planted", ["13-form-944.pdf"], None, None,
        fatal="FORM_944")

# ---- 14 not payroll forms at all
buf = io.BytesIO(); cv = canvas.Canvas(buf, pagesize=letter); cv.setFont("Helvetica", 11)
for i, line in enumerate(["First Coastal Bank", "Business Checking Statement", "Account ending 4410", "Statement period: December 1 - December 31, 2026",
                          "Beginning balance 48,210.55", "Deposits 31,904.12", "Withdrawals 29,440.80", "Ending balance 50,673.87"]):
    cv.drawString(60, 730 - i * 18, line)
cv.save(); buf.seek(0); write_pages("14-bank-statement.pdf", PdfReader(buf).pages)
key_for("14", "A bank statement, not payroll forms: must refuse", "planted", ["14-bank-statement.pdf"], None, None, fatal="NO_FORMS")

# ---- 15 four 941s and no W-3
qs, w3 = payroll_year(staff_office()); EIN, NAME = "84-2716053", "Brightwater Dental Group LLC"
for i in range(4): write_writer(f"15-q{i+1}-941.pdf", fill_941_fields("f941-2026.pdf", qs[i], EIN, NAME, i + 1))
key_for("15", "Four 941s but no W-3: must total the 941s and say there is nothing to compare", "ugly",
        [f"15-q{i}-941.pdf" for i in range(1, 5)], year, {i + 1: qs[i] for i in range(4)}, None, EIN,
        exceptions=["NO_W3"], status="NOT_RECONCILED")

# ---- 16 the provider switch again, this time with both providers' W-3s: must add them and agree
staff = staff_office(); qs, w3_full = payroll_year(staff); EIN, NAME = "36-7741209", "Harbor Freight Forwarding LLC"
h1 = [dict(s, pay=s["pay"][:2] + [0, 0], k401=s.get("k401", [0] * 4)[:2] + [0, 0]) for s in staff]
h2 = [dict(s, pay=[0, 0] + s["pay"][2:], k401=[0, 0] + s.get("k401", [0] * 4)[2:]) for s in staff]
_, w3_h1 = payroll_year(h1); _, w3_h2 = payroll_year(h2)
for i in range(2): write_writer(f"16-q{i+1}-941-old-provider.pdf", fill_941_fields("f941-2026.pdf", qs[i], EIN, NAME, i + 1))
for i in range(2, 4): write_pages(f"16-q{i+1}-941-ledgerline.pdf", provider_941(qs[i], EIN, NAME, i + 1))
write_writer("16-w3-old-provider.pdf", fill_w3_fields(w3_h1, EIN, NAME))
write_pages("16-w3-ledgerline.pdf", provider_w3(w3_h2, EIN, NAME))
w3_sum = {b: w3_h1[b] + w3_h2[b] for b in w3_h1}
key_for("16", "Provider switch with both providers' W-3s: must add them together and agree", "ugly",
        ["16-q1-941-old-provider.pdf", "16-q2-941-old-provider.pdf", "16-q3-941-ledgerline.pdf", "16-q4-941-ledgerline.pdf", "16-w3-old-provider.pdf", "16-w3-ledgerline.pdf"],
        year, {i + 1: qs[i] for i in range(4)}, w3_sum, EIN, exceptions=["W3_ADDED"], status="AGREES")

# ---- 17 third-party sick pay: box 2 includes the insurer's withholding (box 14); line 3 does not
staff = staff_firm(); staff[2]["third_party"] = {1: (640.00, 4200.00)}
qs, w3 = payroll_year(staff); EIN, NAME = "61-5520147", "Okafor & Lindqvist CPAs PLLC"
assert w3["b14"] > 0 and qs[1]["8"] != 0
for i in range(4): write_writer(f"17-q{i+1}-941.pdf", fill_941_fields("f941-2026.pdf", qs[i], EIN, NAME, i + 1, commas=True))
w3w = fill_w3_fields(w3, EIN, NAME, commas=True); set_text(widgets(w3w.pages[1]), "f1_22[0]", f"{r2(w3['b14']):,.2f}")
write_writer("17-w3.pdf", w3w)
key_for("17", "Third-party sick pay: W-3 box 2 less box 14 must agree with line 3", "rules",
        [f"17-q{i}-941.pdf" for i in range(1, 5)] + ["17-w3.pdf"], year, {i + 1: qs[i] for i in range(4)}, w3, EIN,
        exceptions=["THIRD_PARTY_SICK_PAY"], status="AGREES")

with open(os.path.join(HERE, "answer-key.json"), "w") as f:
    json.dump(KEY, f, indent=1)
print("wrote", len(KEY), "cases,", len(os.listdir(CASES)), "files")
