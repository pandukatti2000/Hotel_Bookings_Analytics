from typing import Optional, Dict, Any, List
from src.services.base import build_filter_clause, execute_query

def get_monthly_adr_and_value(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        TO_CHAR(arrival_date, 'YYYY-MM') AS year_month,
        arrival_year,
        arrival_month,
        COUNT(*) AS total_bookings,
        ROUND(AVG(adr), 2) AS mean_adr,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY adr) AS median_adr,
        ROUND(SUM(estimated_booking_value), 2) AS gross_booking_value,
        ROUND(SUM(estimated_realized_booking_value), 2) AS realized_booking_value,
        SUM(total_stay_nights) AS total_room_nights
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY TO_CHAR(arrival_date, 'YYYY-MM'), arrival_year, arrival_month
    ORDER BY year_month ASC;
    """
    return execute_query(sql, params)

def get_revenue_by_market_segment(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        market_segment_name,
        COUNT(*) AS total_bookings,
        COUNT(*) FILTER (WHERE is_canceled = 0) AS confirmed_bookings,
        ROUND(AVG(adr), 2) AS avg_adr,
        ROUND(SUM(estimated_booking_value), 2) AS gross_booking_value,
        ROUND(SUM(estimated_realized_booking_value), 2) AS realized_booking_value,
        ROUND(100.0 * SUM(estimated_realized_booking_value) / NULLIF(SUM(SUM(estimated_realized_booking_value)) OVER (), 0), 2) AS realized_share_pct
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY market_segment_name
    ORDER BY realized_booking_value DESC;
    """
    return execute_query(sql, params)

def get_stay_duration_vs_adr(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(hotel=hotel, start_date=start_date, end_date=end_date)
    sql = f"""
    SELECT 
        CASE 
            WHEN total_stay_nights = 0 THEN '0 Nights (Day Use)'
            WHEN total_stay_nights = 1 THEN '1 Night'
            WHEN total_stay_nights = 2 THEN '2 Nights'
            WHEN total_stay_nights = 3 THEN '3 Nights'
            WHEN total_stay_nights <= 7 THEN '4-7 Nights'
            WHEN total_stay_nights <= 14 THEN '8-14 Nights'
            ELSE '15+ Nights (Extended)'
        END AS stay_length_category,
        COUNT(*) AS total_bookings,
        ROUND(AVG(adr), 2) AS avg_adr,
        ROUND(SUM(estimated_realized_booking_value), 2) AS realized_booking_value
    FROM analytics.v_hotel_bookings_analytics
    {where_clause}
    GROUP BY 
        CASE 
            WHEN total_stay_nights = 0 THEN '0 Nights (Day Use)'
            WHEN total_stay_nights = 1 THEN '1 Night'
            WHEN total_stay_nights = 2 THEN '2 Nights'
            WHEN total_stay_nights = 3 THEN '3 Nights'
            WHEN total_stay_nights <= 7 THEN '4-7 Nights'
            WHEN total_stay_nights <= 14 THEN '8-14 Nights'
            ELSE '15+ Nights (Extended)'
        END
    ORDER BY total_bookings DESC;
    """
    return execute_query(sql, params)
