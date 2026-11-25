#!/usr/bin/env node
/*
 * Acceptance test for Acquire-to-Retire 01, "What goes on the asset schedule?".
 *
 *   node run-tests.js [path/to/agent.html] [--md results.md]
 *
 * Opens the agent in a real browser with the network blocked, gives it each case's file through
 * input#file, and where the case says so: chooses an account's role in select.role[data-account],
 * types the threshold into input#threshold and presses button#update-threshold, types last year's
 * schedule and this year's depreciation into input#sched-cost, input#sched-ad, input#tax-dep and
 * presses button#update. It then reads window.__report and compares it with answer-key.json (worked
 * out in make_cases.py from the model). Any build that passes is "the same agent".
 */
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const HERE = __dirname;
const args = process.argv.slice(2);
const mdAt = args.indexOf("--md");
const mdOut = mdAt >= 0 ? args[mdAt + 1] : null;
const positional = args.filter((a, i) => !a.startsWith("--") && !(mdAt >= 0 && i === mdAt + 1));
const agentPath = path.resolve(positional[0] || path.join(HERE, "../agent/what-goes-on-the-asset-schedule.html"));
if (!fs.existsSync(agentPath)) { console.error("No such agent file: " + agentPath); process.exit(2); }
console.log("Testing: " + agentPath + "\n");
const KEY = JSON.parse(fs.readFileSync(path.join(HERE, "answer-key.json"), "utf8"));
const XLSX_LOCAL = path.join(HERE, "../../../tools/node_modules/xlsx/dist/xlsx.full.min.js");
const near = (a, b) => typeof a === "number" && typeof b === "number" && Math.abs(a - b) < 0.005;
const m2 = (v) => (typeof v === "number" ? v.toFixed(2) : String(v));
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
  check("period", key.period ? key.period.from + " to " + key.period.to : "none", rep.period ? rep.period.from + " to " + rep.period.to : "none");
  for (const [name, role] of Object.entries(key.accounts)) check("account role: " + name, role, rep.accounts && rep.accounts[name]);
  check("accounts read", Object.keys(key.accounts).length, rep.accounts ? Object.keys(rep.accounts).length : 0);
  check("cost roll-forward", pairs(key.rollforward, (r) => `${r.account}: ${m2(r.opening)} + ${m2(r.additions)} ${m2(r.disposals)} = ${m2(r.ending)}`),
    pairs(rep.rollforward, (r) => `${r.account}: ${m2(r.opening)} + ${m2(r.additions)} ${m2(r.disposals)} = ${m2(r.ending)}`));
  check("accumulated depreciation roll-forward", pairs(key.adRollforward, (r) => `${r.account}: ${m2(r.opening)} ${m2(r.credits)} + ${m2(r.debits)} = ${m2(r.ending)}`),
    pairs(rep.adRollforward, (r) => `${r.account}: ${m2(r.opening)} ${m2(r.credits)} + ${m2(r.debits)} = ${m2(r.ending)}`));
  check("additions", pairs(key.additions, (x) => `${x.account} ${x.date} ${x.name} ${m2(x.amount)} je:${x.journal}`), pairs(rep.additions, (x) => `${x.account} ${x.date} ${x.name} ${m2(x.amount)} je:${x.journal}`));
  check("disposals", pairs(key.disposals, (x) => `${x.account} ${x.date} ${x.name} ${m2(x.amount)}`), pairs(rep.disposals, (x) => `${x.account} ${x.date} ${x.name} ${m2(x.amount)}`));
  check("reversals", pairs(key.reversals, (x) => `${x.account} ${x.name} ${m2(x.amount)}`), pairs(rep.reversals, (x) => `${x.account} ${x.name} ${m2(x.amount)}`));
  check("purchases in expense accounts", pairs(key.candidates, (x) => `${x.account} ${x.date} ${x.name} ${m2(x.amount)} lines:${x.lines}`),
    pairs(rep.candidates, (x) => `${x.account} ${x.date} ${x.name} ${m2(x.amount)} lines:${x.lines}`));
  check("routine charges", pairs(key.routine, (x) => `${x.account} ${x.name} ${x.count} ${m2(x.amount)}`), pairs(rep.routine, (x) => `${x.account} ${x.name} ${x.count} ${m2(x.amount)}`));
  for (const f of ["costOpening", "adOpening", "costEnding", "adEnding", "additionsTotal", "candidatesTotal", "depreciationBooked", "threshold"])
    check(f, key[f], rep[f], near(key[f], rep[f]));
  for (const f of ["taxDepreciation", "depreciationAdjustment", "scheduleCost", "scheduleAD", "openingDiffCost", "openingDiffAD"])
    if (key[f] !== undefined) check(f, key[f], rep[f], near(key[f], rep[f]));
  if (key.notAddUp) check("accounts that do not add up", key.notAddUp.join(","), (rep.notAddUp || []).join(","));
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
      const wait = async (before) => page.waitForFunction((b) => window.__report && JSON.stringify(window.__report) !== b, before, { timeout: 10000 });
      if (key.setRoles) {
        const first = await page.evaluate(() => (window.__report.exceptions || []).map((e) => e.code));
        for (const c of key.firstExceptions || []) if (!first.includes(c)) errors.push("before the role was changed, expected " + c);
        for (const [acc, role] of Object.entries(key.setRoles)) {
          const before = await page.evaluate(() => JSON.stringify(window.__report));
          await page.selectOption(`select.role[data-account="${acc}"]`, role);
          await wait(before);
        }
      }
      if (key.typed && key.typed.threshold !== undefined) {
        const before = await page.evaluate(() => JSON.stringify(window.__report));
        await page.fill("input#threshold", key.typed.threshold.toFixed(2));
        await page.click("button#update-threshold");
        await wait(before);
      }
      if (key.typed && (key.typed.scheduleCost !== undefined || key.typed.taxDepreciation !== undefined)) {
        const before = await page.evaluate(() => JSON.stringify(window.__report));
        if (key.typed.scheduleCost !== undefined) await page.fill("input#sched-cost", key.typed.scheduleCost.toFixed(2));
        if (key.typed.scheduleAD !== undefined) await page.fill("input#sched-ad", key.typed.scheduleAD.toFixed(2));
        if (key.typed.taxDepreciation !== undefined) await page.fill("input#tax-dep", key.typed.taxDepreciation.toFixed(2));
        await page.click("button#update");
        await wait(before);
      }
      rep = await page.evaluate(() => JSON.parse(JSON.stringify(window.__report)));
      shown = await page.evaluate(() => {
        const vis = (el) => !!el && !el.hidden && el.offsetParent !== null && el.innerText.trim().length > 0;
        return { stop: vis(document.getElementById("stop-banner")) || vis(document.getElementById("problem")) };
      });
    } catch (e) { errors.push(String(e).split("\n")[0]); }
    const ms = Date.now() - t0;
    const checks = compare(key, rep);
    const wantStop = key.exceptions.some((c) => ["NOT_RECOGNIZED", "FILE_DOES_NOT_ADD_UP", "UNREAD_ROWS"].includes(c));
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
