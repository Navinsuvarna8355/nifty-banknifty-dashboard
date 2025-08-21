import streamlit as st
from datetime import datetime, timedelta

# Sample data — replace with your live fetch logic
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

# Format time delta for display
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

# Check if data is stale
def is_stale(ts_str, threshold_minutes=5):
    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    return datetime.now() - ts > timedelta(minutes=threshold_minutes)

# Display strategy card
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

    # Timestamp logic
    time_str = format_time_delta(info["Timestamp"])
    st.write(f"⏱ Last updated {time_str}")
    if is_stale(info["Timestamp"]):
        st.warning("⚠️ Data may be stale. Consider refreshing or checking source reliability.")

# App layout
st.set_page_config(page_title="NIFTY & BANKNIFTY Strategy Dashboard", layout="wide")
st.title("📊 NIFTY & BANKNIFTY Strategy Dashboard")

# Manual refresh
if st.button("🔄 Refresh Now"):
    st.experimental_rerun()

# Display both cards side by side
col1, col2 = st.columns(2)
with col1:
    display_card("📈 NIFTY", info_nifty)
with col2:
    display_card("📈 BANKNIFTY", info_banknifty)
