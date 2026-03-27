import csv
import re
from typing import Iterable

DOMAIN_SUFFIX_KEEP = {"ai", "co", "io"}
DOMAIN_SUFFIX_DROP = {"com", "net", "org", "biz", "info", "us", "uk", "ca"}

BUSINESS_TERMS = (
    "enterprises",
    "enterprise",
    "solutions",
    "solution",
    "marketing",
    "automation",
    "media",
)

COMMON_CHUNKS = {
    "locate",
    "your",
    "apt",
    "tech",
    "globe",
    "spark",
    "angel",
    "market",
    "marketing",
    "auto",
    "automation",
    "media",
    "solution",
    "solutions",
    "enterprise",
    "enterprises",
}

UPPER_WORDS = {"AI", "LLC", "LTD" , "CO", "IO"}


# -------------------------
# Word formatting
# -------------------------

def title_word(word: str) -> str:
    if not word:
        return ""

    upper = word.upper()

    if upper in UPPER_WORDS:
        return upper

    return word[:1].upper() + word[1:].lower()


def split_camel_case(value: str) -> str:
    return re.sub(r"([a-z])([A-Z])", r"\1 \2", value)


# -------------------------
# Business suffix spacing
# -------------------------

def space_before_business_suffix(token: str) -> str:
    for term in BUSINESS_TERMS:
        pattern = re.compile(rf"(?i)^(.+?)({term})$")
        match = pattern.match(token)

        if match:
            left, right = match.groups()

            if left.strip():
                return f"{left} {right}"

    return token


# -------------------------
# Split merged words
# -------------------------

def break_using_common_chunks(token: str) -> str:
    raw = token.strip()

    if not raw or not raw.isalpha() or len(raw) < 8:
        return raw

    lower = raw.lower()
    n = len(lower)

    dp: list[list[str] | None] = [None] * (n + 1)
    dp[0] = []

    for i in range(n):
        if dp[i] is None:
            continue

        for j in range(i + 1, n + 1):
            piece = lower[i:j]

            if piece in COMMON_CHUNKS:
                candidate = (dp[i] or []) + [piece]

                if dp[j] is None or len(candidate) < len(dp[j] or []):
                    dp[j] = candidate

    if not dp[n] or len(dp[n]) <= 1:
        return raw

    return " ".join(dp[n])


# -------------------------
# Normalize contact name
# -------------------------

def normalize_contact_name(contact_name: str) -> str:
    value = (contact_name or "").strip()

    if not value:
        return value

    value = re.sub(
        r"^[\s\[\](){}<>_\-.,;:]+|[\s\[\](){}<>_\-.,;:]+$",
        "",
        value,
    )

    value = re.sub(
        r"^(https?://)?(www\.)",
        "",
        value,
        flags=re.IGNORECASE,
    )

    raw_parts = [
        p for p in re.split(r"[.\s/_-]+", value)
        if p
    ]

    normalized_parts: list[str] = []

    for part in raw_parts:

        piece = split_camel_case(part)
        piece = space_before_business_suffix(piece)
        piece = break_using_common_chunks(piece)

        for token in piece.split():

            cleaned = re.sub(r"[^A-Za-z0-9]+", "", token)

            if not cleaned:
                continue

            low = cleaned.lower()

            if low in DOMAIN_SUFFIX_DROP:
                continue

            if low in DOMAIN_SUFFIX_KEEP:
                normalized_parts.append(low.upper())
                continue

            spaced = space_before_business_suffix(cleaned)

            normalized_parts.extend(spaced.split())

    if not normalized_parts:
        return ""

    titled = [title_word(w) for w in normalized_parts]

    return " ".join(titled)


# -------------------------
# Header finder
# -------------------------

def find_header_key(
    fieldnames: Iterable[str],
    *candidates: str,
) -> str | None:

    lowered = {
        f.strip().lower(): f
        for f in fieldnames if f
    }

    for candidate in candidates:
        key = lowered.get(candidate.strip().lower())

        if key is not None:
            return key

    return None


# -------------------------
# CSV processor
# -------------------------

def process_csv(
    input_csv_path: str,
    output_csv_path: str,
) -> None:

    with open(
        input_csv_path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as source:

        reader = csv.DictReader(source)

        if not reader.fieldnames:
            raise ValueError("CSV has no header row")

        email_key = find_header_key(
            reader.fieldnames,
            "email",
        )

        contact_key = find_header_key(
            reader.fieldnames,
            "contact name",
            "contact_name",
        )

        if not email_key or not contact_key:
            raise ValueError(
                "CSV must include Email and Contact Name"
            )

        rows = list(reader)

    for row in rows:

        row[contact_key] = normalize_contact_name(
            row.get(contact_key) or ""
        )

    with open(
        output_csv_path,
        "w",
        encoding="utf-8",
        newline="",
    ) as target:

        writer = csv.DictWriter(
            target,
            fieldnames=reader.fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


# -------------------------
# CLI
# -------------------------

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Normalize Contact Name values in CSV"
    )

    parser.add_argument("input_csv")
    parser.add_argument("output_csv")

    args = parser.parse_args()

    process_csv(
        args.input_csv,
        args.output_csv,
    )



# TO RUN THIS SCRIPT : python3 two.py input.csv output.csv
# OUTPUT.CSV WILL BE CREATED BY SCRIPT IF NOT AVAILABLE OR OVERWRITEN
