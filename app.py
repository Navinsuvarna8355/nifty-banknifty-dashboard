import streamlit as st
import requests
import json
import pandas as pd
import altair as alt

# ------------------ CONFIG ------------------
st.set_page_config(page_title="📊 NIFTY/BANKNIFTY Dashboard", layout="wide")
st.title("📊 NIFTY & BANKNIFTY Dashboard")
st.caption("Live Spot Prices + NIFTY Option Chain OI + Strategy Insights")

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
        price = data.get("priceInfo", {}).get("lastPrice")
        if price:
            return float(price)
        else:
            st.warning(f"⚠️ Spot price not found for {symbol}")
            return None
    except Exception as e:
        st.error(f"❌ Error fetching spot price for {symbol}: {e}")
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

# ------------------ STRATEGY LOGIC ------------------
def generate_strategy(df):
    if df.empty:
        return "⚠️ No data to generate strategy."

    max_ce = df.loc[df["Call OI"].idxmax()]
    max_pe = df.loc[df["Put OI"].idxmax()]
    ce_strike = max_ce["Strike"]
    pe_strike = max_pe["Strike"]

    if ce_strike > pe_strike:
        return f"🔺 Bullish Bias: Max CE OI at {ce_strike}, Max PE OI at {pe_strike}. Consider Bull Call Spread."
    elif pe_strike > ce_strike:
        return f"🔻 Bearish Bias: Max PE OI at {pe_strike}, Max CE OI at {ce_strike}. Consider Bear Put Spread."
    else:
        return f"⚖️ Neutral Bias: Max OI at same strike {ce_strike}. Consider Iron Condor or Straddle."

# ------------------ DISPLAY PRICES ------------------
nifty_price = fetch_spot_price("NIFTY")
banknifty_price = fetch_spot_price("BANKNIFTY")

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

    ce_chart = base.mark_bar(color="#1f77b4").encode(y="Call OI:Q")
    pe_chart = base.mark_bar(color="#ff7f0e").encode(y="Put OI:Q")

    st.altair_chart(ce_chart + pe_chart, use_container_width=True)
    st.dataframe(df_oi, use_container_width=True)

    # ------------------ DISPLAY STRATEGY ------------------
    st.subheader("🧠 Strategy Suggestion")
    strategy_text = generate_strategy(df_oi)
    st.info(strategy_text)

# ------------------ CUSTOM STRATEGY INSIGHTS ------------------
st.subheader("📌 Strategy Insights")

nifty_expiry = "21-Aug-2025"
nifty_pcr = 1.35
nifty_ema_signal = "BEARISH"
nifty_strategy = "SIDEWAYS 📉"

banknifty_expiry = "28-Aug-2025"
banknifty_pcr = 0.71
banknifty_ema_signal = "BEARISH"
banknifty_strategy = "BUY PE"

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 NIFTY")
    st.write(f"**Expiry:** {nifty_expiry}")
    st.write(f"**PCR:** {nifty_pcr}")
    st.write(f"**EMA Signal:** {nifty_ema_signal}")
    st.write(f"**Strategy:** {nifty_strategy}")

with col2:
    st.markdown("### 🏦 BANKNIFTY")
    st.write(f"**Expiry:** {banknifty_expiry}")
    st.write(f"**PCR:** {banknifty_pcr}")
    st.write(f"**EMA Signal:** {banknifty_ema_signal}")
    st.write(f"**Strategy:** {banknifty_strategy}")

# ------------------ MANUAL REFRESH ------------------
st.button("🔄 Refresh Now")
