#!/usr/bin/env node
/* Renders the LinkedIn carousel: node render.js -> slides/NN.png and whats-really-collectible-carousel.pdf (1080 x 1350 pages).
   The figures are from test cases 03, 04, 05, 08, 13, 14 and 17 (answer-key.json). Needs playwright. */
const path = require("path"), fs = require("fs"), { chromium } = require("playwright");
const HERE = __dirname;
(async () => {
  const b = await chromium.launch();
  const q = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await q.goto("file://" + path.join(HERE, "carousel.html")); await q.evaluate(() => document.fonts.ready);
  fs.mkdirSync(path.join(HERE, "slides"), { recursive: true });
  const slides = await q.$$(".slide");
  for (let i = 0; i < slides.length; i++) await slides[i].screenshot({ path: path.join(HERE, "slides", String(i + 1).padStart(2, "0") + ".png") });
  await q.addStyleTag({ content: "@page{size:1080px 1350px;margin:0} body{background:#fff} .slide{margin:0;break-after:page}" });
  await q.pdf({ path: path.join(HERE, "whats-really-collectible-carousel.pdf"), width: "1080px", height: "1350px", printBackground: true });
  console.log("wrote", slides.length, "slides and the PDF");
  await b.close();
})();
