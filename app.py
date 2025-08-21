import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="NIFTY/BANKNIFTY Dashboard", layout="wide")

# ------------------ CONFIG ------------------
INDEX = st.selectbox("Choose Index", ["NIFTY", "BANKNIFTY"])
EXPIRY = "21-Aug-2025" if INDEX == "NIFTY" else "28-Aug-2025"
SPOT_FALLBACK = 25050.55 if INDEX == "NIFTY" else 55698.50

# ------------------ FETCH OPTION CHAIN ------------------
@st.cache_data(ttl=60)
def fetch_option_chain(index):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={index}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        data = res.json()
        return pd.DataFrame(data["records"]["data"])
    except:
        return pd.DataFrame()

df_raw = fetch_option_chain(INDEX)

# ------------------ SPOT PRICE ------------------
try:
    spot_price = df_raw["underlyingValue"].iloc[0]
except:
    spot_price = SPOT_FALLBACK

st.metric(f"{INDEX} Spot Price", f"{spot_price:.2f}")

# ------------------ OI TABLE ------------------
def extract_oi(df):
    rows = []
    for row in df.itertuples():
        ce = getattr(row, "CE", {}) or {}
        pe = getattr(row, "PE", {}) or {}

        if not isinstance(ce, dict): ce = {}
        if not isinstance(pe, dict): pe = {}

        strike = ce.get("strikePrice") or pe.get("strikePrice")
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
df_oi = df_oi.dropna().sort_values("Strike")

# ------------------ PCR CALCULATION ------------------
def calculate_pcr(df):
    total_pe = df["Put OI"].sum()
    total_ce = df["Call OI"].sum()
    return round(total_pe / total_ce, 2) if total_ce else None

pcr = calculate_pcr(df_oi)

# ------------------ EMA SIGNAL ------------------
@st.cache_data(ttl=300)
def fetch_price_history(index):
    # Replace with real API or CSV later
    prices = pd.Series([spot_price - i*10 for i in range(30)][::-1])
    return prices

def get_ema_signal(prices):
    ema_fast = prices.ewm(span=9).mean()
    ema_slow = prices.ewm(span=21).mean()
    return "BULLISH" if ema_fast.iloc[-1] > ema_slow.iloc[-1] else "BEARISH"

prices = fetch_price_history(INDEX)
ema_signal = get_ema_signal(prices)

# ------------------ STRATEGY ENGINE ------------------
def get_strategy(pcr, ema):
    if pcr > 1.2 and ema == "BULLISH":
        return "BUY CALL"
    elif pcr < 0.8 and ema == "BEARISH":
        return "BUY PUT"
    else:
        return "SIDEWAYS"

strategy = get_strategy(pcr, ema_signal)

# ------------------ DISPLAY STRATEGY ------------------
st.subheader("📊 Strategy Insights")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Expiry", EXPIRY)
col2.metric("PCR", pcr)
col3.metric("EMA Signal", ema_signal)
col4.metric("Strategy", strategy)

# ------------------ OI TABLE ------------------
st.subheader("🔍 Option Chain Open Interest")
st.dataframe(df_oi, use_container_width=True)
