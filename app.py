# app.py
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from datetime import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="NIFTY & BANKNIFTY — Change in OI", layout="wide")

# ---------- SETTINGS ----------
SPOT_FALLBACK = {"NIFTY": 25050.55, "BANKNIFTY": 55698.50}
Y1_RANGE = (-40000, 160000)  # ΔOI fixed range
FUT_PAD   = {"NIFTY": 80, "BANKNIFTY": 200}  # Futures axis padding

# ---------- LIVE FUTURES FETCH ----------
@st.cache_data(ttl=60)
def fetch_futures_price(symbol: str) -> float:
    ticker_map = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK"}
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker_map[symbol]}"
    try:
        r = requests.get(url, timeout=5)
        res = r.json().get("quoteResponse", {}).get("result", [])
        if res:
            return float(res[0]["regularMarketPrice"])
    except Exception:
        pass
    return SPOT_FALLBACK[symbol]

# ---------- SAMPLE ΔOI DATA (replace with live feed) ----------
@st.cache_data(ttl=60)
def generate_intraday_3min(symbol: str, base_future: float) -> pd.DataFrame:
    times = pd.date_range("09:15", "15:15", freq="3T")
    n = len(times)
    ce_delta = np.random.randint(Y1_RANGE[0], Y1_RANGE[1], size=n)
    pe_delta = np.random.randint(Y1_RANGE[0], Y1_RANGE[1], size=n)
    fut = base_future + np.cumsum(np.random.normal(0, 2, size=n))
    return pd.DataFrame({
        "Time": times.strftime("%H:%M"),
        "CE_DeltaOI": ce_delta,
        "PE_DeltaOI": pe_delta,
        "Futures": fut
    })

# ---------- PLOT BUILDER ----------
def make_change_in_oi_chart(df: pd.DataFrame, symbol: str, live_fut: float) -> go.Figure:
    last_time = df["Time"].iloc[-1]
    last_ce   = df["CE_DeltaOI"].iloc[-1]
    pad = FUT_PAD[symbol]
    y2_min, y2_max = live_fut - pad, live_fut + pad

    fig = go.Figure()

    # CE line
    fig.add_trace(go.Scatter(
        x=df["Time"], y=df["CE_DeltaOI"],
        mode="lines", name="CE ΔOI",
        line=dict(color="#00CED1", width=2, shape="spline")
    ))
    fig.add_trace(go.Scatter(
        x=[last_time], y=[last_ce],
        mode="markers", name="CE Last",
        marker=dict(color="#00CED1", size=8),
        showlegend=False
    ))
    # PE line
    fig.add_trace(go.Scatter(
        x=df["Time"], y=df["PE_DeltaOI"],
        mode="lines", name="PE ΔOI",
        line=dict(color="#FF4136", width=2, shape="spline")
    ))
    # Futures (secondary axis)
    fig.add_trace(go.Scatter(
        x=df["Time"], y=df["Futures"],
        mode="lines", name="Futures",
        line=dict(color="#000000", width=2, dash="dash", shape="spline"),
        yaxis="y2"
    ))

    step = max(1, len(df) // 8)
    tick_vals = df["Time"][::step]

    fig.update_layout(
        title="Change in OI",
        template="plotly_white",
        xaxis=dict(title="Time", tickmode="array", tickvals=tick_vals),
        yaxis=dict(title="ΔOI (K)", range=list(Y1_RANGE), zeroline=True, zerolinecolor="rgba(0,0,0,0.25)"),
        yaxis2=dict(title="Futures Price", range=[y2_min, y2_max], overlaying="y", side="right", showgrid=False),
        legend=dict(y=0.5, traceorder="reversed"),
        margin=dict(l=60, r=60, t=50, b=40)
    )
    return fig

# ---------- PANEL RENDER ----------
def render_panel(symbol: str):
    live_fut = fetch_futures_price(symbol)
    df = generate_intraday_3min(symbol, live_fut)
    fig = make_change_in_oi_chart(df, symbol, live_fut)
    as_of = datetime.now().strftime("%H:%M")
    st.markdown(f"**{symbol} — As of {as_of}**")
    st.plotly_chart(fig, use_container_width=True)

# ---------- MAIN APP ----------
def main():
    st.title("📊 Change in OI — NIFTY & BANKNIFTY")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_panel("NIFTY")
    with col2:
        render_panel("BANKNIFTY")

if __name__ == "__main__":
    main()
