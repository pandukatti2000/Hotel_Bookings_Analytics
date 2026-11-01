# StayWise AI — Data Quality & Anomaly Report

## 1. Executive Summary

An exhaustive profiling across all 11 source files revealed critical data-quality anomalies spanning structural formatting, corrupted string encodings, sentinel values, whitespace padding, numeric outliers, and logical boundary violations.

All findings are documented below with empirical row counts and recommended remediation steps for the Phase 2 ETL pipeline.

---

## 2. Completeness & Missing Value Profile

| Table | Column | Null Count | % Missing | Observed Impact | Recommended Phase 2 Treatment |
|---|---|---|---|---|---|
| `Guest_info.csv` | `children` | 4 | <0.01% | Floating-point column contains 4 null values. | Impute with `0` and cast to `SMALLINT`. |
| `Booking_details.csv` | `country` | 488 | 0.41% | Country of guest is missing. | Impute with `'NULL'` (matches lookup code `'NULL'` -> `'Unknown'`). |
| `Booking_Source_and_History.csv` | `country` | 488 | 0.41% | Exactly duplicates `Booking_details.country`. | Drop duplicate column during ETL to enforce 3NF. |
| `Booking_Source_and_History.csv` | `agent` | 16,340 | 13.69% | Bookings made without an external travel agency. | Retain as `NULL` or impute with sentinel `0` (`Direct / No Agent`). |
| `Booking_Source_and_History.csv` | `company` | 112,593 | 94.31% | Bookings made without corporate sponsorship. | Retain as `NULL` or impute with sentinel `0` (`Individual / No Company`). |
| `Room_Details.csv` | `Unnamed: 3` | 119,390 | 100.0% | Empty artifact caused by trailing delimiter in CSV generation. | Drop column entirely during staging. |

---

## 3. Formatting & Whitespace Anomalies

### 3.1 Padded Whitespace in `country.csv`
- **Issue**: Both `country_code` and `country_name` in `country.csv` are formatted with leading spaces and trailing whitespace padding (e.g. `' PRT          '`, `' Portugal             '`).
- **Impact**: Without explicit trimming, any foreign-key constraint or SQL join between `booking_details.country` and `country.country_code` produces **100% orphaned foreign keys** (0 successful matches across all 119,390 rows).
- **Remediation**: Apply `TRIM(country_code)` and `TRIM(country_name)` during ingestion. Following trimming, 177 distinct country codes in `booking_details` match `country.csv` with **zero orphans**.
- **Lookup Sentinel**: Row 7 of `country.csv` contains `country_code = 'NULL'` and `country_name = 'Unknown'`. This explicitly accommodates the 488 missing country rows.

### 3.2 Filename Duplicates with Whitespace
- `Room_Details .csv` (with a space before `.csv`) is a bit-for-bit duplicate of `Room_Details.csv`.
- `market Segment.csv` (with a space) is a bit-for-bit duplicate of `market_Segment.csv`.
- **Remediation**: Explicitly ignore the duplicate filenames in ETL file discovery.

---

## 4. Numeric & Financial Anomalies

### 4.1 Negative Average Daily Rate (ADR)
- **Finding**: Row index `a89dd2e8` (`Meal_And_Stay_Details.csv`) has `adr = -6.38`.
  - Stays: 2 week nights, 0 weekend nights.
  - Status: Check-Out.
  - Context: An accounting adjustment, credit, or booking rebate.
- **Impact**: Negative ADR distorts room revenue calculations.
- **Remediation**: Flag in a `data_quality_flag` column or clamp revenue calculations at 0 using `GREATEST(adr, 0.00)` with documented business audit notes.

### 4.2 Extreme ADR Outlier
- **Finding**: Row index `75ac1e61` has `adr = 5400.00`.
  - Hotel: City Hotel, arrival March 25, 2016.
  - Room: Reserved Room Type `A`, Assigned `A`, 1 adult, 0 children, 0 babies.
  - Stays: 0 weekend nights, 1 week night.
  - Status: Canceled.
  - Next highest ADR in the dataset is `510.00`.
- **Impact**: Skewing mean ADR by ~$0.04 across the dataset, and significantly distorting March 2016 City Hotel metrics.
- **Remediation**: Cap or isolate in robust statistical views (report median ADR alongside mean ADR).

### 4.3 Zero ADR Bookings
- **Finding**: 1,959 bookings (1.64%) have `adr = 0.00`.
  - 1,749 checked out; 210 canceled/no-show.
  - Market segments: 741 Complementary, 545 Online TA, 276 Direct, 192 Corporate, 192 Groups.
- **Business Reality**: These reflect complimentary stays, reward nights, timeshare contracts, or barter arrangements. They must be included in occupancy calculations but excluded or separated in pure room-rate yield analyses.

---

## 5. Logical & Operational Boundary Anomalies

### 5.1 Zero-Night Bookings
- **Finding**: 715 bookings (0.60%) have `stays_in_weekend_nights = 0` and `stays_in_week_nights = 0`.
  - 680 checked out; 35 canceled.
  - Business context: Day-use rooms, conference room check-ins, or cancellations prior to check-in that never occupied room nights.
- **Impact on Metrics**: When calculating `estimated_booking_value = (stays_in_weekend_nights + stays_in_week_nights) * adr`, these 715 records yield $0 regardless of ADR.

### 5.2 Zero-Guest Bookings
- **Finding**: 180 bookings (0.15%) have `adults = 0`, `children = 0`, and `babies = 0`.
  - 155 checked out; 25 canceled.
  - Context: Corporate bookings reserving room blocks without passenger manifest names, or system test bookings.

### 5.3 Room Reassignments Without Booking Changes
- **Finding**: In 14,917 reservations (12.49%), `reserved_room_type != assigned_room_type`.
  - In 11,028 of these (73.93% of reassignments), `booking_changes = 0`.
  - Business context: Upgrades or downgrades executed dynamically by hotel front-desk operations at check-in (overbooking mitigation, loyalty upgrades, room maintenance), rather than guest-initiated reservation edits.
- **Unreserved Room Types**: Room types `I` (363 occurrences) and `K` (279 occurrences) appear in `assigned_room_type`, but never in `reserved_room_type`. These represent back-of-house operational room classifications (e.g. suites, accessible rooms, temporary overflow).

### 5.4 Meal Plan "Undefined"
- **Finding**: 1,169 reservations have `meal = 'Undefined'`.
  - In standard hotel analytics benchmarks (e.g. Antonio, de Almeida and Nunes, 2019), `Undefined` corresponds to `SC` (Self-Catering / no meals included).
- **Remediation**: Standardize `Undefined` to `SC` or document as `SC / Room Only`.

---

## 6. Status & Cancellation Flag Integrity

- `is_canceled = 0`: Exactly 75,166 records.
- `reservation_status = 'Check-Out'`: Exactly 75,166 records.
- `is_canceled = 1`: Exactly 44,224 records.
- `reservation_status = 'Canceled'`: 43,017 records.
- `reservation_status = 'No-Show'`: 1,207 records.
- **Conclusion**: There is **100% mathematical consistency** between `is_canceled` and `reservation_status`. `No-Show` bookings are classified under `is_canceled = 1`.
