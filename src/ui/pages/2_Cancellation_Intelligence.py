import streamlit as st
import pandas as pd
from src.ui.components.filters import render_sidebar_filters
from src.ui.components.charts import create_bar_chart
from src.services.cancellation_service import (
    get_cancellations_by_lead_time_band,
    get_cancellations_by_deposit_type,
    get_cancellations_by_market_segment,
    get_cancellations_by_customer_type,
    get_cancellations_by_repeat_guest
)

st.set_page_config(page_title="Cancellation Intelligence | StayWise AI", page_icon="🚫", layout="wide")
filters = render_sidebar_filters()

st.title("🚫 Cancellation Intelligence & Risk Analysis")
st.markdown("Understand the drivers of cancellation behavior: lead time bands, deposit policies, channels, and customer types.")

col1, col2 = st.columns(2)

# Lead Time Bands
with col1:
    st.subheader("⏳ Cancellation by Lead Time Band")
    lead_data = get_cancellations_by_lead_time_band(
        hotel=filters["hotel"],
        start_date=filters["start_date"],
        end_date=filters["end_date"]
    )
    if lead_data:
        df_lead = pd.DataFrame(lead_data)
        fig_lead = create_bar_chart(
            df_lead, x="lead_time_band", y="cancellation_rate_pct",
            title="Cancellation Rate % by Lead Time Window"
        )
        st.plotly_chart(fig_lead, use_container_width=True)

# Deposit Type Analysis
with col2:
    st.subheader("💳 The Non-Refundable Deposit Paradox")
    deposit_data = get_cancellations_by_deposit_type(
        hotel=filters["hotel"],
        start_date=filters["start_date"],
        end_date=filters["end_date"]
    )
    if deposit_data:
        df_dep = pd.DataFrame(deposit_data)
        fig_dep = create_bar_chart(
            df_dep, x="deposit_type", y="cancellation_rate_pct",
            title="Cancellation Rate % by Deposit Policy"
        )
        st.plotly_chart(fig_dep, use_container_width=True)
    st.info("ℹ️ **Operational Insight**: 'Non Refund' bookings show a 99.36% cancellation rate due to wholesale travel agencies holding and releasing large group tour blocks. While classified as cancellations, the property may retain non-refundable deposit fees.")

st.markdown("---")

col3, col4 = st.columns(2)

# Market Segment Risk
with col3:
    st.subheader("🏢 Cancellation Rate by Market Segment")
    mkt_data = get_cancellations_by_market_segment(
        hotel=filters["hotel"],
        start_date=filters["start_date"],
        end_date=filters["end_date"]
    )
    if mkt_data:
        df_mkt = pd.DataFrame(mkt_data)
        fig_mkt = create_bar_chart(
            df_mkt, x="market_segment_name", y="cancellation_rate_pct",
            title="Cancellation Rate % by Market Segment"
        )
        st.plotly_chart(fig_mkt, use_container_width=True)

# Customer Type & Repeat Guest
with col4:
    st.subheader("🔁 Repeat Guests vs First-Time Guests")
    rep_data = get_cancellations_by_repeat_guest(
        hotel=filters["hotel"],
        start_date=filters["start_date"],
        end_date=filters["end_date"]
    )
    if rep_data:
        df_rep = pd.DataFrame(rep_data)
        fig_rep = create_bar_chart(
            df_rep, x="guest_type", y="cancellation_rate_pct",
            title="Cancellation Rate %: Loyalty Impact"
        )
        st.plotly_chart(fig_rep, use_container_width=True)
