import streamlit as st
import pandas as pd
import plotly.express as px
from src.ui.components.filters import render_sidebar_filters
from src.ui.components.charts import create_bar_chart, DARK_THEME_LAYOUT
from src.services.revenue_service import (
    get_monthly_adr_and_value,
    get_revenue_by_market_segment,
    get_stay_duration_vs_adr
)

st.set_page_config(page_title="ADR & Booking Value | StayWise AI", page_icon="💰", layout="wide")
filters = render_sidebar_filters()

st.title("💰 ADR Dynamics & Estimated Booking Value")
st.markdown("Analyze room rate yield, seasonal pricing curves, outlier impact, and segment contributions.")

# Monthly ADR & Value
st.subheader("📅 Monthly ADR Trends (Mean ADR vs Median ADR)")
monthly_data = get_monthly_adr_and_value(
    hotel=filters["hotel"],
    start_date=filters["start_date"],
    end_date=filters["end_date"]
)

if monthly_data:
    df_m = pd.DataFrame(monthly_data)
    
    fig = px.line(
        df_m, x="year_month", y=["mean_adr", "median_adr"],
        title="Monthly Mean ADR vs Median ADR (Outlier Robustness)",
        labels={"value": "ADR ($)", "variable": "Metric", "year_month": "Month"},
        template="plotly_dark",
        color_discrete_map={"mean_adr": "#58A6FF", "median_adr": "#3FB950"}
    )
    fig.update_layout(**DARK_THEME_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

col1, col2 = st.columns(2)

# Value by Market Segment
with col1:
    st.subheader("💼 Estimated Realized Value by Market Segment")
    seg_data = get_revenue_by_market_segment(
        hotel=filters["hotel"],
        start_date=filters["start_date"],
        end_date=filters["end_date"]
    )
    if seg_data:
        df_seg = pd.DataFrame(seg_data)
        fig_seg = create_bar_chart(
            df_seg, x="market_segment_name", y="realized_booking_value",
            title="Realized Booking Value by Segment ($)"
        )
        st.plotly_chart(fig_seg, use_container_width=True)

# Stay Duration vs ADR
with col2:
    st.subheader("🛏️ Stay Duration vs Average ADR")
    stay_data = get_stay_duration_vs_adr(
        hotel=filters["hotel"],
        start_date=filters["start_date"],
        end_date=filters["end_date"]
    )
    if stay_data:
        df_stay = pd.DataFrame(stay_data)
        fig_stay = create_bar_chart(
            df_stay, x="stay_length_category", y="avg_adr",
            title="Average ADR by Length of Stay Category ($)"
        )
        st.plotly_chart(fig_stay, use_container_width=True)
