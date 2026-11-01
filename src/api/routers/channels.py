from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from src.services.channel_service import (
    get_channel_performance,
    get_top_agents
)

router = APIRouter(prefix="/analytics/channels", tags=["Distribution Channels"])

@router.get("/performance")
def read_channel_performance(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    return get_channel_performance(hotel=hotel, start_date=start_date, end_date=end_date)

@router.get("/agents")
def read_top_agents(
    hotel: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
) -> List[Dict[str, Any]]:
    return get_top_agents(hotel=hotel, start_date=start_date, end_date=end_date, limit=limit)
