# StayWise AI — Entity Relationship Diagram (ERD)

## 1. Relational Core Architecture (Cleaned 3NF Model)

The diagram below illustrates the normalized relational structure designed for PostgreSQL (`hotel_bookings_db`), connecting the core booking reservation entity to its operational child tables and validated dimension lookup tables.

```mermaid
erDiagram
    DIM_COUNTRY ||--o{ FCT_BOOKINGS : "originates from"
    DIM_MARKET_SEGMENT ||--o{ FCT_BOOKINGS : "acquired through"
    DIM_DISTRIBUTION_CHANNEL ||--o{ FCT_BOOKINGS : "distributed via"
    
    FCT_BOOKINGS ||--|| FCT_GUEST_INFO : "comprises party"
    FCT_BOOKINGS ||--|| FCT_MEAL_AND_STAY : "billed under"
    FCT_BOOKINGS ||--|| FCT_ROOM_OPERATIONS : "allocates room"
    FCT_BOOKINGS ||--|| FCT_RESERVATION_STATUS : "terminates with"

    DIM_COUNTRY {
        char(3) country_code PK
        varchar(100) country_name
    }

    DIM_MARKET_SEGMENT {
        smallint market_segment_id PK
        varchar(50) market_segment_name
    }

    DIM_DISTRIBUTION_CHANNEL {
        smallint distribution_channel_id PK
        varchar(50) distribution_channel_name
    }

    FCT_BOOKINGS {
        char(8) booking_id PK
        varchar(30) hotel
        smallint is_canceled
        integer lead_time
        date arrival_date
        smallint arrival_year
        varchar(15) arrival_month
        smallint arrival_week_number
        smallint arrival_day_of_month
        smallint stays_in_weekend_nights
        smallint stays_in_week_nights
        integer total_stay_nights
        char(3) country_code FK
        smallint market_segment_id FK
        smallint distribution_channel_id FK
        smallint is_repeated_guest
        integer previous_cancellations
        integer previous_bookings_not_canceled
        varchar(20) deposit_type
        integer agent_id
        integer company_id
        integer days_in_waiting_list
        varchar(20) customer_type
    }

    FCT_GUEST_INFO {
        char(8) booking_id PK, FK
        smallint adults
        smallint children
        smallint babies
        smallint total_guests
    }

    FCT_MEAL_AND_STAY {
        char(8) booking_id PK, FK
        varchar(15) meal_code
        numeric adr
        smallint required_car_parking_spaces
        smallint total_of_special_requests
        numeric estimated_booking_value
    }

    FCT_ROOM_OPERATIONS {
        char(8) booking_id PK, FK
        char(1) reserved_room_type
        char(1) assigned_room_type
        smallint is_room_reassigned
        smallint booking_changes
    }

    FCT_RESERVATION_STATUS {
        char(8) booking_id PK, FK
        varchar(15) reservation_status
        date reservation_status_date
    }
```

---

## 2. Curated Dimensional / Analytical View (`v_hotel_bookings_analytics`)

For high-performance BI reporting, Streamlit visualization, and LLM text-to-SQL generation, all normalized entities are projected into a single, fully typed, denormalized view:

```mermaid
flowchart TD
    subgraph Dimension_Tables [Lookup Dimensions]
        DC[dim_country]
        DMS[dim_market_segment]
        DDC[dim_distribution_channel]
    end

    subgraph Relational_Entities [Transactional Facts]
        FB[fct_bookings]
        FGI[fct_guest_info]
        FMS[fct_meal_and_stay]
        FRO[fct_room_operations]
        FRS[fct_reservation_status]
    end

    subgraph Analytical_View [v_hotel_bookings_analytics]
        direction TB
        V1["booking_id PK"]
        V2["hotel, is_canceled, lead_time, arrival_date"]
        V3["stays_weekend, stays_week, total_stay_nights"]
        V4["country_code, country_name"]
        V5["market_segment, distribution_channel"]
        V6["adults, children, babies, total_guests"]
        V7["meal, adr, estimated_booking_value"]
        V8["reserved_room, assigned_room, is_room_reassigned"]
        V9["deposit_type, customer_type, is_repeated_guest"]
        V10["special_requests, parking_spaces, booking_changes"]
        V11["reservation_status, reservation_status_date"]
    end

    DC --> V4
    DMS --> V5
    DDC --> V5
    FB --> V1
    FGI --> V6
    FMS --> V7
    FRO --> V8
    FRS --> V11

    V1 --> Streamlit["Streamlit Dashboard"]
    V1 --> FastAPI["FastAPI Backend Services"]
    V1 --> AI_Agent["LangGraph AI SQL Assistant"]
```
