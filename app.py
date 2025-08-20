import streamlit as st
from nsepython import nse_fno
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ------------------ CONFIG ------------------
st.set_page_config(page_title="📈 NIFTY Dashboard", layout="wide")
st.title("📈 NIFTY Futures Dashboard")
st.caption("Live price tracking with auto-refresh")

# ------------------ AUTO-REFRESH ------------------
st_autorefresh(interval=60 * 1000, limit=100, key="refresh")

# ------------------ FUNCTION ------------------
def get_futures_price(symbol):
    """
    Fetches the latest futures price for a given symbol (e.g., 'NIFTY', 'BANKNIFTY').
    Returns float or None.
    """
    try:
        fut_data = nse_fno(symbol)
        if "data" in fut_data and isinstance(fut_data["data"], list) and len(fut_data["data"]) > 0:
            return float(fut_data["data"][0].get("lastPrice", 0))
        else:
            st.warning(f"⚠️ No futures data found for {symbol}")
            return None
    except Exception as e:
        st.error(f"❌ Error fetching futures price for {symbol}: {e}")
        return None

def plot_futures_price(price, symbol):
    """
    Displays the futures price using a Plotly indicator chart.
    """
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=price,
        title={"text": f"{symbol} Futures"},
        number={"prefix": "₹"}
    ))
    fig.update_layout(height=200, margin=dict(t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

# ------------------ MAIN ------------------
symbol = "NIFTY"
price = get_futures_price(symbol)

if price:
    plot_futures_price(price, symbol)
else:
    st.text("Futures price unavailable.")
