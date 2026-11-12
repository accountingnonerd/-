#!/usr/bin/env node
/*
 * Acceptance test for "Do the 941s match the W-3?" (Hire-to-Retire, episode 01).
 *
 *   node run-tests.js [path/to/agent.html] [--md results.md]
 *
 * Opens the agent in a real browser with the network blocked, gives it each case's PDFs
 * through its file input, reads window.__report, and compares it with answer-key.json
 * (worked out independently in make_cases.py). It prints the file it is testing.
 */
const fs = require("fs"), path = require("path"), { chromium } = require("playwright");
const HERE = __dirname, args = process.argv.slice(2), mdAt = args.indexOf("--md");
const mdOut = mdAt >= 0 ? args[mdAt + 1] : null;
const positional = args.filter((a, i) => !a.startsWith("--") && !(mdAt >= 0 && i === mdAt + 1));
const agentPath = path.resolve(positional[0] || path.join(HERE, "../agent/do-the-941s-match-the-w3.html"));
if (!fs.existsSync(agentPath)) { console.error("No such agent file: " + agentPath); process.exit(2); }
console.log("Testing: " + agentPath + "\n");
const KEY = JSON.parse(fs.readFileSync(path.join(HERE, "answer-key.json"), "utf8"));
const PDFJS = path.join(HERE, "../../../tools/node_modules/pdfjs-dist/build/");
const near = (a, b) => typeof a === "number" && typeof b === "number" && Math.abs(a - b) < 0.005;

function compare(key, rep, shown) {
  const out = [], check = (what, expected, got, ok) => out.push({ what, expected, got, ok: ok === undefined ? JSON.stringify(expected) === JSON.stringify(got) : ok });
  if (key.fatal) {
    check("refuses with reason " + key.fatal, key.fatal, rep && rep.fatal);
    check("shows the reason on the start screen", true, !!shown.problem, !!shown.problem);
    return out;
  }
  if (!rep || rep.fatal) { check("produces a report", "a report", rep ? "refused: " + rep.fatal : "nothing"); return out; }
  check("tax year", key.year, rep.year);
  check("EIN", key.ein, rep.ein);
  check("status", key.status, rep.status);
  check("quarters found", key.quartersFound, rep.quartersFound);
  const codes = [...new Set((rep.exceptions || []).map((e) => e.code))].sort();
  const quiet = new Set(["OTHER_EIN_LISTED", "DUPLICATE_SAME"]);
  check("exceptions raised", key.exceptions, codes.filter((c) => !quiet.has(c)));
  for (const [q, lines] of Object.entries(key.quarters)) {
    if (key.dupQuarter && +q === key.dupQuarter) continue;
    const got = rep.quarters && rep.quarters[q] && rep.quarters[q].lines;
    for (const [ln, v] of Object.entries(lines)) check(`Q${q} line ${ln}`, v, got ? (got[ln] || 0) : null, got ? near(v, got[ln] || 0) : false);
  }
  if (key.w3) for (const [b, v] of Object.entries(key.w3)) check(`W-3 ${b}`, v, rep.w3 && rep.w3.boxes[b], rep.w3 ? near(v, rep.w3.boxes[b] || 0) : false);
  if (key.recon === null) check("no reconciliation computed", null, rep.recon);
  else for (const [b, r] of Object.entries(key.recon)) {
    const g = rep.recon && rep.recon[b];
    check(`${b}: 941 total`, r.total941, g && g.total941, g ? near(r.total941, g.total941) : false);
    check(`${b}: difference`, r.diff, g && g.diff, g ? near(r.diff, g.diff) : false);
    check(`${b}: agrees`, r.agrees, g && g.agrees);
  }
  if (key.patternQuarters) check("names the quarters the difference equals", key.patternQuarters, rep.recon && rep.recon.b1 && rep.recon.b1.pattern);
  if (key.arithmeticQuarter) check("flags the quarter that does not add up", key.arithmeticQuarter, ((rep.exceptions || []).find((e) => e.code === "ARITHMETIC") || {}).quarter);
  const stopExpected = key.status !== "AGREES";
  check(stopExpected ? "shows the STOP warning" : "shows no STOP warning", stopExpected, shown.stop);
  return out;
}

(async () => {
  const browser = await chromium.launch(), results = [];
  for (const id of Object.keys(KEY).sort()) {
    const key = KEY[id], page = await browser.newPage(), errors = [];
    page.on("pageerror", (e) => errors.push(String(e)));
    await page.route(/^https?:/, (route) => {
      const u = route.request().url();
      if (/pdf\.worker/.test(u)) return route.fulfill({ path: PDFJS + "pdf.worker.min.js", contentType: "application/javascript" });
      if (/pdf\.min\.js|pdf\.js/.test(u)) return route.fulfill({ path: PDFJS + "pdf.min.js", contentType: "application/javascript" });
      return route.abort();
    });
    await page.goto("file://" + agentPath);
    const t0 = Date.now(); let rep = null, shown = {};
    try {
      await page.setInputFiles('input[type="file"]', key.files.map((f) => path.join(HERE, "cases", f)));
      await page.waitForFunction(() => window.__report !== undefined && window.__report !== null, null, { timeout: 30000 });
      rep = await page.evaluate(() => JSON.parse(JSON.stringify(window.__report)));
      shown = await page.evaluate(() => {
        const vis = (el) => !!el && el.offsetParent !== null && el.innerText.trim().length > 0;
        return { stop: vis(document.getElementById("stop-banner")), problem: vis(document.getElementById("problem")) };
      });
    } catch (e) { errors.push(String(e).split("\n")[0]); }
    const ms = Date.now() - t0, checks = compare(key, rep, shown);
    if (errors.length) checks.push({ what: "runs without errors", expected: "none", got: errors.join(" | "), ok: false });
    results.push({ id, key, checks, ms, pass: checks.every((c) => c.ok) });
    await page.close();
  }
  await browser.close();
  let passed = 0, total = 0, failed = 0; const md = [];
  for (const r of results) {
    const f = r.checks.filter((c) => !c.ok); total += r.checks.length; failed += f.length; if (r.pass) passed++;
    console.log(`${r.pass ? "PASS" : "FAIL"}  ${r.id}  ${r.key.title}  (${r.checks.length - f.length}/${r.checks.length} checks, ${r.ms} ms)`);
    for (const x of f) console.log(`        x ${x.what}: expected ${JSON.stringify(x.expected)}, got ${JSON.stringify(x.got)}`);
    md.push(`| ${r.id} | ${r.key.title} | ${r.key.kind} | ${r.key.files.length} | ${r.checks.length - f.length}/${r.checks.length} | ${r.ms} | ${r.pass ? "PASS" : "**FAIL**"} |`);
    for (const x of f) md.push(`| | x ${x.what}: expected \`${JSON.stringify(x.expected)}\`, got \`${JSON.stringify(x.got)}\` | | | | | |`);
  }
  console.log(`\n${passed}/${results.length} cases passed, ${total - failed}/${total} checks.`);
  if (mdOut) fs.writeFileSync(mdOut, [`Agent file: \`${path.basename(agentPath)}\``, "", `**${passed} of ${results.length} cases passed; ${total - failed} of ${total} individual checks.**`, "",
    "| Case | What it is | Type | Files | Checks passed | Run time (ms) | Result |", "|---|---|---|---|---|---|---|", ...md, ""].join("\n"));
  process.exit(passed === results.length ? 0 : 1);
})();
