# first charector capital
```excel
=ARRAYFORMULA(IF(B2:B="","",PROPER(B2:B)))
```

## Google Sheets – Normalize last word to LLC / LTD (case-insensitive)

These formulas fix company names where the last word is `llc` or `ltd`
and convert it to uppercase (`LLC`, `LTD`) only when it appears as the last word.

✅ Case-insensitive  
✅ Only affects last word  
✅ Does NOT change words like `VINAMLLC` or `TESTLTD`  
✅ Works for whole column using ARRAYFORMULA  

Column used in examples: `B` (contact name)

---

### Fix last word → LLC

```excel
=ARRAYFORMULA(
IF(B2:B="","",
IF(REGEXMATCH(B2:B,"(?i)\s+llc$"),
REGEXREPLACE(B2:B,"(?i)\s+llc$"," LLC"),
B2:B)))
```

**Explanation**

- `(?i)` → case-insensitive match  
- `\s+llc$` → space + llc at end of text  
- `REGEXREPLACE` → replaces only the last word  
- `ARRAYFORMULA` → applies to whole column  

Examples:

| Input | Output |
|--------|---------|
| Marketing Prime Leads, llc | Marketing Prime Leads, LLC |
| abc llc | abc LLC |
| ABC LLC | ABC LLC |
| VINAMLLC | VINAMLLC |

---

### Fix last word → LTD

```excel
=ARRAYFORMULA(
IF(B2:B="","",
IF(REGEXMATCH(B2:B,"(?i)\s+ltd$"),
REGEXREPLACE(B2:B,"(?i)\s+ltd$"," LTD"),
B2:B)))
```

**Explanation**

- `(?i)` → case-insensitive match  
- `\s+ltd$` → space + ltd at end of text  
- Only replaces last word  
- Safe for CSV imports

Examples:

| Input | Output |
|--------|---------|
| Naliglo (Pty) Ltd | Naliglo (Pty) LTD |
| abc ltd | abc LTD |
| ABC LTD | ABC LTD |
| VINAMLTD | VINAMLTD |

---

### Notes

- Put formula in a different column (ex: H2)
- Change `B2:B` if your column is different
- Works in Google Sheets (CSV imports supported)
