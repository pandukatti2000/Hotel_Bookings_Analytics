from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import text
from src.db.session import engine

def build_filter_clause(
    hotel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    market_segment: Optional[str] = None,
    distribution_channel: Optional[str] = None,
    customer_type: Optional[str] = None
) -> Tuple[str, Dict[str, Any]]:
    conditions: List[str] = []
    params: Dict[str, Any] = {}

    if hotel and hotel != "All":
        conditions.append("hotel = :hotel")
        params["hotel"] = hotel

    if start_date:
        conditions.append("arrival_date >= :start_date")
        params["start_date"] = start_date

    if end_date:
        conditions.append("arrival_date <= :end_date")
        params["end_date"] = end_date

    if market_segment and market_segment != "All":
        conditions.append("market_segment_name = :market_segment")
        params["market_segment"] = market_segment

    if distribution_channel and distribution_channel != "All":
        conditions.append("distribution_channel_name = :distribution_channel")
        params["distribution_channel"] = distribution_channel

    if customer_type and customer_type != "All":
        conditions.append("customer_type = :customer_type")
        params["customer_type"] = customer_type

    clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return clause, params

def execute_query(sql_str: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    with engine.connect() as conn:
        stmt = text(sql_str)
        result = conn.execute(stmt, params or {})
        return [dict(row._mapping) for row in result.fetchall()]
