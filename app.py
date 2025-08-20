# app.py

import streamlit as st
import requests
import json
import pandas as pd
import altair as alt

# ------------------ CONFIG ------------------
st.set_page_config(page_title="NIFTY OI Dashboard", layout="wide")
st.title("📈 NIFTY Option Chain Open Interest")
st.caption("Live CE/PE OI for nearest expiry | Auto-refresh every 60s")

# ------------------ HEADERS ------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com"
}

# ------------------ FETCH FUNCTION ------------------
@st.cache_data(ttl=60)
def fetch_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com/option-chain", headers=HEADERS)
        response = session.get(url, headers=HEADERS)
        data = json.loads(response.text)
        return data
    except Exception as e:
        st.error(f"❌ Failed to fetch option chain: {e}")
        return None

# ------------------ PARSE FUNCTION ------------------
def extract_oi_by_expiry(data):
    if not data:
        return pd.DataFrame()

    expiry_dates = data.get("records", {}).get("expiryDates", [])
    if not expiry_dates:
        return pd.DataFrame()

    current_expiry = expiry_dates[0]
    rows = []

    for item in data["records"]["data"]:
        if item.get("expiryDate") == current_expiry:
            strike = item.get("strikePrice")
            ce_oi = item.get("CE", {}).get("openInterest", 0)
            pe_oi = item.get("PE", {}).get("openInterest", 0)
            rows.append({"Strike": strike, "Call OI": ce_oi, "Put OI": pe_oi})

    df = pd.DataFrame(rows).sort_values("Strike")
    return df

# ------------------ MAIN ------------------
data = fetch_option_chain("NIFTY")
df_oi = extract_oi_by_expiry(data)

if df_oi.empty:
    st.warning("⚠️ No option chain data available.")
else:
    st.subheader("🔍 CE vs PE Open Interest")
    base = alt.Chart(df_oi).encode(x="Strike:O")

    ce_chart = base.mark_bar(color="#1f77b4").encode(y="Call OI:Q")
    pe_chart = base.mark_bar(color="#ff7f0e").encode(y="Put OI:Q")

    st.altair_chart(ce_chart + pe_chart, use_container_width=True)

    st.dataframe(df_oi, use_container_width=True)

# ------------------ AUTO REFRESH ------------------
st.experimental_rerun()  # Optional: use with st_autorefresh if needed
