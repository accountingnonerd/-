#!/usr/bin/env node
/* Renders the article's images: node render.js
   images/00-cover.png (1920 x 1080), images/02-four-steps.png, and screenshots of the real tool on the
   sample client (sample/): images/03-decide.png before the decisions, then with the decisions from
   sample/README.md, images/01-verdict.png and images/01-proof.png. */
const path = require("path"), fs = require("fs"), { chromium } = require("playwright");
const HERE = __dirname, EP = path.join(HERE, ".."), IMG = path.join(HERE, "images");
fs.mkdirSync(IMG, { recursive: true });
(async () => {
  const b = await chromium.launch();
  const v = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await v.goto("file://" + path.join(HERE, "visuals.html")); await v.evaluate(() => document.fonts.ready);
  await (await v.$("#cover")).screenshot({ path: path.join(IMG, "00-cover.png") });
  await (await v.$("#steps")).screenshot({ path: path.join(IMG, "02-four-steps.png") });
  const p = await b.newPage({ viewport: { width: 1180, height: 900 }, deviceScaleFactor: 2 });
  await p.goto("file://" + path.join(EP, "agent/why-wont-the-bank-rec-tie.html"));
  await p.setInputFiles("#bank-file", path.join(EP, "sample/mapleton-checking-bank-download-q1-2026.csv"));
  await p.setInputFiles("#books-file", path.join(EP, "sample/mapleton-general-ledger.xlsx"));
  await p.waitForFunction(() => window.__report);
  await p.fill("#preparedBy", "J. Rivera, CPA");
  await p.click("#read-ok");
  await p.addStyleTag({ content: "#steps{position:static!important} *:focus{outline:none!important}" });
  const clip = async (fromSel, toSel, file) => {   // from the first element (or the heading just above it) to the end of the second
    const box = await p.evaluate(([a, z]) => { let e = document.querySelector(a), h = (e.closest(".scroll") || e).previousElementSibling;
      for (let i = 0; h && i < 4 && !/^H[1-4]$/.test(h.tagName); i++) h = h.previousElementSibling;
      if (h && /^H[1-4]$/.test(h.tagName)) e = h; const A = e.getBoundingClientRect(), Z = document.querySelector(z).getBoundingClientRect();
      return { x: 0, y: A.top + scrollY - 16, width: document.documentElement.clientWidth, height: Z.bottom - A.top + 32 }; }, [fromSel, toSel]);
    await p.screenshot({ path: path.join(IMG, file), clip: box, fullPage: true });
  };
  await p.evaluate(() => document.activeElement && document.activeElement.blur());
  await clip("#errors", "#errors", "03-decide.png");
  for (const [id, val] of [["n0", "fix"], ["u0", "fix"], ["o0", "keep"]]) {
    const before = await p.evaluate(() => JSON.stringify(window.__report));
    await p.check(`input.dec[data-id="${id}"][value="${val}"]`);
    await p.waitForFunction((s) => JSON.stringify(window.__report) !== s, before);
  }
  await p.evaluate(() => { document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0); });
  await clip("#verdict", "#verdict", "01-verdict.png");
  await clip("#proof", "#proof", "01-proof.png");
  console.log("images written");
  await b.close();
})();
