#!/usr/bin/env python3
"""Builds the article for LinkedIn from ARTICLE.md and ../PROMPT.txt:

  PREVIEW.html          the article as a reader will see it (cover, headline, body, images embedded),
                        laid out like a LinkedIn article; shoot.js photographs it on desktop and phone.
  LINKEDIN-PASTE.html   the paste kit: step-by-step instructions, the body as rich text with a Copy
                        button, a marker where each image and the prompt go, and a separate Copy button
                        for the prompt. Open it in your own browser.

Handles the small Markdown subset ARTICLE.md uses. Run: python3 build_article.py
"""
import base64, html, os, re
here = os.path.dirname(os.path.abspath(__file__))
md = open(os.path.join(here, "ARTICLE.md"), encoding="utf-8").read()
prompt = open(os.path.join(here, "..", "PROMPT.txt"), encoding="utf-8").read().rstrip("\n")
meta = re.search(r"<!--(.*?)-->", md, re.S).group(1)
seo_title = re.search(r"SEO title[^:]*:\s*(.+)", meta).group(1).strip()
seo_desc = re.search(r"SEO description[^:]*:\s*(.+)", meta).group(1).strip()
md = re.sub(r"<!--.*?-->", "", md, flags=re.S).strip()
headline = md.split("\n", 1)[0].lstrip("# ").strip()
body = md.split("\n", 1)[1]

def inline(t, target=""):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2"' + target + r'>\1</a>', t)

def convert(body, mode):
    out, lines, i, n = [], body.split("\n"), 0, 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            j = i + 1
            while not lines[j].startswith("```"): j += 1
            if mode == "paste": out.append('<p class="img">[Insert the prompt here: in LinkedIn\'s editor choose the Code block, then use the "Copy the prompt" button above and paste.]</p>')
            else: out.append('<pre class="code" id="prompt-block"><code>' + html.escape(prompt) + "</code></pre>")
            i = j + 1; continue
        m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", ln)
        if m:
            if mode == "paste":
                n += 1; out.append(f'<p class="img">[Insert image {n}: {html.escape(m.group(2))}, alt text: {html.escape(m.group(1))}]</p>')
            else:
                data = base64.b64encode(open(os.path.join(here, m.group(2)), "rb").read()).decode()
                out.append(f'<figure><img src="data:image/png;base64,{data}" alt="{html.escape(m.group(1))}"></figure>')
        elif ln.startswith("## "): out.append("<h2>" + inline(ln[3:]) + "</h2>")
        elif ln.strip() == "---": out.append("<hr>")
        elif re.match(r"^- ", ln):
            items = []
            while i < len(lines) and lines[i].startswith("- "): items.append(lines[i][2:]); i += 1
            out.append("<ul>" + "".join("<li>" + inline(x) + "</li>" for x in items) + "</ul>"); continue
        elif re.match(r"^\d+\. ", ln):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]): items.append(re.sub(r"^\d+\. ", "", lines[i])); i += 1
            out.append("<ol>" + "".join("<li>" + inline(x) + "</li>" for x in items) + "</ol>"); continue
        elif ln.startswith("> "): out.append("<blockquote>" + inline(ln[2:]) + "</blockquote>")
        elif ln.strip():
            para = [ln]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"(#|!\[|---|```|- |\d+\. |> )", lines[i + 1]): i += 1; para.append(lines[i])
            out.append("<p>" + inline(" ".join(para)) + "</p>")
        i += 1
    return "\n".join(out)

cover = base64.b64encode(open(os.path.join(here, "images/00-cover.png"), "rb").read()).decode()
preview = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(headline)}</title>
<style>
body{{margin:0;background:#f4f2ee;font-family:-apple-system,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#191919}}
.note{{background:#fff8e1;border-bottom:1px solid #e6d9a8;padding:10px 16px;font-size:14px;text-align:center}}
article{{max-width:744px;margin:24px auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 0 0 1px rgba(0,0,0,.08)}}
.cover img{{width:100%;display:block}}
.inner{{padding:24px 40px 48px}}
h1{{font-size:32px;line-height:1.25;margin:8px 0 16px}}
.by{{display:flex;gap:12px;align-items:center;color:#666;font-size:14px;margin-bottom:24px}}
.by .av{{width:48px;height:48px;border-radius:50%;background:#123d30}}
.by b{{color:#191919;display:block;font-size:16px}}
.nl{{border:1px solid #ddd;border-radius:8px;padding:12px 16px;margin:0 0 24px;font-size:14px}}
.nl b{{color:#0a66c2}}
h2{{font-size:24px;line-height:1.3;margin:32px 0 8px}}
p,li{{font-size:18px;line-height:1.6}}
blockquote{{border-left:3px solid #191919;margin:16px 0;padding-left:16px;font-size:18px;line-height:1.6}}
figure{{margin:24px 0}} figure img{{width:100%;display:block}}
pre.code{{background:#f3f3f3;border-radius:4px;padding:16px;font:13px/1.5 ui-monospace,Menlo,Consolas,monospace;white-space:pre-wrap;word-wrap:break-word;max-height:none}}
a{{color:#0a66c2}}
hr{{border:0;border-top:1px solid #ddd;margin:32px 0}}
@media (max-width:600px){{article{{margin:0;border-radius:0}} .inner{{padding:16px}} h1{{font-size:26px}} h2{{font-size:21px}} p,li,blockquote{{font-size:16px}}}}
</style></head><body>
<div class="note">Preview of the LinkedIn article (draft, not published). LinkedIn's own layout differs in detail.</div>
<article>
<div class="cover"><img src="data:image/png;base64,{cover}" alt="Cover: What goes on the asset schedule?"></div>
<div class="inner">
<div class="nl">Newsletter: <b>One Painful Problem</b> · Edition 1</div>
<h1>{html.escape(headline)}</h1>
<div class="by"><span class="av"></span><span><b>Zac Lu, CPA, LSSBB</b>Free, tested tools for accountants</span></div>
{convert(body, "preview")}
</div></article></body></html>"""
open(os.path.join(here, "PREVIEW.html"), "w", encoding="utf-8").write(preview)

imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", body)
paste = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>LinkedIn article: paste kit</title>
<style>
body{{margin:0;background:#f4f6f5;font:17px/1.55 -apple-system,system-ui,"Segoe UI",Arial,sans-serif;color:#14201c}}
.wrap{{max-width:820px;margin:0 auto;padding:28px 20px 60px}}
h1{{font-size:28px;margin:0 0 8px}} h3{{margin:28px 0 8px}}
ol li{{margin:8px 0}}
.box{{background:#fff;border:1px solid #c9d1ce;border-radius:8px;padding:20px 24px}}
.box h2{{font-size:22px;margin:26px 0 8px}}
.img{{background:#fdf3d9;color:#8a5a00;font-weight:700;padding:8px 12px;border-radius:4px}}
button{{font:inherit;font-weight:700;background:#15614a;color:#fff;border:0;border-radius:6px;padding:10px 18px;cursor:pointer;margin:6px 8px 12px 0}}
.ok{{color:#15614a;font-weight:700}} code{{background:#eef1f0;padding:1px 5px;border-radius:4px}}
textarea{{position:absolute;left:-9999px}}
</style></head><body><div class="wrap">
<h1>LinkedIn article: paste kit</h1>
<p>Open this file in your own browser (Chrome, Edge, Safari or Firefox), not a preview pane, so the Copy buttons work. Work on a computer: LinkedIn articles cannot be written in the phone app.</p>
<h3>Once only: create the newsletter</h3>
<ol>
<li>On LinkedIn, at the top of the home feed, choose <b>Write article</b>.</li>
<li>In the editor, open the menu next to your name (or <b>Manage</b>) and choose <b>Create a newsletter</b>. Title: <b>One Painful Problem</b>. Description: <i>Free, tested tools for accountants: one painful problem at a time, with the prompt to rebuild each one.</i> How often: <b>Biweekly</b> (or Monthly). Logo: <code>images/00-cover.png</code> works, cropped square.</li>
<li>When you publish the first edition, LinkedIn invites your connections and followers to subscribe. That is the point of doing it this way.</li>
</ol>
<h3>The article (edition 1)</h3>
<ol>
<li>In the newsletter, start a new edition (an article in it). <b>Cover image:</b> <code>images/00-cover.png</code> (1920 x 1080).</li>
<li><b>Title:</b> <code>{html.escape(headline)}</code></li>
<li>Press <b>Copy the article</b> below and paste it into the body. Headings, bold, lists and links come across.</li>
<li>Replace each yellow <b>[Insert image ...]</b> line with that file from <code>images/</code> using the editor's image button, and paste the alt text when asked.</li>
<li>At the yellow <b>[Insert the prompt here ...]</b> line: choose the editor's <b>Code</b> block, press <b>Copy the prompt</b> below, and paste inside the block.</li>
<li>Open the settings for the article and fill in the <b>SEO title</b> and <b>SEO description</b> below.</li>
<li>Press <b>Next</b>. In "Tell your network what your article is about", paste the companion text from <code>COMPANION-POST.txt</code>.</li>
<li><b>Do not publish yet:</b> save it as a draft, preview it on desktop and on your phone (open the draft link in the phone's browser), and send me screenshots. Publish (or schedule with the clock icon) only after we have checked it.</li>
</ol>
<p><b>SEO title</b> ({len(seo_title)} characters): <code>{html.escape(seo_title)}</code><br><b>SEO description</b> ({len(seo_desc)} characters): <code>{html.escape(seo_desc)}</code></p>
<p><b>Images, in order:</b> {", ".join(html.escape(x) for x in imgs)}.</p>
<button type="button" onclick="cp('art',this)">Copy the article</button><button type="button" onclick="cpText(this)">Copy the prompt</button><span></span>
<textarea id="ptext" readonly>{html.escape(prompt)}</textarea>
<div class="box" id="art">{convert(body, "paste")}</div>
</div>
<script>
function done(b, ok){{ var s = b.parentNode.querySelector("span"); s.className = "ok"; s.textContent = ok ? " Copied. Paste it into LinkedIn." : " Selected. Press Ctrl+C (Cmd+C on a Mac)."; }}
function cp(id, b){{ var el = document.getElementById(id), r = document.createRange(); r.selectNodeContents(el); var s = getSelection(); s.removeAllRanges(); s.addRange(r);
  var ok = false; try {{ ok = document.execCommand("copy"); }} catch (e) {{}} done(b, ok); }}
function cpText(b){{ var t = document.getElementById("ptext"); t.select(); var ok = false; try {{ ok = document.execCommand("copy"); }} catch (e) {{}} done(b, ok); }}
</script></body></html>"""
open(os.path.join(here, "LINKEDIN-PASTE.html"), "w", encoding="utf-8").write(paste)
print("PREVIEW.html and LINKEDIN-PASTE.html written;", len(imgs), "images; SEO", len(seo_title), len(seo_desc), "; headline", len(headline), "characters")
