# Sample: Ridgeline Landscaping LLC (invented)

Use these files to try the tool, or to check a version you rebuilt from the prompt, before you
use a real client's file. Everything here is made up: the business, the people, the vendors, the
amounts.

| File | What it is |
|---|---|
| `ridgeline-general-ledger-2026.xlsx` | The client's general ledger for 2026, as QuickBooks Online exports it (Reports, General Ledger, Export to Excel). |
| `ridgeline-depreciation-schedule-2025.csv` | Last year's depreciation schedule: each asset's cost and accumulated depreciation at December 31, 2025. |

This year's depreciation, from the tax software: **$24,610.00**.

## What you should see

**After you drop in the ledger** (step 1), the verdict at the top reads:

> Ridgeline Landscaping LLC: $76,050.00 recorded as assets this year; $26,980.00 more found in
> expense accounts for you to decide; 1 sale or write-off to settle.

**Step 2, the accounts.** Equipment and Vehicles are fixed assets; Accumulated Depreciation and
Depreciation Expense are what they say; Repairs and Maintenance, Office Supplies & Software, and
Small Tools and Equipment are expense accounts to check; Fuel, Utilities and Rent are ignored.
They are right: press the button.

**Step 3a, recorded as assets:** the zero-turn mower, $14,800.00 (March 9), and the 2026 F-350,
$61,250.00 (May 20).

**Step 3b, seven bills to decide.** The page decides none of them. A reasonable set of decisions:

| Bill | Amount | Decision | Why |
|---|---|---|---|
| Coastal Door Co, replace shop overhead door | $6,900.00 | Capitalize | It replaces a whole component of the building, which the repair regulations can treat as a restoration. A judgment call: yours. |
| Greenfield Tools, trailer-mounted sprayer | $5,600.00 | Capitalize | New equipment over the limit. |
| Summit Office Systems, laptops (2) and docking station | $3,480.00 | Keep as expense | Each item is under $2,500: de minimis, per item. |
| Clearwater Irrigation, quarterly maintenance (4 bills, marked "repeats") | $2,750.00 each | Keep as expense | A service contract. |

**Step 3c, the sold truck.** $16,000.00 received from Jones Turf Services on June 3 was credited to
Vehicles. On last year's schedule the 2017 Ford F-250 cost **$42,000.00** with **$36,750.00** of
depreciation: type those two figures and press the button. The page shows a **gain of $10,750.00**.

**Step 3d, does it agree?** Type 210,900.00, 97,350.00 and 24,610.00. Both opening balances agree;
depreciation booked, $16,800.00, is $7,810.00 lower than $24,610.00.

**Step 4, the workpaper:**
- Total to add to the depreciation schedule: **$88,550.00** (mower, F-350, door, sprayer).
- Proposed entries:
  1. Dr the fixed asset account the item belongs in, Cr Small Tools and Equipment, $5,600.00.
  2. Dr the fixed asset account the item belongs in, Cr Repairs and Maintenance, $6,900.00.
  3. The truck: Dr Accumulated depreciation $36,750.00; Dr Vehicles $16,000.00; Cr Vehicles
     $42,000.00; Cr Gain on sale of assets $10,750.00.
  4. Dr Depreciation expense, Cr Accumulated depreciation, $7,810.00.

If your rebuilt tool shows the same, it works. If it does not, see "If it does not work" in the
episode's README.
