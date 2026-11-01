import streamlit as st
import pandas as pd
from src.ui.components.filters import render_sidebar_filters
from src.ui.components.charts import create_pie_chart, create_bar_chart
from src.services.channel_service import (
    get_channel_performance,
    get_top_agents
)

st.set_page_config(page_title="Booking Sources | StayWise AI", page_icon="🌐", layout="wide")
filters = render_sidebar_filters()

st.title("🌐 Distribution Channels & Booking Sources")
st.markdown("Examine reservation distribution across Direct, Online Travel Agencies (OTAs), Tour Operators, and Corporate accounts.")

col1, col2 = st.columns(2)

# Channel Share Donut
with col1:
    st.subheader("🍩 Distribution Channel Booking Share")
    channel_data = get_channel_performance(
        hotel=filters["hotel"],
        start_date=filters["start_date"],
        end_date=filters["end_date"]
    )
    if channel_data:
        df_chan = pd.DataFrame(channel_data)
        fig_donut = create_pie_chart(
            df_chan, names="distribution_channel_name", values="total_bookings",
            title="Reservation Share by Distribution Channel"
        )
        st.plotly_chart(fig_donut, use_container_width=True)

# Channel Cancellation Risk
with col2:
    st.subheader("⚠️ Cancellation Rate by Distribution Channel")
    if channel_data:
        fig_bar = create_bar_chart(
            df_chan, x="distribution_channel_name", y="cancellation_rate_pct",
            title="Channel Cancellation Rate %"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Top Agents
st.subheader("🤝 Top 10 Travel Agencies by Reservation Volume")
agent_data = get_top_agents(
    hotel=filters["hotel"],
    start_date=filters["start_date"],
    end_date=filters["end_date"],
    limit=10
)
if agent_data:
    df_agent = pd.DataFrame(agent_data)
    st.dataframe(
        df_agent.rename(columns={
            "agent_id": "Agency ID",
            "total_bookings": "Total Bookings",
            "canceled_bookings": "Canceled Bookings",
            "cancellation_rate_pct": "Cancellation Rate %",
            "realized_booking_value": "Realized Booking Value ($)"
        }),
        use_container_width=True,
        hide_index=True
    )
