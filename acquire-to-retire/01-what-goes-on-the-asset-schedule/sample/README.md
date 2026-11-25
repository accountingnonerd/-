# Sample: Ridgeline Landscaping LLC (invented)

Use these files to try the tool, or to check a version you rebuilt from the prompt, before you use a
real client's file. Everything here is made up: the business, the people, the vendors, the amounts.

| File | What it is |
|---|---|
| `ridgeline-general-ledger-2026.xlsx` | The client's general ledger for 2026, as QuickBooks Online exports it (Reports, General Ledger, Export to Excel). This is the file you drop in. |
| `ridgeline-depreciation-schedule-2025.csv` | Last year's depreciation schedule: each asset's cost and accumulated depreciation at December 31, 2025. |
| `ridgeline-depreciation-2026-from-tax-software.csv` | This year's depreciation by asset, from the tax software, before the purchases found in expense accounts are added. Total $24,610.00. |

## What you should see

**Step 1. Drop in the ledger.** The line at the top reads:

> Ridgeline Landscaping LLC: $76,050.00 recorded as assets this year; $26,980.00 more found in
> expense accounts for you to decide; 1 sale or write-off to settle.

**Step 2. Check the accounts.** Equipment and Vehicles are fixed assets. Accumulated Depreciation and
Depreciation Expense are what they say. Repairs and Maintenance, Office Supplies & Software, and
Small Tools and Equipment are expense accounts to check. Fuel, Utilities and Rent are ignored. They
are right, so press "The accounts are right".

**Step 3a. Recorded as assets:** the zero-turn mower, $14,800.00 (March 9), and the 2026 F-350,
$61,250.00 (May 20).

**Step 3b. Seven bills to decide.** The page decides none of them. A reasonable set of decisions:

| Bill | Amount | Decision | Why |
|---|---|---|---|
| Coastal Door Co, replace shop overhead door | $6,900.00 | Capitalize, to Equipment | It replaces a whole component of the building, which the repair regulations can treat as a restoration. A judgment call, and yours to make. |
| Greenfield Tools, trailer-mounted sprayer | $5,600.00 | Capitalize, to Equipment | New equipment over the limit. |
| Summit Office Systems, laptops (2) and docking station | $3,480.00 | Keep as expense | Each item is $2,500 or less: de minimis, per item. |
| Clearwater Irrigation, quarterly maintenance (4 bills, marked "repeats") | $2,750.00 each | Keep as expense | A service contract. |

**Step 3c. The sold truck.** $16,000.00 received from Jones Turf Services on June 3 was credited to
Vehicles. It was the 2017 Ford F-250. Type three figures:
- its cost, **42,000.00** (last year's schedule);
- its depreciation at the end of last year, **36,750.00** (last year's schedule);
- its depreciation this year up to the sale, **2,625.00** (this year's report).

The page shows a **gain of $13,375.00**.

**Step 3d. Does it agree?** Type the Total rows of the two schedules, 210,900.00 and 97,350.00, and this year's total, 24,610.00, then press Compare. Both opening balances agree.
Depreciation booked, $16,800.00, is $7,810.00 lower than $24,610.00.

**Step 4. The workpaper.** The line at the top now reads "Ridgeline Landscaping LLC: $88,550.00 to add
to the depreciation schedule; 1 asset to take off."
- **Add to the schedule:** the mower, the F-350, the sprayer and the door, $88,550.00 in total.
- **Take off:** the 2017 F-250.
- **Proposed entries:**
  - AJE 1: Dr Equipment $5,600.00; Cr Small Tools and Equipment $5,600.00.
  - AJE 2: Dr Equipment $6,900.00; Cr Repairs and Maintenance $6,900.00.
  - AJE 3, the truck: Dr Accumulated depreciation $39,375.00; Dr Vehicles $16,000.00; Cr Vehicles
    $42,000.00; Cr Gain on sale of assets $13,375.00.
  - AJE 4: Dr Depreciation expense $7,810.00; Cr Accumulated depreciation $7,810.00.
- **After the proposed entries:** cost $257,450.00; accumulated depreciation $82,585.00.

One more step, outside the tool. Once you enter the door and the sprayer in the tax software, this
year's depreciation goes up. Type the new total in 3d, and the last entry follows it.

If your rebuilt tool shows the same, it works. If it does not, see "If it does not work" in the
episode's README.
