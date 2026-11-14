#!/usr/bin/env node
/*
 * Acceptance test for Order-to-Cash 01, "Does the 1099-K tie?".
 *
 *   node run-tests.js [path/to/agent.html] [--md results.md]
 *
 * Opens the agent in a real browser with the network blocked, gives it each case's file through
 * input#file, types box 1a into input#box1a and presses button#compare where the case has one,
 * reads window.__report and compares it with answer-key.json (worked out in make_cases.py from
 * the transaction model). Any build that passes is "the same agent".
 *
 * Needs: playwright, and xlsx@0.18.5 in ../../../tools (served in place of the CDN copy).
 */
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const HERE = __dirname;
const args = process.argv.slice(2);
const mdAt = args.indexOf("--md");
const mdOut = mdAt >= 0 ? args[mdAt + 1] : null;
const positional = args.filter((a, i) => !a.startsWith("--") && !(mdAt >= 0 && i === mdAt + 1));
const agentPath = path.resolve(positional[0] || path.join(HERE, "../agent/does-the-1099k-tie.html"));
if (!fs.existsSync(agentPath)) { console.error("No such agent file: " + agentPath); process.exit(2); }
console.log("Testing: " + agentPath + "\n");
const KEY = JSON.parse(fs.readFileSync(path.join(HERE, "answer-key.json"), "utf8"));
const XLSX_LOCAL = path.join(HERE, "../../../tools/node_modules/xlsx/dist/xlsx.full.min.js");
const near = (a, b) => typeof a === "number" && typeof b === "number" && Math.abs(a - b) < 0.005;

function compare(key, rep) {
  const out = [];
  const check = (what, expected, got, ok) => out.push({ what, expected, got, ok: ok === undefined ? expected === got : ok });
  if (!rep) { check("produces a report", "a report", "nothing"); return out; }
  check("status", key.status, rep.status);
  const codes = [...new Set((rep.exceptions || []).map((e) => e.code))];
  for (const c of key.exceptions) check("raises " + c, "raised", codes.includes(c) ? "raised" : "missing");
  const extra = codes.filter((c) => !key.exceptions.includes(c));
  check("raises nothing else", "none", extra.length ? extra.join(",") : "none");
  if (key.status === "NOT_RECOGNIZED") return out;
  if (key.processor) check("processor", key.processor, rep.processor);
  check("year", key.year, rep.year);
  check("box 1a (gross)", key.box1a, rep.box1a, near(key.box1a, rep.box1a));
  check("box 3 (number of payments)", key.box3, rep.box3);
  for (let m = 0; m < 12; m++) check("box 5" + "abcdefghijkl"[m] + " (month " + (m + 1) + ")", key.monthly[m], rep.monthly && rep.monthly[m], near(key.monthly[m], rep.monthly && rep.monthly[m]));
  for (const [k, v] of Object.entries(key.bridge)) check("bridge: " + k, v, rep.bridge && rep.bridge[k], near(v, rep.bridge && rep.bridge[k]));
  const lines = (rep.entry && rep.entry.lines) || [];
  check("entry lines", key.entry.length, lines.length);
  for (const l of key.entry) {
    const g = lines.find((x) => x.account === l.account);
    if (!g) { check("entry: " + l.account, "present", "missing"); continue; }
    check("entry: " + l.account + " debit", l.debit, g.debit, near(l.debit, g.debit));
    check("entry: " + l.account + " credit", l.credit, g.credit, near(l.credit, g.credit));
  }
  check("entry balances", true, !!rep.entry && near(rep.entry.totalDebit, rep.entry.totalCredit));
  if (key.typedBox1a !== undefined) {
    check("box 1a typed", key.typedBox1a, rep.typedBox1a, near(key.typedBox1a, rep.typedBox1a));
    check("difference from the 1099-K", key.difference, rep.difference, near(key.difference, rep.difference));
  }
  if (key.boundary) {
    check("January 1 UTC sales: count", key.boundary.count, rep.boundary && rep.boundary.count);
    check("January 1 UTC sales: amount", key.boundary.amount, rep.boundary && rep.boundary.amount, near(key.boundary.amount, rep.boundary && rep.boundary.amount));
  }
  if (key.duplicates !== undefined) check("duplicate lines removed", key.duplicates, rep.duplicates);
  if (key.missingMonths) check("missing months", key.missingMonths.join(","), (rep.missingMonths || []).join(","));
  if (key.outside) check("lines outside the year", key.outside.count, rep.outside && rep.outside.count);
  if (key.foreign) {
    check("foreign-currency sales", key.foreign.count, rep.foreign && rep.foreign.count);
    check("foreign-currency sales in dollars", key.foreign.usd, rep.foreign && rep.foreign.usd, near(key.foreign.usd, rep.foreign && rep.foreign.usd));
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
    await page.route(/^https?:/, (route) => {
      if (/xlsx/i.test(route.request().url())) route.fulfill({ path: XLSX_LOCAL, contentType: "application/javascript" });
      else route.abort();
    });
    await page.goto("file://" + agentPath);
    const t0 = Date.now();
    let rep = null, shown = {};
    try {
      await page.setInputFiles("input#file", path.join(HERE, "cases", key.file));
      await page.waitForFunction(() => window.__report !== undefined && window.__report !== null, null, { timeout: 20000 });
      if (key.typedBox1a !== undefined) {
        await page.fill("input#box1a", key.typedBox1a.toFixed(2));
        await page.click("button#compare");
        await page.waitForFunction(() => window.__report && (window.__report.status === "TIES" || window.__report.status === "DIFFERS"), null, { timeout: 10000 });
      }
      rep = await page.evaluate(() => JSON.parse(JSON.stringify(window.__report)));
      shown = await page.evaluate(() => {
        const vis = (el) => !!el && !el.hidden && el.offsetParent !== null && el.innerText.trim().length > 0;
        return { stop: vis(document.getElementById("stop-banner")) || vis(document.getElementById("problem")), verdict: (document.getElementById("verdict") || document.getElementById("problem") || {}).innerText || "" };
      });
    } catch (e) { errors.push(String(e).split("\n")[0]); }
    const ms = Date.now() - t0;
    const checks = compare(key, rep);
    const wantStop = key.exceptions.some((c) => ["NOT_RECOGNIZED", "DUPLICATE_ROWS", "MISSING_MONTH", "DIFFERS_FROM_1099K", "UNREAD_ROWS"].includes(c));
    checks.push({ what: wantStop ? "shows the stop message" : "shows no stop message", expected: wantStop, got: !!shown.stop, ok: wantStop === !!shown.stop });
    const vOk = { COMPUTED: /should show/i, TIES: /ties/i, DIFFERS: /does not tie/i, NOT_RECOGNIZED: /not an export|cannot read/i }[key.status].test(shown.verdict || "");
    checks.push({ what: "verdict on screen matches the status", expected: key.status, got: (shown.verdict || "").split("\n")[0].slice(0, 90), ok: vOk });
    if (errors.length) checks.push({ what: "runs without errors", expected: "no errors", got: errors.join(" | "), ok: false });
    results.push({ id, key, checks, ms, pass: checks.every((c) => c.ok) });
    await page.close();
  }
  await browser.close();
  let passed = 0, total = 0, failed = 0;
  const lines = [];
  for (const r of results) {
    const fails = r.checks.filter((c) => !c.ok);
    total += r.checks.length; failed += fails.length; if (r.pass) passed++;
    console.log(`${r.pass ? "PASS" : "FAIL"}  ${r.id}  ${r.key.title}  (${r.checks.length - fails.length}/${r.checks.length} checks, ${r.ms} ms)`);
    for (const f of fails) console.log(`        x ${f.what}: expected ${JSON.stringify(f.expected)}, got ${JSON.stringify(f.got)}`);
    lines.push(`| ${r.id} | ${r.key.title} | ${r.key.kind} | ${r.key.status} | ${r.checks.length - fails.length}/${r.checks.length} | ${r.ms} | ${r.pass ? "PASS" : "**FAIL**"} |`);
    for (const f of fails) lines.push(`| | x ${f.what}: expected \`${JSON.stringify(f.expected)}\`, got \`${JSON.stringify(f.got)}\` | | | | | |`);
  }
  console.log(`\n${passed}/${results.length} cases passed, ${total - failed}/${total} checks.`);
  if (mdOut) fs.writeFileSync(mdOut, [`Agent file: \`${path.basename(agentPath)}\``, "", `**${passed} of ${results.length} cases passed; ${total - failed} of ${total} individual checks.**`, "",
    "| Case | What it is | Type | Expected verdict | Checks passed | Run time (ms) | Result |", "|---|---|---|---|---|---|---|", ...lines, ""].join("\n"));
  process.exit(passed === results.length ? 0 : 1);
})();
