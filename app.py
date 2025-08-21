# app.py

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Dummy data — replace with live API
index_data = {
    "NIFTY": {
        "Live Price": 25119.85,
        "Suggested Option": "25100 CE",
        "Trend": "BULLISH",
        "Signal": "BUY",
        "Strategy": "3 EMA Crossover + PCR (option-chain)",
        "Confidence": 90,
        "PCR (used)": 1.14,
        "PCR total": 1.33,
        "PCR near": 1.14,
        "Expiry": "21-Aug-2025",
        "Timestamp": "2025-08-21 11:12:41",
        "Strikes": [24900, 25000, 25100, 25200, 25300],
        "CE OI": [120000, 135000, 150000, 160000, 170000],
        "PE OI": [80000, 95000, 110000, 130000, 140000],
        "Futures": [25010, 25040, 25085, 25120, 25150]
    },
    "BANKNIFTY": {
        "Live Price": 55902.35,
        "Suggested Option": "—",
        "Trend": "BEARISH",
        "Signal": "SIDEWAYS",
        "Strategy": "3 EMA Crossover + PCR (option-chain)",
        "Confidence": 90,
        "PCR (used)": 0.84,
        "PCR total": 0.76,
        "PCR near": 0.84,
        "Expiry": "28-Aug-2025",
        "Timestamp": "2025-08-21 11:12:41",
        "Strikes": [55800, 55900, 56000, 56100, 56200],
        "CE OI": [180000, 190000, 200000, 210000, 220000],
        "PE OI": [160000, 155000, 150000, 145000, 140000],
        "Futures": [55850, 55890, 55980, 56020, 56060]
    }
}

# Page setup
st.set_page_config(page_title="Index Strategy Dashboard", layout="wide")
st.title("📊 NIFTY & BANKNIFTY Strategy Dashboard")

# Render strategy cards side by side
col1, col2 = st.columns(2)

def render_card(col, index_name, info):
    with col:
        st.subheader(f"📈 {index_name}")
        st.metric("Live Price", f"₹{info['Live Price']:.2f}")
        st.text(f"Suggested Option: {info['Suggested Option']}")
        st.text(f"Trend: {info['Trend']}")
        st.text(f"Signal: {info['Signal']}")
        st.text(f"Strategy: {info['Strategy']}")
        st.text(f"Confidence: {info['Confidence']}%")
        st.text(f"PCR (used): {info['PCR (used)']}")
        st.text(f"PCR total: {info['PCR total']}")
        st.text(f"PCR near: {info['PCR near']}")
        st.text(f"Expiry: {info['Expiry']}")

        # Timestamp delta
        ts = datetime.strptime(info["Timestamp"], "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        delta = (now - ts).seconds
        st.text(f"⏱ Last updated {delta} seconds ago")

render_card(col1, "NIFTY", index_data["NIFTY"])
render_card(col2, "BANKNIFTY", index_data["BANKNIFTY"])

st.markdown("---")

# Render charts side by side
chart1, chart2 = st.columns(2)

def render_chart(col, index_name, info):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=info["Strikes"], y=info["CE OI"],
                             mode="lines+markers", name="Call OI", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=info["Strikes"], y=info["PE OI"],
                             mode="lines+markers", name="Put OI", line=dict(color="lightblue")))
    fig.add_trace(go.Scatter(x=info["Strikes"], y=info["Futures"],
                             mode="lines+markers", name="Futures", line=dict(color="red"), yaxis="y2"))

    fig.update_layout(
        title=f"{index_name} CE/PE/Futures Line Chart",
        xaxis=dict(title="Strike Price"),
        yaxis=dict(title="Open Interest", side="left"),
        yaxis2=dict(title="Futures Price", overlaying="y", side="right"),
        legend_title="Type",
        template="plotly_white"
    )

    with col:
        st.plotly_chart(fig, use_container_width=True)

render_chart(chart1, "NIFTY", index_data["NIFTY"])
render_chart(chart2, "BANKNIFTY", index_data["BANKNIFTY"])
