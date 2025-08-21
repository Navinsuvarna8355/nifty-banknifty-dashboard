import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import numpy as np
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# ------------------ CONFIG & CONSTANTS ------------------

st.set_page_config(page_title="NIFTY/BANKNIFTY Live Dashboard", layout="wide")

SPOT_FALLBACK = {"NIFTY": 25050.55, "BANKNIFTY": 55698.50}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/option-chain"
}

# ------------------ AUTO-REFRESH EVERY SECOND ------------------

# rerun the script every 1000 ms
st_autorefresh(interval=1000, limit=None, key="live_refresh")

# ------------------ LIVE FUTURES PRICE via requests ------------------

@st.cache_data(ttl=1)
def fetch_futures_price(symbol: str) -> float:
    ticker_map = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK"}
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker_map[symbol]}"
    try:
        data = requests.get(url, timeout=3).json()
        return float(data["quoteResponse"]["result"][0]["regularMarketPrice"])
    except:
        return SPOT_FALLBACK[symbol]

# ------------------ SESSION STATE: ROLLING INTRADAY DATA ------------------

def init_intraday_df():
    return pd.DataFrame(columns=["Time", "CE_OI", "PE_OI", "Futures"])

if "intraday_df" not in st.session_state:
    st.session_state.intraday_df = init_intraday_df()

def append_new_datapoint(symbol: str):
    now = datetime.now().strftime("%H:%M:%S")
    ce = np.random.randint(20000, 160000)       # replace with real CE OI fetch
    pe = np.random.randint(20000, 160000)       # replace with real PE OI fetch
    fut = fetch_futures_price(symbol)
    new_row = pd.DataFrame([{
        "Time": now,
        "CE_OI": ce,
        "PE_OI": pe,
        "Futures": fut
    }])
    # concat instead of append()
    st.session_state.intraday_df = pd.concat(
        [st.session_state.intraday_df, new_row],
        ignore_index=True
    ).tail(100)  # keep last 100 points

# ------------------ MAIN APP ------------------

def main():
    st.title("🚀 NIFTY / BANKNIFTY Live Dashboard (1 sec updates)")

    # 1) Index selector
    symbol = st.selectbox("Choose Index", ["NIFTY", "BANKNIFTY"])

    # 2) Display live futures metric
    live_price = fetch_futures_price(symbol)
    st.metric(f"{symbol} Futures (Live)", f"{live_price:.2f}")

    # 3) Update rolling intraday df
    append_new_datapoint(symbol)
    df_live = st.session_state.intraday_df

    # 4) Plot live-moving intraday chart
    st.subheader("⏱️ Intraday Open Interest & Futures")
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_live["Time"], y=df_live["CE_OI"],
        mode="lines+markers", name="CE OI",
        line=dict(color="green"), marker=dict(size=4)
    ))
    fig.add_trace(go.Scatter(
        x=df_live["Time"], y=df_live["PE_OI"],
        mode="lines+markers", name="PE OI",
        line=dict(color="red"), marker=dict(size=4)
    ))
    fig.add_trace(go.Scatter(
        x=df_live["Time"], y=df_live["Futures"],
        mode="lines", name="Futures Price",
        line=dict(color="yellow", dash="dash"), yaxis="y2"
    ))

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Time",
        yaxis=dict(title="Open Interest"),
        yaxis2=dict(
            title="Futures Price",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=40, r=40, t=60, b=40),
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
