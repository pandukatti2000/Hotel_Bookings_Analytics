import os
import sys
import uuid
import time
import psycopg2
import pandas as pd
from datetime import datetime
from config.settings import settings
from config.logging_config import logger, setup_logging

setup_logging()

def run_etl():
    run_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    logger.info(f"Starting ETL pipeline run_id='{run_id}'...")

    conn = psycopg2.connect(
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT
    )
    conn.autocommit = False
    cur = conn.cursor()

    try:
        # 1. Ingest Lookup Tables
        logger.info("Ingesting lookup tables...")
        
        # 1.1 dim_country (with whitespace trimming)
        country_csv = settings.CSV_DIR / "country.csv"
        df_country = pd.read_csv(country_csv)
        df_country["country_code"] = df_country["country_code"].astype(str).str.strip()
        df_country["country_name"] = df_country["country_name"].astype(str).str.strip()
        
        cur.execute("TRUNCATE TABLE core.dim_country CASCADE;")
        for _, r in df_country.iterrows():
            cur.execute(
                "INSERT INTO core.dim_country (country_code, country_name) VALUES (%s, %s) ON CONFLICT (country_code) DO NOTHING;",
                (r["country_code"], r["country_name"])
            )
        logger.info(f"Loaded {len(df_country)} countries into core.dim_country.")

        # 1.2 dim_market_segment
        mkt_csv = settings.CSV_DIR / "market_Segment.csv"
        df_mkt = pd.read_csv(mkt_csv)
        cur.execute("TRUNCATE TABLE core.dim_market_segment CASCADE;")
        for _, r in df_mkt.iterrows():
            cur.execute(
                "INSERT INTO core.dim_market_segment (market_segment_id, market_segment_name) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (int(r["market_segment_id"]), str(r["market_segment"]).strip())
            )
        logger.info(f"Loaded {len(df_mkt)} segments into core.dim_market_segment.")

        # 1.3 dim_distribution_channel
        dist_csv = settings.CSV_DIR / "distribution_channel.csv"
        df_dist = pd.read_csv(dist_csv)
        cur.execute("TRUNCATE TABLE core.dim_distribution_channel CASCADE;")
        for _, r in df_dist.iterrows():
            cur.execute(
                "INSERT INTO core.dim_distribution_channel (distribution_channel_id, distribution_channel_name) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (int(r["distribution_channel_id"]), str(r["distribution_channel"]).strip())
            )
        logger.info(f"Loaded {len(df_dist)} channels into core.dim_distribution_channel.")

        # 2. Stage Transactional CSVs
        logger.info("Staging raw transactional tables...")
        
        tables_to_csv = [
            ("staging.stg_booking_details", "Booking_details.csv", 
             "(hotel, is_canceled, lead_time, arrival_date_year, arrival_date_month, arrival_date_week_number, arrival_date_day_of_month, stays_in_weekend_nights, stays_in_week_nights, country, Booking_id)"),
            
            ("staging.stg_booking_source_and_history", "Booking_Source_and_History.csv",
             "(country, market_segment_id, distribution_channel_id, is_repeated_guest, previous_cancellations, previous_bookings_not_canceled, deposit_type, agent, company, days_in_waiting_list, customer_type, Booking_id)"),
            
            ("staging.stg_guest_info", "Guest_info.csv",
             "(adults, children, babies, Booking_id)"),
            
            ("staging.stg_meal_and_stay_details", "Meal_And_Stay_Details.csv",
             "(meal, adr, required_car_parking_spaces, total_of_special_requests, Booking_id)"),
            
            ("staging.stg_reservation_status", "Reservation_status.csv",
             "(reservation_status, reservation_status_date, Booking_id)"),
            
            ("staging.stg_room_details", "Room_Details.csv",
             "(reserved_room_type, assigned_room_type, booking_changes, unnamed_col, Booking_id)")
        ]

        for tbl, fname, cols in tables_to_csv:
            cur.execute(f"TRUNCATE TABLE {tbl};")
            csv_path = settings.CSV_DIR / fname
            with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Use COPY
                copy_sql = f"COPY {tbl} {cols} FROM STDIN WITH (FORMAT csv, HEADER true, NULL '');"
                cur.copy_expert(copy_sql, f)
            
            cur.execute(f"SELECT COUNT(*) FROM {tbl};")
            cnt = cur.fetchone()[0]
            logger.info(f"Staged {cnt} rows into {tbl}.")

        # 3. Deterministic Reconciliation & Repair of Guest_info
        logger.info("Reconciling and repairing Guest_info Booking_id corruption...")
        reconcile_sql = """
        INSERT INTO audit.etl_data_quality_reconciliation_log 
            (pipeline_run_id, table_name, source_row_id, original_value, repaired_value, reconciliation_rule)
        SELECT 
            %s,
            'staging.stg_guest_info',
            g.source_row_id,
            g.Booking_id AS original_value,
            b.Booking_id AS repaired_value,
            CASE 
                WHEN g.Booking_id LIKE '%%E+%%' THEN 'Excel scientific notation corruption'
                ELSE 'Excel stripped leading zeros'
            END AS reconciliation_rule
        FROM staging.stg_guest_info g
        JOIN staging.stg_booking_details b ON g.source_row_id = b.source_row_id
        WHERE g.Booking_id <> b.Booking_id;
        """
        cur.execute(reconcile_sql, (run_id,))
        cur.execute("SELECT COUNT(*) FROM audit.etl_data_quality_reconciliation_log WHERE pipeline_run_id = %s;", (run_id,))
        repaired_count = cur.fetchone()[0]
        logger.info(f"Audited {repaired_count} corrupted Booking_id values in Guest_info.")

        # Apply repair
        update_guest_sql = """
        UPDATE staging.stg_guest_info g
        SET Booking_id = b.Booking_id
        FROM staging.stg_booking_details b
        WHERE g.source_row_id = b.source_row_id AND g.Booking_id <> b.Booking_id;
        """
        cur.execute(update_guest_sql)
        logger.info("Applied deterministic Booking_id repairs to staging.stg_guest_info.")

        # 4. Truncate and Load Core Normalized Relational Tables
        logger.info("Transforming and populating core relational schema...")
        cur.execute("TRUNCATE TABLE core.fct_bookings CASCADE;")

        # 4.1 Load core.fct_bookings
        load_bookings_sql = """
        INSERT INTO core.fct_bookings (
            booking_id,
            hotel,
            is_canceled,
            lead_time,
            arrival_date,
            arrival_year,
            arrival_month,
            arrival_week_number,
            arrival_day_of_month,
            stays_in_weekend_nights,
            stays_in_week_nights,
            country_code,
            market_segment_id,
            distribution_channel_id,
            is_repeated_guest,
            previous_cancellations,
            previous_bookings_not_canceled,
            deposit_type,
            agent_id,
            company_id,
            days_in_waiting_list,
            customer_type
        )
        SELECT 
            b.Booking_id,
            b.hotel,
            b.is_canceled::SMALLINT,
            b.lead_time::INTEGER,
            TO_DATE(b.arrival_date_year || '-' || 
                CASE b.arrival_date_month
                    WHEN 'January' THEN '01'
                    WHEN 'February' THEN '02'
                    WHEN 'March' THEN '03'
                    WHEN 'April' THEN '04'
                    WHEN 'May' THEN '05'
                    WHEN 'June' THEN '06'
                    WHEN 'July' THEN '07'
                    WHEN 'August' THEN '08'
                    WHEN 'September' THEN '09'
                    WHEN 'October' THEN '10'
                    WHEN 'November' THEN '11'
                    WHEN 'December' THEN '12'
                END || '-' || LPAD(b.arrival_date_day_of_month, 2, '0'), 'YYYY-MM-DD'),
            b.arrival_date_year::SMALLINT,
            b.arrival_date_month,
            b.arrival_date_week_number::SMALLINT,
            b.arrival_date_day_of_month::SMALLINT,
            b.stays_in_weekend_nights::SMALLINT,
            b.stays_in_week_nights::SMALLINT,
            COALESCE(NULLIF(TRIM(b.country), ''), 'NULL'),
            s.market_segment_id::SMALLINT,
            s.distribution_channel_id::SMALLINT,
            s.is_repeated_guest::SMALLINT,
            s.previous_cancellations::INTEGER,
            s.previous_bookings_not_canceled::INTEGER,
            s.deposit_type,
            NULLIF(s.agent, '')::NUMERIC::INTEGER,
            NULLIF(s.company, '')::NUMERIC::INTEGER,
            s.days_in_waiting_list::INTEGER,
            s.customer_type
        FROM staging.stg_booking_details b
        JOIN staging.stg_booking_source_and_history s ON b.Booking_id = s.Booking_id;
        """
        cur.execute(load_bookings_sql)
        cur.execute("SELECT COUNT(*) FROM core.fct_bookings;")
        loaded_bookings = cur.fetchone()[0]
        logger.info(f"Loaded {loaded_bookings} rows into core.fct_bookings.")

        # 4.2 Load core.fct_guest_info
        load_guest_sql = """
        INSERT INTO core.fct_guest_info (booking_id, adults, children, babies)
        SELECT 
            Booking_id,
            adults::SMALLINT,
            COALESCE(NULLIF(children, '')::NUMERIC, 0)::SMALLINT,
            babies::SMALLINT
        FROM staging.stg_guest_info;
        """
        cur.execute(load_guest_sql)
        logger.info("Loaded core.fct_guest_info.")

        # 4.3 Load core.fct_meal_and_stay
        load_meal_sql = """
        INSERT INTO core.fct_meal_and_stay (booking_id, meal_code, adr, required_car_parking_spaces, total_of_special_requests)
        SELECT 
            Booking_id,
            meal,
            adr::NUMERIC(10,2),
            required_car_parking_spaces::SMALLINT,
            total_of_special_requests::SMALLINT
        FROM staging.stg_meal_and_stay_details;
        """
        cur.execute(load_meal_sql)
        logger.info("Loaded core.fct_meal_and_stay.")

        # 4.4 Load core.fct_room_operations
        load_room_sql = """
        INSERT INTO core.fct_room_operations (booking_id, reserved_room_type, assigned_room_type, booking_changes)
        SELECT 
            Booking_id,
            reserved_room_type,
            assigned_room_type,
            booking_changes::SMALLINT
        FROM staging.stg_room_details;
        """
        cur.execute(load_room_sql)
        logger.info("Loaded core.fct_room_operations.")

        # 4.5 Load core.fct_reservation_status
        load_status_sql = """
        INSERT INTO core.fct_reservation_status (booking_id, reservation_status, reservation_status_date)
        SELECT 
            Booking_id,
            reservation_status,
            reservation_status_date::DATE
        FROM staging.stg_reservation_status;
        """
        cur.execute(load_status_sql)
        logger.info("Loaded core.fct_reservation_status.")

        # 5. Verification & Integrity Checks
        cur.execute("SELECT COUNT(*) FROM analytics.v_hotel_bookings_analytics;")
        view_count = cur.fetchone()[0]
        logger.info(f"Analytical View v_hotel_bookings_analytics record count: {view_count}")

        if view_count != 119390:
            raise ValueError(f"Reconciliation error: expected 119,390 rows in analytical view, got {view_count}")

        # Log to audit table
        cur.execute("""
            INSERT INTO audit.etl_ingestion_audit 
            (pipeline_run_id, table_name, source_file, rows_read, rows_staged, rows_loaded, status, error_message, completed_at)
            VALUES (%s, 'core.fct_bookings', 'ALL_CSV_FILES', 119390, 119390, %s, 'SUCCESS', NULL, CURRENT_TIMESTAMP);
        """, (run_id, view_count))

        conn.commit()
        duration = round(time.time() - start_time, 2)
        logger.info(f"ETL pipeline completed successfully in {duration} seconds! All 119,390 rows verified.")

    except Exception as e:
        conn.rollback()
        logger.error(f"ETL pipeline failed: {e}")
        try:
            cur.execute("""
                INSERT INTO audit.etl_ingestion_audit 
                (pipeline_run_id, table_name, source_file, rows_read, rows_staged, rows_loaded, status, error_message, completed_at)
                VALUES (%s, 'core.fct_bookings', 'ALL_CSV_FILES', 0, 0, 0, 'FAILED', %s, CURRENT_TIMESTAMP);
            """, (run_id, str(e)))
            conn.commit()
        except:
            pass
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_etl()
