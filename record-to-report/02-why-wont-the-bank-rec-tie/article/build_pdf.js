#!/usr/bin/env node
/* Makes the article as a PDF for a regular LinkedIn document post: node build_pdf.js (run build_article.py first).
   The 34,000-character prompt is not printed; the PDF links to the master copy on GitHub instead. */
const path = require("path"), { chromium } = require("playwright");
const GH = "https://github.com/accountingnonerd/-/blob/main/record-to-report/02-why-wont-the-bank-rec-tie/PROMPT.txt";
(async () => {
  const b = await chromium.launch(), p = await b.newPage();
  await p.goto("file://" + path.join(__dirname, "PREVIEW.html"));
  await p.evaluate((gh) => {
    document.querySelector(".note").remove();
    document.querySelector(".nl").remove();
    const pre = document.getElementById("prompt-block");
    const box = document.createElement("p");
    const nw = (t) => '<span style="white-space:nowrap">' + t + '</span>';
    box.innerHTML = '<b>The prompt</b> is about 34,000 characters, so it lives on GitHub. Links in a PDF may not open on LinkedIn: use the link in the post, or type ' + nw('github.com/accountingnonerd/-') + ' and open ' + nw('record-to-report') + ', then ' + nw('02-why-wont-the-bank-rec-tie') + ', then ' + nw('PROMPT.txt') + '. Press "Copy raw file" there. The sample files are in the ' + nw('sample') + ' folder next to it.';
    box.style.cssText = "background:#e4f0eb;border-left:6px solid #15614a;padding:14px 18px";
    pre.replaceWith(box);
    for (const el of document.querySelectorAll("p, li")) {
      el.innerHTML = el.innerHTML
        .replace(" It is also printed in full below.", "")
        .replace(/<b>Subscribe to the One Painful Problem newsletter<\/b> so the next one reaches you, and so do the prompt, the sample and the tests\./, "<b>Follow me</b> so the next one reaches you, with its prompt, its sample and its tests.");
      if (/^<b>The prompt\.<\/b> Copy it from the master copy/.test(el.innerHTML)) el.remove();
    }
    const s = document.createElement("style");
    s.textContent = `@page{size:Letter;margin:12mm 12mm 14mm} body{background:#fff} article{box-shadow:none;margin:0;max-width:none;border-radius:0}
      .inner{padding:18px 6px 0} h2{break-after:avoid} figure{break-inside:avoid} li,p{orphans:3;widows:3}`;
    document.head.appendChild(s);
  }, GH);
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: path.join(__dirname, "why-wont-the-bank-rec-tie-article.pdf"), format: "Letter", printBackground: true,
    displayHeaderFooter: true, headerTemplate: "<span></span>",
    footerTemplate: '<div style="font:8pt Arial;color:#888;width:100%;text-align:center">One Painful Problem · Series 2 · Agent 1 · page <span class="pageNumber"></span> of <span class="totalPages"></span></div>' });
  await b.close();
})();
