import streamlit as st
import plotly.graph_objects as go
from nse_option_chain import fetch_live_chart_data

st.set_page_config(layout="wide")
st.title("📈 NIFTY & BANKNIFTY Signal Dashboard")

def plot_chart(df, index_name):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price',
        increasing_line_color='green',
        decreasing_line_color='red'
    ))

    # Breakout logic: yellow dot if close > open + 30
    breakout_mask = df['close'] > df['open'] + 30
    breakout_points = df[breakout_mask]

    fig.add_trace(go.Scatter(
        x=breakout_points['timestamp'],
        y=breakout_points['close'],
        mode='markers',
        marker=dict(color='yellow', size=8),
        name='Breakout'
    ))

    fig.update_layout(
        title=f"{index_name} Chart",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        height=700,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            type='category',
            tickmode='auto',
            nticks=30,
            tickangle=45
        )
    )

    return fig

# Fetch full data
nifty_data = fetch_live_chart_data("NIFTY")
banknifty_data = fetch_live_chart_data("BANKNIFTY")

# Layout: side-by-side charts
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(plot_chart(nifty_data, "NIFTY"), use_container_width=True)
with col2:
    st.plotly_chart(plot_chart(banknifty_data, "BANKNIFTY"), use_container_width=True)
