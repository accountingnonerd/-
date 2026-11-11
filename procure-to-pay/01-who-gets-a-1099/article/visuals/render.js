#!/usr/bin/env node
/*
 * Renders the article images from the HTML files in this folder.
 *   node render.js        (needs playwright; Inter, Inter Display and JetBrains Mono installed)
 * Writes ../images/*.png. Figure 3 is a real screenshot of the tool on test file 04,
 * with numbered badges placed over it.
 */
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");
const HERE = __dirname, OUT = path.join(HERE, "../images");
const AGENT = path.join(HERE, "../../agent/who-gets-a-1099.html");
const CASE = path.join(HERE, "../../tests/cases/04-vendor-name-variants.csv");

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch();

  // 1. the real worksheet, with badges
  const p = await b.newPage({ viewport: { width: 1180, height: 900 }, deviceScaleFactor: 2 });
  await p.goto("file://" + AGENT);
  await p.setInputFiles('input[type="file"]', CASE);
  await p.waitForFunction(() => window.__report);
  await p.fill("#client", "Larkspur Cafe");
  await p.fill("#preparedBy", "M. Okafor, CPA");
  await p.check("#w-file-0");
  const clip = await p.evaluate(() => {
    document.querySelector(".bar").style.display = "none";
    const badge = (el, n, dx, dy) => {
      const r = el.getBoundingClientRect(), b = document.createElement("div");
      b.textContent = n;
      Object.assign(b.style, { position: "absolute", left: (r.left + window.scrollX + dx) + "px", top: (r.top + window.scrollY + dy) + "px",
        width: "38px", height: "38px", borderRadius: "50%", background: "#15614a", color: "#fff", font: "700 20px/38px Inter, sans-serif",
        textAlign: "center", boxShadow: "0 0 0 4px #fff", zIndex: 9 });
      document.body.appendChild(b);
    };
    badge(document.getElementById("summary"), "1", -20, -16);
    badge(document.querySelector("ul.first"), "2", -20, -10);
    const rivera = [...document.querySelectorAll("#sec-file ~ div table tbody tr")][0];
    badge(rivera, "3", -46, -2);
    badge(document.querySelector(".sign"), "4", -50, -6);
    const top = document.querySelector(".wp-head").getBoundingClientRect().top + window.scrollY - 24;
    const t = document.querySelector("#sec-file").nextElementSibling.nextElementSibling;
    const bottom = t.getBoundingClientRect().bottom + window.scrollY + 20;
    return { x: 0, y: top, width: 1180, height: bottom - top };
  });
  await p.screenshot({ path: path.join(HERE, "_worksheet.png"), clip, fullPage: true });
  await p.close();

  // 2. every figure
  const figs = [["cover.html", "cover.png", 960], ["fig1-three-spellings.html", "fig1-three-spellings.png", 1200],
    ["fig2-what-it-adds.html", "fig2-what-it-adds.png", 1200], ["fig3-worksheet.html", "fig3-worksheet.png", 1200],
    ["fig4-we-tried-to-break-it.html", "fig4-we-tried-to-break-it.png", 1200], ["fig5-series-map.html", "fig5-series-map.png", 1200]];
  for (const [src, out, w] of figs) {
    const q = await b.newPage({ viewport: { width: w, height: 600 }, deviceScaleFactor: 2 });
    await q.goto("file://" + path.join(HERE, src));
    await q.evaluate(() => document.fonts.ready);
    const el = await q.$(src === "cover.html" ? ".cover" : ".frame");
    await el.screenshot({ path: path.join(OUT, out) });
    console.log("wrote", out);
    await q.close();
  }
  await b.close();
})();
