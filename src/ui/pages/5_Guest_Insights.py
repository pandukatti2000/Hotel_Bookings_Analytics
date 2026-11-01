import streamlit as st
import pandas as pd
from src.ui.components.filters import render_sidebar_filters
from src.ui.components.charts import create_pie_chart, create_bar_chart
from src.services.guest_service import (
    get_guest_composition_stats,
    get_top_countries,
    get_meal_preferences,
    get_special_requests_and_parking
)

st.set_page_config(page_title="Guest Insights | StayWise AI", page_icon="👥", layout="wide")
filters = render_sidebar_filters()

st.title("👥 Guest Demographics & Hospitality Preferences")
st.markdown("Understand guest party compositions, geographic origin markets, meal plan adoption, and operational service requests.")

col1, col2 = st.columns(2)

# Party Composition
with col1:
    st.subheader("👨‍👩‍👧 Party Composition Mix")
    comp_data = get_guest_composition_stats(
        hotel=filters["hotel"],
        start_date=filters["start_date"],
        end_date=filters["end_date"]
    )
    if comp_data:
        df_comp = pd.DataFrame(comp_data)
        fig_comp = create_pie_chart(
            df_comp, names="guest_composition_type", values="total_bookings",
            title="Bookings by Travel Party Type"
        )
        st.plotly_chart(fig_comp, use_container_width=True)

# Meal Preferences
with col2:
    st.subheader("🍽️ Boarding Meal Package Distribution")
    meal_data = get_meal_preferences(
        hotel=filters["hotel"],
        start_date=filters["start_date"],
        end_date=filters["end_date"]
    )
    if meal_data:
        df_meal = pd.DataFrame(meal_data)
        fig_meal = create_bar_chart(
            df_meal, x="meal_description", y="total_bookings",
            title="Bookings by Meal Plan"
        )
        st.plotly_chart(fig_meal, use_container_width=True)

st.markdown("---")

col3, col4 = st.columns(2)

# Top 15 Origin Countries
with col3:
    st.subheader("🌍 Top 15 Guest Origin Countries")
    country_data = get_top_countries(
        hotel=filters["hotel"],
        start_date=filters["start_date"],
        end_date=filters["end_date"],
        limit=15
    )
    if country_data:
        df_c = pd.DataFrame(country_data)
        fig_c = create_bar_chart(
            df_c, x="country_name", y="total_bookings",
            title="Top 15 Countries of Residence"
        )
        st.plotly_chart(fig_c, use_container_width=True)

# Special Requests & Parking
with col4:
    st.subheader("🛎️ Special Requests & Parking Demand")
    req_park = get_special_requests_and_parking(
        hotel=filters["hotel"],
        start_date=filters["start_date"],
        end_date=filters["end_date"]
    )
    if req_park.get("special_requests"):
        df_req = pd.DataFrame(req_park["special_requests"])
        fig_req = create_bar_chart(
            df_req, x="total_of_special_requests", y="cancellation_rate_pct",
            title="Cancellation Rate % by Number of Special Requests"
        )
        st.plotly_chart(fig_req, use_container_width=True)
    st.caption("Notice: Higher number of special requests strongly correlates with lower cancellation rates (increased guest commitment).")
