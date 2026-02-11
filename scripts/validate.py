#!/usr/bin/env python3
"""Validate Swedish geodata CSV files.

Run from the repository root:
    python scripts/validate.py

Uses only the Python standard library (no external dependencies).
Exit code 0 = all checks pass, 1 = one or more failures.
"""

import csv
import re
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

COUNTIES_FILE = DATA_DIR / "counties.csv"
MUNICIPALITIES_FILE = DATA_DIR / "municipalities.csv"
MUNICIPALITY_COUNTY_FILE = DATA_DIR / "municipality_county.csv"
POSTAL_FILE = DATA_DIR / "postal_to_municipality.csv"

COUNTIES_HEADER = ["county_code", "county_name", "county_name_short"]
MUNICIPALITIES_HEADER = [
    "municipality_code",
    "municipality_name",
    "municipality_name_short",
    "county_code",
]
MUNICIPALITY_COUNTY_HEADER = [
    "municipality_code",
    "municipality_name",
    "municipality_name_short",
    "county_code",
    "county_name",
    "county_name_short",
]
POSTAL_HEADER = [
    "postal_code",
    "locality",
    "municipality_code",
    "municipality_name",
]


failures = 0


def check(label: str, ok: bool, detail: str = "") -> bool:
    global failures
    if ok:
        print(f"  \u2713 {label}")
    else:
        msg = f"  \u2717 {label}"
        if detail:
            msg += f" — {detail}"
        print(msg)
        failures += 1
    return ok


def read_raw_bytes(path: Path) -> bytes:
    return path.read_bytes()


def check_utf8_no_bom(path: Path, raw: bytes) -> bool:
    return check(
        "UTF-8, no BOM",
        not raw.startswith(b"\xef\xbb\xbf"),
        "file starts with UTF-8 BOM",
    )


def check_lf_line_endings(path: Path, raw: bytes) -> bool:
    has_crlf = b"\r\n" in raw
    has_cr = b"\r" in raw.replace(b"\r\n", b"")
    return check(
        "LF line endings",
        not has_crlf and not has_cr,
        "found CR or CRLF line endings",
    )


def check_correct_header(path: Path, expected: list[str]) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
    return check("Correct header", header == expected, f"got {header}")


def check_no_trailing_commas(path: Path, raw: bytes) -> bool:
    text = raw.decode("utf-8")
    bad_lines = []
    for i, line in enumerate(text.split("\n"), 1):
        if line.endswith(","):
            bad_lines.append(i)
    return check(
        "No trailing commas",
        len(bad_lines) == 0,
        f"trailing commas on lines: {bad_lines[:5]}",
    )


def check_no_empty_rows(path: Path) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        empty = [i for i, row in enumerate(reader, 2) if all(c == "" for c in row)]
    return check("No empty rows", len(empty) == 0, f"empty rows at lines: {empty[:5]}")


def load_csv(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_code_format(rows: list[dict], col: str, length: int) -> bool:
    bad = []
    for i, row in enumerate(rows, 2):
        val = row[col]
        if not (len(val) == length and val.isdigit()):
            bad.append(f"line {i}: {val!r}")
    return check(
        f"{col} format ({length}-digit zero-padded)",
        len(bad) == 0,
        f"invalid: {bad[:5]}",
    )


def check_no_duplicates(rows: list[dict], col: str) -> bool:
    seen = {}
    dupes = []
    for i, row in enumerate(rows, 2):
        val = row[col]
        if val in seen:
            dupes.append(f"{val} (lines {seen[val]} and {i})")
        else:
            seen[val] = i
    return check(
        f"No duplicate {col}",
        len(dupes) == 0,
        f"duplicates: {dupes[:5]}",
    )


def check_row_count(rows: list[dict], expected: int) -> bool:
    return check(
        f"Row count = {expected}",
        len(rows) == expected,
        f"got {len(rows)}",
    )


def check_fk(
    rows: list[dict], col: str, ref_set: set, ref_name: str
) -> bool:
    missing = set()
    for row in rows:
        if row[col] not in ref_set:
            missing.add(row[col])
    return check(
        f"FK {col} → {ref_name}",
        len(missing) == 0,
        f"missing: {sorted(missing)[:10]}",
    )


def check_municipality_county_prefix(rows: list[dict]) -> bool:
    bad = []
    for i, row in enumerate(rows, 2):
        if row["municipality_code"][:2] != row["county_code"]:
            bad.append(f"line {i}: {row['municipality_code']} vs {row['county_code']}")
    return check(
        "municipality_code[:2] == county_code",
        len(bad) == 0,
        f"mismatches: {bad[:5]}",
    )


# ---------------------------------------------------------------------------
# Validate each file
# ---------------------------------------------------------------------------


def validate_counties():
    print(f"\n{'='*60}")
    print(f"counties.csv")
    print(f"{'='*60}")

    raw = read_raw_bytes(COUNTIES_FILE)
    check_utf8_no_bom(COUNTIES_FILE, raw)
    check_lf_line_endings(COUNTIES_FILE, raw)
    check_correct_header(COUNTIES_FILE, COUNTIES_HEADER)
    check_no_trailing_commas(COUNTIES_FILE, raw)
    check_no_empty_rows(COUNTIES_FILE)

    rows = load_csv(COUNTIES_FILE)
    check_code_format(rows, "county_code", 2)
    check_no_duplicates(rows, "county_code")
    check_row_count(rows, 21)

    print(f"  — {len(rows)} rows")
    return rows


def validate_municipalities(county_codes: set):
    print(f"\n{'='*60}")
    print(f"municipalities.csv")
    print(f"{'='*60}")

    raw = read_raw_bytes(MUNICIPALITIES_FILE)
    check_utf8_no_bom(MUNICIPALITIES_FILE, raw)
    check_lf_line_endings(MUNICIPALITIES_FILE, raw)
    check_correct_header(MUNICIPALITIES_FILE, MUNICIPALITIES_HEADER)
    check_no_trailing_commas(MUNICIPALITIES_FILE, raw)
    check_no_empty_rows(MUNICIPALITIES_FILE)

    rows = load_csv(MUNICIPALITIES_FILE)
    check_code_format(rows, "municipality_code", 4)
    check_code_format(rows, "county_code", 2)
    check_no_duplicates(rows, "municipality_code")
    check_row_count(rows, 290)
    check_fk(rows, "county_code", county_codes, "counties.csv")
    check_municipality_county_prefix(rows)

    print(f"  — {len(rows)} rows")
    return rows


def validate_municipality_county(
    county_codes: set,
    county_lookup: dict,
    municipality_codes: set,
    municipality_lookup: dict,
):
    print(f"\n{'='*60}")
    print(f"municipality_county.csv")
    print(f"{'='*60}")

    raw = read_raw_bytes(MUNICIPALITY_COUNTY_FILE)
    check_utf8_no_bom(MUNICIPALITY_COUNTY_FILE, raw)
    check_lf_line_endings(MUNICIPALITY_COUNTY_FILE, raw)
    check_correct_header(MUNICIPALITY_COUNTY_FILE, MUNICIPALITY_COUNTY_HEADER)
    check_no_trailing_commas(MUNICIPALITY_COUNTY_FILE, raw)
    check_no_empty_rows(MUNICIPALITY_COUNTY_FILE)

    rows = load_csv(MUNICIPALITY_COUNTY_FILE)
    check_code_format(rows, "municipality_code", 4)
    check_code_format(rows, "county_code", 2)
    check_no_duplicates(rows, "municipality_code")
    check_row_count(rows, 290)
    check_fk(rows, "county_code", county_codes, "counties.csv")
    check_fk(rows, "municipality_code", municipality_codes, "municipalities.csv")
    check_municipality_county_prefix(rows)

    # Join consistency: county_name and county_name_short must match counties.csv
    join_bad = []
    for i, row in enumerate(rows, 2):
        cc = row["county_code"]
        if cc in county_lookup:
            ref = county_lookup[cc]
            if row["county_name"] != ref["county_name"]:
                join_bad.append(
                    f"line {i}: county_name {row['county_name']!r} vs {ref['county_name']!r}"
                )
            if row["county_name_short"] != ref["county_name_short"]:
                join_bad.append(
                    f"line {i}: county_name_short {row['county_name_short']!r} vs {ref['county_name_short']!r}"
                )
    check(
        "Join consistency (county columns match counties.csv)",
        len(join_bad) == 0,
        f"mismatches: {join_bad[:5]}",
    )

    # Municipality columns must match municipalities.csv
    muni_bad = []
    for i, row in enumerate(rows, 2):
        mc = row["municipality_code"]
        if mc in municipality_lookup:
            ref = municipality_lookup[mc]
            if row["municipality_name"] != ref["municipality_name"]:
                muni_bad.append(
                    f"line {i}: municipality_name {row['municipality_name']!r} vs {ref['municipality_name']!r}"
                )
            if row["municipality_name_short"] != ref["municipality_name_short"]:
                muni_bad.append(
                    f"line {i}: municipality_name_short {row['municipality_name_short']!r} vs {ref['municipality_name_short']!r}"
                )
    check(
        "Join consistency (municipality columns match municipalities.csv)",
        len(muni_bad) == 0,
        f"mismatches: {muni_bad[:5]}",
    )

    print(f"  — {len(rows)} rows")
    return rows


def validate_postal(municipality_codes: set, municipality_lookup: dict):
    print(f"\n{'='*60}")
    print(f"postal_to_municipality.csv")
    print(f"{'='*60}")

    raw = read_raw_bytes(POSTAL_FILE)
    check_utf8_no_bom(POSTAL_FILE, raw)
    check_lf_line_endings(POSTAL_FILE, raw)
    check_correct_header(POSTAL_FILE, POSTAL_HEADER)
    check_no_trailing_commas(POSTAL_FILE, raw)
    check_no_empty_rows(POSTAL_FILE)

    rows = load_csv(POSTAL_FILE)
    check_code_format(rows, "postal_code", 5)
    check_code_format(rows, "municipality_code", 4)
    check_no_duplicates(rows, "postal_code")
    check_fk(rows, "municipality_code", municipality_codes, "municipalities.csv")

    # municipality_name must match municipalities.csv
    name_bad = []
    for i, row in enumerate(rows, 2):
        mc = row["municipality_code"]
        if mc in municipality_lookup:
            expected = municipality_lookup[mc]["municipality_name"]
            if row["municipality_name"] != expected:
                name_bad.append(
                    f"line {i}: {row['municipality_name']!r} vs {expected!r}"
                )
    check(
        "municipality_name matches municipalities.csv",
        len(name_bad) == 0,
        f"mismatches: {name_bad[:5]}",
    )

    print(f"  — {len(rows)} rows")
    return rows


def main():
    global failures

    print("Swedish Geodata — CSV Validation")
    print("=" * 60)

    # Validate counties
    county_rows = validate_counties()
    county_codes = {r["county_code"] for r in county_rows}
    county_lookup = {r["county_code"]: r for r in county_rows}

    # Validate municipalities
    muni_rows = validate_municipalities(county_codes)
    municipality_codes = {r["municipality_code"] for r in muni_rows}
    municipality_lookup = {r["municipality_code"]: r for r in muni_rows}

    # Validate municipality_county join
    validate_municipality_county(
        county_codes, county_lookup, municipality_codes, municipality_lookup
    )

    # Validate postal codes
    validate_postal(municipality_codes, municipality_lookup)

    # Summary
    print(f"\n{'='*60}")
    if failures == 0:
        print("All checks passed.")
        sys.exit(0)
    else:
        print(f"{failures} check(s) FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
