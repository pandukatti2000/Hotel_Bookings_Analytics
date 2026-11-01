import re
from typing import Tuple, Optional
import sqlglot
from sqlglot import exp

ALLOWED_TABLES = {
    "v_hotel_bookings_analytics",
    "analytics.v_hotel_bookings_analytics",
    "fct_bookings",
    "core.fct_bookings",
    "fct_guest_info",
    "core.fct_guest_info",
    "fct_meal_and_stay",
    "core.fct_meal_and_stay",
    "fct_room_operations",
    "core.fct_room_operations",
    "fct_reservation_status",
    "core.fct_reservation_status",
    "dim_country",
    "core.dim_country",
    "dim_market_segment",
    "core.dim_market_segment",
    "dim_distribution_channel",
    "core.dim_distribution_channel"
}

FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER", "CREATE",
    "GRANT", "REVOKE", "COPY", "EXECUTE", "PG_SLEEP", "INFORMATION_SCHEMA", "PG_CATALOG"
]

def sanitize_and_validate_sql(sql_query: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates a SQL query using SQLGlot AST inspection:
    - Must be a single SELECT statement.
    - No write, DDL, or privilege alteration commands.
    - Restricted to authorized analytical tables/views.
    - Enforces a maximum LIMIT of 500.
    Returns (is_valid, sanitized_sql, error_message).
    """
    clean_sql = sql_query.strip().rstrip(";")
    
    # Strip markdown fences if present
    if clean_sql.startswith("```sql"):
        clean_sql = clean_sql[6:]
    elif clean_sql.startswith("```"):
        clean_sql = clean_sql[3:]
    if clean_sql.endswith("```"):
        clean_sql = clean_sql[:-3]
    clean_sql = clean_sql.strip().rstrip(";")

    # Fast regex check for forbidden keywords
    upper_sql = clean_sql.upper()
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{kw}\b", upper_sql):
            return False, None, f"Security Violation: Query contains forbidden keyword '{kw}'."

    # Parse with SQLGlot targeting Postgres dialect
    try:
        expressions = sqlglot.parse(clean_sql, read="postgres")
    except Exception as e:
        return False, None, f"SQL Syntax Error: Unable to parse query: {e}"

    if len(expressions) != 1:
        return False, None, "Security Violation: Multi-statement queries are strictly prohibited."

    expression = expressions[0]

    # Verify statement is SELECT
    if not isinstance(expression, exp.Select):
        return False, None, f"Security Violation: Only SELECT queries are permitted (got {expression.key.upper()})."

    # Verify tables accessed
    tables = [table.name.lower() for table in expression.find_all(exp.Table)]
    for tbl in tables:
        # Check against allowed tables
        matching = any(tbl == allowed.split(".")[-1].lower() for allowed in ALLOWED_TABLES)
        if not matching:
            return False, None, f"Security Violation: Access to unauthorized table or catalog '{tbl}' is forbidden."

    # Enforce LIMIT 500
    limit_node = expression.args.get("limit")
    if not limit_node:
        expression = expression.limit(500)
    else:
        try:
            curr_limit = int(limit_node.expression.this)
            if curr_limit > 500:
                expression = expression.limit(500)
        except:
            expression = expression.limit(500)

    final_sql = expression.sql(dialect="postgres")
    return True, final_sql, None
