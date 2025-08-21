import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="NIFTY & BANKNIFTY Dashboard", layout="wide")

SPOT_FALLBACKS = {"NIFTY": 25050.55, "BANKNIFTY": 55698.50}
EXPIRIES = {"NIFTY": "21-Aug-2025", "BANKNIFTY": "28-Aug-2025"}

@st.cache_data(ttl=60)
def fetch_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        df = pd.DataFrame(data["records"]["data"])
        spot = data["records"].get("underlyingValue", SPOT_FALLBACKS[symbol])
        return df, spot
    except Exception as e:
        st.error(f"❌ Failed to fetch {symbol} option chain: {e}")
        return pd.DataFrame(), SPOT_FALLBACKS[symbol]

def extract_oi_change(df):
    rows = []
    for _, row in df.iterrows():
        ce = row.get("CE", {}) if isinstance(row.get("CE", {}), dict) else {}
        pe = row.get("PE", {}) if isinstance(row.get("PE", {}), dict) else {}
        strike = ce.get("strikePrice") or pe.get("strikePrice")
        ce_chg = ce.get("changeinOpenInterest", 0)
        pe_chg = pe.get("changeinOpenInterest", 0)
        if strike is not None:
            rows.append({"Strike": strike, "CE_ChgOI": ce_chg, "PE_ChgOI": pe_chg})
    return pd.DataFrame(rows)

def calculate_pcr(df):
    total_pe = df["PE_ChgOI"].sum()
    total_ce = df["CE_ChgOI"].sum()
    return round(total_pe / total_ce, 2) if total_ce else None

@st.cache_data(ttl=300)
def fetch_price_history(sym, spot_price):
    return pd.Series([spot_price - i * 10 for i in range(30)][::-1])

def get_ema_signal(prices):
    ema_fast = prices.ewm(span=9).mean()
    ema_slow = prices.ewm(span=21).mean()
    return "BULLISH" if ema_fast.iloc[-1] > ema_slow.iloc[-1] else "BEARISH"

def get_strategy(pcr_val, ema_val):
    if pcr_val and pcr_val > 1.2 and ema_val == "BULLISH":
        return "BUY CALL"
    if pcr_val and pcr_val < 0.8 and ema_val == "BEARISH":
        return "BUY PUT"
    return "SIDEWAYS"

def generate_intraday_data(spot_price):
    times = pd.date_range("09:15", "15:30", freq="15min").strftime("%H:%M")
    ce = np.random.randint(20000, 160000, len(times))
    pe = np.random.randint(20000, 160000, len(times))
    fut = np.linspace(spot_price - 50, spot_price + 50, len(times))
    return pd.DataFrame({"Time": times, "CE_OI": ce, "PE_OI": pe, "Futures": fut})

def render_panel(symbol):
    df_raw, spot_price = fetch_option_chain(symbol)
    df_chg = extract_oi_change(df_raw)
    if not df_chg.empty and "Strike" in df_chg.columns:
        df_chg = df_chg.dropna().sort_values("Strike")
    else:
        st.warning(f"⚠️ No valid OI data found for {symbol}.")
        df_chg = pd.DataFrame(columns=["Strike", "CE_ChgOI", "PE_ChgOI"])

    pcr = calculate_pcr(df_chg)
    prices = fetch_price_history(symbol, spot_price)
    ema_signal = get_ema_signal(prices)
    strategy = get_strategy(pcr, ema_signal)

    # METRICS
    st.metric("Expiry", EXPIRIES[symbol])
    st.metric("PCR", pcr)
    st.metric("EMA Signal", ema_signal)
    st.metric("Strategy", strategy)

    # OI Overview Bar
    tot_ce = df_chg["CE_ChgOI"].sum() / 100000
    tot_pe = df_chg["PE_ChgOI"].sum() / 100000
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(x=["CALL"], y=[tot_ce], marker_color="green"))
    bar_fig.add_trace(go.Bar(x=["PUT"], y=[tot_pe], marker_color="red"))
    bar_fig.update_layout(template="plotly_dark", title="Change in OI (in Lakhs)",
                          height=300, margin=dict(l=10, r=10, t=40, b=20))
    st.plotly_chart(bar_fig, use_container_width=True)

    # Strike-wise line plot
    max_oi = max(df_chg["CE_ChgOI"].max(), df_chg["PE_ChgOI"].max()) if not df_chg.empty else 1
    strike_fig = go.Figure()
    strike_fig.add_trace(go.Scatter(x=df_chg["Strike"], y=df_chg["CE_ChgOI"],
                                    mode="lines+markers", name="CE", line=dict(color="green")))
    strike_fig.add_trace(go.Scatter(x=df_chg["Strike"], y=df_chg["PE_ChgOI"],
                                    mode="lines+markers", name="PE", line=dict(color="red")))
    strike_fig.add_trace(go.Scatter(x=df_chg["Strike"], y=[spot_price]*len(df_chg),
                                    mode="lines", name="Future", line=dict(color="gray", dash="dot"),
                                    opacity=0.5, yaxis="y2"))
    strike_fig.update_layout(template="plotly_dark", title="Change in OI vs Strike",
                             yaxis=dict(title="OI Change"),
                             yaxis2=dict(title="Future Price", overlaying="y", side="right",
                                         range=[spot_price - 200, spot_price + 200], showgrid=False),
                             height=400)
    st.plotly_chart(strike_fig, use_container_width=True)

    # Intraday tracker
    df_intraday = generate_intraday_data(spot_price)
    fig_intraday = go.Figure()
    fig_intraday.add_trace(go.Scatter(x=df_intraday["Time"], y=df_intraday["CE_OI"], name="CE OI", line=dict(color="green")))
    fig_intraday.add_trace(go.Scatter(x=df_intraday["Time"], y=df_intraday["PE_OI"], name="PE OI", line=dict(color="red")))
    fig_intraday.add_trace(go.Scatter(x=df_intraday["Time"], y=df_intraday["Futures"], name="Futures", line=dict(color="gray", dash="dash"), yaxis="y2"))
    fig_intraday.update_layout(template="plotly_dark", title="Intraday OI & Futures",
                               yaxis2=dict(title="Futures Price", overlaying="y", side="right"), height=300)
    st.plotly_chart(fig_intraday, use_container_width=True)

# MAIN — 2 columns for 2 indices
col1, col2 = st.columns(2, gap="large")
with col1:
    st.header("NIFTY")
    render_panel("NIFTY")
with col2:
    st.header("BANKNIFTY")
    render_panel("BANKNIFTY")
