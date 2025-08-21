import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

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
        return pd.DataFrame(data["records"]["data"]), data["records"]["underlyingValue"]
    except:
        return pd.DataFrame(), SPOT_FALLBACK

df_raw, spot_price = fetch_option_chain(INDEX)

st.metric(f"{INDEX} Spot Price", f"{spot_price:.2f}")

# ------------------ Extract OI Change ------------------
def extract_oi_change(df):
    rows = []
    for row in df.itertuples():
        ce = getattr(row, "CE", {}) or {}
        pe = getattr(row, "PE", {}) or {}

        if not isinstance(ce, dict): ce = {}
        if not isinstance(pe, dict): pe = {}

        strike = ce.get("strikePrice") or pe.get("strikePrice")
        ce_chg = ce.get("changeinOpenInterest", 0)
        pe_chg = pe.get("changeinOpenInterest", 0)
        fut = spot_price

        if strike:
            rows.append({
                "Strike": strike,
                "CE_ChgOI": ce_chg,
                "PE_ChgOI": pe_chg,
                "Future": fut
            })
    return pd.DataFrame(rows)

df_chg = extract_oi_change(df_raw).dropna().sort_values("Strike")

# ------------------ PCR & EMA ------------------
def calculate_pcr(df):
    total_pe = df["PE_ChgOI"].sum()
    total_ce = df["CE_ChgOI"].sum()
    return round(total_pe / total_ce, 2) if total_ce else None

pcr = calculate_pcr(df_chg)

@st.cache_data(ttl=300)
def fetch_price_history(index):
    return pd.Series([spot_price - i*10 for i in range(30)][::-1])

def get_ema_signal(prices):
    ema_fast = prices.ewm(span=9).mean()
    ema_slow = prices.ewm(span=21).mean()
    return "BULLISH" if ema_fast.iloc[-1] > ema_slow.iloc[-1] else "BEARISH"

prices = fetch_price_history(INDEX)
ema_signal = get_ema_signal(prices)

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

# ------------------ BAR CHART: Total Change in OI ------------------
st.subheader("📊 Total Change in OI")
total_ce_chg = df_chg["CE_ChgOI"].sum() / 100000
total_pe_chg = df_chg["PE_ChgOI"].sum() / 100000

st.plotly_chart(
    go.Figure(data=[
        go.Bar(name="CALL", x=["CALL"], y=[total_ce_chg], marker_color="turquoise"),
        go.Bar(name="PUT", x=["PUT"], y=[total_pe_chg], marker_color="red")
    ]).update_layout(title="Change in OI (in Lakhs)", yaxis_title="OI Change (L)")
)

# ------------------ LINE CHART: CE/PE/Future Trend ------------------
st.subheader("📈 CE/PE/Futures Trend")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_chg["Strike"], y=df_chg["CE_ChgOI"], mode="lines+markers", name="CE", line=dict(color="turquoise")))
fig.add_trace(go.Scatter(x=df_chg["Strike"], y=df_chg["PE_ChgOI"], mode="lines+markers", name="PE", line=dict(color="red")))
fig.add_trace(go.Scatter(x=df_chg["Strike"], y=df_chg["Future"], mode="lines", name="Future", line=dict(color="black", dash="dot"), yaxis="y2"))

fig.update_layout(
    title="Change in OI vs Strike",
    xaxis_title="Strike Price",
    yaxis=dict(title="OI Change"),
    yaxis2=dict(title="Future Price", overlaying="y", side="right", showgrid=False),
    legend=dict(x=0.01, y=0.99),
    margin=dict(l=40, r=40, t=40, b=40),
    height=400
)

st.plotly_chart(fig, use_container_width=True)
