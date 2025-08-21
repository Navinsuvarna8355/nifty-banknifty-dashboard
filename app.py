import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Sample strategy data (replace with live fetch logic)
info_nifty = {
    "Live Price": 25119.85,
    "Suggested Option": "25100 CE",
    "Trend": "BULLISH",
    "Signal": "BUY",
    "Strategy": "3 EMA Crossover + PCR (option-chain)",
    "Confidence": "90%",
    "PCR used": 1.14,
    "PCR total": 1.33,
    "PCR near": 1.14,
    "Expiry": "21-Aug-2025",
    "Timestamp": "2025-08-21 11:12:41"
}

info_banknifty = {
    "Live Price": 55902.35,
    "Suggested Option": "—",
    "Trend": "BEARISH",
    "Signal": "SIDEWAYS",
    "Strategy": "3 EMA Crossover + PCR (option-chain)",
    "Confidence": "90%",
    "PCR used": 0.84,
    "PCR total": 0.76,
    "PCR near": 0.84,
    "Expiry": "28-Aug-2025",
    "Timestamp": "2025-08-21 11:12:41"
}

# Sample chart data (replace with live fetch logic)
nifty_df = pd.DataFrame({
    "Strike": [24900, 25000, 25100, 25200, 25300],
    "Call OI": [120000, 130000, 140000, 150000, 160000],
    "Put OI": [80000, 85000, 90000, 95000, 100000],
    "Futures": [80000, 100000, 120000, 140000, 160000]
})

banknifty_df = pd.DataFrame({
    "Strike": [55800, 55900, 56000, 56100, 56200],
    "Call OI": [160000, 180000, 200000, 210000, 220000],
    "Put OI": [160000, 155000, 150000, 145000, 140000],
    "Futures": [140000, 160000, 180000, 200000, 220000]
})

# Format time delta
def format_time_delta(ts_str):
    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    delta = now - ts
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{seconds} seconds ago"
    elif seconds < 3600:
        return f"{seconds // 60} minutes ago"
    else:
        return f"{seconds // 3600} hours ago"

# Check staleness
def is_stale(ts_str, threshold_minutes=5):
    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    return datetime.now() - ts > timedelta(minutes=threshold_minutes)

# Strategy card
def display_card(title, info):
    st.subheader(title)
    st.metric("Live Price", f"₹{info['Live Price']}")
    st.write(f"**Suggested Option:** {info['Suggested Option']}")
    st.write(f"**Trend:** {info['Trend']}")
    st.write(f"**Signal:** {info['Signal']}")
    st.write(f"**Strategy:** {info['Strategy']}")
    st.write(f"**Confidence:** {info['Confidence']}")
    st.write(f"**PCR (used):** {info['PCR used']}")
    st.write(f"**PCR total:** {info['PCR total']}")
    st.write(f"**PCR near:** {info['PCR near']}")
    st.write(f"**Expiry:** {info['Expiry']}")

    time_str = format_time_delta(info["Timestamp"])
    st.write(f"⏱ Last updated {time_str}")
    if is_stale(info["Timestamp"]):
        st.warning("⚠️ Data may be stale. Consider refreshing or checking source reliability.")

# Chart renderer
def plot_oi_chart(df, title):
    if df.empty:
        st.warning(f"{title} data missing — chart not rendered.")
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(df["Strike"], df["Call OI"], label="Call OI", color="blue", marker="o")
    ax.plot(df["Strike"], df["Put OI"], label="Put OI", color="skyblue", marker="o")
    ax.plot(df["Strike"], df["Futures"], label="Futures", color="red", marker="o")
    ax.set_title(title)
    ax.set_xlabel("Strike Price")
    ax.set_ylabel("Open Interest")
    ax.legend()
    st.pyplot(fig)

# Layout
st.set_page_config(page_title="NIFTY & BANKNIFTY Strategy Dashboard", layout="wide")
st.title("📊 NIFTY & BANKNIFTY Strategy Dashboard")

if st.button("🔄 Refresh Now"):
    st.experimental_rerun()

# Strategy Cards
col1, col2 = st.columns(2)
with col1:
    display_card("📈 NIFTY", info_nifty)
with col2:
    display_card("📈 BANKNIFTY", info_banknifty)

# Charts
st.markdown("---")
col3, col4 = st.columns(2)
with col3:
    plot_oi_chart(nifty_df, "NIFTY CE/PE/Futures Line Chart")
with col4:
    plot_oi_chart(banknifty_df, "BANKNIFTY CE/PE/Futures Line Chart")
