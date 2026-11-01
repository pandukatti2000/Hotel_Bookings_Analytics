from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from src.services.overview_service import (
    get_executive_kpis,
    get_monthly_booking_trends,
    get_hotel_comparison
)

router = APIRouter(prefix="/analytics", tags=["Overview & Trends"])

@router.get("/overview")
def read_overview(
    hotel: Optional[str] = Query(None, description="City Hotel or Resort Hotel"),
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    market_segment: Optional[str] = Query(None),
    distribution_channel: Optional[str] = Query(None),
    customer_type: Optional[str] = Query(None)
) -> Dict[str, Any]:
    return get_executive_kpis(
        hotel=hotel,
        start_date=start_date,
        end_date=end_date,
        market_segment=market_segment,
        distribution_channel=distribution_channel,
        customer_type=customer_type
    )

@router.get("/trends")
def read_trends(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    market_segment: Optional[str] = Query(None),
    distribution_channel: Optional[str] = Query(None),
    customer_type: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_monthly_booking_trends(
        hotel=hotel,
        start_date=start_date,
        end_date=end_date,
        market_segment=market_segment,
        distribution_channel=distribution_channel,
        customer_type=customer_type
    )

@router.get("/hotels")
def read_hotel_comparison(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_hotel_comparison(start_date=start_date, end_date=end_date)
