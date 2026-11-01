import streamlit as st
from config.settings import settings

st.set_page_config(
    page_title="StayWise AI — Hotel Analytics",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark Styling
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    .stMetric {
        background-color: #161B22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363D;
    }
    .stMetric label {
        color: #8B949E !important;
        font-weight: 500;
    }
    .stMetric div[data-testid="stMetricValue"] {
        color: #58A6FF !important;
        font-weight: 700;
    }
    div[data-testid="stSidebarNav"] {
        background-color: #0D1117;
    }
    .hero-banner {
        background: linear-gradient(135deg, #1F242C 0%, #0D1117 100%);
        padding: 28px;
        border-radius: 12px;
        border: 1px solid #30363D;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-banner">
    <h1 style="color: #58A6FF; margin-bottom: 8px;">🏨 StayWise AI</h1>
    <h3 style="color: #E6EDF3; font-weight: 400; margin-top: 0px;">
        Production Hotel Booking Analytics & Conversational Intelligence Platform
    </h3>
    <p style="color: #8B949E; font-size: 15px; margin-bottom: 0px;">
        Empowering General Managers, Revenue Yield Analysts, and Hotel Operations with 
        100% verified deterministic SQL metrics and safe GenAI querying over 119,390 reservations.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🧭 Platform Navigation")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    - **[1. Executive Overview](Executive_Overview)**: Portfolio KPIs, monthly demand trends, and property comparison.
    - **[2. Cancellation Intelligence](Cancellation_Intelligence)**: Lead-time risk curves, deposit type paradox, and segment vulnerability.
    - **[3. ADR & Booking Value](ADR_and_Booking_Value)**: Pricing seasonality, Median vs Mean ADR, and realized booking yield.
    - **[4. Booking Sources](Booking_Sources)**: Direct vs OTA channel performance, market segments, and agent volume.
    """)

with col2:
    st.markdown("""
    - **[5. Guest Insights](Guest_Insights)**: Demographic composition, top origin countries, meal packages, and parking.
    - **[6. Room Operations](Room_Operations)**: Reserved vs assigned room allocations, operational upgrades, and modifications.
    - **[7. AI Analytics Assistant](AI_Analytics_Assistant)**: Natural-language Text-to-SQL with SQLGlot AST safety and live Plotly visualization.
    - **[8. Data Quality & Methodology](Data_Quality_and_Methodology)**: Source lineage, Excel corruption reconciliation audit, and KPI glossary.
    """)

st.markdown("---")
st.info("💡 **Quick Start**: Use the left sidebar to navigate across analytical modules or set global filters.")
