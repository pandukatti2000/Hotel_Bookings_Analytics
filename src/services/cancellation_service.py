from typing import Optional, Dict, Any, List
from src.services.base import build_filter_clause, execute_query

def get_cancellations_by_lead_time_band(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        lead_time_band,
        COUNT(*) AS total_bookings,
        COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
        ROUND(AVG(adr), 2) AS avg_adr
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY lead_time_band
    ORDER BY 
        CASE lead_time_band
            WHEN '0-7 Days (Immediate)' THEN 1
            WHEN '8-30 Days (Short-Lead)' THEN 2
            WHEN '31-90 Days (Medium-Lead)' THEN 3
            WHEN '91-180 Days (Long-Lead)' THEN 4
            ELSE 5
        END;
    """
    return execute_query(sql, params)

def get_cancellations_by_deposit_type(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        deposit_type,
        COUNT(*) AS total_bookings,
        COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
        ROUND(AVG(lead_time), 2) AS avg_lead_time_days
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY deposit_type
    ORDER BY total_bookings DESC;
    """
    return execute_query(sql, params)

def get_cancellations_by_market_segment(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        market_segment_name,
        COUNT(*) AS total_bookings,
        COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
        ROUND(AVG(adr), 2) AS avg_adr
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY market_segment_name
    ORDER BY total_bookings DESC;
    """
    return execute_query(sql, params)

def get_cancellations_by_customer_type(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        customer_type,
        COUNT(*) AS total_bookings,
        COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY customer_type
    ORDER BY total_bookings DESC;
    """
    return execute_query(sql, params)

def get_cancellations_by_repeat_guest(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        CASE WHEN is_repeated_guest = 1 THEN 'Repeat Guest' ELSE 'First-Time Guest' END AS guest_type,
        COUNT(*) AS total_bookings,
        COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY is_repeated_guest
    ORDER BY is_repeated_guest DESC;
    """
    return execute_query(sql, params)
