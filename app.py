# app.py

import streamlit as st
from datetime import datetime

# Static snapshot data — replace with live API later
data = {
    "NIFTY": {
        "Signal": "BUY",
        "Live Price": 25119.85,
        "Suggested Option": "25100 CE",
        "Trend": "BULLISH",
        "Strategy": "3 EMA Crossover + PCR (option-chain)",
        "Confidence": 90,
        "PCR (used)": 1.14,
        "PCR total": 1.33,
        "PCR near": 1.14,
        "Expiry": "21-Aug-2025",
        "Timestamp": "2025-08-21 11:12:41"
    },
    "BANKNIFTY": {
        "Signal": "SIDEWAYS",
        "Live Price": 55902.35,
        "Suggested Option": "—",
        "Trend": "BEARISH",
        "Strategy": "3 EMA Crossover + PCR (option-chain)",
        "Confidence": 90,
        "PCR (used)": 0.84,
        "PCR total": 0.76,
        "PCR near": 0.84,
        "Expiry": "28-Aug-2025",
        "Timestamp": "2025-08-21 11:12:41"
    }
}

# Page setup
st.set_page_config(page_title="Index Strategy Snapshot", layout="wide")
st.title("📊 NIFTY & BANKNIFTY Strategy Snapshot")

# Card renderer
def render_snapshot(index_name, info):
    st.subheader(f"📈 {index_name}")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Live Price", f"₹{info['Live Price']:.2f}")
        st.text(f"Suggested Option: {info['Suggested Option']}")
        st.text(f"Trend: {info['Trend']}")
        st.text(f"Signal: {info['Signal']}")
        st.text(f"Confidence: {info['Confidence']}%")

    with col2:
        st.text(f"Strategy: {info['Strategy']}")
        st.text(f"PCR (used): {info['PCR (used)']}")
        st.text(f"PCR total: {info['PCR total']}")
        st.text(f"PCR near: {info['PCR near']}")
        st.text(f"Expiry: {info['Expiry']}")
        st.text(f"Timestamp: {info['Timestamp']}")

    st.markdown("---")

# Render both snapshots
for index_name, info in data.items():
    render_snapshot(index_name, info)
