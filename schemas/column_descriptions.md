# Column Descriptions

Detailed documentation for each column in the data files.

## data/counties.csv

| Column | Type | Format | Description | Example | Constraints |
|--------|------|--------|-------------|---------|-------------|
| `county_code` | string | 2-digit zero-padded | SCB county code | `"01"` | Primary key, unique |
| `county_name` | string | — | Full official county name with "län" suffix | `"Stockholms län"` | Non-empty |
| `county_name_short` | string | — | Short name without "län" suffix | `"Stockholm"` | Non-empty |

21 rows. Codes range from 01 to 25 with gaps at 02, 11, 15, 16 (historically discontinued).

## data/municipalities.csv

| Column | Type | Format | Description | Example | Constraints |
|--------|------|--------|-------------|---------|-------------|
| `municipality_code` | string | 4-digit zero-padded | SCB municipality code | `"0180"` | Primary key, unique |
| `municipality_name` | string | — | Full name with "kommun" suffix | `"Stockholms kommun"` | Non-empty |
| `municipality_name_short` | string | — | Base place name without "kommun" | `"Stockholm"` | Non-empty |
| `county_code` | string | 2-digit zero-padded | County this municipality belongs to | `"01"` | FK → `counties.csv(county_code)`, equals `municipality_code[:2]` |

290 rows. Every municipality belongs to exactly one county.

## data/municipality_county.csv

Denormalized join of `municipalities.csv` and `counties.csv` on `county_code`.

| Column | Type | Format | Description | Example | Constraints |
|--------|------|--------|-------------|---------|-------------|
| `municipality_code` | string | 4-digit zero-padded | SCB municipality code | `"0180"` | Primary key, unique, FK → `municipalities.csv` |
| `municipality_name` | string | — | Full name with "kommun" suffix | `"Stockholms kommun"` | Must match `municipalities.csv` |
| `municipality_name_short` | string | — | Base place name | `"Stockholm"` | Must match `municipalities.csv` |
| `county_code` | string | 2-digit zero-padded | County code | `"01"` | FK → `counties.csv(county_code)`, equals `municipality_code[:2]` |
| `county_name` | string | — | Full county name with "län" suffix | `"Stockholms län"` | Must match `counties.csv` |
| `county_name_short` | string | — | Short county name | `"Stockholm"` | Must match `counties.csv` |

290 rows. This is a convenience file — the same data can be reconstructed by joining `municipalities.csv` with `counties.csv`.

## data/postal_to_municipality.csv

| Column | Type | Format | Description | Example | Constraints |
|--------|------|--------|-------------|---------|-------------|
| `postal_code` | string | 5-digit, no spaces | Swedish postal code | `"11520"` | Primary key, unique |
| `locality` | string | — | Place/locality name (title case) | `"Stockholm"` | Non-empty |
| `municipality_code` | string | 4-digit zero-padded | Municipality this postal code belongs to | `"0180"` | FK → `municipalities.csv(municipality_code)` |
| `municipality_name` | string | — | Full municipality name with "kommun" suffix | `"Stockholms kommun"` | Must match `municipalities.csv` |

~15,400 rows (September 2024 extract). Some postal codes may be missing if not covered by the source data.
