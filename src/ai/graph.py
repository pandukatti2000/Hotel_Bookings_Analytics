import time
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from config.settings import settings
from config.logging_config import logger
from src.ai.state import AgentState
from src.ai.prompts import SYSTEM_SQL_PROMPT, SYSTEM_SYNTHESIS_PROMPT
from src.ai.sql_guard import sanitize_and_validate_sql
from src.ai.tools import execute_readonly_sql
from src.ai.tracer import configure_langsmith

configure_langsmith()

def get_llm():
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0.0
    )

def classify_intent_node(state: AgentState) -> Dict[str, Any]:
    question = state.get("question", "").strip()
    
    # Fast heuristic check for simple greetings
    greetings = ["hi", "hello", "hey", "who are you", "what can you do", "help"]
    if question.lower() in greetings or len(question.split()) < 2:
        return {
            "intent": "GENERAL_CONVERSATION",
            "answer": "Hello! I am StayWise AI, your hotel analytics intelligence assistant. You can ask me questions about booking volumes, cancellation risks, lead times, ADR trends, market segments, distribution channels, and room reassignments.",
            "chart_type": "none",
            "data": [],
            "sql_query": None
        }
    return {"intent": "DATA_QUERY"}

def generate_sql_node(state: AgentState) -> Dict[str, Any]:
    if state.get("intent") == "GENERAL_CONVERSATION":
        return {}

    question = state["question"]
    hotel_filter = state.get("hotel_filter", "All")
    
    prompt = f"User Question: {question}\n"
    if hotel_filter and hotel_filter != "All":
        prompt += f"Active Property Filter: hotel = '{hotel_filter}'. Enforce this filter in the WHERE clause.\n"
    prompt += "Generate PostgreSQL SQL targeting analytics.v_hotel_bookings_analytics:"

    llm = get_llm()
    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_SQL_PROMPT),
            HumanMessage(content=prompt)
        ])
        raw_sql = response.content.strip()
        return {"sql_query": raw_sql}
    except Exception as e:
        logger.error(f"SQL generation error: {e}")
        return {
            "sql_query": None,
            "error": f"Failed to generate query: {e}",
            "answer": "I encountered an error generating the SQL query. Please verify your OpenAI API key and network connection."
        }

def validate_sql_node(state: AgentState) -> Dict[str, Any]:
    if state.get("intent") == "GENERAL_CONVERSATION" or not state.get("sql_query"):
        return {}

    raw_sql = state["sql_query"]
    is_valid, sanitized_sql, error = sanitize_and_validate_sql(raw_sql)
    
    if not is_valid:
        logger.warning(f"SQL validation rejected query: {error}")
        return {
            "sql_valid": False,
            "sql_error": error,
            "error": error,
            "answer": f"The query could not be executed due to security validation: {error}"
        }
    return {
        "sql_valid": True,
        "sql_query": sanitized_sql,
        "sql_error": None
    }

def execute_sql_node(state: AgentState) -> Dict[str, Any]:
    if not state.get("sql_valid"):
        return {}

    sql = state["sql_query"]
    data, error = execute_readonly_sql(sql)
    
    if error:
        return {
            "error": error,
            "data": None,
            "answer": f"Database execution error: {error}"
        }
    return {"data": data, "error": None}

def synthesize_response_node(state: AgentState) -> Dict[str, Any]:
    if state.get("intent") == "GENERAL_CONVERSATION" or state.get("error"):
        return {}

    data = state.get("data")
    if data is None or len(data) == 0:
        return {
            "answer": "The query executed successfully, but returned 0 matching records for the specified criteria.",
            "chart_type": "none"
        }

    question = state["question"]
    sql = state["sql_query"]
    
    sample_data = data[:50]  # Limit tokens for prompt
    data_json = json.dumps(sample_data, default=str)

    prompt = f"""User Question: {question}
Executed SQL: {sql}
Returned Data Records (total {len(data)} rows):
{data_json}

Provide your grounded business answer and recommend a chart type."""

    llm = get_llm()
    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_SYNTHESIS_PROMPT),
            HumanMessage(content=prompt)
        ])
        content = response.content.strip()

        # Heuristic extraction of chart_type if recommended
        chart_type = "bar"
        if "line" in content.lower() and ("trend" in question.lower() or "month" in question.lower() or "over time" in question.lower()):
            chart_type = "line"
        elif "pie" in content.lower() or "share" in question.lower() or "distribution" in question.lower():
            chart_type = "pie"
        elif len(data) == 1 and len(data[0]) <= 2:
            chart_type = "none"

        return {
            "answer": content,
            "chart_type": chart_type
        }
    except Exception as e:
        logger.error(f"Response synthesis error: {e}")
        return {
            "answer": f"Query returned {len(data)} records successfully. See tabular data below.",
            "chart_type": "bar"
        }

def route_intent(state: AgentState) -> str:
    if state.get("intent") == "GENERAL_CONVERSATION":
        return END
    return "generate_sql"

def route_validation(state: AgentState) -> str:
    if not state.get("sql_valid"):
        return END
    return "execute_sql"

def route_execution(state: AgentState) -> str:
    if state.get("error"):
        return END
    return "synthesize_response"

# Construct LangGraph
builder = StateGraph(AgentState)
builder.add_node("classify_intent", classify_intent_node)
builder.add_node("generate_sql", generate_sql_node)
builder.add_node("validate_sql", validate_sql_node)
builder.add_node("execute_sql", execute_sql_node)
builder.add_node("synthesize_response", synthesize_response_node)

builder.set_entry_point("classify_intent")
builder.add_conditional_edges("classify_intent", route_intent)
builder.add_edge("generate_sql", "validate_sql")
builder.add_conditional_edges("validate_sql", route_validation)
builder.add_conditional_edges("execute_sql", route_execution)
builder.add_edge("synthesize_response", END)

agent_graph = builder.compile()

def run_agent(question: str, thread_id: str = "default", hotel_filter: str = "All") -> Dict[str, Any]:
    start = time.time()
    initial_state: AgentState = {
        "question": question,
        "thread_id": thread_id,
        "hotel_filter": hotel_filter,
        "intent": None,
        "sql_query": None,
        "sql_valid": False,
        "sql_error": None,
        "data": None,
        "chart_type": "none",
        "answer": None,
        "error": None,
        "execution_time_seconds": 0.0
    }
    final_state = agent_graph.invoke(initial_state)
    final_state["execution_time_seconds"] = round(time.time() - start, 2)
    return final_state
