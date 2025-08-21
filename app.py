import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime
import plotly.graph_objects as go

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Clear Change in OI", layout="wide")

# ------------------ SETTINGS ------------------
SPOT_FALLBACK = {"NIFTY": 25050.55, "BANKNIFTY": 55698.50}
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

# ------------------ DATA FETCHING ------------------
@st.cache_data(ttl=60)
def fetch_futures_price(symbol: str) -> float:
    """Fetch live futures price from Yahoo Finance."""
    ticker_map = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK"}
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker_map[symbol]}"
    try:
        r = requests.get(url, timeout=5)
        res = r.json().get("quoteResponse", {}).get("result", [])
        if res:
            return float(res[0]["regularMarketPrice"])
    except:
        pass
    return SPOT_FALLBACK[symbol]

@st.cache_data(ttl=60)
def generate_intraday_3min(symbol: str):
    """Generate 3-minute interval ΔOI + Futures data. Replace with real feed if available."""
    times = pd.date_range("09:15", "15:30", freq="3T")
    n = len(times)
    ce = np.random.randint(-40000, 160000, size=n)   # Simulated CE ΔOI
    pe = np.random.randint(-40000, 160000, size=n)   # Simulated PE ΔOI
    fut = [fetch_futures_price(symbol) + np.random.uniform(-20, 20) for _ in range(n)]
    return pd.DataFrame({
        "Time": times.strftime("%H:%M"),
        "CE_OI": ce,
        "PE_OI": pe,
        "Futures": fut
    })

# ------------------ PLOTLY CHART ------------------
def make_clear_change_in_oi(df_intraday: pd.DataFrame) -> go.Figure:
    last_time = df_intraday["Time"].iloc[-1]
    last_ce   = df_intraday["CE_OI"].iloc[-1]

    fig = go.Figure()

    # CE line – turquoise
    fig.add_trace(go.Scatter(
        x=df_intraday["Time"],
        y=df_intraday["CE_OI"],
        mode="lines",
        name="CE ΔOI",
        line=dict(color="turquoise", width=2, shape="spline"),
        connectgaps=False
    ))

    # Last CE point marker
    fig.add_trace(go.Scatter(
        x=[last_time],
        y=[last_ce],
        mode="markers",
        name="CE Last",
        marker=dict(color="turquoise", size=8)
    ))

    # PE line – red
    fig.add_trace(go.Scatter(
        x=df_intraday["Time"],
        y=df_intraday["PE_OI"],
        mode="lines",
        name="PE ΔOI",
        line=dict(color="red", width=2, shape="spline"),
        connectgaps=False
    ))

    # Futures line – black dashed (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=df_intraday["Time"],
        y=df_intraday["Futures"],
        mode="lines",
        name="Futures",
        line=dict(color="black", width=2, dash="dash", shape="spline"),
        yaxis="y2",
        connectgaps=False
    ))

    # Layout adjustments for clean spacing
    tick_vals = df_intraday["Time"][:: max(1, len(df_intraday)//8)]
    fig.update_layout(
        title="Change in OI",
        xaxis=dict(
            title="Time",
            tickmode="array",
            tickvals=tick_vals
        ),
        yaxis=dict(
            title="ΔOI (K)",
            range=[-40000, 160000],
            zeroline=True,
            zerolinecolor="gray"
        ),
        yaxis2=dict(
            title="Futures Price",
            range=[25100, 25180],
            overlaying="y",
            side="right",
            showgrid=False
        ),
        legend=dict(y=0.5, traceorder="reversed"),
        margin=dict(l=60, r=60, t=50, b=40),
        template="plotly_white"
    )

    return fig

# ------------------ STREAMLIT APP ------------------
def main():
    st.title("📊 Clear & Spaced Change in OI Chart")
    symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    df_intraday = generate_intraday_3min(symbol)
    chart = make_clear_change_in_oi(df_intraday)
    st.plotly_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()
