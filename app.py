import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from nsepython import nse_optionchain_scrapper
import random

# Page setup
st.set_page_config(page_title="OI + Futures Chart", layout="wide")
st.title("📈 NIFTY/FINNIFTY Open Interest + Futures Price Chart")

# Sidebar inputs
symbol = st.sidebar.selectbox("Select Symbol", ["NIFTY", "FINNIFTY"])

# Fetch data using nsepython
@st.cache_data(ttl=300)
def fetch_data(symbol):
    try:
        return nse_optionchain_scrapper(symbol)
    except Exception:
        return None

data = fetch_data(symbol)

# Validate response
if not data or "records" not in data or "data" not in data["records"]:
    st.error("❌ Failed to fetch valid data from NSE. Please try again later.")
    st.stop()

# Extract expiry dates
expiries = sorted(list(set(item["expiryDate"] for item in data["records"]["data"])))
selected_expiry = st.sidebar.selectbox("Select Expiry Date", expiries)

# Prepare data
strike_data = []
for item in data["records"]["data"]:
    if item["expiryDate"] == selected_expiry:
        strike = item["strikePrice"]
        ce_oi = item.get("CE", {}).get("openInterest", 0)
        pe_oi = item.get("PE", {}).get("openInterest", 0)
        strike_data.append((strike, ce_oi, pe_oi))

df = pd.DataFrame(strike_data, columns=["Strike", "Call OI", "Put OI"])
df.sort_values("Strike", inplace=True)

# Simulate Futures Price per strike
df["Futures Price"] = [
    random.randint(24500, 25500) if symbol == "NIFTY" else random.randint(55000, 56000)
    for _ in range(len(df))
]

# Create combined chart
fig = make_subplots(specs=[[{"secondary_y": True}]])

# CE/PE OI on primary y-axis
fig.add_trace(go.Scatter(x=df["Strike"], y=df["Call OI"], mode='lines+markers', name='Call OI'), secondary_y=False)
fig.add_trace(go.Scatter(x=df["Strike"], y=df["Put OI"], mode='lines+markers', name='Put OI'), secondary_y=False)

# Futures Price on secondary y-axis
fig.add_trace(go.Scatter(x=df["Strike"], y=df["Futures Price"], mode='lines+markers', name='Futures Price'), secondary_y=True)

fig.update_layout(
    title=f"{symbol} CE/PE Open Interest + Futures Price Trend ({selected_expiry})",
    xaxis_title="Strike Price",
    legend=dict(x=0.01, y=0.99),
    margin=dict(t=60, b=40)
)
fig.update_yaxes(title_text="Open Interest", secondary_y=False)
fig.update_yaxes(title_text="Futures Price", secondary_y=True)

# Show chart
st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit, Plotly & NSEPython")
