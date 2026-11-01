from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from src.services.cancellation_service import (
    get_cancellations_by_lead_time_band,
    get_cancellations_by_deposit_type,
    get_cancellations_by_market_segment,
    get_cancellations_by_customer_type,
    get_cancellations_by_repeat_guest
)

router = APIRouter(prefix="/analytics/cancellations", tags=["Cancellation Intelligence"])

@router.get("/lead-time")
def read_cancellations_lead_time(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_cancellations_by_lead_time_band(hotel=hotel, start_date=start_date, end_date=end_date)

@router.get("/deposit-type")
def read_cancellations_deposit(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_cancellations_by_deposit_type(hotel=hotel, start_date=start_date, end_date=end_date)

@router.get("/market-segment")
def read_cancellations_market_segment(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_cancellations_by_market_segment(hotel=hotel, start_date=start_date, end_date=end_date)

@router.get("/customer-type")
def read_cancellations_customer_type(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_cancellations_by_customer_type(hotel=hotel, start_date=start_date, end_date=end_date)

@router.get("/repeat-guest")
def read_cancellations_repeat_guest(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_cancellations_by_repeat_guest(hotel=hotel, start_date=start_date, end_date=end_date)
