import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --------- CONFIG ---------
st.set_page_config(layout="wide")
REFRESH_INTERVAL = 60000  # in ms → 60s

# Static fallbacks if live spot fails
SPOT_FALLBACKS = {
    "NIFTY": 24500,
    "BANKNIFTY": 52000
}

# --------- AUTO‑REFRESH ---------
st_autorefresh(interval=REFRESH_INTERVAL, key="data_refresh")

# --------- OPTION CHAIN FETCHER ---------
@st.cache_data(ttl=60)
def fetch_option_chain(symbol):
    """
    Fetch NSE option chain for a given symbol, with cookie priming + headers
    to avoid 401 / empty JSON responses.
    """
    base_url = "https://www.nseindia.com"
    api_url = f"{base_url}/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": f"{base_url}/option-chain"
    }

    session = requests.Session()
    try:
        # Step 1: Prime cookies
        session.get(base_url, headers=headers, timeout=5)
        # Step 2: Fetch API JSON
        res = session.get(api_url, headers=headers, timeout=10)
        if res.status_code != 200:
            st.warning(f"⚠️ NSE returned {res.status_code} for {symbol}")
            return pd.DataFrame(), SPOT_FALLBACKS[symbol]
        data = res.json()
        df = pd.DataFrame(data["records"]["data"])
        spot = data["records"].get("underlyingValue", SPOT_FALLBACKS[symbol])
        return df, spot
    except Exception as e:
        st.error(f"❌ Failed to fetch {symbol} option chain: {e}")
        return pd.DataFrame(), SPOT_FALLBACKS[symbol]

# --------- CALCULATIONS ---------
def calculate_oi_summary(df):
    try:
        ce_oi = sum(item["CE"]["openInterest"] for item in df if "CE" in item)
        pe_oi = sum(item["PE"]["openInterest"] for item in df if "PE" in item)
        pcr = pe_oi / ce_oi if ce_oi else None
        return ce_oi, pe_oi, pcr
    except Exception:
        return None, None, None

def decide_strategy(pcr, ema_signal):
    if pcr is None:
        return "—"
    if 0.7 <= pcr <= 1.2:
        return "SIDEWAYS"
    return "BULLISH" if ema_signal == "BULLISH" else "BEARISH"

# --------- UI ---------
st.title("📊 NIFTY & BANKNIFTY Live Dashboard")

col1, col2 = st.columns(2)

for idx, symbol in enumerate(["NIFTY", "BANKNIFTY"]):
    df, spot = fetch_option_chain(symbol)
    ce_oi, pe_oi, pcr = calculate_oi_summary(df.to_dict("records"))
    ema_signal = "BULLISH"  # hook up your live EMA here
    strategy = decide_strategy(pcr, ema_signal)

    with (col1 if idx == 0 else col2):
        st.subheader(symbol)
        if df.empty:
            st.warning(f"⚠️ No valid OI data found for {symbol}.")
        st.markdown(f"**Expiry:** {datetime.now().strftime('%d-%b-%Y')}")
        st.markdown(f"**PCR:** {pcr:.2f}" if pcr else "—")
        st.markdown(f"**EMA Signal:** {ema_signal}")
        st.markdown(f"**Strategy:** {strategy}")
