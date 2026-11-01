import streamlit as st
import pandas as pd
from sqlalchemy import text
from src.db.session import engine

st.set_page_config(page_title="Data Quality & Methodology | StayWise AI", page_icon="🛡️", layout="wide")

st.title("🛡️ Data Quality, Lineage & Methodology")
st.markdown("Detailed audit trail of source ingestion, reconciliation logs, deterministic repairs, and KPI definitions.")

# 1. Reconciliation Audit Log
st.subheader("📋 Excel Corruption Reconciliation Audit Log")
st.markdown("""
In the source `Guest_info.csv` file, 895 booking IDs were mangled by Microsoft Excel (598 converted into scientific notation floats like `1.25E+11`, creating 6 duplicate key collisions; and 297 with stripped leading zeros). 

During Phase 2 ETL, our ingestion pipeline matched sequential `source_row_id` alignment against `Booking_details.csv` to restore the true 8-character hexadecimal keys with **100% mathematical fidelity and 0 row multiplication**.
""")

with engine.connect() as conn:
    reconciled_sample = conn.execute(text("""
        SELECT source_row_id, original_value, repaired_value, reconciliation_rule, created_at
        FROM audit.etl_data_quality_reconciliation_log
        ORDER BY source_row_id ASC
        LIMIT 25;
    """)).fetchall()
    
    audit_runs = conn.execute(text("""
        SELECT pipeline_run_id, table_name, rows_read, rows_staged, rows_loaded, status, completed_at
        FROM audit.etl_ingestion_audit
        ORDER BY completed_at DESC
        LIMIT 5;
    """)).fetchall()

if reconciled_sample:
    df_sample = pd.DataFrame([dict(r._mapping) for r in reconciled_sample])
    st.dataframe(
        df_sample.rename(columns={
            "source_row_id": "Row Index",
            "original_value": "Mangled Excel ID",
            "repaired_value": "Restored Canonical ID",
            "reconciliation_rule": "Diagnostic Rule",
            "created_at": "Timestamp"
        }),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# 2. Ingestion Pipeline Run Audit
st.subheader("🚀 ETL Ingestion Runs & Row Reconciliation")
if audit_runs:
    df_runs = pd.DataFrame([dict(r._mapping) for r in audit_runs])
    st.dataframe(df_runs, use_container_width=True, hide_index=True)

st.markdown("---")

# 3. KPI Methodology & Analytical Limitations
st.subheader("📐 KPI Methodology & Analytical Guardrails")
st.markdown("""
| Metric Name | Exact SQL Formula | Key Business Limitation / Caveat |
|---|---|---|
| **Total Bookings** | `COUNT(*)` | Denominator for all reservation rates across dataset (119,390). |
| **Cancellation Rate %** | `100.0 * COUNT(*) FILTER (WHERE is_canceled = 1) / COUNT(*)` | Includes both canceled reservations (43,017) and no-shows (1,207). |
| **Average ADR ($)** | `AVG(GREATEST(adr, 0.00))` | Excludes 1 negative rebate row (`-6.38`). 1,959 complimentary bookings have ADR = $0.00. |
| **Median ADR ($)** | `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY adr)` | Outlier-resilient benchmark ($94.58) preventing skew from the single $5,400.00 anomaly. |
| **Estimated Gross Value** | `SUM(total_stay_nights * adr)` | **Estimated booking value only**. The dataset does not record cash receipts, refunds, or penalties. |
| **Estimated Realized Value**| `SUM(total_stay_nights * adr) FILTER (WHERE is_canceled = 0)` | Room value of confirmed fulfilled stays. Does not subtract operational operating costs. |
| **Room Reassignment Rate** | `100.0 * COUNT(*) FILTER (WHERE reserved != assigned) / COUNT(*)` | 12.49% of stays were reassigned. 73.9% occurred without guest changes (front-desk upgrades/moves). |
""")
