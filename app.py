# 📁 app.py

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# 🔧 Fetch option chain data from NSE
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
        session.get("https://www.nseindia.com", headers=headers)
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
def generate_strategy(option_data):
    ce_oi = sum(item["CE"]["openInterest"] for item in option_data if "CE" in item)
    pe_oi = sum(item["PE"]["openInterest"] for item in option_data if "PE" in item)

    if ce_oi > pe_oi:
        return "🔻 Bearish Signal (More Call OI)"
    elif pe_oi > ce_oi:
        return "🔺 Bullish Signal (More Put OI)"
    else:
        return "⚖️ Neutral Market"

# 📈 Plot CE vs PE Open Interest
def plot_oi(option_data):
    strikes = []
    ce_oi = []
    pe_oi = []

    for item in option_data:
        if "CE" in item and "PE" in item:
            strikes.append(item["strikePrice"])
            ce_oi.append(item["CE"]["openInterest"])
            pe_oi.append(item["PE"]["openInterest"])

    plt.figure(figsize=(10, 5))
    plt.plot(strikes, ce_oi, label="Call OI", color="red", marker="o")
    plt.plot(strikes, pe_oi, label="Put OI", color="green", marker="o")
    plt.xlabel("Strike Price")
    plt.ylabel("Open Interest")
    plt.title("CE vs PE Open Interest")
    plt.legend()
    st.pyplot(plt)

# 🚀 Streamlit UI
st.set_page_config(page_title="NIFTY & BANKNIFTY Strategy Signal", layout="wide")
st.title("📈 NIFTY & BANKNIFTY Strategy Signal Dashboard")

symbol = st.selectbox("Choose Index", ["NIFTY", "BANKNIFTY"])
data = fetch_option_chain(symbol)

if data and "records" in data and "data" in data["records"]:
    all_data = data["records"]["data"]

    # 📅 Expiry Date Filter
    expiry_dates = sorted(set(item["expiryDate"] for item in all_data if "expiryDate" in item))
    selected_expiry = st.selectbox("Choose Expiry Date", expiry_dates)

    filtered_data = [item for item in all_data if item.get("expiryDate") == selected_expiry]

    # 🧠 Strategy Signal
    signal = generate_strategy(filtered_data)
    st.subheader(f"Strategy Signal for {symbol} ({selected_expiry})")
    st.success(signal)

    # 📊 Chart
    st.subheader("Open Interest Chart")
    plot_oi(filtered_data)

    # 📋 Raw Data
    if st.checkbox("Show Raw Option Chain Data"):
        df = pd.json_normalize(filtered_data)
        st.dataframe(df)
else:
    st.warning("⚠️ Could not fetch valid data. Please try again later.")
