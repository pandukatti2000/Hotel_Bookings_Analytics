from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from src.services.revenue_service import (
    get_monthly_adr_and_value,
    get_revenue_by_market_segment,
    get_stay_duration_vs_adr
)

router = APIRouter(prefix="/analytics/revenue", tags=["Revenue & ADR Intelligence"])

@router.get("/monthly")
def read_revenue_monthly(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_monthly_adr_and_value(hotel=hotel, start_date=start_date, end_date=end_date)

@router.get("/market-segment")
def read_revenue_market_segment(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_revenue_by_market_segment(hotel=hotel, start_date=start_date, end_date=end_date)

@router.get("/stay-duration")
def read_stay_duration_vs_adr(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_stay_duration_vs_adr(hotel=hotel, start_date=start_date, end_date=end_date)
