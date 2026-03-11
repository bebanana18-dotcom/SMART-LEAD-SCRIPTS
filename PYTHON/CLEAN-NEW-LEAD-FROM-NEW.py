import pandas as pd
import os
import sys
from datetime import datetime

# ============================================================
#   LEAD DEDUPLICATOR - FINAL VERSION
#   Removes already-used leads from new leads
#   Works with multi-column CSV (Email, Name, etc.)
# ============================================================


# -----------------------------
# CONFIG
# -----------------------------

OLD_FILE    = "OLD-USED-LEAD.csv"
NEW_FILE    = "NEW-LEAD.csv"
OUTPUT_FILE = "CLEAN-NEW-LEAD.csv"

EMAIL_COL = "email"   # after normalization


# -----------------------------
# CHECK FILES EXIST
# -----------------------------

for f in [OLD_FILE, NEW_FILE]:
    if not os.path.exists(f):
        print(f"ERROR: File not found -> {f}")
        sys.exit(1)


# -----------------------------
# READ FILES
# -----------------------------

print("Reading CSV files...")

old_df = pd.read_csv(
    OLD_FILE,
    dtype=str,
    on_bad_lines="skip",
    encoding="utf-8"
)

new_df = pd.read_csv(
    NEW_FILE,
    dtype=str,
    on_bad_lines="skip",
    encoding="utf-8"
)


# -----------------------------
# NORMALIZE COLUMN NAMES
# -----------------------------

old_df.columns = old_df.columns.str.strip().str.lower()
new_df.columns = new_df.columns.str.strip().str.lower()


# -----------------------------
# CHECK EMAIL COLUMN EXISTS
# -----------------------------

for name, df in [("OLD", old_df), ("NEW", new_df)]:
    if EMAIL_COL not in df.columns:
        print(f"ERROR: 'Email' column not found in {name} file")
        print("Columns found:", list(df.columns))
        sys.exit(1)


# -----------------------------
# CLEAN EMAIL COLUMN
# -----------------------------

old_df[EMAIL_COL] = (
    old_df[EMAIL_COL]
    .fillna("")
    .str.strip()
    .str.lower()
)

new_df[EMAIL_COL] = (
    new_df[EMAIL_COL]
    .fillna("")
    .str.strip()
    .str.lower()
)


# -----------------------------
# REMOVE EMPTY / INVALID EMAILS
# -----------------------------

old_df = old_df[
    (old_df[EMAIL_COL] != "") &
    (old_df[EMAIL_COL].str.contains("@", na=False))
]

new_df = new_df[
    (new_df[EMAIL_COL] != "") &
    (new_df[EMAIL_COL].str.contains("@", na=False))
]


# -----------------------------
# REMOVE DUPLICATES INSIDE NEW
# -----------------------------

dupes_in_new = new_df.duplicated(
    subset=[EMAIL_COL]
).sum()

new_df = new_df.drop_duplicates(
    subset=[EMAIL_COL],
    keep="first"
)


# -----------------------------
# MATCH + REMOVE OLD LEADS
# -----------------------------

old_emails = set(old_df[EMAIL_COL])

clean_df = new_df[
    ~new_df[EMAIL_COL].isin(old_emails)
]


# -----------------------------
# SAVE OUTPUT
# -----------------------------

clean_df.to_csv(
    OUTPUT_FILE,
    index=False,
    header=True,
    encoding="utf-8"
)


# -----------------------------
# STATS
# -----------------------------

removed = len(new_df) - len(clean_df)

rate = (
    removed / len(new_df) * 100
    if len(new_df) > 0 else 0
)

time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


print(f"""
==============================

OLD leads      : {len(old_df)}
NEW leads      : {len(new_df)}
Dupes in NEW   : {dupes_in_new}
Removed match  : {removed}
Clean output   : {len(clean_df)}

Overlap %      : {rate:.1f}%

Saved file     : {OUTPUT_FILE}
Time           : {time_now}

==============================
""")
