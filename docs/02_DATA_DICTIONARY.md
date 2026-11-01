# StayWise AI — Detailed Data Dictionary

## 1. Overview

The dataset models hotel reservations split across 6 transactional entity files and 3 dimension/lookup files. All 6 transactional tables share an 8-character hexadecimal identifier (`Booking_id`) representing 119,390 reservations.

---

## 2. Table: `booking_details` (`Booking_details.csv`)

Primary transactional table describing the property, booking timeline, arrival calendar components, length of stay, and country of origin.

| Column Name | CSV Type | MySQL Type | Proposed PostgreSQL Type | Null Count | Nullable? | Valid Values / Range | Description & Business Semantics |
|---|---|---|---|---|---|---|---|
| `hotel` | string | text | `VARCHAR(30)` | 0 | No | `'City Hotel'`, `'Resort Hotel'` | Type of hotel property. |
| `is_canceled` | int64 | bigint | `SMALLINT` | 0 | No | `0, 1` | Cancellation indicator: `1` if canceled or no-show; `0` if checked out. |
| `lead_time` | int64 | bigint | `INTEGER` | 0 | No | `0` to `737` | Number of days elapsed between booking date and arrival date. |
| `arrival_date_year` | int64 | bigint | `SMALLINT` | 0 | No | `2015, 2016, 2017` | Calendar year of arrival date. |
| `arrival_date_month` | string | text | `VARCHAR(15)` | 0 | No | `'January'` – `'December'` | Calendar month name of arrival. |
| `arrival_date_week_number` | int64 | bigint | `SMALLINT` | 0 | No | `1` to `53` | ISO week number for arrival date. |
| `arrival_date_day_of_month` | int64 | bigint | `SMALLINT` | 0 | No | `1` to `31` | Day of the month of arrival. |
| `stays_in_weekend_nights` | int64 | bigint | `SMALLINT` | 0 | No | `0` to `19` | Number of weekend nights (Saturday, Sunday) booked. |
| `stays_in_week_nights` | int64 | bigint | `SMALLINT` | 0 | No | `0` to `50` | Number of week nights (Monday – Friday) booked. |
| `country` | string | text | `CHAR(3)` | 488 | Yes | 177 ISO-3166-1 alpha-3 codes | Country of residence of guest. Matches `country.country_code`. |
| `Booking_id` | string | text | `CHAR(8)` | 0 | No | 8-character hex string | Primary Key / Business key for the reservation. |

---

## 3. Table: `booking_source_and_history` (`Booking_Source_and_History.csv`)

Captures distribution channel, market segment, customer type, booking agent/company, deposit type, and guest reservation history.

| Column Name | CSV Type | MySQL Type | Proposed PostgreSQL Type | Null Count | Nullable? | Valid Values / Range | Description & Business Semantics |
|---|---|---|---|---|---|---|---|
| `country` | string | text | `CHAR(3)` | 488 | Yes | 177 ISO-3166-1 alpha-3 codes | Redundant country code matching `booking_details.country`. |
| `market_segment_id` | int64 | bigint | `SMALLINT` | 0 | No | `1` to `8` | Foreign Key to `market_segment.market_segment_id`. |
| `distribution_channel_id` | int64 | bigint | `SMALLINT` | 0 | No | `1` to `5` | Foreign Key to `distribution_channel.distribution_channel_id`. |
| `is_repeated_guest` | int64 | bigint | `SMALLINT` | 0 | No | `0, 1` | `1` if the guest has booked previously; `0` otherwise. |
| `previous_cancellations` | int64 | bigint | `INTEGER` | 0 | No | `0` to `26` | Number of prior bookings canceled by guest prior to current booking. |
| `previous_bookings_not_canceled` | int64 | bigint | `INTEGER` | 0 | No | `0` to `72` | Number of prior bookings confirmed and not canceled by guest. |
| `deposit_type` | string | text | `VARCHAR(20)` | 0 | No | `'No Deposit'`, `'Non Refund'`, `'Refundable'` | Deposit terms under which booking was accepted. |
| `agent` | float64 | double | `INTEGER` | 16,340 | Yes | `1` to `535` | Identifier of travel agency that made the booking (null if direct). |
| `company` | float64 | double | `INTEGER` | 112,593 | Yes | `6` to `543` | Identifier of company that made/paid for booking (null if individual). |
| `days_in_waiting_list` | int64 | bigint | `INTEGER` | 0 | No | `0` to `391` | Days the reservation spent on the waiting list before confirmation. |
| `customer_type` | string | text | `VARCHAR(20)` | 0 | No | `'Transient'`, `'Transient-Party'`, `'Contract'`, `'Group'` | Classification of booking contract/stay type. |
| `Booking_id` | string | text | `CHAR(8)` | 0 | No | 8-character hex string | Foreign Key to `booking_details.Booking_id`. |

---

## 4. Table: `guest_info` (`Guest_info.csv`)

Captures party composition (adults, children, babies).

| Column Name | CSV Type | MySQL Type | Proposed PostgreSQL Type | Null Count | Nullable? | Valid Values / Range | Description & Business Semantics |
|---|---|---|---|---|---|---|---|
| `adults` | int64 | bigint | `SMALLINT` | 0 | No | `0` to `55` | Number of adults in party. |
| `children` | float64 | double | `SMALLINT` | 4 | Yes | `0` to `10` (4 nulls) | Number of children. Missing values represent 0 children. |
| `babies` | int64 | bigint | `SMALLINT` | 0 | No | `0` to `10` | Number of babies in party. |
| `Booking_id` | string | text | `CHAR(8)` | 0 | No | Corrupted hex/scientific strings | Foreign Key to `booking_details.Booking_id`. Subject to repair. |

---

## 5. Table: `meal_and_stay_details` (`Meal_And_Stay_Details.csv`)

Captures boarding meal plan, financial rate (ADR), and operational services.

| Column Name | CSV Type | MySQL Type | Proposed PostgreSQL Type | Null Count | Nullable? | Valid Values / Range | Description & Business Semantics |
|---|---|---|---|---|---|---|---|
| `meal` | string | text | `VARCHAR(15)` | 0 | No | `'BB'`, `'HB'`, `'FB'`, `'SC'`, `'Undefined'` | Board package (`BB`=Bed & Breakfast, `HB`=Half Board, `FB`=Full Board, `SC`=Self Catering). |
| `adr` | float64 | double | `NUMERIC(10,2)` | 0 | No | `-6.38` to `5400.00` | Average Daily Rate (total room revenue divided by total nights). |
| `required_car_parking_spaces` | int64 | bigint | `SMALLINT` | 0 | No | `0` to `8` | Number of parking spaces requested by the guest. |
| `total_of_special_requests` | int64 | bigint | `SMALLINT` | 0 | No | `0` to `5` | Total number of special requests (e.g. high floor, twin bed). |
| `Booking_id` | string | text | `CHAR(8)` | 0 | No | 8-character hex string | Foreign Key to `booking_details.Booking_id`. |

---

## 6. Table: `reservation_status` (`Reservation_status.csv`)

Captures the terminal disposition of the booking and date of that status change.

| Column Name | CSV Type | MySQL Type | Proposed PostgreSQL Type | Null Count | Nullable? | Valid Values / Range | Description & Business Semantics |
|---|---|---|---|---|---|---|---|
| `reservation_status` | string | text | `VARCHAR(15)` | 0 | No | `'Check-Out'`, `'Canceled'`, `'No-Show'` | Final booking status. Strictly correlates with `is_canceled`. |
| `reservation_status_date` | string | text | `DATE` | 0 | No | `'2014-10-17'` to `'2017-09-14'` | Date status was recorded (cancellation date or check-out date). |
| `Booking_id` | string | text | `CHAR(8)` | 0 | No | 8-character hex string | Foreign Key to `booking_details.Booking_id`. |

---

## 7. Table: `room_details` (`Room_Details.csv`)

Captures room reservation versus allocation, and modification frequency.

| Column Name | CSV Type | MySQL Type | Proposed PostgreSQL Type | Null Count | Nullable? | Valid Values / Range | Description & Business Semantics |
|---|---|---|---|---|---|---|---|
| `reserved_room_type` | string | text | `CHAR(1)` | 0 | No | `'A'`, `'B'`, `'C'`, `'D'`, `'E'`, `'F'`, `'G'`, `'H'`, `'L'`, `'P'` | Code of room type reserved at booking time. |
| `assigned_room_type` | string | text | `CHAR(1)` | 0 | No | `'A'`, `'B'`, `'C'`, `'D'`, `'E'`, `'F'`, `'G'`, `'H'`, `'I'`, `'K'`, `'L'`, `'P'` | Code of room type actually assigned at check-in. |
| `booking_changes` | int64 | bigint | `SMALLINT` | 0 | No | `0` to `21` | Number of modifications made to booking between booking and check-in. |
| `Unnamed: 3` | float64 | double | N/A (Drop) | 119,390 | Yes | 100% NULL | Completely empty trailing delimiter column. Drop during ETL. |
| `Booking_id` | string | text | `CHAR(8)` | 0 | No | 8-character hex string | Foreign Key to `booking_details.Booking_id`. |

---

## 8. Lookup Tables

### 8.1 `country` (`country.csv`)
- `country_code` (`CHAR(3)`): ISO-3166-1 alpha-3 code (e.g. `'PRT'`, `'GBR'`, `'USA'`). Contains padded whitespace in source CSV.
- `country_name` (`VARCHAR(100)`): Full country name (e.g. `'Portugal'`, `'United Kingdom'`). Contains padded whitespace in source CSV.
- Includes row `'NULL'` with name `'Unknown'`.

### 8.2 `market_segment` (`market_Segment.csv`)
- `market_segment_id` (`SMALLINT`): Primary key (`1` to `8`).
- `market_segment` (`VARCHAR(50)`): Name (`'Direct'`, `'Corporate'`, `'Online TA'`, `'Offline TA/TO'`, `'Complementary'`, `'Groups'`, `'Undefined'`, `'Aviation'`).

### 8.3 `distribution_channel` (`distribution_channel.csv`)
- `distribution_channel_id` (`SMALLINT`): Primary key (`1` to `5`).
- `distribution_channel` (`VARCHAR(50)`): Name (`'Direct'`, `'Corporate'`, `'TA/TO'`, `'Undefined'`, `'GDS'`).
