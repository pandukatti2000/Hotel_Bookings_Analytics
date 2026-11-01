import streamlit as st
from datetime import date
from typing import Dict, Any

def render_sidebar_filters() -> Dict[str, Any]:
    st.sidebar.markdown("## 🔍 Global Filters")
    st.sidebar.markdown("Filter all dashboard analytics in real-time.")

    hotel = st.sidebar.selectbox(
        "Hotel Property",
        options=["All", "City Hotel", "Resort Hotel"],
        index=0,
        help="Select specific hotel type or analyze both"
    )

    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=date(2015, 7, 1),
            min_value=date(2015, 7, 1),
            max_value=date(2017, 8, 31)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=date(2017, 8, 31),
            min_value=date(2015, 7, 1),
            max_value=date(2017, 8, 31)
        )

    market_segment = st.sidebar.selectbox(
        "Market Segment",
        options=["All", "Online TA", "Offline TA/TO", "Groups", "Direct", "Corporate", "Complementary", "Aviation"],
        index=0
    )

    distribution_channel = st.sidebar.selectbox(
        "Distribution Channel",
        options=["All", "TA/TO", "Direct", "Corporate", "GDS"],
        index=0
    )

    customer_type = st.sidebar.selectbox(
        "Customer Type",
        options=["All", "Transient", "Transient-Party", "Contract", "Group"],
        index=0
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("🏨 StayWise AI Analytics v1.0.0")

    return {
        "hotel": hotel,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "market_segment": market_segment,
        "distribution_channel": distribution_channel,
        "customer_type": customer_type
    }
