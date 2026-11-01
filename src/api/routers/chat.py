import uuid
from fastapi import APIRouter, HTTPException
from src.api.schemas import AnalyzeRequest, AnalyzeResponse
from src.ai.graph import run_agent

router = APIRouter(prefix="/analyze", tags=["AI Analytics Assistant"])

@router.post("", response_model=AnalyzeResponse)
def analyze_question(payload: AnalyzeRequest):
    thread_id = payload.thread_id or str(uuid.uuid4())[:8]
    try:
        result = run_agent(
            question=payload.question,
            thread_id=thread_id,
            hotel_filter=payload.hotel_filter or "All"
        )
        return AnalyzeResponse(
            answer=result.get("answer") or "No response could be generated.",
            sql_query=result.get("sql_query"),
            data=result.get("data"),
            chart_type=result.get("chart_type", "none"),
            thread_id=thread_id,
            execution_time_seconds=result.get("execution_time_seconds", 0.0),
            tokens_used=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
