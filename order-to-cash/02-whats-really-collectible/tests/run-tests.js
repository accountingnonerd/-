#!/usr/bin/env node
/*
 * Acceptance test for Order-to-Cash 02, "What's really collectible?".
 *
 *   node run-tests.js [path/to/agent.html] [--md results.md]
 *
 * Opens the agent in a real browser with the network blocked, gives it each case's file through
 * input#file, types A/R from the balance sheet into input#ar and presses button#compare where the
 * case has one, types allowance rates into input#rate-<bucket> and presses button#apply-rates where
 * the case has them, reads window.__report and compares it with answer-key.json (worked out in
 * make_cases.py from the model). Any build that passes is "the same agent".
 */
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const HERE = __dirname;
const args = process.argv.slice(2);
const mdAt = args.indexOf("--md");
const mdOut = mdAt >= 0 ? args[mdAt + 1] : null;
const positional = args.filter((a, i) => !a.startsWith("--") && !(mdAt >= 0 && i === mdAt + 1));
const agentPath = path.resolve(positional[0] || path.join(HERE, "../agent/whats-really-collectible.html"));
if (!fs.existsSync(agentPath)) { console.error("No such agent file: " + agentPath); process.exit(2); }
console.log("Testing: " + agentPath + "\n");
const KEY = JSON.parse(fs.readFileSync(path.join(HERE, "answer-key.json"), "utf8"));
const XLSX_LOCAL = path.join(HERE, "../../../tools/node_modules/xlsx/dist/xlsx.full.min.js");
const BUCKETS = ["current", "d1_30", "d31_60", "d61_90", "d91_180", "d181_365", "over365"];
const near = (a, b) => typeof a === "number" && typeof b === "number" && Math.abs(a - b) < 0.005;
const pairs = (list, f) => (list || []).map(f).sort().join(" | ");

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
  check("as-of date", key.asOf, rep.asOf);
  check("open items read", key.rows, rep.rows);
  check("total owed", key.total, rep.total, near(key.total, rep.total));
  check("customers", key.customers, rep.customers);
  for (const b of BUCKETS) {
    check("aging as reported: " + b, key.buckets[b], rep.buckets && rep.buckets[b], near(key.buckets[b], rep.buckets && rep.buckets[b]));
    check("aging after clean-up: " + b, key.bucketsClean[b], rep.bucketsClean && rep.bucketsClean[b], near(key.bucketsClean[b], rep.bucketsClean && rep.bucketsClean[b]));
  }
  check("credits matched exactly", pairs(key.matches, (m) => `${m.customer}: ${m.credit} -> ${m.invoice} ${m.amount.toFixed(2)}`), pairs(rep.matches, (m) => `${m.customer}: ${m.credit} -> ${m.invoice} ${Number(m.amount).toFixed(2)}`));
  check("credits applied to oldest invoices", pairs(key.applyOldest, (m) => `${m.customer}: ${m.credit} ${m.amount.toFixed(2)}`), pairs(rep.applyOldest, (m) => `${m.customer}: ${m.credit} ${Number(m.amount).toFixed(2)}`));
  check("customers in credit", pairs(key.creditBalances, (m) => `${m.customer} ${m.amount.toFixed(2)}`), pairs(rep.creditBalances, (m) => `${m.customer} ${Number(m.amount).toFixed(2)}`));
  check("duplicate invoices", pairs(key.duplicates, (m) => `${m.customer}: ${m.a}/${m.b}`), pairs(rep.duplicates, (m) => `${m.customer}: ${m.a}/${m.b}`));
  check("small balances", key.small.join(","), (rep.small || []).join(","));
  check("over a year", key.old.join(","), (rep.old || []).join(","));
  check("proposed write-off", key.writeOff, rep.writeOff, near(key.writeOff, rep.writeOff));
  check("journal entries in A/R", key.journalEntries, rep.journalEntries);
  check("concentration", pairs(key.concentration, (m) => `${m.customer} ${m.share}`), pairs(rep.concentration, (m) => `${m.customer} ${m.share}`));
  const w = rep.worklist || [];
  check("customers to chase", key.worklist.length, w.length);
  key.worklist.forEach((k, i) => {
    const g = w[i] || {};
    check(`chase #${i + 1}: customer`, k.customer, g.customer);
    check(`chase #${i + 1}: overdue`, k.overdue, g.overdue, near(k.overdue, g.overdue));
    check(`chase #${i + 1}: oldest days`, k.oldestDays, g.oldestDays);
    check(`chase #${i + 1}: next step`, k.step, g.step);
  });
  if (key.typedAR !== undefined) check("difference from the balance sheet", key.difference, rep.difference, near(key.difference, rep.difference));
  if (key.allowance !== undefined) check("allowance", key.allowance, rep.allowance, near(key.allowance, rep.allowance));
  if (key.duplicates_removed !== undefined) check("duplicate lines removed", key.duplicates_removed, rep.duplicates_removed);
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
      if (key.typedAR !== undefined) {
        await page.fill("input#ar", key.typedAR.toFixed(2));
        await page.click("button#compare");
        await page.waitForFunction(() => window.__report && (window.__report.status === "TIES" || window.__report.status === "DIFFERS"), null, { timeout: 10000 });
      }
      if (key.rates) {
        for (const b of BUCKETS) await page.fill("input#rate-" + b, String(key.rates[b]));
        await page.click("button#apply-rates");
        await page.waitForFunction(() => window.__report && window.__report.allowance !== undefined && window.__report.allowance !== null, null, { timeout: 10000 });
      }
      rep = await page.evaluate(() => JSON.parse(JSON.stringify(window.__report)));
      shown = await page.evaluate(() => {
        const vis = (el) => !!el && !el.hidden && el.offsetParent !== null && el.innerText.trim().length > 0;
        return { stop: vis(document.getElementById("stop-banner")) || vis(document.getElementById("problem")) };
      });
    } catch (e) { errors.push(String(e).split("\n")[0]); }
    const ms = Date.now() - t0;
    const checks = compare(key, rep);
    const wantStop = key.exceptions.some((c) => ["NOT_RECOGNIZED", "SUMMARY_ONLY", "DUPLICATE_ROWS", "TOTAL_MISMATCH", "DIFFERS_FROM_BALANCE_SHEET", "UNREAD_ROWS"].includes(c));
    checks.push({ what: wantStop ? "shows the stop message" : "shows no stop message", expected: wantStop, got: !!shown.stop, ok: wantStop === !!shown.stop });
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
