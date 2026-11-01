import streamlit as st
import pandas as pd
from src.ui.components.filters import render_sidebar_filters
from src.ui.components.charts import create_trend_chart
from src.services.overview_service import (
    get_executive_kpis,
    get_monthly_booking_trends,
    get_hotel_comparison
)

st.set_page_config(page_title="Executive Overview | StayWise AI", page_icon="📊", layout="wide")
filters = render_sidebar_filters()

st.title("📊 Executive Overview & Demand Trends")
st.markdown("High-level portfolio performance, cancellation rates, booking values, and property comparison.")

# KPI Ribbon
kpis = get_executive_kpis(
    hotel=filters["hotel"],
    start_date=filters["start_date"],
    end_date=filters["end_date"],
    market_segment=filters["market_segment"],
    distribution_channel=filters["distribution_channel"],
    customer_type=filters["customer_type"]
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Bookings", f"{kpis.get('total_bookings', 0):,}")
    st.metric("Cancellation Rate", f"{kpis.get('cancellation_rate_pct', 0.0)}%")
with col2:
    st.metric("Average ADR", f"${kpis.get('avg_adr', 0.0):.2f}")
    st.metric("Median ADR", f"${kpis.get('median_adr', 0.0):.2f}")
with col3:
    st.metric("Est. Gross Value", f"${kpis.get('estimated_gross_booking_value', 0.0):,.0f}")
    st.metric("Est. Realized Value", f"${kpis.get('estimated_realized_booking_value', 0.0):,.0f}")
with col4:
    st.metric("Average Lead Time", f"{kpis.get('avg_lead_time_days', 0.0)} days")
    st.metric("Room Reassignment", f"{kpis.get('room_reassignment_pct', 0.0)}%")

st.markdown("---")

# Monthly Booking Trends
st.subheader("📈 Monthly Booking Volume & Cancellation Rate")
trends_data = get_monthly_booking_trends(
    hotel=filters["hotel"],
    start_date=filters["start_date"],
    end_date=filters["end_date"],
    market_segment=filters["market_segment"],
    distribution_channel=filters["distribution_channel"],
    customer_type=filters["customer_type"]
)
if trends_data:
    df_trends = pd.DataFrame(trends_data)
    fig_trends = create_trend_chart(df_trends)
    st.plotly_chart(fig_trends, use_container_width=True)
else:
    st.warning("No booking trend records found for current filters.")

st.markdown("---")

# Property Comparison
st.subheader("🏨 Property Comparison: City Hotel vs Resort Hotel")
hotel_comp = get_hotel_comparison(
    start_date=filters["start_date"],
    end_date=filters["end_date"]
)
if hotel_comp:
    df_comp = pd.DataFrame(hotel_comp)
    st.dataframe(
        df_comp.rename(columns={
            "hotel": "Hotel Property",
            "total_bookings": "Total Bookings",
            "cancellation_rate_pct": "Cancellation Rate %",
            "avg_lead_time_days": "Avg Lead Time (Days)",
            "avg_adr": "Avg ADR ($)",
            "median_adr": "Median ADR ($)",
            "avg_stay_nights": "Avg Stay Nights",
            "realized_booking_value": "Realized Value ($)",
            "repeat_guest_pct": "Repeat Guest %",
            "room_reassignment_pct": "Reassigned %"
        }),
        use_container_width=True,
        hide_index=True
    )
