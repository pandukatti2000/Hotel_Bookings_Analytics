import pytest
from src.ai.sql_guard import sanitize_and_validate_sql

def test_valid_select_queries():
    """Verify that legitimate SELECT queries pass and receive LIMIT 500."""
    queries = [
        "SELECT hotel, COUNT(*) FROM analytics.v_hotel_bookings_analytics GROUP BY hotel",
        "SELECT * FROM v_hotel_bookings_analytics WHERE is_canceled = 1",
        "SELECT arrival_month, AVG(adr) FROM analytics.v_hotel_bookings_analytics GROUP BY arrival_month ORDER BY 2 DESC"
    ]
    for q in queries:
        valid, sanitized, err = sanitize_and_validate_sql(q)
        assert valid is True, f"Failed for query '{q}': {err}"
        assert "LIMIT 500" in sanitized or "limit 500" in sanitized.lower()

def test_forbidden_keywords_rejected():
    """Verify that queries with destructive keywords are rejected."""
    bad_queries = [
        "DROP TABLE core.fct_bookings;",
        "DELETE FROM analytics.v_hotel_bookings_analytics;",
        "UPDATE core.fct_bookings SET is_canceled = 0;",
        "INSERT INTO core.dim_country VALUES ('ZZZ', 'Fake');",
        "TRUNCATE core.fct_bookings;",
        "ALTER TABLE core.fct_bookings DROP COLUMN hotel;"
    ]
    for q in bad_queries:
        valid, sanitized, err = sanitize_and_validate_sql(q)
        assert valid is False
        assert "Security Violation" in err

def test_multi_statement_rejected():
    """Verify that multi-statement SQL injection attempts are blocked."""
    multi = "SELECT 1; DROP TABLE core.fct_bookings;"
    valid, _, err = sanitize_and_validate_sql(multi)
    assert valid is False

def test_unauthorized_tables_rejected():
    """Verify that unauthorized system catalogs and staging tables cannot be queried."""
    unauth = [
        "SELECT * FROM pg_catalog.pg_user",
        "SELECT * FROM information_schema.tables",
        "SELECT * FROM staging.stg_booking_details"
    ]
    for q in unauth:
        valid, _, err = sanitize_and_validate_sql(q)
        assert valid is False
        assert "Security Violation" in err
