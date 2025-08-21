import streamlit as st
import pandas as pd
import requests
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Exact Match Change in OI", layout="wide")

SPOT_FALLBACK = {"NIFTY": 25050.55, "BANKNIFTY": 55698.50}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

# ---------------- DATA ----------------
@st.cache_data(ttl=60)
def fetch_futures_price(symbol: str) -> float:
    ticker_map = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK"}
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker_map[symbol]}"
    try:
        r = requests.get(url, timeout=5)
        result = r.json().get("quoteResponse", {}).get("result", [])
        if result:
            return float(result[0]["regularMarketPrice"])
    except:
        pass
    return SPOT_FALLBACK[symbol]

@st.cache_data(ttl=60)
def generate_intraday(symbol: str):
    # Replace with your REAL ΔOI feed here
    times = pd.date_range("09:15", "15:15", freq="3T")
    n = len(times)
    ce = np.random.randint(-40000, 160000, size=n)
    pe = np.random.randint(-40000, 160000, size=n)
    fut = [fetch_futures_price(symbol) + np.random.uniform(-20, 20) for _ in range(n)]
    return pd.DataFrame({
        "Time": times.strftime("%H:%M"),
        "CE_DeltaOI": ce,
        "PE_DeltaOI": pe,
        "Futures": fut
    })

# ---------------- PLOT ----------------
def make_exact_match_chart(df):
    last_time = df["Time"].iloc[-1]
    last_ce = df["CE_DeltaOI"].iloc[-1]

    fig = go.Figure()

    # CE line — turquoise
    fig.add_trace(go.Scatter(
        x=df["Time"],
        y=df["CE_DeltaOI"],
        mode="lines",
        name="CE ΔOI",
        line=dict(color="cyan", width=2, shape="spline"),
        connectgaps=False
    ))
    # Last CE marker
    fig.add_trace(go.Scatter(
        x=[last_time],
        y=[last_ce],
        mode="markers",
        name="CE Last",
        marker=dict(color="cyan", size=8)
    ))
    # PE line — red
    fig.add_trace(go.Scatter(
        x=df["Time"],
        y=df["PE_DeltaOI"],
        mode="lines",
        name="PE ΔOI",
        line=dict(color="red", width=2, shape="spline"),
        connectgaps=False
    ))
    # Futures — black dashed
    fig.add_trace(go.Scatter(
        x=df["Time"],
        y=df["Futures"],
        mode="lines",
        name="Futures",
        line=dict(color="black", width=2, dash="dash", shape="spline"),
        yaxis="y2",
        connectgaps=False
    ))

    tick_vals = df["Time"][:: max(1, len(df)//8)]
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

# ---------------- APP ----------------
def main():
    st.title("📊 Exact Match — Change in OI")
    symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    df = generate_intraday(symbol)
    fig = make_exact_match_chart(df)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
