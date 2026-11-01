from typing import Optional, Dict, Any, List
from src.services.base import build_filter_clause, execute_query

def get_executive_kpis(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    market_segment: Optional[str] = None,
    distribution_channel: Optional[str] = None,
    customer_type: Optional[str] = None
) -> Dict[str, Any]:
    where_clause, params = build_filter_clause(
        hotel, start_date, end_date, market_segment, distribution_channel, customer_type
    )

    sql = f"""
    SELECT 
        COUNT(*) AS total_bookings,
        COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings,
        COUNT(*) FILTER (WHERE is_canceled = 0) AS non_canceled_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
        ROUND(AVG(lead_time), 2) AS avg_lead_time_days,
        ROUND(AVG(adr), 2) AS avg_adr,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY adr) AS median_adr,
        SUM(total_stay_nights) AS total_booked_nights,
        ROUND(SUM(estimated_booking_value), 2) AS estimated_gross_booking_value,
        ROUND(SUM(estimated_realized_booking_value), 2) AS estimated_realized_booking_value,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_repeated_guest = 1) / NULLIF(COUNT(*), 0), 2) AS repeat_guest_pct,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_room_reassigned = 1) / NULLIF(COUNT(*), 0), 2) AS room_reassignment_pct,
        ROUND(AVG(total_of_special_requests), 2) AS avg_special_requests
    FROM analytics.v_hotel_bookings_analytics
    {where_clause};
    """
    rows = execute_query(sql, params)
    return rows[0] if rows else {}

def get_monthly_booking_trends(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    market_segment: Optional[str] = None,
    distribution_channel: Optional[str] = None,
    customer_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(
        hotel, start_date, end_date, market_segment, distribution_channel, customer_type
    )

    sql = f"""
    SELECT 
        TO_CHAR(arrival_date, 'YYYY-MM') AS year_month,
        arrival_year,
        arrival_month,
        COUNT(*) AS total_bookings,
        COUNT(*) FILTER (WHERE is_canceled = 0) AS confirmed_bookings,
        COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
        ROUND(AVG(adr), 2) AS avg_adr,
        ROUND(SUM(estimated_realized_booking_value), 2) AS realized_booking_value
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY TO_CHAR(arrival_date, 'YYYY-MM'), arrival_year, arrival_month
    ORDER BY year_month ASC;
    """
    return execute_query(sql, params)

def get_hotel_comparison(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(start_date=start_date, end_date=end_date)

    sql = f"""
    SELECT 
        hotel,
        COUNT(*) AS total_bookings,
        COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
        ROUND(AVG(lead_time), 2) AS avg_lead_time_days,
        ROUND(AVG(adr), 2) AS avg_adr,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY adr) AS median_adr,
        ROUND(AVG(total_stay_nights), 2) AS avg_stay_nights,
        ROUND(SUM(estimated_realized_booking_value), 2) AS realized_booking_value,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_repeated_guest = 1) / NULLIF(COUNT(*), 0), 2) AS repeat_guest_pct,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_room_reassigned = 1) / NULLIF(COUNT(*), 0), 2) AS room_reassignment_pct
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY hotel
    ORDER BY total_bookings DESC;
    """
    return execute_query(sql, params)
