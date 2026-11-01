from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from src.services.room_service import (
    get_room_reassignment_summary,
    get_room_allocation_matrix,
    get_booking_changes_distribution
)

router = APIRouter(prefix="/analytics/rooms", tags=["Room Operations"])

@router.get("/reassignment-summary")
def read_reassignment_summary(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> Dict[str, Any]:
    return get_room_reassignment_summary(hotel=hotel, start_date=start_date, end_date=end_date)

@router.get("/allocation-matrix")
def read_allocation_matrix(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_room_allocation_matrix(hotel=hotel, start_date=start_date, end_date=end_date)

@router.get("/changes-distribution")
def read_changes_distribution(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_booking_changes_distribution(hotel=hotel, start_date=start_date, end_date=end_date)
