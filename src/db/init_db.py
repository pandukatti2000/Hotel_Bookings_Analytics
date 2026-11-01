import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config.settings import settings
from config.logging_config import logger, setup_logging

setup_logging()

def create_database_if_not_exists():
    logger.info(f"Checking if database '{settings.POSTGRES_DB}' exists...")
    conn = psycopg2.connect(
        dbname="postgres",
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (settings.POSTGRES_DB,))
    exists = cur.fetchone()
    if not exists:
        logger.info(f"Database '{settings.POSTGRES_DB}' does not exist. Creating...")
        cur.execute(f"CREATE DATABASE {settings.POSTGRES_DB};")
        logger.info(f"Database '{settings.POSTGRES_DB}' created successfully.")
    else:
        logger.info(f"Database '{settings.POSTGRES_DB}' already exists.")

    # Check/Create Readonly Role
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s;", (settings.POSTGRES_READONLY_USER,))
    role_exists = cur.fetchone()
    if not role_exists:
        logger.info(f"Creating read-only user '{settings.POSTGRES_READONLY_USER}'...")
        cur.execute(f"CREATE USER {settings.POSTGRES_READONLY_USER} WITH PASSWORD '{settings.POSTGRES_READONLY_PASSWORD}';")
        logger.info(f"Read-only user '{settings.POSTGRES_READONLY_USER}' created.")
    else:
        logger.info(f"Read-only user '{settings.POSTGRES_READONLY_USER}' already exists.")

    cur.close()
    conn.close()

def init_schemas_and_tables():
    logger.info("Initializing schemas, tables, and views in hotel_bookings_db...")
    conn = psycopg2.connect(
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()

    ddl_script = """
    -- Schemas
    CREATE SCHEMA IF NOT EXISTS staging;
    CREATE SCHEMA IF NOT EXISTS core;
    CREATE SCHEMA IF NOT EXISTS analytics;
    CREATE SCHEMA IF NOT EXISTS audit;

    -- Audit & Lineage
    CREATE TABLE IF NOT EXISTS audit.etl_ingestion_audit (
        audit_id SERIAL PRIMARY KEY,
        pipeline_run_id VARCHAR(50) NOT NULL,
        table_name VARCHAR(100) NOT NULL,
        source_file VARCHAR(255) NOT NULL,
        rows_read INTEGER NOT NULL,
        rows_staged INTEGER NOT NULL,
        rows_loaded INTEGER NOT NULL,
        status VARCHAR(30) NOT NULL,
        error_message TEXT,
        started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP WITH TIME ZONE
    );

    CREATE TABLE IF NOT EXISTS audit.etl_data_quality_reconciliation_log (
        log_id SERIAL PRIMARY KEY,
        pipeline_run_id VARCHAR(50) NOT NULL,
        table_name VARCHAR(100) NOT NULL,
        source_row_id BIGINT NOT NULL,
        original_value TEXT,
        repaired_value TEXT,
        reconciliation_rule VARCHAR(100) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Staging Tables
    DROP TABLE IF EXISTS staging.stg_booking_details;
    CREATE TABLE staging.stg_booking_details (
        source_row_id BIGSERIAL PRIMARY KEY,
        hotel TEXT,
        is_canceled TEXT,
        lead_time TEXT,
        arrival_date_year TEXT,
        arrival_date_month TEXT,
        arrival_date_week_number TEXT,
        arrival_date_day_of_month TEXT,
        stays_in_weekend_nights TEXT,
        stays_in_week_nights TEXT,
        country TEXT,
        Booking_id TEXT
    );

    DROP TABLE IF EXISTS staging.stg_booking_source_and_history;
    CREATE TABLE staging.stg_booking_source_and_history (
        source_row_id BIGSERIAL PRIMARY KEY,
        country TEXT,
        market_segment_id TEXT,
        distribution_channel_id TEXT,
        is_repeated_guest TEXT,
        previous_cancellations TEXT,
        previous_bookings_not_canceled TEXT,
        deposit_type TEXT,
        agent TEXT,
        company TEXT,
        days_in_waiting_list TEXT,
        customer_type TEXT,
        Booking_id TEXT
    );

    DROP TABLE IF EXISTS staging.stg_guest_info;
    CREATE TABLE staging.stg_guest_info (
        source_row_id BIGSERIAL PRIMARY KEY,
        adults TEXT,
        children TEXT,
        babies TEXT,
        Booking_id TEXT
    );

    DROP TABLE IF EXISTS staging.stg_meal_and_stay_details;
    CREATE TABLE staging.stg_meal_and_stay_details (
        source_row_id BIGSERIAL PRIMARY KEY,
        meal TEXT,
        adr TEXT,
        required_car_parking_spaces TEXT,
        total_of_special_requests TEXT,
        Booking_id TEXT
    );

    DROP TABLE IF EXISTS staging.stg_reservation_status;
    CREATE TABLE staging.stg_reservation_status (
        source_row_id BIGSERIAL PRIMARY KEY,
        reservation_status TEXT,
        reservation_status_date TEXT,
        Booking_id TEXT
    );

    DROP TABLE IF EXISTS staging.stg_room_details;
    CREATE TABLE staging.stg_room_details (
        source_row_id BIGSERIAL PRIMARY KEY,
        reserved_room_type TEXT,
        assigned_room_type TEXT,
        booking_changes TEXT,
        unnamed_col TEXT,
        Booking_id TEXT
    );

    -- Core Dimensions
    DROP TABLE IF EXISTS core.fct_guest_info CASCADE;
    DROP TABLE IF EXISTS core.fct_meal_and_stay CASCADE;
    DROP TABLE IF EXISTS core.fct_room_operations CASCADE;
    DROP TABLE IF EXISTS core.fct_reservation_status CASCADE;
    DROP TABLE IF EXISTS core.fct_bookings CASCADE;
    DROP TABLE IF EXISTS core.dim_country CASCADE;
    DROP TABLE IF EXISTS core.dim_market_segment CASCADE;
    DROP TABLE IF EXISTS core.dim_distribution_channel CASCADE;

    CREATE TABLE IF NOT EXISTS core.dim_country (
        country_code VARCHAR(10) PRIMARY KEY,
        country_name VARCHAR(100) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS core.dim_market_segment (
        market_segment_id SMALLINT PRIMARY KEY,
        market_segment_name VARCHAR(50) NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS core.dim_distribution_channel (
        distribution_channel_id SMALLINT PRIMARY KEY,
        distribution_channel_name VARCHAR(50) NOT NULL UNIQUE
    );

    -- Core Facts
    CREATE TABLE IF NOT EXISTS core.fct_bookings (
        booking_id CHAR(8) PRIMARY KEY,
        hotel VARCHAR(30) NOT NULL CHECK (hotel IN ('City Hotel', 'Resort Hotel')),
        is_canceled SMALLINT NOT NULL CHECK (is_canceled IN (0, 1)),
        lead_time INTEGER NOT NULL CHECK (lead_time >= 0),
        arrival_date DATE NOT NULL,
        arrival_year SMALLINT NOT NULL,
        arrival_month VARCHAR(15) NOT NULL,
        arrival_week_number SMALLINT NOT NULL,
        arrival_day_of_month SMALLINT NOT NULL,
        stays_in_weekend_nights SMALLINT NOT NULL CHECK (stays_in_weekend_nights >= 0),
        stays_in_week_nights SMALLINT NOT NULL CHECK (stays_in_week_nights >= 0),
        total_stay_nights INTEGER GENERATED ALWAYS AS (stays_in_weekend_nights + stays_in_week_nights) STORED,
        country_code VARCHAR(10) NOT NULL REFERENCES core.dim_country(country_code),
        market_segment_id SMALLINT NOT NULL REFERENCES core.dim_market_segment(market_segment_id),
        distribution_channel_id SMALLINT NOT NULL REFERENCES core.dim_distribution_channel(distribution_channel_id),
        is_repeated_guest SMALLINT NOT NULL CHECK (is_repeated_guest IN (0, 1)),
        previous_cancellations INTEGER NOT NULL CHECK (previous_cancellations >= 0),
        previous_bookings_not_canceled INTEGER NOT NULL CHECK (previous_bookings_not_canceled >= 0),
        deposit_type VARCHAR(20) NOT NULL CHECK (deposit_type IN ('No Deposit', 'Non Refund', 'Refundable')),
        agent_id INTEGER,
        company_id INTEGER,
        days_in_waiting_list INTEGER NOT NULL CHECK (days_in_waiting_list >= 0),
        customer_type VARCHAR(20) NOT NULL CHECK (customer_type IN ('Transient', 'Transient-Party', 'Contract', 'Group')),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS core.fct_guest_info (
        booking_id CHAR(8) PRIMARY KEY REFERENCES core.fct_bookings(booking_id) ON DELETE CASCADE,
        adults SMALLINT NOT NULL CHECK (adults >= 0),
        children SMALLINT NOT NULL DEFAULT 0 CHECK (children >= 0),
        babies SMALLINT NOT NULL CHECK (babies >= 0),
        total_guests SMALLINT GENERATED ALWAYS AS (adults + children + babies) STORED
    );

    CREATE TABLE IF NOT EXISTS core.fct_meal_and_stay (
        booking_id CHAR(8) PRIMARY KEY REFERENCES core.fct_bookings(booking_id) ON DELETE CASCADE,
        meal_code VARCHAR(15) NOT NULL,
        adr NUMERIC(10,2) NOT NULL,
        required_car_parking_spaces SMALLINT NOT NULL CHECK (required_car_parking_spaces >= 0),
        total_of_special_requests SMALLINT NOT NULL CHECK (total_of_special_requests >= 0)
    );

    CREATE TABLE IF NOT EXISTS core.fct_room_operations (
        booking_id CHAR(8) PRIMARY KEY REFERENCES core.fct_bookings(booking_id) ON DELETE CASCADE,
        reserved_room_type CHAR(1) NOT NULL,
        assigned_room_type CHAR(1) NOT NULL,
        is_room_reassigned SMALLINT GENERATED ALWAYS AS (CASE WHEN reserved_room_type <> assigned_room_type THEN 1 ELSE 0 END) STORED,
        booking_changes SMALLINT NOT NULL CHECK (booking_changes >= 0)
    );

    CREATE TABLE IF NOT EXISTS core.fct_reservation_status (
        booking_id CHAR(8) PRIMARY KEY REFERENCES core.fct_bookings(booking_id) ON DELETE CASCADE,
        reservation_status VARCHAR(15) NOT NULL CHECK (reservation_status IN ('Check-Out', 'Canceled', 'No-Show')),
        reservation_status_date DATE NOT NULL
    );

    -- Performance Indexes
    CREATE INDEX IF NOT EXISTS idx_fct_bookings_arrival_date ON core.fct_bookings(arrival_date);
    CREATE INDEX IF NOT EXISTS idx_fct_bookings_hotel_canceled ON core.fct_bookings(hotel, is_canceled);
    CREATE INDEX IF NOT EXISTS idx_fct_bookings_channel_segment ON core.fct_bookings(distribution_channel_id, market_segment_id);
    CREATE INDEX IF NOT EXISTS idx_fct_bookings_country ON core.fct_bookings(country_code);
    CREATE INDEX IF NOT EXISTS idx_fct_meal_stay_adr ON core.fct_meal_and_stay(adr);
    CREATE INDEX IF NOT EXISTS idx_fct_res_status_date ON core.fct_reservation_status(reservation_status_date);

    -- Analytical Star Schema View
    CREATE OR REPLACE VIEW analytics.v_hotel_bookings_analytics AS
    SELECT 
        b.booking_id,
        b.hotel,
        b.is_canceled,
        CASE WHEN b.is_canceled = 1 THEN 'Canceled / No-Show' ELSE 'Confirmed / Checked-Out' END AS booking_status_category,
        b.lead_time,
        CASE 
            WHEN b.lead_time <= 7 THEN '0-7 Days (Immediate)'
            WHEN b.lead_time <= 30 THEN '8-30 Days (Short-Lead)'
            WHEN b.lead_time <= 90 THEN '31-90 Days (Medium-Lead)'
            WHEN b.lead_time <= 180 THEN '91-180 Days (Long-Lead)'
            ELSE '180+ Days (Advance)'
        END AS lead_time_band,
        b.arrival_date,
        b.arrival_year,
        b.arrival_month,
        b.arrival_week_number,
        b.arrival_day_of_month,
        b.stays_in_weekend_nights,
        b.stays_in_week_nights,
        b.total_stay_nights,
        c.country_code,
        c.country_name,
        m.market_segment_id,
        m.market_segment_name,
        d.distribution_channel_id,
        d.distribution_channel_name,
        b.is_repeated_guest,
        b.previous_cancellations,
        b.previous_bookings_not_canceled,
        b.deposit_type,
        b.agent_id,
        b.company_id,
        b.days_in_waiting_list,
        b.customer_type,
        g.adults,
        g.children,
        g.babies,
        g.total_guests,
        CASE 
            WHEN g.adults = 1 AND g.children = 0 AND g.babies = 0 THEN 'Solo'
            WHEN g.adults = 2 AND g.children = 0 AND g.babies = 0 THEN 'Couple'
            WHEN g.children > 0 OR g.babies > 0 THEN 'Family'
            WHEN g.adults > 2 THEN 'Group / Adult Friends'
            ELSE 'Other'
        END AS guest_composition_type,
        ms.meal_code,
        CASE 
            WHEN ms.meal_code = 'BB' THEN 'Bed & Breakfast'
            WHEN ms.meal_code = 'HB' THEN 'Half Board'
            WHEN ms.meal_code = 'FB' THEN 'Full Board'
            WHEN ms.meal_code IN ('SC', 'Undefined') THEN 'Self Catering / Room Only'
            ELSE ms.meal_code
        END AS meal_description,
        GREATEST(ms.adr, 0.00) AS adr,
        ROUND((b.total_stay_nights * GREATEST(ms.adr, 0.00)), 2) AS estimated_booking_value,
        CASE WHEN b.is_canceled = 0 THEN ROUND((b.total_stay_nights * GREATEST(ms.adr, 0.00)), 2) ELSE 0.00 END AS estimated_realized_booking_value,
        ms.required_car_parking_spaces,
        ms.total_of_special_requests,
        ro.reserved_room_type,
        ro.assigned_room_type,
        ro.is_room_reassigned,
        ro.booking_changes,
        rs.reservation_status,
        rs.reservation_status_date
    FROM core.fct_bookings b
    JOIN core.dim_country c ON b.country_code = c.country_code
    JOIN core.dim_market_segment m ON b.market_segment_id = m.market_segment_id
    JOIN core.dim_distribution_channel d ON b.distribution_channel_id = d.distribution_channel_id
    JOIN core.fct_guest_info g ON b.booking_id = g.booking_id
    JOIN core.fct_meal_and_stay ms ON b.booking_id = ms.booking_id
    JOIN core.fct_room_operations ro ON b.booking_id = ro.booking_id
    JOIN core.fct_reservation_status rs ON b.booking_id = rs.booking_id;

    -- Grant Permissions to Read-Only User
    GRANT USAGE ON SCHEMA analytics TO hotel_readonly;
    GRANT USAGE ON SCHEMA core TO hotel_readonly;
    GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO hotel_readonly;
    GRANT SELECT ON ALL TABLES IN SCHEMA core TO hotel_readonly;
    ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT SELECT ON TABLES TO hotel_readonly;
    ALTER DEFAULT PRIVILEGES IN SCHEMA core GRANT SELECT ON TABLES TO hotel_readonly;
    """

    cur.execute(ddl_script)
    logger.info("Database schemas, tables, views, and permissions initialized successfully.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_database_if_not_exists()
    init_schemas_and_tables()
