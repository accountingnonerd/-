#!/usr/bin/env python3
"""Builds the file people actually open.

who-gets-a-1099.src.html  is the readable source. It loads the spreadsheet reader (SheetJS,
                          Apache-2.0 licence) from a CDN, so it needs internet for Excel files.
who-gets-a-1099.html      is the same page with that library pasted inside it, so it works
                          with no internet at all and makes no network request of any kind.

Run:  python3 build.py     (needs ../../tools/node_modules/xlsx, from `npm install` in tools/)
"""
import os, re
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "who-gets-a-1099.src.html"), encoding="utf-8").read()
lib = open(os.path.join(here, "../../tools/node_modules/xlsx/dist/xlsx.full.min.js"), encoding="utf-8").read()
lib = lib.replace("</script", "<\\/script")
line = re.search(r"<script src=[^>]*xlsx[^>]*></script><!--XLSX[^>]*-->", src)
assert line, "library line not found"
out = src[:line.start()] + "<script>/* SheetJS Community Edition 0.18.5, (C) SheetJS LLC, Apache License 2.0, https://sheetjs.com */\n" + lib + "\n</script>" + src[line.end():]
open(os.path.join(here, "who-gets-a-1099.html"), "w", encoding="utf-8").write(out)
print("built who-gets-a-1099.html,", len(out) // 1024, "KB")
