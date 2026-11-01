from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict):
    question: str
    thread_id: str
    hotel_filter: Optional[str]
    intent: Optional[str]            # 'DATA_QUERY' | 'GENERAL_CONVERSATION'
    sql_query: Optional[str]
    sql_valid: bool
    sql_error: Optional[str]
    data: Optional[List[Dict[str, Any]]]
    chart_type: Optional[str]        # 'bar', 'line', 'pie', 'heatmap', 'none'
    answer: Optional[str]
    error: Optional[str]
    execution_time_seconds: float
