import streamlit as st
import pandas as pd
import plotly.express as px

# Dummy data (replace with live API or fallback logic)
index_data = {
    "NIFTY": {
        "spot": 25050.55,
        "futures": 25085.20,
        "expiry": "21-Aug-2025",
        "pcr": 1.33,
        "ema_signal": "BULLISH",
        "strategy": "BUY CALL",
        "oi_ce": [120000, 135000, 150000, 160000, 170000],
        "oi_pe": [80000, 95000, 110000, 130000, 140000],
        "strikes": [24900, 25000, 25100, 25200, 25300]
    },
    "BANKNIFTY": {
        "spot": 55926.60,
        "futures": 55980.10,
        "expiry": "21-Aug-2025",
        "pcr": 0.716,
        "ema_signal": "NEUTRAL to BULLISH",
        "strategy": "WATCH or SELL PUT",
        "oi_ce": [180000, 190000, 200000, 210000, 220000],
        "oi_pe": [160000, 155000, 150000, 145000, 140000],
        "strikes": [55800, 55900, 56000, 56100, 56200]
    }
}

def render_strategy_card(index_name, data):
    st.subheader(f"📈 {index_name} Strategy Insights")
    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Spot Price", value=f"₹{data['spot']:.2f}")
        st.metric(label="Futures Price", value=f"₹{data['futures']:.2f}")
        st.text(f"Expiry: {data['expiry']}")
        st.text(f"PCR: {data['pcr']}")
    
    with col2:
        st.text(f"EMA Signal: {data['ema_signal']}")
        st.text(f"Strategy: {data['strategy']}")

    st.markdown("---")

def render_oi_chart(index_name, data):
    df = pd.DataFrame({
        "Strike": data["strikes"],
        "Call OI": data["oi_ce"],
        "Put OI": data["oi_pe"]
    })

    fig = px.line(df, x="Strike", y=["Call OI", "Put OI"],
                  title=f"{index_name} CE/PE Open Interest",
                  markers=True)
    st.plotly_chart(fig, use_container_width=True)

# Streamlit layout
st.set_page_config(page_title="Index Strategy Dashboard", layout="wide")
st.title("📊 NIFTY & BANKNIFTY Strategy Dashboard")

for index_name, data in index_data.items():
    render_strategy_card(index_name, data)
    render_oi_chart(index_name, data)

# Optional: Add external links
st.markdown("🔍 [BANKNIFTY OI Tracker](https://www.niftytrader.in/banknifty-live-oi-tracker)")
st.markdown("🔍 [NIFTY OI Tracker](https://www.niftytrader.in/nifty-live-oi-tracker)")
