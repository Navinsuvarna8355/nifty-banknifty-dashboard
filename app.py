import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────
# 🔄 Replace this with your actual NSE scraper
def fetch_nse_data(index_name):
    # Simulated data — replace with real scraper output
    if index_name == "NIFTY":
        df = pd.DataFrame({
            'Strike': [24900, 25000, 25100, 25200, 25300],
            'Call_OI': [80000, 100000, 120000, 140000, 160000],
            'Put_OI': [60000, 62000, 61000, 61500, 61800],
            'Futures': [25100] * 5  # Replace with live Futures price
        })
        strategy = {
            "Live Price": "₹25119.85",
            "Suggested Option": "25100 CE",
            "Trend": "BULLISH",
            "Signal": "BUY",
            "Strategy": "3 EMA Crossover + PCR (option-chain)",
            "Confidence": "90%",
            "PCR (used)": "1.14",
            "PCR total": "1.33",
            "PCR near": "1.14",
            "Expiry": "21-Aug-2025"
        }
    else:
        df = pd.DataFrame({
            'Strike': [55800, 55900, 56000, 56100, 56200],
            'Call_OI': [120000, 150000, 180000, 200000, 220000],
            'Put_OI': [100000, 102000, 101500, 101800, 102200],
            'Futures': [56000] * 5  # Replace with live Futures price
        })
        strategy = {
            "Live Price": "₹55902.35",
            "Suggested Option": "—",
            "Trend": "BEARISH",
            "Signal": "SIDEWAYS",
            "Strategy": "3 EMA Crossover + PCR (option-chain)",
            "Confidence": "90%",
            "PCR (used)": "0.84",
            "PCR total": "0.76",
            "PCR near": "0.84",
            "Expiry": "28-Aug-2025"
        }

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df, strategy, timestamp

# ─────────────────────────────────────────────
# 📈 Dual Y-Axis Plotly Chart
def plot_dual_axis(df, title):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['Strike'], y=df['Call_OI'],
                             mode='lines+markers', name='Call OI', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df['Strike'], y=df['Put_OI'],
                             mode='lines+markers', name='Put OI', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df['Strike'], y=df['Futures'],
                             mode='lines+markers', name='Futures', line=dict(color='lightblue'), yaxis='y2'))

    fig.update_layout(
        title=title,
        xaxis_title='Strike Price',
        yaxis=dict(title='Open Interest'),
        yaxis2=dict(title='Futures Price', overlaying='y', side='right'),
        legend=dict(x=0.01, y=0.99),
        margin=dict(l=40, r=40, t=40, b=40),
        height=400
    )
    return fig

# ─────────────────────────────────────────────
# 📋 Strategy Card Renderer
def render_strategy_card(title, data, timestamp):
    st.subheader(title)
    st.markdown(f"**Live Price:** {data['Live Price']}")
    st.markdown(f"**Suggested Option:** {data['Suggested Option']}")
    st.markdown(f"**Trend:** {data['Trend']}")
    st.markdown(f"**Signal:** {data['Signal']}")
    st.markdown(f"**Strategy:** {data['Strategy']}")
    st.markdown(f"**Confidence:** {data['Confidence']}")
    st.markdown(f"**PCR (used):** {data['PCR (used)']}")
    st.markdown(f"**PCR total:** {data['PCR total']}")
    st.markdown(f"**PCR near:** {data['PCR near']}")
    st.markdown(f"**Expiry:** {data['Expiry']}")
    st.caption(f"Last updated: {timestamp}")

# ─────────────────────────────────────────────
# 🧠 Dashboard Layout
st.set_page_config(page_title="NIFTY/BANKNIFTY Dashboard", layout="wide")
st.title("📌 NIFTY & BANKNIFTY Strategy + OI Dashboard")

# Fetch live data
nifty_df, nifty_strategy, nifty_time = fetch_nse_data("NIFTY")
banknifty_df, banknifty_strategy, banknifty_time = fetch_nse_data("BANKNIFTY")

# Strategy Cards
st.markdown("### 🔍 Strategy Overview")
col1, col2 = st.columns(2)
with col1:
    render_strategy_card("📈 NIFTY Strategy", nifty_strategy, nifty_time)
with col2:
    render_strategy_card("📉 BANKNIFTY Strategy", banknifty_strategy, banknifty_time)

# Charts
st.markdown("### 📊 CE/PE/Futures Line Charts")
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(plot_dual_axis(nifty_df, "NIFTY CE/PE/Futures"), use_container_width=True)
with col4:
    st.plotly_chart(plot_dual_axis(banknifty_df, "BANKNIFTY CE/PE/Futures"), use_container_width=True)
