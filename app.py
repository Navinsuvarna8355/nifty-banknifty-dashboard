# 📁 app.py

import streamlit as st
import requests
import pandas as pd

# 🔧 Function to fetch option chain data from NSE
def fetch_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/option-chain",
        "Connection": "keep-alive",
    }

    session = requests.Session()
    try:
        # First request to set cookies
        session.get("https://www.nseindia.com", headers=headers)

        # Second request to get option chain data
        response = session.get(url, headers=headers)

        if response.headers.get("Content-Type", "").startswith("application/json"):
            return response.json()
        else:
            st.error("⚠️ NSE blocked the request. Try again later.")
            return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

# 📊 Strategy signal based on Open Interest
def generate_strategy(data):
    option_data = data["records"]["data"]

    ce_oi = sum(item["CE"]["openInterest"] for item in option_data if "CE" in item)
    pe_oi = sum(item["PE"]["openInterest"] for item in option_data if "PE" in item)

    if ce_oi > pe_oi:
        return "🔻 Bearish Signal (More Call OI)"
    elif pe_oi > ce_oi:
        return "🔺 Bullish Signal (More Put OI)"
    else:
        return "⚖️ Neutral Market"

# 🖥️ Streamlit UI
st.set_page_config(page_title="NIFTY & BANKNIFTY Strategy Signal", layout="wide")
st.title("📈 NIFTY & BANKNIFTY Strategy Signal Dashboard")

symbol = st.selectbox("Choose Index", ["NIFTY", "BANKNIFTY"])

data = fetch_option_chain(symbol)

if data and "records" in data and "data" in data["records"]:
    signal = generate_strategy(data)
    st.subheader(f"Strategy Signal for {symbol}")
    st.success(signal)

    # Optional: Show raw option chain data
    if st.checkbox("Show Raw Option Chain Data"):
        df = pd.json_normalize(data["records"]["data"])
        st.dataframe(df)
else:
    st.warning("⚠️ Could not fetch valid data. Please try again later.")
