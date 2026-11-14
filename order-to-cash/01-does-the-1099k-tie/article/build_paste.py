#!/usr/bin/env python3
"""Makes NEWSLETTER-PASTE.html: the article as rich text for a LinkedIn newsletter edition, with a
marker where each image goes. Open it in a browser, use the Copy button, paste into LinkedIn.
Run: python3 build_paste.py"""
import html, os, re
here = os.path.dirname(os.path.abspath(__file__))
md = re.sub(r"<!--.*?-->", "", open(os.path.join(here, "ARTICLE.md"), encoding="utf-8").read(), flags=re.S).strip()
md = md.split("\n", 1)[1]  # the headline goes in LinkedIn's own title field

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)

out, lines, i, n = [], md.split("\n"), 0, 0
while i < len(lines):
    ln = lines[i]
    if ln.startswith("````"):
        j = i + 1
        while not lines[j].startswith("````"): j += 1
        out += ["<p>" + inline(x) + "</p>" for x in lines[i + 1:j] if x.strip()]; i = j + 1; continue
    m = re.match(r"!\[([^\]]*)\]\(carousel/slides/([^)]+)\)", ln)
    if m:
        if m.group(2) != "01.png":
            n += 1; out.append(f'<p class="img">[Insert image {n}: {m.group(2)}]</p>')
    elif ln.startswith("## "): out.append("<h2>" + inline(ln[3:]) + "</h2>")
    elif ln.strip() == "---": out.append("<p>* * *</p>")
    elif ln.strip():
        para = [ln]
        while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"(#|!\[|---|````)", lines[i + 1]): i += 1; para.append(lines[i])
        out.append("<p>" + inline(" ".join(para)) + "</p>")
    i += 1

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Newsletter Paste Kit</title>
<style>
:root{{--ink:#14201c;--soft:#56635e;--rule:#d3dbd8;--accent:#15614a;--ground:#f2f5f3;--warn:#8a5a00;--warn-tint:#fdf3d9}}
body{{margin:0;background:var(--ground);color:var(--ink);font:400 17px/1.6 Inter,"Segoe UI",Arial,sans-serif}}
.wrap{{max-width:780px;margin:0 auto;padding:28px max(16px,4vw) 60px}}
h1{{font-size:28px;margin:0 0 8px}} h3{{margin:30px 0 8px}}
ol li{{margin:6px 0}}
.box{{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:20px 24px}}
.box h2{{font-size:22px;margin:26px 0 8px}}
.img{{background:var(--warn-tint);color:var(--warn);font-weight:700;padding:8px 12px;border-radius:4px}}
button{{font:inherit;font-weight:700;background:var(--accent);color:#fff;border:0;border-radius:6px;padding:10px 18px;cursor:pointer;margin:6px 0 12px}}
pre{{white-space:pre-wrap;font:inherit}}
.ok{{color:var(--accent);font-weight:700;margin-left:10px}}
</style></head><body><div class="wrap">
<h1>Newsletter edition: paste kit</h1>
<p>Open this file in your own browser (not a preview pane) so the Copy button works.</p>
<ol>
<li>On LinkedIn: <b>Write article</b>. The first time, choose <b>Create a newsletter</b>: name <b>One Painful Problem</b>, description <i>Free, tested tools for accountants: one painful task at a time.</i>, frequency <b>Weekly</b>. LinkedIn invites your connections and followers to subscribe when the first edition is published.</li>
<li>Cover image: <b>carousel/slides/01.png</b>.</li>
<li>Headline: <b>The 1099-K says one number. The bank says another.</b></li>
<li>Press <b>Copy the article</b> and paste into the body.</li>
<li>Replace each yellow <b>[Insert image ...]</b> line with that slide from <b>carousel/slides</b>, using LinkedIn's image button.</li>
<li>Publish the edition the same day as the carousel post, or the next morning.</li>
</ol>
<h3>The article body</h3>
<button type="button" onclick="cp('art',this)">Copy the article</button><span></span>
<div class="box" id="art">{"".join(out)}</div>
</div>
<script>
function cp(id,b){{var el=document.getElementById(id),r=document.createRange();r.selectNodeContents(el);var s=getSelection();s.removeAllRanges();s.addRange(r);
var ok=false;try{{ok=document.execCommand("copy");}}catch(e){{}}
b.nextElementSibling.className="ok";b.nextElementSibling.textContent=ok?"Copied. Paste it into LinkedIn.":"Selected. Press Ctrl+C (Cmd+C on a Mac).";}}
</script></body></html>"""
open(os.path.join(here, "NEWSLETTER-PASTE.html"), "w", encoding="utf-8").write(page)
print("NEWSLETTER-PASTE.html written,", n, "image markers")
