import pytest
from src.ai.graph import run_agent

def test_conversational_intent():
    """Verify greeting and general conversation handling without SQL execution."""
    res = run_agent("hello")
    assert res["intent"] == "GENERAL_CONVERSATION"
    assert "StayWise AI" in res["answer"]
    assert res["sql_query"] is None

def test_data_query_execution():
    """Verify natural-language analytical query translates to valid SQL and returns data."""
    res = run_agent("What is the total number of bookings and the cancellation rate by hotel?")
    assert res["intent"] == "DATA_QUERY"
    assert res["sql_valid"] is True
    assert res["data"] is not None
    assert len(res["data"]) >= 2
    assert "City Hotel" in str(res["data"])
    assert res["answer"] is not None
