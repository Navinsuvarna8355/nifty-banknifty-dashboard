import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="NIFTY/BANKNIFTY Dashboard", layout="wide")

# ------------------ CONFIG ------------------
INDEX = st.selectbox("Choose Index", ["NIFTY", "BANKNIFTY"])
EXPIRY = "21-Aug-2025" if INDEX == "NIFTY" else "28-Aug-2025"
SPOT_FALLBACK = 25050.55 if INDEX == "NIFTY" else 55698.50

# ------------------ FETCH OPTION CHAIN ------------------
@st.cache_data(ttl=60)
def fetch_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        df = pd.DataFrame(data["records"]["data"])
        spot = data["records"].get("underlyingValue", SPOT_FALLBACK)
        return df, spot
    except Exception as e:
        st.error(f"❌ Failed to fetch option chain: {e}")
        return pd.DataFrame(), SPOT_FALLBACK

df_raw, spot_price = fetch_option_chain(INDEX)
st.metric(f"{INDEX} Spot Price", f"{spot_price:.2f}")

# ------------------ EXTRACT OI CHANGE ------------------
def extract_oi_change(df):
    rows = []
    for row in df.itertuples():
        ce = getattr(row, "CE", {}) or {}
        pe = getattr(row, "PE", {}) or {}
        strike = ce.get("strikePrice") or pe.get("strikePrice")
        ce_chg = ce.get("changeinOpenInterest", 0)
        pe_chg = pe.get("changeinOpenInterest", 0)
        if strike is not None:
            rows.append({"Strike": strike, "CE_ChgOI": ce_chg, "PE_ChgOI": pe_chg})
    return pd.DataFrame(rows)

df_chg = extract_oi_change(df_raw)
if "Strike" in df_chg.columns and not df_chg.empty:
    df_chg = df_chg.dropna().sort_values("Strike")
else:
    st.warning("⚠️ No valid OI data found. Check NSE API or fallback logic.")
    df_chg = pd.DataFrame(columns=["Strike", "CE_ChgOI", "PE_ChgOI"])

# ------------------ PCR & EMA ------------------
def calculate_pcr(df):
    total_pe = df["PE_ChgOI"].sum()
    total_ce = df["CE_ChgOI"].sum()
    return round(total_pe / total_ce, 2) if total_ce else None

pcr = calculate_pcr(df_chg)

@st.cache_data(ttl=300)
def fetch_price_history(sym):
    return pd.Series([spot_price - i * 10 for i in range(30)][::-1])

def get_ema_signal(prices):
    ema_fast = prices.ewm(span=9).mean()
    ema_slow = prices.ewm(span=21).mean()
    return "BULLISH" if ema_fast.iloc[-1] > ema_slow.iloc[-1] else "BEARISH"

prices = fetch_price_history(INDEX)
ema_signal = get_ema_signal(prices)

def get_strategy(pcr_val, ema_val):
    if pcr_val and pcr_val > 1.2 and ema_val == "BULLISH":
        return "BUY CALL"
    if pcr_val and pcr_val < 0.8 and ema_val == "BEARISH":
        return "BUY PUT"
    return "SIDEWAYS"

strategy = get_strategy(pcr, ema_signal)

# ------------------ DISPLAY STRATEGY ------------------
st.subheader("📊 Strategy Insights")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Expiry", EXPIRY)
c2.metric("PCR", pcr)
c3.metric("EMA Signal", ema_signal)
c4.metric("Strategy", strategy)

# ------------------ STRIKE-WISE CHARTS ------------------
st.subheader("📈 Strike-wise OI Overview")
col_left, col_right = st.columns([1, 2])

with col_left:
    tot_ce = df_chg["CE_ChgOI"].sum() / 100000
    tot_pe = df_chg["PE_ChgOI"].sum() / 100000
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(x=["CALL"], y=[tot_ce], name="CALL", marker_color="green"))
    bar_fig.add_trace(go.Bar(x=["PUT"], y=[tot_pe], name="PUT", marker_color="red"))
    bar_fig.update_layout(
        template="plotly_dark",
        title="Change in OI (in Lakhs)",
        xaxis_title="Option Type",
        yaxis_title="OI Change (L)",
        height=400,
        margin=dict(l=30, r=30, t=40, b=30),
    )
    st.plotly_chart(bar_fig, use_container_width=True)

with col_right:
    max_oi = max(df_chg["CE_ChgOI"].max(), df_chg["PE_ChgOI"].max()) if not df_chg.empty else 1
    strike_fig = go.Figure()
    strike_fig.add_trace(go.Scatter(
        x=df_chg["Strike"], y=df_chg["CE_ChgOI"],
        mode="lines+markers", name="CE",
        line=dict(color="green", width=2), marker=dict(size=5)
    ))
    strike_fig.add_trace(go.Scatter(
        x=df_chg["Strike"], y=df_chg["PE_ChgOI"],
        mode="lines+markers", name="PE",
        line=dict(color="red", width=2), marker=dict(size=5)
    ))
    strike_fig.add_trace(go.Scatter(
        x=df_chg["Strike"], y=[spot_price] * len(df_chg),
        mode="lines", name="Future",
        line=dict(color="gray", dash="dot", width=1),
        opacity=0.5,
        yaxis="y2"
    ))
    strike_fig.update_layout(
        template="plotly_dark",
        title="Change in OI vs Strike",
        xaxis_title="Strike Price",
        yaxis=dict(title="OI Change", side="left"),
        yaxis2=dict(
            title="Future Price",
            overlaying="y",
            side="right",
            range=[spot_price - 200, spot_price + 200],
            showgrid=False,
        ),
        shapes=[dict(
            type="line",
            x0=spot_price, x1=spot_price,
            y0=0, y1=max_oi,
            line=dict(color="yellow", dash="dash"),
        )],
        annotations=[dict(
            x=spot_price, y=max_oi * 0.15,
            text=f"Spot @ {spot_price:.2f}",
            showarrow=False, font=dict(color="yellow"), xanchor="left"
        )],
        legend=dict(x=0.01, y=0.99),
        height=550,
        margin=dict(l=50, r=50, t=50, b=50),
    )
    st.plotly_chart(strike_fig, use_container_width=True)

# ------------------ INTRADAY TIME-SERIES CHART ------------------
st.subheader("⏱️ Intraday OI Tracker")

def generate_intraday_data():
    times = pd.date_range("09:15", "15:30", freq="15min").strftime("%H:%M")
    ce = np.random.randint(20000, 160000, len(times))
    pe = np.random.randint(20000, 160000, len(times))
    fut = np.linspace(spot_price - 50, spot_price + 50, len(times))
    return pd.DataFrame({"Time": times, "CE_OI": ce, "PE_OI": pe, "Futures": fut})

df_intraday = generate_intraday_data()

fig_intraday = go.Figure()
fig_intraday.add_trace(go.Scatter(
    x=df_intraday["Time"], y=df
