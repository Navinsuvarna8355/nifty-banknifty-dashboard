from nsepython import *
import streamlit as st
import pandas as pd

def get_strategy(pcr: float, ema_signal: str) -> str:
    """
    Returns trading strategy based on PCR and EMA signal.

    Parameters:
    - pcr (float): Put-Call Ratio
    - ema_signal (str): 'BULLISH', 'BEARISH', or 'NEUTRAL'

    Returns:
    - str: Strategy recommendation ('BUY CE', 'BUY PE', 'SIDEWAYS')
    """
    ema_signal = ema_signal.upper()

    if ema_signal == "BULLISH":
        if pcr > 1.0:
            return "BUY CE"
        else:
            return "SIDEWAYS"
    elif ema_signal == "BEARISH":
        if pcr < 1.0:
            return "BUY PE"
        else:
            return "SIDEWAYS"
    else:
        return "SIDEWAYS"


# Function to extract PCR
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

# Function to calculate EMA signal
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

# Strategy logic
def get_strategy(pcr, ema_signal):
    if pcr < 0.8 and ema_signal == "BEARISH":
        return "BUY PE"
    elif pcr > 1.2 and ema_signal == "BULLISH":
        return "BUY CE"
    else:
        return "SIDEWAYS"

# Streamlit layout
st.set_page_config(layout="wide")
col1, col2 = st.columns(2)

with col1:
    st.header("📈 NIFTY Dashboard")
    nifty_data = nse_optionchain_scrapper("NIFTY")
    nifty_pcr, nifty_expiry = extract_pcr(nifty_data)
    nifty_prices = [25050, 25080, 25110, 25140, 25100, 25090, 25068]  # Replace with live feed
    nifty_ema_signal = get_ema_signal(nifty_prices)
    nifty_strategy = get_strategy(nifty_pcr, nifty_ema_signal)
    st.metric("Expiry", nifty_expiry)
    st.metric("PCR", round(nifty_pcr, 2))
    st.metric("EMA Signal", nifty_ema_signal)
    st.metric("Strategy", nifty_strategy)

with col2:
    st.header("📉 BANKNIFTY Dashboard")
    bank_data = nse_optionchain_scrapper("BANKNIFTY")
    bank_pcr, bank_expiry = extract_pcr(bank_data)
    bank_prices = [55700, 55680, 55650, 55620, 55600, 55580, 55550]  # Replace with live feed
    bank_ema_signal = get_ema_signal(bank_prices)
    bank_strategy = get_strategy(bank_pcr, bank_ema_signal)
    st.metric("Expiry", bank_expiry)
    st.metric("PCR", round(bank_pcr, 2))
    st.metric("EMA Signal", bank_ema_signal)
    st.metric("Strategy", bank_strategy)

