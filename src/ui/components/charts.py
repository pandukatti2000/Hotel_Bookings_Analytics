import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any, Optional

DARK_THEME_LAYOUT = dict(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#161B22",
    font=dict(color="#E6EDF3", family="Inter, system-ui, sans-serif"),
    margin=dict(l=40, r=40, t=50, b=40),
    legend=dict(
        bgcolor="rgba(22, 27, 34, 0.8)",
        bordercolor="#30363D",
        borderwidth=1
    ),
    xaxis=dict(gridcolor="#21262D", zerolinecolor="#30363D"),
    yaxis=dict(gridcolor="#21262D", zerolinecolor="#30363D")
)

def create_trend_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["year_month"],
        y=df["total_bookings"],
        name="Total Bookings",
        marker_color="#238636"
    ))
    fig.add_trace(go.Scatter(
        x=df["year_month"],
        y=df["cancellation_rate_pct"],
        name="Cancellation Rate %",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="#F85149", width=3)
    ))
    layout = DARK_THEME_LAYOUT.copy()
    layout["yaxis2"] = dict(
        title="Cancellation Rate %",
        overlaying="y",
        side="right",
        range=[0, 100],
        gridcolor="#30363D"
    )
    fig.update_layout(**layout)
    fig.update_layout(title="Monthly Booking Volume & Cancellation Rate", hovermode="x unified")
    return fig

def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color: Optional[str] = None) -> go.Figure:
    fig = px.bar(
        df, x=x, y=y, title=title,
        color=color or x,
        color_discrete_sequence=px.colors.qualitative.Prism,
        template="plotly_dark"
    )
    fig.update_layout(**DARK_THEME_LAYOUT)
    return fig

def create_pie_chart(df: pd.DataFrame, names: str, values: str, title: str) -> go.Figure:
    fig = px.pie(
        df, names=names, values=values, title=title,
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Prism,
        template="plotly_dark"
    )
    fig.update_layout(**DARK_THEME_LAYOUT)
    return fig

def create_heatmap(df: pd.DataFrame, x: str, y: str, z: str, title: str) -> go.Figure:
    pivot_df = df.pivot(index=y, columns=x, values=z).fillna(0)
    fig = px.imshow(
        pivot_df,
        labels=dict(x=x, y=y, color=z),
        title=title,
        color_continuous_scale="Viridis",
        template="plotly_dark"
    )
    fig.update_layout(**DARK_THEME_LAYOUT)
    return fig
