import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# ------------------ CONFIG ------------------

st.set_page_config(page_title="3-Min OI & Futures Chart", layout="wide")
SPOT_FALLBACK = {"NIFTY": 25050.55, "BANKNIFTY": 55698.50}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/option-chain"
}

# ------------------ FUNCTIONS ------------------

@st.cache_data(ttl=60)
def fetch_option_chain(symbol: str):
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    res = session.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    records = res.json()["records"]
    df = pd.json_normalize(records["data"])
    df["expiryDate"] = pd.to_datetime(df["expiryDate"], format="%d-%b-%Y")
    spot = records.get("underlyingValue", SPOT_FALLBACK[symbol])
    return df, spot

@st.cache_data(ttl=60)
def fetch_futures_price(symbol: str) -> float:
    ticker_map = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK"}
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker_map[symbol]}"
    resp = requests.get(url, timeout=5)
    data = resp.json().get("quoteResponse", {}).get("result", [])
    if data:
        return float(data[0]["regularMarketPrice"])
    return SPOT_FALLBACK[symbol]

def generate_intraday_3min(symbol: str):
    times = pd.date_range("09:15", "15:30", freq="3T")
    n = len(times)
    ce = np.random.randint(20000, 160000, size=n)
    pe = np.random.randint(20000, 160000, size=n)
    fut = [fetch_futures_price(symbol) for _ in range(n)]
    return pd.DataFrame({
        "Time": times.strftime("%H:%M"),
        "CE_OI": ce,
        "PE_OI": pe,
        "Futures": fut
    })

# ------------------ MAIN ------------------

def main():
    st.title("📊 NIFTY/BANKNIFTY: ΔOI Bar & 3-Min Intraday Chart")

    # 1) Select index & fetch option chain
    symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    df, spot = fetch_option_chain(symbol)
    if df.empty:
        st.error("Failed to load option chain.")
        return

    # 2) Choose expiry
    expiries = sorted(df["expiryDate"].dt.date.unique())
    expiry_date = st.selectbox(
        "Select Expiry",
        options=expiries,
        format_func=lambda d: d.strftime("%d-%m-%Y")
    )
    df_exp = df[df["expiryDate"].dt.date == expiry_date]

    # 3) Compute total ΔOI (CE & PE)
    ce_change = df_exp["CE.changeinOpenInterest"].fillna(0).sum()
    pe_change = df_exp["PE.changeinOpenInterest"].fillna(0).sum()
    ce_k, pe_k = ce_change/1e3, pe_change/1e3

    # 4) Generate intraday 3-min data
    df_intraday = generate_intraday_3min(symbol)
    last_time = df_intraday["Time"].iloc[-1]

    # 5) Caption
    st.markdown(f"**As of {last_time}  Expiry {expiry_date.strftime('%d-%m-%Y')}**")

    # 6) Layout: bar + line
    left, right = st.columns([1, 2])

    # Left: ΔOI Bar
    with left:
        bar_fig = go.Figure([
            go.Bar(name="CALL ΔOI", x=["CALL"], y=[ce_k], marker_color="green"),
            go.Bar(name="PUT ΔOI",  x=["PUT"],  y=[pe_k], marker_color="red")
        ])
        bar_fig.update_layout(
            template="plotly_dark",
            title="Total ΔOI (in K)",
            yaxis_title="ΔOI (K)",
            height=350, margin=dict(t=40, b=30)
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    # Right: 3-Min Intraday Line
    with right:
        line_fig = go.Figure()
        line_fig.add_trace(go.Scatter(
            x=df_intraday["Time"], y=df_intraday["CE_OI"],
            mode="lines+markers", name="CE OI",
            line=dict(color="green"), marker=dict(size=6)
        ))
        line_fig.add_trace(go.Scatter(
            x=df_intraday["Time"], y=df_intraday["PE_OI"],
            mode="lines+markers", name="PE OI",
            line=dict(color="red"), marker=dict(size=6)
        ))
        line_fig.add_trace(go.Scatter(
            x=df_intraday["Time"], y=df_intraday["Futures"],
            mode="lines+markers", name="Futures",
            line=dict(color="yellow", dash="dash"), marker=dict(size=6),
            yaxis="y2"
        ))
        line_fig.update_layout(
            template="plotly_dark",
            title="3-Minute Intraday OI & Futures",
            xaxis_title="Time (HH:MM)",
            yaxis=dict(title="Open Interest"),
            yaxis2=dict(
                title="Futures Price",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            height=500, margin=dict(t=50, b=40)
        )
        st.plotly_chart(line_fig, use_container_width=True)


if __name__ == "__main__":
    main()
