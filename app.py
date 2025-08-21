import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(layout="wide", page_title="NIFTY/BANKNIFTY Dashboard")
st.set_page_config(page_title="NIFTY/BANKNIFTY Dashboard", layout="wide")

# ------------------ CONFIG ------------------
INDEX = st.selectbox("Choose Index", ["NIFTY", "BANKNIFTY"])
@@ -36,14 +35,22 @@ def fetch_option_chain(index):
def extract_oi(df):
    rows = []
    for row in df.itertuples():
        ce = getattr(row, "CE", {})
        pe = getattr(row, "PE", {})
        ce = getattr(row, "CE", {}) or {}
        pe = getattr(row, "PE", {}) or {}

        if not isinstance(ce, dict): ce = {}
        if not isinstance(pe, dict): pe = {}

        strike = ce.get("strikePrice") or pe.get("strikePrice")
        rows.append({
            "Strike": strike,
            "Call OI": ce.get("openInterest", 0),
            "Put OI": pe.get("openInterest", 0)
        })
        call_oi = ce.get("openInterest", 0)
        put_oi = pe.get("openInterest", 0)

        if strike:
            rows.append({
                "Strike": strike,
                "Call OI": call_oi,
                "Put OI": put_oi
            })
    return pd.DataFrame(rows)

df_oi = extract_oi(df_raw)
@@ -60,7 +67,7 @@ def calculate_pcr(df):
# ------------------ EMA SIGNAL ------------------
@st.cache_data(ttl=300)
def fetch_price_history(index):
    # Replace with real API or CSV
    # Replace with real API or CSV later
    prices = pd.Series([spot_price - i*10 for i in range(30)][::-1])
    return prices

@@ -91,6 +98,6 @@ def get_strategy(pcr, ema):
col3.metric("EMA Signal", ema_signal)
col4.metric("Strategy", strategy)

# ------------------ OI Chart ------------------
# ------------------ OI TABLE ------------------
st.subheader("🔍 Option Chain Open Interest")
st.dataframe(df_oi, use_container_width=True)
