#!/usr/bin/env node
/* Renders the article's images: node render.js
   images/00-cover.png (1920 x 1080), images/02-four-steps.png, and screenshots of the real tool on the
   sample client with the decisions from sample/README.md: images/01-workpaper.png, images/03-decide.png. */
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
  await p.goto("file://" + path.join(EP, "agent/what-goes-on-the-asset-schedule.html"));
  await p.setInputFiles("#file", path.join(EP, "sample/ridgeline-general-ledger-2026.xlsx"));
  await p.waitForFunction(() => window.__report);
  await p.click("#accounts-ok");
  const choice = { "Coastal Door Co": "cap", "Greenfield Tools": "cap", "Summit Office Systems": "exp", "Clearwater Irrigation": "exp" };
  const why = { "Coastal Door Co": "Improvement or restoration", "Greenfield Tools": "New equipment", "Summit Office Systems": "De minimis: items $2,500 or less", "Clearwater Irrigation": "Service contract or subscription" };
  for (;;) {
    const c = await p.evaluate(() => window.__report.candidates.find((x) => x.decision === "undecided"));
    if (!c) break;
    await p.check(`input.dec[data-id="${c.id}"][value="${choice[c.name]}"]`);
    await p.waitForFunction((id) => window.__report.candidates.find((x) => x.id === id).decision !== "undecided", c.id);
  }
  for (const c of await p.evaluate(() => window.__report.candidates.map((x) => ({ id: x.id, name: x.name })))) {
    await p.selectOption(`select.reason[data-id="${c.id}"]`, why[c.name]);
    await p.waitForFunction((id) => window.__report.candidates.find((x) => x.id === id).reason, c.id);
  }
  const vals = ["42000.00", "36750.00", "2625.00"];
  for (let j = 0; j < 3; j++) await p.locator("input.disp").nth(j).fill(vals[j]);
  await p.fill("#sched-cost", "210900.00"); await p.waitForFunction(() => window.__report.disposals[0].gain !== undefined);
  await p.fill("#sched-ad", "97350.00"); await p.fill("#tax-dep", "24610.00"); await p.click("#update");
  await p.waitForFunction(() => window.__report.taxDepreciation !== undefined);
  await p.addStyleTag({ content: "#steps{position:static!important} *:focus{outline:none!important}" });
  const clip = async (fromSel, toSel, file) => {   // from the heading just above the first element to the end of the second
    const box = await p.evaluate(([a, z]) => { let e = document.querySelector(a), h = (e.closest(".scroll") || e).previousElementSibling;
      for (let i = 0; h && i < 4 && !/^H[1-4]$/.test(h.tagName); i++) h = h.previousElementSibling;
      if (h && /^H[1-4]$/.test(h.tagName)) e = h; const A = e.getBoundingClientRect(), Z = document.querySelector(z).getBoundingClientRect();
      return { x: 0, y: A.top + scrollY - 16, width: document.documentElement.clientWidth, height: Z.bottom - A.top + 32 }; }, [fromSel, toSel]);
    await p.screenshot({ path: path.join(IMG, file), clip: box, fullPage: true });
  };
  await clip("#verdict", "#verdict", "01-verdict.png");
  await clip("#schedule", "#entries", "01-workpaper.png");
  await clip("#candidates", "#update-disp", "03-decide.png");
  console.log("images written");
  await b.close();
})();
