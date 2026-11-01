# StayWise AI — Dataset Inventory

## 1. Executive Summary

This inventory documents all source files located in `hotel_booking-main/hotel_booking-main/Data`. The source data consists of:
- **11 CSV files**: 6 transactional tables and 5 lookup/dimension files (including duplicates).
- **11 MySQL SQL dump files**: DDL and `INSERT` statements generated from MySQL 8.0.34.
- **1 ZIP archive**: Containing a consolidated MySQL dump (`consolidated.sql`, ~41.5 MB uncompressed).

The primary dataset captures **119,390 hotel booking records** across two property types: **City Hotel** (79,330 records / 66.45%) and **Resort Hotel** (40,060 records / 33.55%) from **July 1, 2015 to August 31, 2017**.

---

## 2. Complete File Catalog & Cryptographic Verification

All files were profiled using SHA-256 checksums to verify integrity and detect redundancies.

| Relative Path | Size (Bytes) | Size (KB) | Row Count | Column Count | SHA-256 Checksum | Category / Status |
|---|---|---|---|---|---|---|
| `CSV/Booking_details.csv` | 6,252,031 | 6,105.50 | 119,390 | 11 | `9b24874b45cb8e30b69ba32688942b08fa1ffc5655a6d3f232c4e6101c4c81f3` | Core Transactional Table |
| `CSV/Booking_Source_and_History.csv` | 6,423,764 | 6,273.21 | 119,390 | 12 | `060a3a7667da20e03e5ba826e7a17726a97ee0efb79211fbbece3732ec74f664` | Core Transactional Table |
| `CSV/Guest_info.csv` | 1,910,041 | 1,865.27 | 119,390 | 4 | `50f1afb2cd2595ff9c3a3b5ba660233633e9d30fb39df3df86a7ff2c286ff0d0` | Core Transactional (Corrupted IDs) |
| `CSV/Meal_And_Stay_Details.csv` | 2,707,494 | 2,644.04 | 119,390 | 5 | `2e7e05a3f0d57e4e132c3f8da0ebbb4767104b2b144fa5d070119e7e7a898a3b` | Core Transactional Table |
| `CSV/Reservation_status.csv` | 3,655,714 | 3,570.03 | 119,390 | 3 | `fa75e1aef9733054fb4a4bb4fc1fa8f81fbc0d8434863e4806a771960fb563b7` | Core Transactional Table |
| `CSV/Room_Details.csv` | 2,029,737 | 1,982.17 | 119,390 | 5 | `623d4fed3f58a7b055ff275394be0841ff51e605d8f63459c3a9ba00d64f0ea8` | Core Transactional Table |
| `CSV/Room_Details .csv` | 2,029,737 | 1,982.17 | 119,390 | 5 | `623d4fed3f58a7b055ff275394be0841ff51e605d8f63459c3a9ba00d64f0ea8` | **Identical Duplicate** (Trailing space in filename) |
| `CSV/country.csv` | 7,175 | 7.01 | 178 | 2 | `c05a9477adfb4603c6da1c667087754f9a0f0278bbafba0cb6b67702878bf879` | Lookup Table (Padded with whitespace) |
| `CSV/distribution_channel.csv` | 98 | 0.10 | 5 | 2 | `64ec722abe479532822a1ce3ff050117fcdd9f1e18bf97b57fc6886e92ea20e0` | Lookup Table |
| `CSV/market_Segment.csv` | 139 | 0.14 | 8 | 2 | `64103e52f44c41460ea8fa73ddb27ec4a39556d10db8d697858d4a9466e34274` | Lookup Table |
| `CSV/market Segment.csv` | 139 | 0.14 | 8 | 2 | `64103e52f44c41460ea8fa73ddb27ec4a39556d10db8d697858d4a9466e34274` | **Identical Duplicate** (Space instead of underscore) |
| `SQL/consolidated.zip` | 7,556,037 | 7,378.94 | N/A | N/A | `ecc42e95c8be44962c083fe08285ba05b0b30ef05ec103a085d3ae728d82dbe0` | Zip Archive containing `consolidated.sql` |
| `SQL/hotel_booking_booking_details.sql` | 7,330,108 | 7,158.31 | N/A | N/A | `07cd7cafe100155b90f4dbfbcf26dbeeb85890f507b55928f6e80b2b8eecddf3` | MySQL Dump: `booking_details` |
| `SQL/hotel_booking_booking_source_and_history.sql` | 7,798,070 | 7,615.30 | N/A | N/A | `47219f6259cfb6cfdb41f021e1d3550e6878b209d73d6bb6dc479b37c050e50f` | MySQL Dump: `booking_source_and_history` |
| `SQL/hotel_booking_country.sql` | 10,115 | 9.88 | N/A | N/A | `908653a43f8f90761a293a7431e28988636ba77b077a942a220264db8ea98ba3` | MySQL Dump: `country` |
| `SQL/hotel_booking_df_booking_details.sql` | 7,330,153 | 7,158.35 | N/A | N/A | `f447ab3433c51ee8e860bc0bf82ae446f7734bbd85d71a1c3bb54b38d3807ee1` | MySQL Dump: `df_booking_details` (Redundant) |
| `SQL/hotel_booking_df_booking_source_and_history.sql` | 7,798,115 | 7,615.35 | N/A | N/A | `13c9f599ab426ee41a18c642c8695029e0004e6c99db1c55a5b172a6b46ea4ea` | MySQL Dump: `df_booking_source_and_history` (Redundant) |
| `SQL/hotel_booking_distribution_channel.sql` | 2,282 | 2.23 | N/A | N/A | `e78c03b69a41fc32e8d9756184ca78fa3daaaae26d7022e3ea8667a1ca395353` | MySQL Dump: `distribution_channel` |
| `SQL/hotel_booking_guest_info.sql` | 2,270,436 | 2,217.22 | N/A | N/A | `9d17aee4a2dbfc6cbf09a632734199aa123b3ca794fb3c89b88e178b548b792e` | MySQL Dump: `guest_info` (Contains corrupted IDs) |
| `SQL/hotel_booking_market_segment.sql` | 2,284 | 2.23 | N/A | N/A | `9411840629486c9d7790b8fbe7174dbd2953258c7041764c207903db14eb194f` | MySQL Dump: `market_segment` |
| `SQL/hotel_booking_meal_and_stay_details.sql` | 3,167,071 | 3,092.84 | N/A | N/A | `227b6179c1507d967396a5e1cfcb693a1df93c042eeaaec2fe52882103f6f3e1` | MySQL Dump: `meal_and_stay_details` |
| `SQL/hotel_booking_reservation_status.sql` | 4,493,761 | 4,388.44 | N/A | N/A | `ceb05f263cda1852ebf3a3889b9cae47514a34b277ef5d46e315024218eb8bbd` | MySQL Dump: `reservation_status` |
| `SQL/hotel_booking_room_details.sql` | 3,345,288 | 3,266.88 | N/A | N/A | `faff1f3aaffea96d8ddb51f0c2ef3518e388ffc267ff6109df5eaec4d422ca8e` | MySQL Dump: `room_details` |

---

## 3. Redundancy & Duplicate Analysis

### 3.1 Duplicate CSV Files
1. **`Room_Details .csv` vs `Room_Details.csv`**:
   - Both files have identical size (2,029,737 bytes) and matching SHA-256 (`623d4fed3f58a7b055ff275394be0841ff51e605d8f63459c3a9ba00d64f0ea8`).
   - The file with a trailing space (`Room_Details .csv`) was created inadvertently. **Action**: Target `Room_Details.csv` for ETL.
2. **`market Segment.csv` vs `market_Segment.csv`**:
   - Both files have identical size (139 bytes) and matching SHA-256 (`64103e52f44c41460ea8fa73ddb27ec4a39556d10db8d697858d4a9466e34274`).
   - **Action**: Target `market_Segment.csv` for ETL.

### 3.2 Duplicate / Variant MySQL Dumps
1. **`hotel_booking_booking_details.sql` vs `hotel_booking_df_booking_details.sql`**:
   - Content diff shows the only difference is the table name: `booking_details` vs `df_booking_details` (a pandas export artifact). Data rows and column schemas are identical.
2. **`hotel_booking_booking_source_and_history.sql` vs `hotel_booking_df_booking_source_and_history.sql`**:
   - Content diff shows the only difference is the table name: `booking_source_and_history` vs `df_booking_source_and_history`.
3. **`consolidated.zip`**:
   - Contains a single file `consolidated.sql` (43,533,123 bytes uncompressed), concatenating all MySQL table creation and insert scripts into one file.

---

## 4. Ingestion Recommendation

- **Do NOT execute MySQL dumps** in PostgreSQL:
  - MySQL syntax uses backticks (`` `table` ``), `ENGINE=InnoDB`, MySQL collation `utf8mb4_0900_ai_ci`, and non-standard locking (`LOCK TABLES`).
  - `hotel_booking_guest_info.sql` already contains the corrupted scientific notation values.
- **Recommended Ingestion Strategy**:
  - Ingest directly from canonical CSVs using Python / PostgreSQL `COPY` into raw staging tables.
  - Apply deterministic data-cleaning, whitespace trimming, and booking identifier repair in the staging-to-core ELT transformation pipeline.
