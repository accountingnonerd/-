# Reader test: "Build it yourself" (Series 1, Agent 5)

Sources used: article.txt plus raw GitHub files fetched with curl while logged out (all returned 200). Nothing was read from the local repo except the permitted xlsx.full.min.js fallback.

## Step 1: the prompt
- prompt-github.txt (raw PROMPT.txt) and prompt-article.txt (article lines 121-233): **byte-identical** (`cmp` passes; 113 lines).
- Hesitation: "two small squares, top right of the file". I could not check the icon from curl. The repo is named `-` (github.com/accountingnonerd/-), which looks like a broken link to a non-technical reader.

## Steps 2-4: the AI assistant writes the file
- I wrote the file from the GitHub prompt alone, in one go. It came to about 1,120 lines, in line with the article's "about 1,000 lines".
- Reader hesitation: "If the assistant offers it as a file to download". On claude.ai the code may appear as an artifact or preview panel, not a code block, and the article does not say what to do then.
- Reader hesitation: "save it as what-goes-on-the-asset-schedule.html ... Notepad / TextEdit Make Plain Text". Neither app warns about the classic traps: Notepad saves `.html.txt` unless "Save as type: All files" is chosen, and TextEdit asks "use .html?".

## Step 5: open it
- **Worked**: the screenshot shows "What goes on the asset schedule?" and the drop box (step5-open.png).
- However, the library at cdnjs.cloudflare.com was **blocked by this sandbox's network rules** (proxy 403). The page still looks right at step 5 and only fails at step 6. I served the permitted local copy through page.route.
- The article never says the rebuilt page needs internet. Its repository README says the *ready-made* tool works offline, which suggests the rebuilt one does too.

## Step 6 and "What you should see" (expected vs seen)
| Item | Expected (article/README) | Seen |
|---|---|---|
| First top line | $76,050.00 recorded; $26,980.00 more to decide; 1 sale or write-off to settle | identical |
| Step 2 roles | Equipment, Vehicles FA; AD; Dep exp; 3 review; Fuel/Utilities/Rent ignored | identical |
| 3a | mower $14,800.00 (3/9), F-350 $61,250.00 (5/20) | identical, total $76,050.00 |
| 3b | 7 bills; Clearwater x4 "repeats" | 7 bills; 4 marked "repeats: likely a service contract" |
| 3c gain | $13,375.00 | Gain $13,375.00 |
| 3d | both openings agree; booked $16,800.00 is $7,810.00 lower than $24,610.00 | v1: **AD opening box lost what I typed** (see below); after the fix: agrees / agrees / "books are $7,810.00 lower" |
| Final top line | $88,550.00 to add; 1 asset to take off | identical |
| Entries | AJE1 sprayer 5,600; AJE2 door 6,900; AJE3 AD 39,375 / Veh 16,000 / Veh 42,000 / Gain 13,375; AJE4 7,810 | identical, same order |
| After entries | cost $257,450.00; AD $82,585.00 | identical |

Figures typed were read from the CSVs: 42000.00 and 36750.00 (2025 schedule, F-250 row) and 2625.00 (2026 report, F-250 row); 3d figures as the article gives them.

Reader hesitations in step 6:
- "Capitalize the door and the sprayer and keep the rest as expenses." The page then shows a "to" box (Equipment or Vehicles) and a "why" box. The article says nothing about either; only the sample README says "to Equipment". The default was Equipment, so it worked.
- "Follow the steps on the screen": the "The accounts are right" button is not mentioned in the article (it is in the README). It was still obvious on the screen.
- "1 sale or write-off to settle": "settle" is not explained, but 3c makes it clear.

## Bug found and the fix (troubleshooting)
- v1 (`what-goes-on-the-asset-schedule.v1-as-first-generated.html`): in 3d the page redrew on `change`. When the reader typed 210,900.00 and pressed Tab or clicked the next box, focus fell to the page body, so 97,350.00 went nowhere. The result was that "Accumulated depreciation ... type it above" stayed, and README's "Both opening balances agree" never appeared.
- The article's "If it does not work" has no matching case: the numbers were not different, a box just would not keep its figure. Using "Different numbers: tell the assistant what you expected, quoting the line above", the reader can only quote "Both opening balances agree" and describe what happened.
- Fix (once, as the assistant): redraw on leaving the 3d boxes, not while moving between them, and put focus back where it went, as the prompt already requires for the 3c boxes. Retested by Tab and by click: all three figures kept.
- Minor flaw left in: the 3c table is wider than the page at 1280px, so the Gain column is clipped.

## Suggested edits
1. Under "What you need": "Internet access when you use it: the page loads its spreadsheet reader from cdnjs.cloudflare.com." Add to "If it does not work": "Nothing happens when you drop the file: the page could not load its spreadsheet reader; check the connection or firewall, or use the ready-made tool."
2. Add to "If it does not work": "A box forgets what you typed when you move to the next one: tell the assistant, and ask it to keep what you type in every box (the prompt says so for step 3c)." Optionally add one line to the prompt's 3d: "Work it out when she leaves the boxes, not while she moves between them."
3. In "What you should see": "Capitalize the door and the sprayer (to Equipment, the default; the reason box is optional)" and "press 'The accounts are right' in step 2".
4. In "Save it as a web page": "In Notepad, set Save as type to All files; if TextEdit asks, choose Use .html." Also: "If the assistant shows the page in a preview panel, use its copy or download button."
5. Say where the 3d figures come from: "the Total rows of the two CSV files".

Screenshots: step5-open.png, step6-1-dropped.png, step6-2-accounts-ok.png, step6-3-bills-decided.png, step6-4-sale.png, step6-5-agree.png, step6-5-agree-tab.png, step6-5-agree-click.png, step6-6-workpaper.png, step6-7-full.png, step6-8-print-view.png, step6-8-print.pdf.
