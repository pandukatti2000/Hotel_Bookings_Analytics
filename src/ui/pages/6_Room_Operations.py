import streamlit as st
import pandas as pd
from src.ui.components.filters import render_sidebar_filters
from src.ui.components.charts import create_heatmap, create_bar_chart
from src.services.room_service import (
    get_room_reassignment_summary,
    get_room_allocation_matrix,
    get_booking_changes_distribution
)

st.set_page_config(page_title="Room Operations | StayWise AI", page_icon="🛎️", layout="wide")
filters = render_sidebar_filters()

st.title("🛎️ Room Operations & Reassignment Dynamics")
st.markdown("Monitor reserved versus assigned room allocations, operational upgrades/downgrades, and guest modification patterns.")

# Summary Metrics
summary = get_room_reassignment_summary(
    hotel=filters["hotel"],
    start_date=filters["start_date"],
    end_date=filters["end_date"]
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Bookings", f"{summary.get('total_bookings', 0):,}")
with col2:
    st.metric("Reassigned Bookings", f"{summary.get('reassigned_bookings', 0):,}")
    st.caption(f"{summary.get('reassignment_rate_pct', 0.0)}% Reassignment Rate")
with col3:
    st.metric("Operational Upgrades/Changes", f"{summary.get('operational_reassignments', 0):,}")
    st.caption(f"{summary.get('operational_reassignment_pct', 0.0)}% without guest edits")
with col4:
    st.metric("Reassigned Cancel Rate", f"{summary.get('reassigned_cancellation_rate_pct', 0.0)}%")
    st.caption(f"vs {summary.get('same_room_cancellation_rate_pct', 0.0)}% for unassigned")

st.markdown("---")

col5, col6 = st.columns(2)

# Room Allocation Heatmap
with col5:
    st.subheader("🗺️ Reserved vs Assigned Room Type Matrix")
    matrix_data = get_room_allocation_matrix(
        hotel=filters["hotel"],
        start_date=filters["start_date"],
        end_date=filters["end_date"]
    )
    if matrix_data:
        df_mat = pd.DataFrame(matrix_data)
        fig_heat = create_heatmap(
            df_mat, x="assigned_room_type", y="reserved_room_type", z="booking_count",
            title="Room Assignment Heatmap (Diagonal = Kept Same)"
        )
        st.plotly_chart(fig_heat, use_container_width=True)

# Booking Changes Distribution
with col6:
    st.subheader("🔄 Modifications Prior to Check-In")
    changes_data = get_booking_changes_distribution(
        hotel=filters["hotel"],
        start_date=filters["start_date"],
        end_date=filters["end_date"]
    )
    if changes_data:
        df_ch = pd.DataFrame(changes_data)
        fig_ch = create_bar_chart(
            df_ch.head(8), x="booking_changes", y="total_bookings",
            title="Bookings by Count of Pre-Arrival Changes"
        )
        st.plotly_chart(fig_ch, use_container_width=True)
