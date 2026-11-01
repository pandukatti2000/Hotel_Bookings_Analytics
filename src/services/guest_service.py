from typing import Optional, Dict, Any, List
from src.services.base import build_filter_clause, execute_query

def get_guest_composition_stats(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        guest_composition_type,
        COUNT(*) AS total_bookings,
        ROUND(100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (), 0), 2) AS composition_share_pct,
        COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
        ROUND(AVG(adr), 2) AS avg_adr
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY guest_composition_type
    ORDER BY total_bookings DESC;
    """
    return execute_query(sql, params)

def get_top_countries(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 15
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        country_code,
        country_name,
        COUNT(*) AS total_bookings,
        ROUND(100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (), 0), 2) AS country_share_pct,
        COUNT(*) FILTER (WHERE is_canceled = 1) AS canceled_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
        ROUND(AVG(adr), 2) AS avg_adr
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY country_code, country_name
    ORDER BY total_bookings DESC
    LIMIT {limit};
    """
    return execute_query(sql, params)

def get_meal_preferences(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        meal_code,
        meal_description,
        COUNT(*) AS total_bookings,
        ROUND(100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (), 0), 2) AS meal_share_pct,
        ROUND(AVG(adr), 2) AS avg_adr
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY meal_code, meal_description
    ORDER BY total_bookings DESC;
    """
    return execute_query(sql, params)

def get_special_requests_and_parking(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql_requests = f"""
    SELECT 
        total_of_special_requests,
        COUNT(*) AS total_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY total_of_special_requests
    ORDER BY total_of_special_requests ASC;
    """
    sql_parking = f"""
    SELECT 
        required_car_parking_spaces,
        COUNT(*) AS total_bookings,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY required_car_parking_spaces
    ORDER BY required_car_parking_spaces ASC;
    """
    return {
        "special_requests": execute_query(sql_requests, params),
        "car_parking": execute_query(sql_parking, params)
    }
