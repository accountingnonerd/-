#!/usr/bin/env node
/*
 * Acceptance test for Record-to-Report 01, "Did last year change?".
 *
 *   node run-tests.js [path/to/agent.html] [--md results.md]
 *
 * Opens the agent in a real browser with the network blocked, gives it each case's two files
 * (box 1: input#final, box 2: input#today), reads window.__report and compares it with
 * answer-key.json. The key was worked out from the ledger model in make_cases.py; this script
 * only compares. Any build that passes is "the same agent".
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
const agentPath = path.resolve(positional[0] || path.join(HERE, "../agent/did-last-year-change.html"));
if (!fs.existsSync(agentPath)) { console.error("No such agent file: " + agentPath); process.exit(2); }
console.log("Testing: " + agentPath + "\n");
const KEY = JSON.parse(fs.readFileSync(path.join(HERE, "answer-key.json"), "utf8"));
const XLSX_LOCAL = path.join(HERE, "../../../tools/node_modules/xlsx/dist/xlsx.full.min.js");

const near = (a, b) => typeof a === "number" && typeof b === "number" && Math.abs(a - b) < 0.005;
const norm = (s) => String(s || "").toLowerCase().replace(/&/g, "and").replace(/\(a\/[rp]\)/g, "").replace(/[^a-z0-9]/g, "");

function compare(key, rep) {
  const out = [];
  const check = (what, expected, got, ok) => out.push({ what, expected, got, ok: ok === undefined ? expected === got : ok });
  if (!rep) { check("produces a report", "a report", "nothing"); return out; }
  check("status", key.status, rep.status);
  const codes = [...new Set((rep.exceptions || []).map((e) => e.code))];
  for (const c of key.exceptions) check("raises " + c, "raised", codes.includes(c) ? "raised" : "missing");
  const extra = codes.filter((c) => !key.exceptions.includes(c));
  check("raises nothing else", "none", extra.length ? extra.join(",") : "none");
  if (key.status === "NOT_COMPARABLE") {
    check("lists no account differences", 0, (rep.accounts || []).length);
    check("drafts no entry", null, rep.entry || null);
    return out;
  }
  if (key.asOf) check("date of the balances", key.asOf, rep.asOf);
  if (key.rows) {
    check("accounts read from last year's final", key.rows.final, rep.files && rep.files.final && rep.files.final.rows);
    check("accounts read from today's file", key.rows.today, rep.files && rep.files.today && rep.files.today.rows);
  }
  const accts = rep.accounts || [];
  const real = accts.filter((a) => ["changed", "new", "missing", "aje"].includes(a.status));
  check("number of accounts that differ", key.differences.length, real.length);
  for (const d of key.differences) {
    const a = accts.find((x) => [x.name, x.finalName, x.todayName].some((n) => norm(n) === norm(d.account)));
    if (!a) { check(d.account + ": listed", "listed", "missing"); continue; }
    check(d.account + ": difference", d.diff, a.diff, near(d.diff, a.diff));
    check(d.account + ": " + (d.aje ? "your adjustment not posted" : "changed"), d.aje ? "aje" : "changed", a.status === "aje" ? "aje" : (["changed", "new", "missing"].includes(a.status) ? "changed" : a.status));
    check(d.account + ": type", d.kind, a.type);
  }
  if (key.netIncomeChange === null) check("profit change not given (post-closing)", null, rep.netIncome ? rep.netIncome.change : null);
  else check("change in last year's profit", key.netIncomeChange, rep.netIncome && rep.netIncome.change, near(key.netIncomeChange, rep.netIncome && rep.netIncome.change));
  if (key.retainedEarningsChange !== null)
    check("change in opening retained earnings", key.retainedEarningsChange, rep.retainedEarnings && rep.retainedEarnings.change, near(key.retainedEarningsChange, rep.retainedEarnings && rep.retainedEarnings.change));
  if (!key.entry) check("drafts no entry", null, rep.entry ? "an entry of " + rep.entry.lines.length + " lines" : null);
  else {
    const lines = (rep.entry && rep.entry.lines) || [];
    check("entry lines", key.entry.length, lines.length);
    check("entry dated the first day of the new year", "2026-01-01", rep.entry && rep.entry.date);
    for (const l of key.entry) {
      const g = lines.find((x) => norm(x.account) === norm(l.account));
      if (!g) { check("entry: " + l.account, "present", "missing"); continue; }
      check("entry: " + l.account + " debit", l.debit, g.debit, near(l.debit, g.debit));
      check("entry: " + l.account + " credit", l.credit, g.credit, near(l.credit, g.credit));
    }
    check("entry balances", true, !!rep.entry && near(rep.entry.totalDebit, rep.entry.totalCredit));
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
      await page.setInputFiles("input#final", path.join(HERE, "cases", key.files.final));
      await page.setInputFiles("input#today", path.join(HERE, "cases", key.files.today));
      await page.waitForFunction(() => window.__report !== undefined && window.__report !== null, null, { timeout: 15000 });
      rep = await page.evaluate(() => JSON.parse(JSON.stringify(window.__report)));
      shown = await page.evaluate(() => {
        const vis = (el) => !!el && !el.hidden && el.offsetParent !== null && el.innerText.trim().length > 0;
        return { stop: vis(document.getElementById("stop-banner")), verdict: (document.getElementById("verdict") || {}).innerText || "" };
      });
    } catch (e) { errors.push(String(e).split("\n")[0]); }
    const ms = Date.now() - t0;
    const checks = compare(key, rep);
    const wantStop = key.exceptions.some((c) => ["OUT_OF_BALANCE", "TOTAL_MISMATCH", "NOT_A_TB", "DATE_MISMATCH", "BASIS_MISMATCH", "SAME_FILE"].includes(c));
    checks.push({ what: wantStop ? "shows the stop banner" : "shows no stop banner", expected: wantStop, got: !!shown.stop, ok: wantStop === !!shown.stop });
    const vOk = { AGREES: /still agree/i, CHANGED: /changed|do not have/i, NOT_COMPARABLE: /cannot compare/i }[key.status].test(shown.verdict || "");
    checks.push({ what: "verdict on screen matches the status", expected: key.status, got: (shown.verdict || "").split("\n")[0], ok: vOk });
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
    lines.push(`| ${r.id} | ${r.key.title} | ${r.key.kind} | ${r.key.status} | ${r.checks.length - fails.length}/${r.checks.length} | ${r.ms} | ${r.pass ? "PASS" : "**FAIL**"} |`);
    for (const f of fails) lines.push(`| | x ${f.what}: expected \`${JSON.stringify(f.expected)}\`, got \`${JSON.stringify(f.got)}\` | | | | | |`);
  }
  console.log(`\n${passed}/${results.length} cases passed, ${totalChecks - failedChecks}/${totalChecks} checks.`);
  if (mdOut) {
    fs.writeFileSync(mdOut, [
      `Agent file: \`${path.basename(agentPath)}\``, "",
      `**${passed} of ${results.length} cases passed; ${totalChecks - failedChecks} of ${totalChecks} individual checks.**`, "",
      "| Case | What it is | Type | Expected verdict | Checks passed | Run time (ms) | Result |", "|---|---|---|---|---|---|---|", ...lines, ""].join("\n"));
  }
  process.exit(passed === results.length ? 0 : 1);
})();
