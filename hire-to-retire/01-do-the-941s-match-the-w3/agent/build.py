#!/usr/bin/env python3
"""Builds the file people open: the source page with the PDF reader (pdf.js 3.11.174, Apache-2.0)
pasted inside it, so it works with no internet and makes no network request.
Run: python3 build.py   (needs ../../../tools/node_modules/pdfjs-dist from `npm install` in tools/)"""
import os, re
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "do-the-941s-match-the-w3.src.html"), encoding="utf-8").read()
lib_dir = os.path.join(here, "../../../tools/node_modules/pdfjs-dist/build")
lib = open(os.path.join(lib_dir, "pdf.min.js"), encoding="utf-8").read().replace("</script", "<\\/script")
worker = open(os.path.join(lib_dir, "pdf.worker.min.js"), encoding="utf-8").read().replace("</script", "<\\/script")
line = re.search(r"<script src=[^>]*pdf\.js[^>]*></script><!--PDFJS[^>]*-->", src)
assert line, "library line not found"
note = "/* pdf.js 3.11.174, Mozilla Foundation, Apache License 2.0, https://mozilla.github.io/pdf.js/ */\n"
out = (src[:line.start()] + "<script>" + note + lib + "\n</script>\n<script type=\"text/plain\" id=\"pdfjs-worker\">" + worker + "</script>" + src[line.end():])
open(os.path.join(here, "do-the-941s-match-the-w3.html"), "w", encoding="utf-8").write(out)
print("built do-the-941s-match-the-w3.html,", len(out) // 1024, "KB")
