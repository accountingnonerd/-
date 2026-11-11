# Script for testing with a real accountant

About 25 minutes. One accountant, one observer (you). The point is to watch where she
stops, not to teach her the tool. Do not explain anything unless the script says to.

## Before she arrives
- A laptop with a mouse, internet on, browser open on a blank tab.
- On the desktop: `who-gets-a-1099.html`, and from `tests/cases/` these three files,
  renamed so they look like client work:
  - `03-quickbooks-style-by-vendor.xlsx` as `Northwind Auto Repair 2026.xlsx`
  - `10-planted-totals-do-not-tie.xlsx` as `Alder Creek Farm Supply 2026.xlsx`
  - `04-vendor-name-variants.csv` as `Larkspur Cafe 2026.csv`
- A printed copy of the Northwind file (print the spreadsheet), a calculator, a pen.
- A stopwatch and this sheet.

## Part 1. By hand (10 minutes, timed)
Say exactly: *"This is a client's payments for 2026. Please list who gets a 1099 and for
how much, the way you would in January. Use whatever you normally use. Tell me when you
would sign off on the list."*

Hand her the printout. Start the stopwatch. Do not help.

Write down:
- [ ] Minutes until she says she is done (stop her at 15 if not): ______
- [ ] Her list: vendors and amounts.
- [ ] Did she ask what the dollar limit is this year, or use $600 from memory? ______
- [ ] Did she tie anything to a total? ______

## Part 2. The page, cold (5 minutes, timed)
Say exactly: *"A colleague sent you the file on the desktop called who-gets-a-1099. Try it
on Northwind. Think out loud."* Then say nothing.

Start the stopwatch when she double-clicks the file.

- [ ] Seconds until she drops or chooses the file: ______ (target: under 30)
- [ ] Anything she read aloud with a question in her voice: ______
- [ ] Seconds from the worksheet appearing until she can name one vendor that gets a
      1099: ______
- [ ] Did she find the print button without being told? ______
- [ ] Did she open "Show the lines behind this" on any vendor? ______

Then ask, and write her words:
1. "Which of these would you file without looking further?"
2. "What would you do about Apex Diagnostics Inc?" (It is in "Probably exempt": the right
   answer is "check the W-9".)
3. "What would you do about Miller Hardware & Repair?" (Judgment section: parts or a
   separate sale.)
4. "Do you believe the totals? Why?"
5. Compare with her Part 1 list. Any vendor on one and not the other: ask her which is right.

## Part 3. The planted error (3 minutes)
Say: *"Now try Alder Creek."*

- [ ] Did she notice the red STOP box without prompting? ______
- [ ] In her words, what is wrong with the file? ______
      (Right answer: the vendor subtotal says $4,300 but the lines add to $3,100; the
      export is missing a $1,200 line.)
- [ ] What would she do next? ______ (Right answer: get a fresh export, not file from this.)

## Part 4. The spelling case (3 minutes)
Say: *"Now Larkspur Cafe."*

- [ ] Did she see that Rivera Plumbing was combined from three spellings? ______
- [ ] What would she do about "Mike Chen" and "Mike Chen Electric"? ______
- [ ] Did she agree that Smith Electric and Smith Roofing are different vendors? ______

## Part 5. Three questions to end (4 minutes)
1. "Would you put this printout in the workpaper file as it is? What is missing?"
2. "What on the page did you not trust?"
3. "What is the most tedious thing you will do this January that this does not help with?"
   (This answer goes in `BACKLOG.md`.)

## What to send back
The filled-in sheet, a photo of her Part 1 list, and the three printouts if she marked
them up. The minutes from Part 1 replace the estimates in `tests/MANUAL-BASELINE.md`.
