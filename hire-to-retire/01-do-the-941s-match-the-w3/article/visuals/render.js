#!/usr/bin/env node
/* Renders the article images from the HTML files here: node render.js
   Needs playwright and the Inter, Inter Display and JetBrains Mono fonts. Figure 3 is a real
   screenshot of the tool on test case 04, with numbered badges placed over it. */
const path = require("path"), fs = require("fs"), { chromium } = require("playwright");
const HERE = __dirname, OUT = path.join(HERE, "../images"), C = path.join(HERE, "../../tests/cases/");
(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1180, height: 900 }, deviceScaleFactor: 2 });
  await p.goto("file://" + path.join(HERE, "../../agent/do-the-941s-match-the-w3.html"));
  await p.setInputFiles('input[type="file"]', ["04-q1-941-old-provider.pdf", "04-q2-941-old-provider.pdf", "04-q3-941-ledgerline.pdf", "04-q4-941-ledgerline.pdf", "04-w3-ledgerline.pdf"].map((f) => C + f));
  await p.waitForFunction(() => window.__report);
  await p.fill("#preparedBy", "M. Okafor, CPA");
  const clip = await p.evaluate(() => {
    document.querySelector(".bar").style.display = "none";
    const badge = (el, n, dx, dy) => { const r = el.getBoundingClientRect(), d = document.createElement("div"); d.textContent = n;
      Object.assign(d.style, { position: "absolute", left: (r.left + scrollX + dx) + "px", top: (r.top + scrollY + dy) + "px", width: "38px", height: "38px", borderRadius: "50%",
        background: "#15614a", color: "#fff", font: "700 20px/38px Inter, sans-serif", textAlign: "center", boxShadow: "0 0 0 4px #fff", zIndex: 9 }); document.body.appendChild(d); };
    badge(document.getElementById("verdict"), "1", -46, 0);
    badge(document.querySelector("ul.first li"), "2", -46, 0);
    badge(document.querySelector("table.recon tbody tr"), "3", -46, 4);
    badge(document.querySelector("#sec-tax"), "4", -46, 14);
    const top = document.querySelector(".wp-head").getBoundingClientRect().top + scrollY - 24;
    const bottom = document.querySelector("#sec-tax").nextElementSibling.getBoundingClientRect().bottom + scrollY + 20;
    return { x: 0, y: top, width: 1180, height: bottom - top };
  });
  await p.screenshot({ path: path.join(HERE, "_recon.png"), clip, fullPage: true });
  await p.close();
  const figs = fs.readdirSync(HERE).filter((f) => /^(cover|fig\d.*)\.html$/.test(f));
  for (const src of figs) {
    const q = await b.newPage({ viewport: { width: src === "cover.html" ? 960 : 1200, height: 600 }, deviceScaleFactor: 2 });
    await q.goto("file://" + path.join(HERE, src)); await q.evaluate(() => document.fonts.ready);
    await (await q.$(src === "cover.html" ? ".cover" : ".frame")).screenshot({ path: path.join(OUT, src.replace(".html", ".png")) });
    console.log("wrote", src.replace(".html", ".png")); await q.close();
  }
  await b.close();
})();
