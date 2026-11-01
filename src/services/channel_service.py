from typing import Optional, Dict, Any, List
from src.services.base import build_filter_clause, execute_query

def get_channel_performance(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        distribution_channel_name,
        COUNT(*) AS total_bookings,
        ROUND(100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (), 0), 2) AS booking_share_pct,
        COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
        ROUND(AVG(lead_time), 2) AS avg_lead_time_days,
        ROUND(AVG(adr), 2) AS avg_adr,
        ROUND(SUM(estimated_realized_booking_value), 2) AS realized_booking_value
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY distribution_channel_name
    ORDER BY total_bookings DESC;
    """
    return execute_query(sql, params)

def get_top_agents(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    and_agent = "AND agent_id IS NOT NULL" if where_clause else "WHERE agent_id IS NOT NULL"
    sql = f"""
    SELECT 
        agent_id,
        COUNT(*) AS total_bookings,
        COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
        ROUND(SUM(estimated_realized_booking_value), 2) AS realized_booking_value
    FROM analytics.v_hotel_bookings_analytics
    {where_clause} {and_agent}
    GROUP BY agent_id
    ORDER BY total_bookings DESC
    LIMIT {limit};
    """
    return execute_query(sql, params)
