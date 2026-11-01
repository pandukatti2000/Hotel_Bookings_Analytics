import streamlit as st
import pandas as pd
import uuid
import plotly.express as px
from src.ui.components.filters import render_sidebar_filters
from src.ui.components.charts import DARK_THEME_LAYOUT
from src.ai.graph import run_agent

st.set_page_config(page_title="AI Analytics Assistant | StayWise AI", page_icon="🤖", layout="wide")
filters = render_sidebar_filters()

st.title("🤖 StayWise AI Analytics Assistant")
st.markdown("Ask natural language questions about hotel reservations, cancellations, rates, and guest preferences. Queries are securely validated via SQLGlot AST inspection and executed on an isolated read-only PostgreSQL connection.")

# Initialize Session State for Chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())[:8]

# Suggested Questions
st.markdown("##### 💡 Suggested Questions")
sug_cols = st.columns(3)
with sug_cols[0]:
    if st.button("📊 Cancellation rate by distribution channel"):
        st.session_state.suggested_prompt = "What is the total booking volume and cancellation rate for each distribution channel?"
with sug_cols[1]:
    if st.button("🏨 Compare City vs Resort Hotel ADR & Value"):
        st.session_state.suggested_prompt = "Compare City Hotel and Resort Hotel on total bookings, cancellation rate, average ADR, and realized booking value."
with sug_cols[2]:
    if st.button("🌍 Top 5 origin countries by confirmed volume"):
        st.session_state.suggested_prompt = "What are the top 5 countries by confirmed non-canceled booking volume?"

# Handle suggested prompt click
prompt_to_run = None
if "suggested_prompt" in st.session_state and st.session_state.suggested_prompt:
    prompt_to_run = st.session_state.suggested_prompt
    st.session_state.suggested_prompt = None

# Render Chat History
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sql"):
            with st.expander("🔍 View Verified PostgreSQL Query"):
                st.code(msg["sql"], language="sql")
        if msg.get("data") and len(msg["data"]) > 0:
            df = pd.DataFrame(msg["data"])
            st.dataframe(df, use_container_width=True)
            # Render chart if applicable
            chart_type = msg.get("chart_type", "none")
            if chart_type in ["bar", "line", "pie"] and len(df.columns) >= 2:
                try:
                    c1, c2 = df.columns[0], df.columns[1]
                    if chart_type == "bar":
                        fig = px.bar(df, x=c1, y=c2, title=f"{c2} by {c1}", template="plotly_dark")
                    elif chart_type == "line":
                        fig = px.line(df, x=c1, y=c2, title=f"{c2} over {c1}", template="plotly_dark")
                    elif chart_type == "pie":
                        fig = px.pie(df, names=c1, values=c2, hole=0.4, title=f"Distribution of {c2}", template="plotly_dark")
                    fig.update_layout(**DARK_THEME_LAYOUT)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    pass

# Chat Input
user_input = st.chat_input("Ask a question about hotel performance, cancellations, or revenue...")
query_to_execute = prompt_to_run or user_input

if query_to_execute:
    # Append User Message
    st.session_state.chat_history.append({"role": "user", "content": query_to_execute})
    with st.chat_message("user"):
        st.markdown(query_to_execute)

    # Execute Agent
    with st.chat_message("assistant"):
        with st.spinner("Analyzing schema, generating validated SQL, and querying database..."):
            result = run_agent(
                question=query_to_execute,
                thread_id=st.session_state.thread_id,
                hotel_filter=filters["hotel"]
            )
            
            answer_text = result.get("answer") or "No response generated."
            sql_query = result.get("sql_query")
            data = result.get("data")
            chart_type = result.get("chart_type", "none")

            st.markdown(answer_text)
            if sql_query:
                with st.expander("🔍 View Verified PostgreSQL Query"):
                    st.code(sql_query, language="sql")
            if data and len(data) > 0:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
                
                # Render chart
                if chart_type in ["bar", "line", "pie"] and len(df.columns) >= 2:
                    try:
                        c1, c2 = df.columns[0], df.columns[1]
                        if chart_type == "bar":
                            fig = px.bar(df, x=c1, y=c2, title=f"{c2} by {c1}", template="plotly_dark")
                        elif chart_type == "line":
                            fig = px.line(df, x=c1, y=c2, title=f"{c2} over {c1}", template="plotly_dark")
                        elif chart_type == "pie":
                            fig = px.pie(df, names=c1, values=c2, hole=0.4, title=f"Distribution of {c2}", template="plotly_dark")
                        fig.update_layout(**DARK_THEME_LAYOUT)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass

                # CSV Download button
                csv_bytes = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Data as CSV",
                    data=csv_bytes,
                    file_name="staywise_query_results.csv",
                    mime="text/csv"
                )

            # Append to session history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer_text,
                "sql": sql_query,
                "data": data,
                "chart_type": chart_type
            })
