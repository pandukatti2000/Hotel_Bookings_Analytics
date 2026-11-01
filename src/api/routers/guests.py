from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from src.services.guest_service import (
    get_guest_composition_stats,
    get_top_countries,
    get_meal_preferences,
    get_special_requests_and_parking
)

router = APIRouter(prefix="/analytics/guests", tags=["Guest Intelligence"])

@router.get("/composition")
def read_guest_composition(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_guest_composition_stats(hotel=hotel, start_date=start_date, end_date=end_date)

@router.get("/countries")
def read_top_countries(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(15, ge=1, le=50)
) -> List[Dict[str, Any]]:
    return get_top_countries(hotel=hotel, start_date=start_date, end_date=end_date, limit=limit)

@router.get("/meals")
def read_meal_preferences(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_meal_preferences(hotel=hotel, start_date=start_date, end_date=end_date)

@router.get("/requests-and-parking")
def read_requests_and_parking(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> Dict[str, Any]:
    return get_special_requests_and_parking(hotel=hotel, start_date=start_date, end_date=end_date)
