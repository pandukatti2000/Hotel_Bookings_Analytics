# StayWise AI — KPI Methodology & Analytical Limitations

## 1. Executive Principles

1. **Deterministic SQL Logic**: All metrics must be computed with reproducible, tested SQL aggregations.
2. **Clear Denominators**: Every rate and percentage must declare its exact filtering conditions and denominator.
3. **No Revenue Overstatement**: The dataset records `adr` (Average Daily Rate) and booked nights (`stays_in_weekend_nights + stays_in_week_nights`). It does **NOT** record financial transactions, actual payment receipts, refunds, folio incidentals, penalties collected on non-refundable cancellations, or operational costs. Therefore, `adr * total_nights` must strictly be designated as **Estimated Booking Value**, never "Actual Revenue".
4. **Anti-Leakage Boundaries**: Attributes known strictly at check-in or post-stay (`reservation_status`, `assigned_room_type`, `reservation_status_date`) must be separated from pre-arrival reservation attributes (`lead_time`, `reserved_room_type`, `deposit_type`).

---

## 2. Standard Metric Definitions (SQL Specification)

### 2.1 Total Bookings (`total_bookings`)
- **Formula**: `COUNT(*)`
- **SQL**:
  ```sql
  SELECT COUNT(*) AS total_bookings FROM fct_bookings;
  ```
- **Denominator**: Total reservations in scope. Result across entire dataset: **119,390**.

### 2.2 Canceled Bookings (`canceled_bookings`)
- **Formula**: `COUNT(*) FILTER (WHERE is_canceled = 1)`
- **SQL**:
  ```sql
  SELECT COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings FROM fct_bookings;
  ```
- **Result across dataset**: **44,224** (43,017 Canceled + 1,207 No-Shows).

### 2.3 Cancellation Rate (`cancellation_rate`)
- **Formula**: `(Canceled Bookings / Total Bookings) * 100.0`
- **SQL**:
  ```sql
  SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct 
  FROM fct_bookings;
  ```
- **Result across dataset**: **37.04%** (City Hotel: **41.73%**; Resort Hotel: **27.76%**).

### 2.4 Non-Canceled Bookings (`non_canceled_bookings`)
- **Formula**: `COUNT(*) FILTER (WHERE is_canceled = 0)`
- **SQL**:
  ```sql
  SELECT COUNT(*) FILTER (WHERE is_canceled = 0) AS non_canceled_bookings FROM fct_bookings;
  ```
- **Result across dataset**: **75,166** (100% matched to `reservation_status = 'Check-Out'`).

### 2.5 Average Lead Time (`avg_lead_time`)
- **Formula**: `AVG(lead_time)`
- **SQL**:
  ```sql
  SELECT ROUND(AVG(lead_time), 2) AS avg_lead_time_days FROM fct_bookings;
  ```
- **Result across dataset**: **104.01 days** (Median: **69 days**).

### 2.6 Average Daily Rate (`avg_adr`)
- **Formula**: `AVG(adr)` (Filtered for non-negative rates)
- **SQL**:
  ```sql
  SELECT ROUND(AVG(GREATEST(adr, 0.00)), 2) AS avg_adr FROM fct_meal_and_stay;
  ```
- **Result across dataset**: **$101.83** (Median: **$94.58**; std dev: **$50.54**).

### 2.7 Total Booked Room Nights (`total_booked_nights`)
- **Formula**: `SUM(stays_in_weekend_nights + stays_in_week_nights)`
- **SQL**:
  ```sql
  SELECT SUM(stays_in_weekend_nights + stays_in_week_nights) AS total_booked_room_nights 
  FROM fct_bookings;
  ```
- **Result across dataset**: **409,058 room nights** (Average stay: **3.43 nights**).

### 2.8 Estimated Gross Booking Value (`estimated_gross_booking_value`)
- **Definition**: Estimated value of all booked stays at reservation rate, including reservations subsequently canceled.
- **Formula**: `SUM((stays_in_weekend_nights + stays_in_week_nights) * GREATEST(adr, 0.00))`
- **SQL**:
  ```sql
  SELECT ROUND(SUM((b.stays_in_weekend_nights + b.stays_in_week_nights) * GREATEST(m.adr, 0.00)), 2) AS estimated_gross_booking_value
  FROM fct_bookings b
  JOIN fct_meal_and_stay m ON b.booking_id = m.booking_id;
  ```
- **Result across dataset**: **$42,869,451.72**.

### 2.9 Estimated Realized Booking Value (`estimated_realized_booking_value`)
- **Definition**: Estimated room value of reservations that successfully fulfilled their stay (`is_canceled = 0`).
- **Formula**: `SUM((stays_in_weekend_nights + stays_in_week_nights) * GREATEST(adr, 0.00)) FILTER (WHERE is_canceled = 0)`
- **SQL**:
  ```sql
  SELECT ROUND(SUM((b.stays_in_weekend_nights + b.stays_in_week_nights) * GREATEST(m.adr, 0.00)), 2) AS estimated_realized_booking_value
  FROM fct_bookings b
  JOIN fct_meal_and_stay m ON b.booking_id = m.booking_id
  WHERE b.is_canceled = 0;
  ```
- **Result across dataset**: **$26,981,048.86** (Estimated potential lost booking value from cancellations: **$15,888,402.86** / 37.06%).

### 2.10 Repeat Guest Percentage (`repeat_guest_pct`)
- **Formula**: `(COUNT(*) FILTER (WHERE is_repeated_guest = 1) / COUNT(*)) * 100.0`
- **SQL**:
  ```sql
  SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE is_repeated_guest = 1) / NULLIF(COUNT(*), 0), 2) AS repeat_guest_pct
  FROM fct_bookings;
  ```
- **Result across dataset**: **3.19%** (3,810 bookings).

### 2.11 Room Reassignment Rate (`room_reassignment_rate`)
- **Formula**: `(COUNT(*) FILTER (WHERE reserved_room_type != assigned_room_type) / COUNT(*)) * 100.0`
- **SQL**:
  ```sql
  SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE reserved_room_type != assigned_room_type) / NULLIF(COUNT(*), 0), 2) AS room_reassignment_pct
  FROM fct_room_operations;
  ```
- **Result across dataset**: **12.49%** (14,917 reservations).

### 2.12 Average Special Requests (`avg_special_requests`)
- **Formula**: `AVG(total_of_special_requests)`
- **SQL**:
  ```sql
  SELECT ROUND(AVG(total_of_special_requests), 2) AS avg_special_requests FROM fct_meal_and_stay;
  ```
- **Result across dataset**: **0.57 requests per booking** (70,318 bookings had 0 requests).

### 2.13 Channel Booking Share & Channel Cancellation Rate
- **SQL**:
  ```sql
  SELECT 
      d.distribution_channel_name,
      COUNT(*) AS channel_bookings,
      ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS channel_share_pct,
      COUNT(*) FILTER (WHERE b.is_canceled = 1) AS canceled_bookings,
      ROUND(100.0 * COUNT(*) FILTER (WHERE b.is_canceled = 1) / COUNT(*), 2) AS channel_cancellation_rate_pct
  FROM fct_bookings b
  JOIN dim_distribution_channel d ON b.distribution_channel_id = d.distribution_channel_id
  GROUP BY d.distribution_channel_name
  ORDER BY channel_bookings DESC;
  ```
- **Results across dataset**:
  - `TA/TO`: 97,870 bookings (81.97% share) | Cancellation Rate: **41.06%**
  - `Direct`: 14,645 bookings (12.27% share) | Cancellation Rate: **17.46%**
  - `Corporate`: 6,677 bookings (5.59% share) | Cancellation Rate: **22.08%**
  - `GDS`: 193 bookings (0.16% share) | Cancellation Rate: **19.17%**
  - `Undefined`: 5 bookings (<0.01% share) | Cancellation Rate: **80.00%**

---

## 3. Analytical Limitations & Guardrails

1. **No Accounting Ledger**: The dataset contains no records of payments made, deposits retained, or refunds issued.
2. **Non-Refundable Deposit Paradox**: Bookings under `deposit_type = 'Non Refund'` exhibit a **99.36% cancellation rate** (14,494 canceled out of 14,587 bookings), almost entirely originating from group tours booked via travel agencies. While labeled "canceled", the hotel may have legally retained full deposit revenue. Thus, cancellation does not imply $0 revenue for this segment.
3. **Overbooking & Day-Use**: Zero-night stays (715 records) and zero-guest stays (180 records) represent valid hospitality operational anomalies that must be preserved with metadata flags rather than dropped.
