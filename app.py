import streamlit as st
import requests
from charts import generate_combined_chart

# App title
st.set_page_config(page_title="OI + Futures Chart", layout="wide")
st.title("📈 NIFTY/FINNIFTY Open Interest + Futures Price Chart")

# Sidebar inputs
symbol = st.sidebar.selectbox("Select Symbol", ["NIFTY", "FINNIFTY"])
url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

# NSE headers
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

# Fetch data
@st.cache_data(ttl=300)
def fetch_data():
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    return response.json()

data = fetch_data()

# Extract expiry dates
expiries = sorted(list(set(item["expiryDate"] for item in data["records"]["data"])))
selected_expiry = st.sidebar.selectbox("Select Expiry Date", expiries)

# Generate and show chart
fig = generate_combined_chart(data, selected_expiry, symbol)
st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Plotly")
