#!/usr/bin/env node
/* Photographs PREVIEW.html on desktop and phone, and tests copying the prompt out of the rendered
   article: the copied text is compared with ../PROMPT.txt character by character. */
const path = require("path"), fs = require("fs"), { chromium } = require("playwright");
const HERE = __dirname, OUT = path.join(HERE, "preview"); fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const b = await chromium.launch();
  for (const [w, tag] of [[1366, "desktop"], [390, "mobile"]]) {
    const ctx = await b.newContext({ viewport: { width: w, height: 900 }, deviceScaleFactor: 1, permissions: ["clipboard-read", "clipboard-write"] });
    const p = await ctx.newPage();
    await p.goto("file://" + path.join(HERE, "PREVIEW.html"));
    await p.screenshot({ path: path.join(OUT, tag + "-full.png"), fullPage: true });
    await p.screenshot({ path: path.join(OUT, tag + "-top.png") });
    // copy the prompt the way a reader does: select the whole block, copy
    await p.evaluate(() => { const el = document.querySelector("#prompt-block"); const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); });
    await p.keyboard.press("Control+C");
    const copied = await p.evaluate(() => navigator.clipboard.readText());
    const master = fs.readFileSync(path.join(HERE, "..", "PROMPT.txt"), "utf8").replace(/\n+$/, "");
    const same = copied.replace(/\n+$/, "") === master;
    let first = -1; if (!same) for (let i = 0; i < Math.max(copied.length, master.length); i++) if (copied[i] !== master[i]) { first = i; break; }
    console.log(tag + ": copied " + copied.length + " characters; master " + master.length + "; " + (same ? "IDENTICAL" : "DIFFERS at " + first + ": " + JSON.stringify(copied.slice(first - 20, first + 20)) + " vs " + JSON.stringify(master.slice(first - 20, first + 20))));
    await ctx.close();
  }
  await b.close();
})();
