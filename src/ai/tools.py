import time
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy import text
from src.db.session import readonly_engine
from config.logging_config import logger

def execute_readonly_sql(sql_query: str) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Executes a validated SQL query against the read-only database connection with a statement timeout.
    Returns (data_list, error_message).
    """
    try:
        with readonly_engine.connect() as conn:
            # Set statement timeout to 5000ms
            conn.execute(text("SET statement_timeout = 5000;"))
            result = conn.execute(text(sql_query))
            rows = [dict(row._mapping) for row in result.fetchall()]
            
            # Convert non-serializable types (Decimal, date, datetime) to standard Python types
            clean_rows = []
            for r in rows:
                clean_r = {}
                for k, v in r.items():
                    if hasattr(v, "isoformat"):
                        clean_r[k] = v.isoformat()
                    elif hasattr(v, "__float__"):
                        clean_r[k] = float(v)
                    else:
                        clean_r[k] = v
                clean_rows.append(clean_r)
            return clean_rows, None
    except Exception as e:
        logger.error(f"Read-only SQL execution error: {e}")
        return None, str(e)
