import pytest
from sqlalchemy import text
from src.db.session import engine

def test_database_table_row_counts():
    """Verify that all core tables and analytical view contain exactly 119,390 records."""
    tables = [
        "core.fct_bookings",
        "core.fct_guest_info",
        "core.fct_meal_and_stay",
        "core.fct_room_operations",
        "core.fct_reservation_status",
        "analytics.v_hotel_bookings_analytics"
    ]
    with engine.connect() as conn:
        for tbl in tables:
            cnt = conn.execute(text(f"SELECT COUNT(*) FROM {tbl};")).scalar()
            assert cnt == 119390, f"Expected 119,390 rows in {tbl}, got {cnt}"

def test_lookup_dimensions():
    """Verify dimension table row counts and trimming."""
    with engine.connect() as conn:
        country_cnt = conn.execute(text("SELECT COUNT(*) FROM core.dim_country;")).scalar()
        assert country_cnt == 178
        
        mkt_cnt = conn.execute(text("SELECT COUNT(*) FROM core.dim_market_segment;")).scalar()
        assert mkt_cnt == 8
        
        dist_cnt = conn.execute(text("SELECT COUNT(*) FROM core.dim_distribution_channel;")).scalar()
        assert dist_cnt == 5

def test_reconciliation_audit_log():
    """Verify that exactly 895 corrupted Guest_info IDs were repaired and logged."""
    with engine.connect() as conn:
        reconciled_cnt = conn.execute(text("""
            SELECT COUNT(*) FROM audit.etl_data_quality_reconciliation_log;
        """)).scalar()
        assert reconciled_cnt == 895
