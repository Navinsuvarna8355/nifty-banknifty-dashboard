import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
from nsepython import nse_optionchain_scrapper, nse_fno
import datetime

# 🔁 Auto-refresh every 5 minutes
st_autorefresh(interval=5 * 60 * 1000, limit=100, key="refresh")

# 🧠 Session state to store time-series data
if "nifty_df" not in st.session_state:
    st.session_state.nifty_df = pd.DataFrame(columns=["time", "CE_OI", "PE_OI", "Fut_Price"])
if "bank_df" not in st.session_state:
    st.session_state.bank_df = pd.DataFrame(columns=["time", "CE_OI", "PE_OI", "Fut_Price"])

# 📦 Extract CE/PE OI and Futures price
def extract_data(symbol):
    data = nse_optionchain_scrapper(symbol)
    expiry = data["records"]["expiryDates"][0]
    ce_oi = 0
    pe_oi = 0
    for item in data["records"]["data"]:
        if item["expiryDate"] == expiry:
            ce_oi += item.get("CE", {}).get("openInterest", 0)
            pe_oi += item.get("PE", {}).get("openInterest", 0)
    fut_data = nse_fno(symbol)
    fut_price = float(fut_data["data"][0]["lastPrice"])
    return ce_oi, pe_oi, fut_price

# 📊 Bar chart for OI change
def plot_oi_change_bar(ce_change, pe_change, title):
    fig, ax = plt.subplots()
    ax.bar(["CALL", "PUT"], [ce_change, pe_change], color=["blue", "red"])
    ax.set_title(f"{title} Change in OI")
    st.pyplot(fig)

# 📈 Line chart for CE/PE OI and Futures
def plot_oi_time_series(df, title):
    fig, ax1 = plt.subplots()
    ax1.plot(df["time"], df["CE_OI"], label="CE", color="teal")
    ax1.plot(df["time"], df["PE_OI"], label="PE", color="red")
    ax1.set_ylabel("OI")
    ax1.tick_params(axis='x', rotation=45)

    ax2 = ax1.twinx()
    ax2.plot(df["time"], df["Fut_Price"], label="Future", color="black", linestyle="dotted")
    ax2.set_ylabel("Futures Price")

    fig.legend(loc="upper left")
    ax1.set_title(f"{title} OI & Futures")
    st.pyplot(fig)

# 🕒 Current time label
def get_time_label():
    now = datetime.datetime.now()
    return now.strftime("%H:%M")

# 📈 NIFTY Panel
with st.container():
    st.subheader("📈 NIFTY Dashboard")
    ce_oi, pe_oi, fut_price = extract_data("NIFTY")
    time_label = get_time_label()
    st.session_state.nifty_df.loc[len(st.session_state.nifty_df)] = [time_label, ce_oi, pe_oi, fut_price]

    if len(st.session_state.nifty_df) > 1:
        prev = st.session_state.nifty_df.iloc[-2]
        ce_change = ce_oi - prev["CE_OI"]
        pe_change = pe_oi - prev["PE_OI"]
    else:
        ce_change = pe_change = 0

    plot_oi_change_bar(ce_change, pe_change, "NIFTY")
    plot_oi_time_series(st.session_state.nifty_df, "NIFTY")

# 📉 BANKNIFTY Panel
with st.container():
    st.subheader("📉 BANKNIFTY Dashboard")
    ce_oi, pe_oi, fut_price = extract_data("BANKNIFTY")
    time_label = get_time_label()
    st.session_state.bank_df.loc[len(st.session_state.bank_df)] = [time_label, ce_oi, pe_oi, fut_price]

    if len(st.session_state.bank_df) > 1:
        prev = st.session_state.bank_df.iloc[-2]
        ce_change = ce_oi - prev["CE_OI"]
        pe_change = pe_oi - prev["PE_OI"]
    else:
        ce_change = pe_change = 0

    plot_oi_change_bar(ce_change, pe_change, "BANKNIFTY")
    plot_oi_time_series(st.session_state.bank_df, "BANKNIFTY")
