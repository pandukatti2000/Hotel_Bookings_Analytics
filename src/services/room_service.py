from typing import Optional, Dict, Any, List
from src.services.base import build_filter_clause, execute_query

def get_room_reassignment_summary(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        COUNT(*) AS total_bookings,
        COUNT(*) FILTER (WHERE is_room_reassigned = 1) AS reassigned_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_room_reassigned = 1) / NULLIF(COUNT(*), 0), 2) AS reassignment_rate_pct,
        COUNT(*) FILTER (WHERE is_room_reassigned = 1 AND booking_changes = 0) AS operational_reassignments,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_room_reassigned = 1 AND booking_changes = 0) / NULLIF(COUNT(*) FILTER (WHERE is_room_reassigned = 1), 0), 2) AS operational_reassignment_pct,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_room_reassigned = 1 AND is_canceled = 1) / NULLIF(COUNT(*) FILTER (WHERE is_room_reassigned = 1), 0), 2) AS reassigned_cancellation_rate_pct,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_room_reassigned = 0 AND is_canceled = 1) / NULLIF(COUNT(*) FILTER (WHERE is_room_reassigned = 0), 0), 2) AS same_room_cancellation_rate_pct
    FROM analytics.v_hotel_bookings_analytics
    {where_clause};
    """
    rows = execute_query(sql, params)
    return rows[0] if rows else {}

def get_room_allocation_matrix(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        reserved_room_type,
        assigned_room_type,
        COUNT(*) AS booking_count,
        ROUND(AVG(adr), 2) AS avg_adr
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY reserved_room_type, assigned_room_type
    ORDER BY reserved_room_type, assigned_room_type;
    """
    return execute_query(sql, params)

def get_booking_changes_distribution(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        booking_changes,
        COUNT(*) AS total_bookings,
        COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_room_reassigned = 1) / NULLIF(COUNT(*), 0), 2) AS reassignment_rate_pct
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY booking_changes
    ORDER BY booking_changes ASC;
    """
    return execute_query(sql, params)
