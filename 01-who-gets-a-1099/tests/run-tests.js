#!/usr/bin/env node
/*
 * Acceptance test for agent 01, "Who gets a 1099?".
 *
 *   node run-tests.js [path/to/agent.html] [--md results.md]
 *
 * Opens the agent in a real browser, feeds it each file in cases/ through its file input,
 * reads window.__report, and compares it with answer-key.json. The key was worked out by hand
 * (see make_cases.py); this script only compares. Any agent that passes is "the same agent".
 *
 * Needs: playwright, and the xlsx package (served locally in place of the CDN copy, so the
 * test runs without internet):  npm install xlsx@0.18.5   in ../../tools
 */
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const HERE = __dirname;
const args = process.argv.slice(2);
const mdAt = args.indexOf("--md");
const mdOut = mdAt >= 0 ? args[mdAt + 1] : null;
const agentPath = path.resolve(args.find((a, i) => !a.startsWith("--") && i !== mdAt + 1) || path.join(HERE, "../agent/who-gets-a-1099.html"));
const KEY = JSON.parse(fs.readFileSync(path.join(HERE, "answer-key.json"), "utf8"));
const XLSX_LOCAL = [path.join(HERE, "../../tools/node_modules/xlsx/dist/xlsx.full.min.js")].find(fs.existsSync);

const near = (a, b) => typeof a === "number" && typeof b === "number" && Math.abs(a - b) < 0.005;
const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, "");

function compare(key, rep) {
  const out = []; // {ok, what, expected, got}
  const check = (what, expected, got, ok) => out.push({ what, expected, got, ok: ok === undefined ? expected === got : ok });
  if (key.fatal) {
    check("refuses the file with reason " + key.fatal, key.fatal, rep && rep.fatal);
    return out;
  }
  if (!rep || rep.fatal) { check("produces a report", "a report", rep ? "refused: " + rep.fatal : "nothing"); return out; }
  check("tax year", key.taxYear, rep.taxYear);
  check("dollar limit", key.threshold, rep.threshold);
  const kc = key.controls, rc = rep.controls || {};
  check("payment lines read", kc.linesRead, rc.linesRead);
  check("total of all lines", kc.totalPayments, rc.totalPayments, near(kc.totalPayments, rc.totalPayments));
  for (const m of ["bank", "card", "network"])
    check("total by " + m, kc.byMethod[m], (rc.byMethod || {})[m], near(kc.byMethod[m], (rc.byMethod || {})[m]));
  check("outside-year total", kc.outsideYearTotal, rc.outsideYearTotal, near(kc.outsideYearTotal, rc.outsideYearTotal));
  check("outside-year lines", kc.outsideYearLines, rc.outsideYearLines);
  check("unreadable lines", kc.unreadableLines, rc.unreadableLines);
  check("worksheet ties to the file's lines", true, rc.ties);
  check("file's own total line", kc.fileTotal, rc.fileTotal, kc.fileTotal === null ? rc.fileTotal == null : near(kc.fileTotal, rc.fileTotal));
  check("file's own total ties", kc.fileTotalTies, rc.fileTotalTies, kc.fileTotalTies === null ? rc.fileTotalTies == null : kc.fileTotalTies === rc.fileTotalTies);

  const codes = (rep.exceptions || []).map((e) => e.code);
  for (const c of key.exceptions) check("raises " + c, "raised", codes.includes(c) ? "raised" : "missing");
  if (key.noOtherExceptions) {
    const extra = [...new Set(codes.filter((c) => !key.exceptions.includes(c)))];
    check("raises nothing else", "none", extra.length ? extra.join(",") : "none");
  }
  if (key.duplicateGroups !== undefined) check("duplicate groups flagged", key.duplicateGroups, codes.filter((c) => c === "DUPLICATE").length);

  const vendors = rep.vendors || [];
  check("number of vendors", key.vendors.length, vendors.length);
  for (const e of key.vendors) {
    const v = vendors.find((x) => (x.spellings || [x.name]).some((s) => norm(s) === norm(e.vendor)));
    if (!v) { check(e.vendor + ": listed", "listed", "missing"); continue; }
    check(e.vendor + ": bucket", e.bucket, v.bucket);
    check(e.vendor + ": check/transfer dollars", e.reportable, v.reportable, near(e.reportable, v.reportable));
    if (e.total !== undefined) check(e.vendor + ": paid in all", e.total, v.total, near(e.total, v.total));
    if (e.spellings) check(e.vendor + ": spellings combined", e.spellings, (v.spellings || []).length);
    if (e.rows) check(e.vendor + ": source rows", e.rows.join(","), (v.rows || []).slice().sort((a, b) => a - b).join(","));
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const results = [];
  for (const id of Object.keys(KEY).sort()) {
    const key = KEY[id];
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (e) => errors.push(String(e)));
    await page.route(/cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net|unpkg\.com/, (route) => {
      if (/xlsx/i.test(route.request().url()) && XLSX_LOCAL) route.fulfill({ path: XLSX_LOCAL, contentType: "application/javascript" });
      else route.abort();
    });
    await page.goto("file://" + agentPath);
    const t0 = Date.now();
    let rep = null, shown = {};
    try {
      await page.setInputFiles('input[type="file"]', path.join(HERE, "cases", key.file));
      await page.waitForFunction(() => window.__report !== undefined && window.__report !== null, null, { timeout: 15000 });
      rep = await page.evaluate(() => JSON.parse(JSON.stringify(window.__report)));
      shown = await page.evaluate(() => {
        const vis = (el) => !!el && el.offsetParent !== null && el.innerText.trim().length > 0;
        return { tieBanner: vis(document.getElementById("tie-banner")), bodyText: document.body.innerText };
      });
    } catch (e) { errors.push(String(e).split("\n")[0]); }
    const ms = Date.now() - t0;
    const checks = compare(key, rep);
    if (key.fatal) checks.push({ what: "shows the reason on screen, and no report", expected: true,
      got: /could not|cannot|can't|does not|not a|only knows|will not/i.test(shown.bodyText || ""), ok: /could not|cannot|can't|does not|not a|only knows|will not/i.test(shown.bodyText || "") });
    if (key.controls && key.controls.fileTotalTies === false)
      checks.push({ what: "shows the does-not-tie warning on screen", expected: true, got: !!shown.tieBanner, ok: !!shown.tieBanner });
    if (key.controls && key.controls.fileTotalTies !== false)
      checks.push({ what: "shows no does-not-tie warning", expected: false, got: !!shown.tieBanner, ok: !shown.tieBanner });
    if (errors.length) checks.push({ what: "runs without errors", expected: "no errors", got: errors.join(" | "), ok: false });
    results.push({ id, key, checks, ms, pass: checks.every((c) => c.ok) });
    await page.close();
  }
  await browser.close();

  let passed = 0, totalChecks = 0, failedChecks = 0;
  const lines = [];
  for (const r of results) {
    const fails = r.checks.filter((c) => !c.ok);
    totalChecks += r.checks.length; failedChecks += fails.length; if (r.pass) passed++;
    console.log(`${r.pass ? "PASS" : "FAIL"}  ${r.id}  ${r.key.title}  (${r.checks.length - fails.length}/${r.checks.length} checks, ${r.ms} ms)`);
    for (const f of fails) console.log(`        x ${f.what}: expected ${JSON.stringify(f.expected)}, got ${JSON.stringify(f.got)}`);
    lines.push(`| ${r.id} | ${r.key.title} | ${r.key.kind} | ${r.key.controls ? r.key.controls.linesRead : "-"} | ${r.checks.length - fails.length}/${r.checks.length} | ${r.ms} | ${r.pass ? "PASS" : "**FAIL**"} |`);
    for (const f of fails) lines.push(`| | x ${f.what}: expected \`${JSON.stringify(f.expected)}\`, got \`${JSON.stringify(f.got)}\` | | | | | |`);
  }
  console.log(`\n${passed}/${results.length} cases passed, ${totalChecks - failedChecks}/${totalChecks} checks.`);
  if (mdOut) {
    fs.writeFileSync(mdOut, [
      `Agent file: \`${path.basename(agentPath)}\``, "",
      `**${passed} of ${results.length} cases passed; ${totalChecks - failedChecks} of ${totalChecks} individual checks.**`, "",
      "| Case | What it is | Type | Lines | Checks passed | Run time (ms) | Result |", "|---|---|---|---|---|---|---|", ...lines, ""].join("\n"));
  }
  process.exit(passed === results.length ? 0 : 1);
})();
