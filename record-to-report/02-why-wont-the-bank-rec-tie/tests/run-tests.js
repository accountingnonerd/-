#!/usr/bin/env node
/*
 * Acceptance test for Record-to-Report 02, "Why won't the bank rec tie?".
 *
 *   node run-tests.js [path/to/agent.html] [--md results.md]
 *
 * Opens the agent in a real browser with the network blocked, gives it each case's two files through
 * input#bank-file and input#books-file, and where the case says so chooses the account in
 * select#account and types the statement's balances into input#bank-begin and input#bank-end and
 * presses button#update-balances. It then reads window.__report and compares it with
 * answer-key.json (worked out in make_cases.py with rules.py). Any build that passes is "the same agent".
 */
const fs = require("fs"), path = require("path"), { chromium } = require("playwright");
const HERE = __dirname, args = process.argv.slice(2), mdAt = args.indexOf("--md"), mdOut = mdAt >= 0 ? args[mdAt + 1] : null;
const positional = args.filter((a, i) => !a.startsWith("--") && !(mdAt >= 0 && i === mdAt + 1));
const agentPath = path.resolve(positional[0] || path.join(HERE, "../agent/why-wont-the-bank-rec-tie.html"));
if (!fs.existsSync(agentPath)) { console.error("No such agent file: " + agentPath); process.exit(2); }
console.log("Testing: " + agentPath + "\n");
const KEY = JSON.parse(fs.readFileSync(path.join(HERE, "answer-key.json"), "utf8"));
const XLSX_LOCAL = path.join(HERE, "../../../tools/node_modules/xlsx/dist/xlsx.full.min.js");
const near = (a, b) => typeof a === "number" && typeof b === "number" && Math.abs(a - b) < 0.005;
const m2 = (v) => (typeof v === "number" ? v.toFixed(2) : String(v));
const pairs = (list, f) => (list || []).map(f).sort().join(" | ");

function compare(key, rep) {
  const out = [], check = (what, expected, got, ok) => out.push({ what, expected, got, ok: ok === undefined ? expected === got : ok });
  if (!rep) { check("produces a report", "a report", "nothing"); return out; }
  check("status", key.status, rep.status);
  const codes = [...new Set((rep.exceptions || []).map((e) => e.code))];
  for (const c of key.exceptions) check("raises " + c, "raised", codes.includes(c) ? "raised" : "missing");
  const extra = codes.filter((c) => !key.exceptions.includes(c));
  check("raises nothing else", "none", extra.length ? extra.join(",") : "none");
  if (key.status === "NOT_RECOGNIZED" || key.stopOnly) return out;
  for (const f of ["account", "bankStart", "bankEnd", "bankLines", "matched", "clearedBefore", "afterStatement", "stale", "oldOutstanding", "lateItems", "startMode", "startCandidates", "undecided", "ties"]) check(f, key[f], Array.isArray(rep[f]) ? rep[f].length : rep[f]);
  check("accounts read", key.accounts.join(","), (rep.accounts || []).join(","));
  for (const f of ["bankBegin", "bankEnding", "booksEnding", "bookCorrections", "bankCorrections", "adjustedBank", "adjustedBooks", "difference", "startLeft"])
    check(f, key[f], rep[f], key[f] === null ? rep[f] === null : near(key[f], rep[f]));
  check("batches", pairs(key.batches, (x) => `${x.bankDate} ${m2(x.amount)} x${x.count}`), pairs(rep.batches, (x) => `${x.bankDate} ${m2(x.amount)} x${x.count}`));
  const nk = (x) => `${x.kind} ${x.decision} bank ${x.bankDate} ${m2(x.bankAmount)} book ${x.bookDate} ${m2(x.bookAmount)} #${x.num}`;
  check("book entries that look wrong", pairs(key.near, nk), pairs(rep.near, nk));
  check("entered twice", pairs(key.duplicates, (x) => `${x.date} ${m2(x.amount)} ${x.name}`), pairs(rep.duplicates, (x) => `${x.date} ${m2(x.amount)} ${x.name}`));
  const ok = (x) => `${x.date} #${x.num} ${m2(x.amount)} ${x.age}d`;
  check("outstanding", pairs(key.outstanding, ok), pairs(rep.outstanding, ok));
  check("at the bank, not in the books", pairs(key.bankOnly, (x) => `${x.date} ${m2(x.amount)} ${x.kind}`), pairs(rep.bankOnly, (x) => `${x.date} ${m2(x.amount)} ${x.kind}`));
  check("suggested as recorded before the books file", pairs(key.suggestBank, (x) => `${x.date} ${m2(x.amount)}`), pairs(rep.suggestBank, (x) => `${x.date} ${m2(x.amount)}`));
  check("one book entry to several bank lines", pairs(key.splits, (x) => `${x.bookDate} ${m2(x.amount)} x${x.count}`), pairs(rep.splits, (x) => `${x.bookDate} ${m2(x.amount)} x${x.count}`));
  return out;
}

(async () => {
  const browser = await chromium.launch(), results = [];
  for (const id of Object.keys(KEY).sort()) {
    const key = KEY[id], page = await browser.newPage(), errors = [];
    page.on("pageerror", (e) => errors.push(String(e)));
    await page.route(/^https?:/, (route) => (/xlsx/i.test(route.request().url()) ? route.fulfill({ path: XLSX_LOCAL, contentType: "application/javascript" }) : route.abort()));
    await page.goto("file://" + agentPath);
    const t0 = Date.now(); let rep = null, shown = {};
    try {
      await page.setInputFiles("input#bank-file", path.join(HERE, "cases", key.bankFile));
      await page.setInputFiles("input#books-file", path.join(HERE, "cases", key.booksFile));
      await page.waitForFunction(() => window.__report !== undefined && window.__report !== null, null, { timeout: 20000 });
      const wait = async (before) => page.waitForFunction((b) => window.__report && JSON.stringify(window.__report) !== b, before, { timeout: 10000 });
      if (key.chooseAccount) { const b = await page.evaluate(() => JSON.stringify(window.__report)); await page.selectOption("select#account", key.chooseAccount); await wait(b); }
      if (key.typed) {
        const b = await page.evaluate(() => JSON.stringify(window.__report));
        await page.fill("input#bank-begin", key.typed.bankBegin.toFixed(2)); await page.fill("input#bank-end", key.typed.bankEnd.toFixed(2));
        await page.click("button#update-balances"); await wait(b);
      }
      if (key.ticks) for (const [side, d, a] of key.ticks) {         // the accountant ticks what was outstanding at the start
        const list = await page.evaluate((s) => (s === "book" ? window.__report.startCandidates : window.__report.suggestBank), side);
        const hit = list.find((x) => x.date === d && Math.abs(x.amount - a) < 0.005);
        if (!hit) { errors.push("nothing to tick for " + side + " " + d + " " + a); continue; }
        const b = await page.evaluate(() => JSON.stringify(window.__report)); await page.check(`input.tick[data-id="${hit.id}"]`); await wait(b);
      }
      if (key.decide) for (const [id, choice] of key.decide) {         // the accountant's decisions in step 3a
        const b = await page.evaluate(() => JSON.stringify(window.__report)); await page.check(`input.dec[data-id="${id}"][value="${choice}"]`); await wait(b);
      }
      rep = await page.evaluate(() => JSON.parse(JSON.stringify(window.__report)));
      shown = await page.evaluate(() => { const vis = (el) => !!el && !el.hidden && el.offsetParent !== null && el.innerText.trim().length > 0;
        return { stop: vis(document.getElementById("stop-banner")) || vis(document.getElementById("problem")), boxes: !!document.getElementById("bank-begin") }; });
    } catch (e) { errors.push(String(e).split("\n")[0]); }
    const ms = Date.now() - t0, checks = compare(key, rep);
    const wantStop = key.exceptions.some((c) => ["NOT_RECOGNIZED", "BANK_FILE_GAPS", "BOOKS_DO_NOT_ADD_UP", "UNREAD_ROWS", "BALANCES_DISAGREE", "CARD_NOT_SUPPORTED"].includes(c));
    checks.push({ what: wantStop ? "shows the stop message" : "shows no stop message", expected: wantStop, got: !!shown.stop, ok: wantStop === !!shown.stop });
    if (key.typed) checks.push({ what: "keeps the balance boxes to correct them", expected: true, got: !!shown.boxes, ok: !!shown.boxes });
    if (errors.length) checks.push({ what: "runs without errors", expected: "no errors", got: errors.join(" | "), ok: false });
    results.push({ id, key, checks, ms, pass: checks.every((c) => c.ok) });
    await page.close();
  }
  await browser.close();
  let passed = 0, total = 0, failed = 0; const lines = [];
  for (const r of results) {
    const fails = r.checks.filter((c) => !c.ok); total += r.checks.length; failed += fails.length; if (r.pass) passed++;
    console.log(`${r.pass ? "PASS" : "FAIL"}  ${r.id}  ${r.key.title}  (${r.checks.length - fails.length}/${r.checks.length} checks, ${r.ms} ms)`);
    for (const f of fails) console.log(`        x ${f.what}: expected ${JSON.stringify(f.expected)}, got ${JSON.stringify(f.got)}`);
    lines.push(`| ${r.id} | ${r.key.title} | ${r.key.kind} | ${r.checks.length - fails.length}/${r.checks.length} | ${r.ms} | ${r.pass ? "PASS" : "**FAIL**"} |`);
    for (const f of fails) lines.push(`| | x ${f.what}: expected \`${JSON.stringify(f.expected)}\`, got \`${JSON.stringify(f.got)}\` | | | | |`);
  }
  console.log(`\n${passed}/${results.length} cases passed, ${total - failed}/${total} checks.`);
  if (mdOut) fs.writeFileSync(mdOut, [`Agent file: \`${path.basename(agentPath)}\``, "", `**${passed} of ${results.length} cases passed; ${total - failed} of ${total} individual checks.**`, "",
    "| Case | What it is | Type | Checks passed | Run time (ms) | Result |", "|---|---|---|---|---|---|", ...lines, ""].join("\n"));
  process.exit(passed === results.length ? 0 : 1);
})();
