import streamlit as st
import requests
import json
import pandas as pd
import altair as alt

# ------------------ CONFIG ------------------
st.set_page_config(page_title="📊 NIFTY/BANKNIFTY Dashboard", layout="wide")
st.title("📊 NIFTY & BANKNIFTY Dashboard")
st.caption("Live Spot Prices + NIFTY Option Chain OI")

# ------------------ HEADERS ------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com"
}

# ------------------ PRICE FETCHERS ------------------
@st.cache_data(ttl=60)
def fetch_spot_price(symbol):
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", headers=HEADERS)
        response = session.get(url, headers=HEADERS)
        data = json.loads(response.text)
        return float(data["priceInfo"]["lastPrice"])
    except:
        return None

@st.cache_data(ttl=60)
def fetch_futures_price(symbol):
    url = f"https://www.nseindia.com/api/quote-derivative?symbol={symbol}"
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", headers=HEADERS)
        response = session.get(url, headers=HEADERS)
        data = json.loads(response.text)
        return float(data["priceInfo"]["lastPrice"])
    except:
        return None

# ------------------ OPTION CHAIN ------------------
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

# ------------------ DISPLAY PRICES ------------------
nifty_price = fetch_futures_price("NIFTY") or fetch_spot_price("NIFTY")
banknifty_price = fetch_futures_price("BANKNIFTY") or fetch_spot_price("BANKNIFTY")

col1, col2 = st.columns(2)
with col1:
    st.metric("📈 NIFTY", f"{nifty_price:.2f}" if nifty_price else "N/A")
with col2:
    st.metric("🏦 BANKNIFTY", f"{banknifty_price:.2f}" if banknifty_price else "N/A")

# ------------------ DISPLAY OI ------------------
data = fetch_option_chain("NIFTY")
df_oi = extract_oi_by_expiry(data)

if df_oi.empty:
    st.warning("⚠️ No option chain data available.")
else:
    st.subheader("🔍 CE vs PE Open Interest")
    base = alt.Chart(df_oi).encode(x="Strike:O")

    ce_chart = base.mark_bar(color="#ff7f0e").encode(y="Call OI:Q")
    pe_chart = base.mark_bar(color="#1f77b4").encode(y="Put OI:Q")

    st.altair_chart(ce_chart + pe_chart, use_container_width=True)
    st.dataframe(df_oi, use_container_width=True)

# ------------------ MANUAL REFRESH ------------------
st.button("🔄 Refresh Now")
