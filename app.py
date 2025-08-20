import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from nsepython import nse_optionchain_scrapper, nse_fno
from streamlit_autorefresh import st_autorefresh

# 🔁 Auto-refresh every 5 minutes
st_autorefresh(interval=5 * 60 * 1000, limit=100, key="refresh")

# 📦 Extract strike-wise CE/PE OI
def get_option_oi(symbol):
    data = nse_optionchain_scrapper(symbol)
    expiry = data["records"]["expiryDates"][0]
    strikes = []
    ce_oi = []
    pe_oi = []
    for item in data["records"]["data"]:
        if item["expiryDate"] == expiry:
            strike = item["strikePrice"]
            ce = item.get("CE", {}).get("openInterest", 0)
            pe = item.get("PE", {}).get("openInterest", 0)
            strikes.append(strike)
            ce_oi.append(ce)
            pe_oi.append(pe)
    df = pd.DataFrame({"Strike": strikes, "CE_OI": ce_oi, "PE_OI": pe_oi})
    df = df.sort_values("Strike")
    return df, expiry

# 📈 Get Futures price
def get_futures_price(symbol):
    fut_data = nse_fno(symbol)
    return float(fut_data["data"][0]["lastPrice"])

# 📊 Plot CE/PE OI bar chart
def plot_oi_bar(df, title):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(df["Strike"] - 10, df["CE_OI"], width=20, label="CE", color="blue", alpha=0.6)
    ax.bar(df["Strike"] + 10, df["PE_OI"], width=20, label="PE", color="red", alpha=0.6)
    ax.set_xlabel("Strike Price")
    ax.set_ylabel("Open Interest")
    ax.set_title(f"{title} CE/PE OI")
    ax.legend()
    st.pyplot(fig)

# 📈 Plot Futures price line chart
def plot_futures_line(price, title):
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.plot([price], marker='o', color='black')
    ax.set_title(f"{title} Futures Price")
    ax.set_ylabel("Price")
    st.pyplot(fig)

# 🖥️ Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 NIFTY")
    nifty_df, nifty_expiry = get_option_oi("NIFTY")
    nifty_price = get_futures_price("NIFTY")
    st.text(f"Expiry: {nifty_expiry}")
    plot_oi_bar(nifty_df, "NIFTY")
    plot_futures_line(nifty_price, "NIFTY")

with col2:
    st.subheader("📉 BANKNIFTY")
    bank_df, bank_expiry = get_option_oi("BANKNIFTY")
    bank_price = get_futures_price("BANKNIFTY")
    st.text(f"Expiry: {bank_expiry}")
    plot_oi_bar(bank_df, "BANKNIFTY")
    plot_futures_line(bank_price, "BANKNIFTY")
