import streamlit as st
import csv, os
from datetime import datetime
import pandas as pd
from nse_option_chain import fetch_option_chain, compute_oi_pcr_and_underlying
from signal_strategy import determine_signal

st.set_page_config(page_title="Strategy Signal", layout="wide")
st.title("📈 Strategy Signal — NIFTY & BANKNIFTY")

ema_signal = st.selectbox("EMA Signal", ["BUY", "SELL"])
use_near = st.checkbox("Use Near PCR", value=True)

col1, col2 = st.columns(2)

def log_signal(symbol, pcr, trend, ema_signal, signal, option, expiry):
    file = "strategy_log.csv"
    headers = ["Timestamp", "Symbol", "PCR", "Trend", "EMA", "Signal", "Option", "Expiry"]
    row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, pcr, trend, ema_signal, signal, option, expiry]
    write_header = not os.path.exists(file)
    with open(file, mode="a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(headers)
        writer.writerow(row)

def render_card(symbol, col):
    with col:
        st.subheader(f"{symbol}")
        try:
            data = fetch_option_chain(symbol)
            info = compute_oi_pcr_and_underlying(data)

            pcr = info["pcr_near"] if use_near and info["pcr_near"] else info["pcr_total"]
            trend = "BULLISH" if pcr and pcr >= 1 else "BEARISH"
            signal, side = determine_signal(pcr, trend, ema_signal)
            atm = round(info["underlying"] / 100) * 100
            suggested_option = f"{atm} {'CE' if side == 'CALL' else 'PE'}" if side else "N/A"

            log_signal(symbol, pcr, trend, ema_signal, signal, suggested_option, info["expiry"])

            st.metric("Signal", signal)
            st.metric("Live Price", f"₹{info['underlying']}")
            st.metric("PCR Used", pcr)
            st.metric("Trend", trend)
            st.metric("Suggested Option", suggested_option)
            st.caption(f"Expiry: {info['expiry']}")
        except Exception as e:
            st.error(f"Error fetching {symbol}: {e}")

render_card("NIFTY", col1)
render_card("BANKNIFTY", col2)

st.divider()
if st.checkbox("📋 Show Strategy Log"):
    if os.path.exists("strategy_log.csv"):
        df = pd.read_csv("strategy_log.csv")
        st.dataframe(df)
    else:
        st.info("No signals logged yet.")
