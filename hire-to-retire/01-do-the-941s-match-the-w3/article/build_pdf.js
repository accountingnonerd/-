#!/usr/bin/env node
// Makes the article as a PDF for a LinkedIn document post: node build_pdf.js (run build_preview.py first)
const path = require("path"), { chromium } = require("playwright");
(async () => {
  const b = await chromium.launch(), p = await b.newPage();
  await p.goto("file://" + path.join(__dirname, "PREVIEW.html"));
  await p.evaluate(() => {
    document.querySelector(".note").remove();
    for (const el of document.querySelectorAll("p")) el.innerHTML = el.innerHTML.replace("__none__", "The repository link is in the first comment under this post.");
    const s = document.createElement("style");
    s.textContent = `@page{size:Letter;margin:14mm 14mm 16mm} body{background:#fff;font-size:12.5pt;line-height:1.55}
      main{max-width:none;margin:0;padding:0} h1{font-size:28pt;margin-top:10pt} h2{font-size:17pt;break-after:avoid}
      figure{break-inside:avoid;margin:14pt 0} pre{font-size:8.5pt;background:#f2f5f3} p{orphans:3;widows:3}`;
    document.head.appendChild(s);
  });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: path.join(__dirname, "payroll-letter-article.pdf"), format: "Letter", printBackground: true,
    displayHeaderFooter: true, headerTemplate: "<span></span>",
    footerTemplate: '<div style="font:8pt Inter,Arial;color:#888;width:100%;text-align:center">Series 1 · Agent 2: The payroll letter that arrives two years late · page <span class="pageNumber"></span> of <span class="totalPages"></span></div>' });
  await b.close();
})();
