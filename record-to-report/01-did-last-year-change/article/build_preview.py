#!/usr/bin/env python3
"""Makes PREVIEW.html: the article as a reader would see it, with every image embedded.
Handles the small Markdown subset ARTICLE.md uses. Run: python3 build_preview.py"""
import base64, html, os, re
here = os.path.dirname(os.path.abspath(__file__))
md = open(os.path.join(here, "ARTICLE.md"), encoding="utf-8").read()
md = re.sub(r"<!--.*?-->", "", md, flags=re.S).strip()

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)

def img(alt, src):
    data = base64.b64encode(open(os.path.join(here, src), "rb").read()).decode()
    return f'<figure><img src="data:image/png;base64,{data}" alt="{html.escape(alt)}"></figure>'

out, lines, i = [], md.split("\n"), 0
while i < len(lines):
    ln = lines[i]
    if ln.startswith("````"):
        j = i + 1
        while not lines[j].startswith("````"): j += 1
        out.append("<pre>" + html.escape("\n".join(lines[i + 1:j])) + "</pre>"); i = j + 1; continue
    m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", ln)
    if m: out.append(img(m.group(1), m.group(2)))
    elif ln.startswith("# "): out.append("<h1>" + inline(ln[2:]) + "</h1>")
    elif ln.startswith("## "): out.append("<h2>" + inline(ln[3:]) + "</h2>")
    elif ln.strip() == "---": out.append("<hr>")
    elif ln.strip():
        para = [ln]
        while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"(#|!\[|---|````)", lines[i + 1]): i += 1; para.append(lines[i])
        out.append("<p>" + inline(" ".join(para)) + "</p>")
    i += 1

page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Year That Won’t Stay Closed</title>
<style>
:root{--ink:#14201c;--soft:#56635e;--rule:#d3dbd8;--accent:#15614a;--ground:#f2f5f3;--paper:#fff}
body{margin:0;background:var(--ground);color:var(--ink);font:400 19px/1.65 Inter,"Segoe UI",Arial,sans-serif}
.note{max-width:760px;margin:0 auto;padding:12px max(16px,4vw);font-size:14px;color:var(--soft)}
main{max-width:760px;margin:0 auto 60px;background:var(--paper);padding:40px max(16px,4vw) 60px}
h1{font:700 40px/1.12 "Inter Display",Inter,sans-serif;letter-spacing:-.015em;margin:28px 0 18px}
h2{font:700 26px/1.25 "Inter Display",Inter,sans-serif;margin:44px 0 10px}
p{margin:0 0 18px}
a{color:var(--accent)}
figure{margin:26px 0}
figure img{display:block;width:100%;height:auto;border:1px solid var(--rule);border-radius:4px}
main>figure:first-of-type{margin-top:0}
hr{border:0;border-top:1px solid var(--rule);margin:44px 0}
pre{white-space:pre-wrap;font:13px/1.5 "JetBrains Mono",Consolas,monospace;background:var(--ground);padding:16px;border-radius:6px;overflow-x:auto}
code{font-family:"JetBrains Mono",Consolas,monospace;font-size:.9em}
</style></head><body>
<p class="note">Draft for approval, not published. On LinkedIn the cover image sits above the headline.</p>
<main>""" + "\n".join(out) + "</main></body></html>"
# cover above the headline, as LinkedIn shows it
h1 = page.index("<h1>"); fig = page.index("<figure>", h1); end = page.index("</figure>", fig) + 9
cover = page[fig:end]; page = page[:fig] + page[end:]; page = page[:h1] + cover + page[h1:]
open(os.path.join(here, "PREVIEW.html"), "w", encoding="utf-8").write(page)
print("PREVIEW.html", len(page) // 1024, "KB")
