from nsepython import *
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# 🔁 Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, limit=100, key="refresh")

# 📊 Strategy logic
def get_strategy(pcr, ema_signal):
    if pcr < 0.8 and ema_signal == "BEARISH":
        return "BUY PE"
    elif pcr > 1.2 and ema_signal == "BULLISH":
        return "BUY CE"
    else:
        return "SIDEWAYS"

# 📈 Confidence score
def get_confidence_score(pcr, ema_signal):
    score = 0
    if ema_signal == "BULLISH":
        score += (pcr - 1.0) * 100
    elif ema_signal == "BEARISH":
        score += (1.0 - pcr) * 100
    return max(0, round(score, 1))

# 📦 Extract PCR from option chain
def extract_pcr(data):
    ce_oi = []
    pe_oi = []
    expiry = data["records"]["expiryDates"][0]
    for item in data["records"]["data"]:
        if item["expiryDate"] == expiry:
            ce = item.get("CE", {}).get("openInterest", 0)
            pe = item.get("PE", {}).get("openInterest", 0)
            ce_oi.append(ce)
            pe_oi.append(pe)
    pcr = sum(pe_oi) / sum(ce_oi) if sum(ce_oi) != 0 else 0
    return pcr, expiry

# 📉 EMA crossover signal
def get_ema_signal(prices):
    df = pd.DataFrame({'Price': prices})
    df['EMA3'] = df['Price'].ewm(span=3).mean()
    df['EMA6'] = df['Price'].ewm(span=6).mean()
    df['EMA9'] = df['Price'].ewm(span=9).mean()
    last = df.iloc[-1]
    if last['EMA3'] > last['EMA6'] > last['EMA9']:
        return "BULLISH"
    elif last['EMA3'] < last['EMA6'] < last['EMA9']:
        return "BEARISH"
    else:
        return "NEUTRAL"

# 📊 Plot EMA chart
def plot_ema(prices):
    df = pd.DataFrame({'Price': prices})
    df['EMA3'] = df['Price'].ewm(span=3).mean()
    df['EMA6'] = df['Price'].ewm(span=6).mean()
    df['EMA9'] = df['Price'].ewm(span=9).mean()

    fig, ax = plt.subplots()
    ax.plot(df['Price'], label='Price', color='gray')
    ax.plot(df['EMA3'], label='EMA3', color='green')
    ax.plot(df['EMA6'], label='EMA6', color='orange')
    ax.plot(df['EMA9'], label='EMA9', color='red')
    ax.legend()
    st.pyplot(fig)

# 🖥️ Streamlit layout
st.set_page_config(layout="wide")
col1, col2 = st.columns(2)

# 📈 NIFTY Dashboard
with col1:
    st.header("📈 NIFTY Dashboard")
    nifty_data = nse_optionchain_scrapper("NIFTY")
    nifty_pcr, nifty_expiry = extract_pcr(nifty_data)
    nifty_prices = [25050, 25080, 25110, 25140, 25100, 25090, 25068]  # Replace with live feed
    nifty_ema_signal = get_ema_signal(nifty_prices)
    nifty_strategy = get_strategy(nifty_pcr, nifty_ema_signal)
    nifty_confidence = get_confidence_score(nifty_pcr, nifty_ema_signal)

    st.metric("Expiry", nifty_expiry)
    st.metric("PCR", round(nifty_pcr, 2))
    st.metric("EMA Signal", nifty_ema_signal)
    st.metric("Strategy", nifty_strategy)
    st.metric("Confidence", f"{nifty_confidence}%")
    plot_ema(nifty_prices)

# 📉 BANKNIFTY Dashboard
with col2:
    st.header("📉 BANKNIFTY Dashboard")
    bank_data = nse_optionchain_scrapper("BANKNIFTY")
    bank_pcr, bank_expiry = extract_pcr(bank_data)
    bank_prices = [55700, 55680, 55650, 55620, 55600, 55580, 55550]  # Replace with live feed
    bank_ema_signal = get_ema_signal(bank_prices)
    bank_strategy = get_strategy(bank_pcr, bank_ema_signal)
    bank_confidence = get_confidence_score(bank_pcr, bank_ema_signal)

    st.metric("Expiry", bank_expiry)
    st.metric("PCR", round(bank_pcr, 2))
    st.metric("EMA Signal", bank_ema_signal)
    st.metric("Strategy", bank_strategy)
    st.metric("Confidence", f"{bank_confidence}%")
    plot_ema(bank_prices)
