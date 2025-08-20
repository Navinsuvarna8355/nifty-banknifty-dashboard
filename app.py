import streamlit as st
import pandas as pd
import time
from nsepython import nse_fno
import plotly.graph_objects as go

# ------------------ CONFIG ------------------
st.set_page_config(page_title="📈 NIFTY Dashboard", layout="wide")
st.title("📈 NIFTY Futures Dashboard")
st.caption("Live price tracking with auto-refresh")

# ------------------ FUNCTION ------------------
def get_futures_price(symbol):
    try:
        fut_data = nse_fno(symbol)
        if "data" in fut_data and isinstance(fut_data["data"], list) and len(fut_data["data"]) > 0:
            return float(fut_data["data"][0].get("lastPrice", 0))
        else:
            st.warning(f"⚠️ Futures data not available for {symbol}.")
            return None
    except Exception as e:
        st.error(f"❌ Error fetching futures price for {symbol}: {e}")
        return None

def plot_futures_line(price, symbol):
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=price,
        title={"text": f"{symbol} Futures Price"},
        number={"prefix": "₹"},
        delta={"reference": price, "relative": False}
    ))
    fig.update_layout(height=200)
    st.plotly_chart(fig, use_container_width=True)

# ------------------ MAIN ------------------
refresh_interval = 60  # seconds
placeholder = st.empty()

while True:
    with placeholder.container():
        st.subheader("🔄 Auto-refreshing every 60 seconds")
        price = get_futures_price("NIFTY")
        if price:
            plot_futures_line(price, "NIFTY")
        else:
            st.text("Futures price unavailable.")
        st.markdown("---")
    time.sleep(refresh_interval)
