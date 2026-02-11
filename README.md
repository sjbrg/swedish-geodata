# Swedish Geodata

Open reference data for Swedish geographical divisions: counties (län), municipalities (kommuner), and postal code mappings.

All files are UTF-8 encoded CSV with LF line endings and comma separators. Released under [CC0 1.0](LICENSE) — use freely for any purpose.

## Data overview

| File | Description | Rows | Columns |
|------|-------------|-----:|---------|
| `data/counties.csv` | All 21 Swedish counties | 21 | `county_code`, `county_name`, `county_name_short` |
| `data/municipalities.csv` | All 290 Swedish municipalities | 290 | `municipality_code`, `municipality_name`, `municipality_name_short`, `county_code` |
| `data/municipality_county.csv` | Municipalities with county details (join table) | 290 | `municipality_code`, `municipality_name`, `municipality_name_short`, `county_code`, `county_name`, `county_name_short` |
| `data/postal_to_municipality.csv` | Postal codes mapped to municipalities | 15,463 | `postal_code`, `locality`, `municipality_code`, `municipality_name` |

See [schemas/column_descriptions.md](schemas/column_descriptions.md) for detailed column documentation.

## Column formats

- **County codes** are 2-digit zero-padded strings (`"01"`, not `1`)
- **Municipality codes** are 4-digit zero-padded strings (`"0180"`, not `180`)
- **Postal codes** are 5-digit strings without spaces (`"11520"`, not `"115 20"`)
- All codes must be read as **strings** to preserve leading zeros
- Encoding: UTF-8 (no BOM)
- Separator: comma (`,`)
- No quoting unless a field contains a comma

## Usage examples

### Python (pandas)

```python
import pandas as pd

# Important: use dtype=str to preserve leading zeros in codes
counties = pd.read_csv("data/counties.csv", dtype=str)
municipalities = pd.read_csv("data/municipalities.csv", dtype=str)
postal = pd.read_csv("data/postal_to_municipality.csv", dtype=str)

# Look up municipality for a postal code
postal[postal["postal_code"] == "11520"]
```

### R

```r
# Important: use colClasses = "character" to preserve leading zeros
counties <- read.csv("data/counties.csv", colClasses = "character")
municipalities <- read.csv("data/municipalities.csv", colClasses = "character")
postal <- read.csv("data/postal_to_municipality.csv", colClasses = "character")
```

### Python (stdlib)

```python
import csv

with open("data/municipalities.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["municipality_code"], row["municipality_name"])
```

## Data sources

- **County and municipality codes**: [Statistics Sweden (SCB)](https://www.scb.se/) via [Dataman/Axelsson2000](https://github.com/Axelsson2000/data)
- **Postal code mappings**: [Dataman/Axelsson2000](https://github.com/Axelsson2000/data) (September 2024 extract)

Municipality names follow SCB conventions. The `municipality_name` field uses the standard form with "kommun" suffix (e.g., "Stockholms kommun").

### Coverage notes

`postal_to_municipality.csv` contains 15,463 postal codes from a September 2024 extract. Sweden has roughly 18,000–19,000 postal codes in total (per [GeoNames](https://download.geonames.org/export/zip/SE.zip)), so this dataset covers approximately 82% of known codes. The missing codes are spread across all regions and are likely box/company postal codes and other special-purpose codes that the Dataman source does not include.

- [GeoNames SE postal data](https://download.geonames.org/export/zip/SE.zip) offers broader coverage (~18,870 codes) but does not include municipality code mappings and has some Swedish character encoding issues.

## Validation

Run the validation script (Python 3, no dependencies):

```bash
python scripts/validate.py
```

This checks file encoding, headers, code formats, foreign key integrity, row counts, and join consistency.

## Last updated

2025-01 (initial release)

## License

[CC0 1.0 Universal](LICENSE) — dedicated to the public domain.

## Contributing

Contributions are welcome. Please ensure `python scripts/validate.py` passes before submitting a pull request. Data corrections should reference an authoritative source (e.g., SCB, PostNord).
