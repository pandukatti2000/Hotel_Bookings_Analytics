# StayWise AI — Booking Identifier Integrity & Deduplication Report

## 1. Executive Summary

A critical data-integrity issue was investigated across all six main CSV tables regarding the primary reservation key, `Booking_id`. 

Our investigation identified the **definitive root cause** of the duplicate IDs in `Guest_info.csv`: **Microsoft Excel auto-formatting corruption**.

- Five of the six tables (`Booking_details`, `Booking_Source_and_History`, `Meal_And_Stay_Details`, `Reservation_status`, `Room_Details`) possess **100% unique, uncorrupted, 8-character hexadecimal booking identifiers** across all 119,390 rows.
- The row sequence across all six CSV files is in **100% identical physical order** (index 0 to 119,389).
- `Guest_info.csv` was subjected to Microsoft Excel processing, which mangled 895 identifiers:
  - **598 identifiers** resembling scientific notation (e.g. `125414e6`) were converted into scientific float strings (e.g. `1.25E+11`).
  - **6 pairs of distinct booking records** collided into identical scientific notation strings, producing the **6 duplicate key occurrences (12 rows)**.
  - **297 identifiers** consisting of numeric characters with leading zeros (e.g. `09632730`) had their leading zeros stripped by Excel (e.g. `9632730`).

---

## 2. Table-by-Table Booking_id Uniqueness Audit

| Table Name | Total Rows | Unique `Booking_id` | Duplicate IDs | Is Key 100% Unique? | Row Alignment with `Booking_details` |
|---|---|---|---|---|---|
| `Booking_details.csv` | 119,390 | 119,390 | 0 | **Yes (100.0%)** | Reference Baseline (100.0%) |
| `Booking_Source_and_History.csv` | 119,390 | 119,390 | 0 | **Yes (100.0%)** | 100.0% Perfect Match (0 mismatches) |
| `Meal_And_Stay_Details.csv` | 119,390 | 119,390 | 0 | **Yes (100.0%)** | 100.0% Perfect Match (0 mismatches) |
| `Reservation_status.csv` | 119,390 | 119,390 | 0 | **Yes (100.0%)** | 100.0% Perfect Match (0 mismatches) |
| `Room_Details.csv` | 119,390 | 119,390 | 0 | **Yes (100.0%)** | 100.0% Perfect Match (0 mismatches) |
| `Guest_info.csv` | 119,390 | 119,384 | 6 (12 rows) | **No (99.995%)** | 118,495 exact matches; 895 corrupted keys |

---

## 3. Investigation of the 6 Duplicate Key Pairs in `Guest_info.csv`

The 6 duplicate keys represent 12 physical rows in `Guest_info.csv`. By linking each row to its corresponding row index in `Booking_details.csv`, we recover the true, uncorrupted booking IDs and inspect row contents:

| Corrupted `Booking_id` in `Guest_info` | Row Index | True Canonical `Booking_id` (from `Booking_details`) | Hotel & Arrival Date | `adults` | `children` | `babies` | Row Content Status |
|---|---|---|---|---|---|---|---|
| `1.25E+11` | 44,861 | `125414e6` | City Hotel, 2015-10-13 | 2 | 0 | 0 | **Conflicting Bookings** (Different dates, same guests) |
| `1.25E+11` | 79,702 | `125382e6` | City Hotel, 2015-10-30 | 2 | 0 | 0 | Conflicting Bookings |
| `1.52E+10` | 32,037 | `001523e7` | Resort Hotel, 2017-01-14 | 2 | 0 | 0 | **Conflicting Bookings** (Different hotels and dates) |
| `1.52E+10` | 101,982 | `152137e5` | City Hotel, 2016-11-18 | 2 | 0 | 0 | Conflicting Bookings |
| `2.37E+08` | 46,175 | `236714e3` | City Hotel, 2015-12-21 | 2 | 0 | 0 | **Conflicting Data** (`adults`=2 vs `adults`=1) |
| `2.37E+08` | 106,138 | `237311e3` | City Hotel, 2017-02-20 | 1 | 0 | 0 | Conflicting Data |
| `4.23E+08` | 2,987 | `423029e3` | Resort Hotel, 2015-11-09 | 2 | 0 | 0 | **Conflicting Bookings** (Different hotels and dates) |
| `4.23E+08` | 40,092 | `042333e4` | City Hotel, 2015-07-05 | 2 | 0 | 0 | Conflicting Bookings |
| `7.90E+06` | 51,829 | `078961e2` | City Hotel, 2016-05-26 | 1 | 0 | 0 | **Conflicting Data** (`adults`=1 vs `adults`=2) |
| `7.90E+06` | 71,349 | `789908e1` | City Hotel, 2017-07-03 | 2 | 0 | 0 | Conflicting Data |
| `9.63E+72` | 69,269 | `96288e68` | City Hotel, 2017-05-28 | 2 | 0 | 0 | **Conflicting Bookings** (Different dates, same guests) |
| `9.63E+72` | 107,530 | `96311e68` | City Hotel, 2017-03-09 | 2 | 0 | 0 | Conflicting Bookings |

### Analysis of Conflicts
- These 12 records are **NOT duplicate reservations**; they represent **12 distinct, genuine hotel bookings**.
- The guest compositions are in some cases identical (`adults=2`), but in two pairs they conflict (`adults=2` vs `adults=1`).
- The duplicate IDs are purely an artifact of Excel parsing the string as a floating-point exponential number and truncating digits.

---

## 4. Join Impact & Risk of Row Multiplication

If an engineer executes a standard SQL `JOIN` on `Booking_id` between `Booking_details` and `Guest_info.csv`:
1. **Cartesian Explosion**:
   - Because the 6 keys appear twice in `Guest_info`, joining on the corrupted key multiplies rows ($1 \times 2 = 2$ rows per key), creating phantom reservations and distorting aggregates.
2. **Orphaned / Missing Rows**:
   - The 598 records with `E+` in `Guest_info` would fail to join with the canonical hex keys in `Booking_details`.
   - The 297 records with stripped leading zeros (e.g. `9632730` vs `09632730`) would fail to match `Booking_details`.
   - **Total missing guest info on direct join**: 895 reservations (0.75% of the entire database) would either be dropped (`INNER JOIN`) or produce `NULL` guest metrics (`LEFT JOIN`).

---

## 5. Deterministic Resolution Strategy

Because all six source files were partitioned row-by-row from a single master table, their physical row order (0 to 119,389) is identical.

### Proposed Deterministic Remediation Algorithm:

1. **Staging**: Load `Guest_info.csv` into raw staging table `stg_guest_info` with an auto-generated sequential row index (`source_row_id BIGSERIAL`).
2. **Canonical Alignment**: Load `Booking_details.csv` into `stg_booking_details` with the matching sequential row index (`source_row_id BIGSERIAL`).
3. **Reconciliation & Repair**:
   - For all 118,495 rows where `stg_guest_info.Booking_id = stg_booking_details.Booking_id`, validate 1-to-1 matching.
   - For the 895 rows where `stg_guest_info.Booking_id != stg_booking_details.Booking_id`, replace the corrupted `Booking_id` in `stg_guest_info` with the canonical `stg_booking_details.Booking_id` based on exact `source_row_id` alignment.
4. **Audit Logging**: Write every repaired row to `etl_data_quality_reconciliation_log` documenting:
   - `source_row_id`
   - `original_corrupted_id`
   - `repaired_canonical_id`
   - `repair_reason` (`'Excel scientific notation corruption'` or `'Excel stripped leading zeros'`).
5. **Constraint Enforcement**: Enforce a strict `PRIMARY KEY` and `FOREIGN KEY REFERENCES booking_details(booking_id)` in the core relational schema, ensuring zero duplicate keys and zero orphaned records.
