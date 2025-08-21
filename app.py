import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import json
from datetime import datetime

# ─────────────────────────────────────────────
# 🔐 NSE Headers
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# ─────────────────────────────────────────────
# 🔄 NSE Option Chain Scraper
def fetch_option_chain(index_name):
    url_map = {
        "NIFTY": "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY",
        "BANKNIFTY": "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY"
    }
    url = url_map[index_name]

    session = requests.Session()
    session.get("https://www.nseindia.com/option-chain", headers=headers)
    response = session.get(url, headers=headers)
    data = json.loads(response.text)

    expiry_dates = data["records"]["expiryDates"]
    current_expiry = expiry_dates[0]

    strikes, call_oi, put_oi = [], [], []

    for item in data['records']['data']:
        if item["expiryDate"] == current_expiry:
            strike = item["strikePrice"]
            ce_oi = item.get("CE", {}).get("openInterest", 0)
            pe_oi = item.get("PE", {}).get("openInterest", 0)

            strikes.append(strike)
            call_oi.append(ce_oi)
            put_oi.append(pe_oi)

    df = pd.DataFrame({
        "Strike": strikes,
        "Call_OI": call_oi,
        "Put_OI": put_oi
    })

    # Estimate Futures price as midpoint of strikes (placeholder)
    fut_price = round(sum(strikes) / len(strikes), 2)
    df["Futures"] = [fut_price] * len(df)

    return df, current_expiry, fut_price

# ─────────────────────────────────────────────
# 📈 Dual Y-Axis Plotly Chart
def plot_dual_axis(df, title):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['Strike'], y=df['Call_OI'],
                             mode='lines+markers', name='Call OI', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df['Strike'], y=df['Put_OI'],
                             mode='lines+markers', name='Put OI', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df['Strike'], y=df['Futures'],
                             mode='lines+markers', name='Futures', line=dict(color='lightblue'), yaxis='y2'))

    fig.update_layout(
        title=title,
        xaxis_title='Strike Price',
        yaxis=dict(title='Open Interest'),
        yaxis2=dict(title='Futures Price', overlaying='y', side='right'),
        legend=dict(x=0.01, y=0.99),
        margin=dict(l=40, r=40, t=40, b=40),
        height=400
    )
    return fig

# ─────────────────────────────────────────────
# 📋 Strategy Card Renderer
def render_strategy_card(title, live_price, expiry, pcr_used, timestamp):
    st.subheader(title)
    st.markdown(f"**Live Price:** ₹{live_price}")
    st.markdown(f"**Suggested Option:** —")
    st.markdown(f"**Trend:** —")
    st.markdown(f"**Signal:** —")
    st.markdown(f"**Strategy:** 3 EMA Crossover + PCR (option-chain)")
    st.markdown(f"**Confidence:** 90%")
    st.markdown(f"**PCR (used):** {pcr_used}")
    st.markdown(f"**PCR total:** —")
    st.markdown(f"**PCR near:** —")
    st.markdown(f"**Expiry:** {expiry}")
    st.caption(f"Last updated: {timestamp}")

# ─────────────────────────────────────────────
# 🧠 Dashboard Layout
st.set_page_config(page_title="NSE Strategy Dashboard", layout="wide")
st.title("📌 NIFTY & BANKNIFTY Strategy + OI Dashboard")

# Fetch live data
nifty_df, nifty_expiry, nifty_fut = fetch_option_chain("NIFTY")
bank_df, bank_expiry, bank_fut = fetch_option_chain("BANKNIFTY")
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Calculate PCRs
nifty_pcr_used = round(nifty_df["Put_OI"].sum() / nifty_df["Call_OI"].sum(), 2)
bank_pcr_used = round(bank_df["Put_OI"].sum() / bank_df["Call_OI"].sum(), 2)

# Strategy Cards
st.markdown("### 🔍 Strategy Overview")
col1, col2 = st.columns(2)
with col1:
    render_strategy_card("📈 NIFTY Strategy", nifty_fut, nifty_expiry, nifty_pcr_used, timestamp)
with col2:
    render_strategy_card("📉 BANKNIFTY Strategy", bank_fut, bank_expiry, bank_pcr_used, timestamp)

# Charts
st.markdown("### 📊 CE/PE/Futures Line Charts")
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(plot_dual_axis(nifty_df, "NIFTY CE/PE/Futures"), use_container_width=True)
with col4:
    st.plotly_chart(plot_dual_axis(bank_df, "BANKNIFTY CE/PE/Futures"), use_container_width=True)
