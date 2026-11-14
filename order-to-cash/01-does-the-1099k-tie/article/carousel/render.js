#!/usr/bin/env node
/* Renders the LinkedIn carousel: node render.js -> slides/NN.png and does-the-1099k-tie-carousel.pdf (1080 x 1350 pages).
   Slide 7 is a real screenshot of the tool on test case 01. Needs playwright and the Inter fonts. */
const path = require("path"), fs = require("fs"), { chromium } = require("playwright");
const HERE = __dirname, C = path.join(HERE, "../../tests/cases/"), XLSX = path.join(HERE, "../../../../tools/node_modules/xlsx/dist/xlsx.full.min.js");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1000, height: 1200 }, deviceScaleFactor: 2 });
  await p.route(/^https?:/, (r) => r.fulfill({ path: XLSX, contentType: "application/javascript" }));
  await p.goto("file://" + path.join(HERE, "../../agent/does-the-1099k-tie.html"));
  await p.setInputFiles("#file", C + "01-square-juniper-street-2025.csv");
  await p.waitForFunction(() => window.__report);
  const clip = await p.evaluate(() => {
    document.querySelector(".bar").style.display = "none";
    const top = document.querySelector(".wp-head").getBoundingClientRect().top + scrollY - 10;
    const bottom = document.getElementById("monthly").getBoundingClientRect().bottom + scrollY + 16;
    return { x: 0, y: top, width: 1000, height: bottom - top };
  });
  await p.screenshot({ path: path.join(HERE, "_shot.png"), clip, fullPage: true });
  await p.close();
  const q = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await q.goto("file://" + path.join(HERE, "carousel.html")); await q.evaluate(() => document.fonts.ready);
  fs.mkdirSync(path.join(HERE, "slides"), { recursive: true });
  const slides = await q.$$(".slide");
  for (let i = 0; i < slides.length; i++) await slides[i].screenshot({ path: path.join(HERE, "slides", String(i + 1).padStart(2, "0") + ".png") });
  await q.addStyleTag({ content: "@page{size:1080px 1350px;margin:0} body{background:#fff} .slide{margin:0;break-after:page}" });
  await q.pdf({ path: path.join(HERE, "does-the-1099k-tie-carousel.pdf"), width: "1080px", height: "1350px", printBackground: true });
  console.log("wrote", slides.length, "slides and the PDF");
  await b.close();
})();
