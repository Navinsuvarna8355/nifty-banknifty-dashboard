import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime
import plotly.graph_objects as go

# ------------------ CONFIG ------------------

st.set_page_config(page_title="Change in OI Clone", layout="wide")

SPOT_FALLBACK = {"NIFTY": 25050.55, "BANKNIFTY": 55698.50}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/option-chain"
}


# ------------------ DATA FETCHING ------------------

@st.cache_data(ttl=60)
def fetch_option_chain(symbol: str):
    session = requests.Session()
    for attempt in (1, 2):
        try:
            # Kick off cookies
            session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
            url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
            res = session.get(url, headers=HEADERS, timeout=10)

            if res.status_code != 200:
                if attempt == 1:
                    time.sleep(1)
                    continue
                else:
                    st.warning(f"⚠️ NSE returned {res.status_code}. Using fallback.")
                    return pd.DataFrame(), SPOT_FALLBACK[symbol]

            data = res.json()
            if "records" not in data or "data" not in data["records"]:
                st.warning("⚠️ Unexpected JSON shape. Using fallback.")
                return pd.DataFrame(), SPOT_FALLBACK[symbol]

            df = pd.json_normalize(data["records"]["data"])
            df["expiryDate"] = pd.to_datetime(df["expiryDate"], format="%d-%b-%Y")
            spot = data["records"].get("underlyingValue", SPOT_FALLBACK[symbol])
            return df, spot

        except Exception as e:
            if attempt == 2:
                st.warning(f"⚠️ Error fetching option chain: {e}. Using fallback.")
                return pd.DataFrame(), SPOT_FALLBACK[symbol]
            time.sleep(1)

    return pd.DataFrame(), SPOT_FALLBACK[symbol]


@st.cache_data(ttl=60)
def fetch_futures_price(symbol: str) -> float:
    ticker_map = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK"}
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker_map[symbol]}"
    try:
        resp = requests.get(url, timeout=5)
        result = resp.json().get("quoteResponse", {}).get("result", [])
        if result:
            return float(result[0]["regularMarketPrice"])
    except:
        pass
    return SPOT_FALLBACK[symbol]


@st.cache_data(ttl=60)
def generate_intraday_3min(symbol: str):
    times = pd.date_range("09:15", "15:30", freq="3T")
    n = len(times)
    # Here we simulate ΔOI; replace with real ΔOI if you have it
    ce = np.random.randint(-40000, 160000, size=n)
    pe = np.random.randint(-40000, 160000, size=n)
    fut = [fetch_futures_price(symbol) for _ in range(n)]

    return pd.DataFrame({
        "Time": times.strftime("%H:%M"),
        "CE_OI": ce,
        "PE_OI": pe,
        "Futures": fut
    })


# ------------------ PLOTLY LAYOUT FUNCTION ------------------

def make_change_in_oi_lookalike(df_intraday: pd.DataFrame) -> go.Figure:
    last_time = df_intraday["Time"].iloc[-1]
    last_ce   = df_intraday["CE_OI"].iloc[-1]

    fig = go.Figure()

    # 1) Turquoise CE ΔOI line
    fig.add_trace(go.Scatter(
        x=df_intraday["Time"],
        y=df_intraday["CE_OI"],
        mode="lines",
        name="CE ΔOI",
        line=dict(color="turquoise", width=2)
    ))

    # 2) Highlight last CE point
    fig.add_trace(go.Scatter(
        x=[last_time],
        y=[last_ce],
        mode="markers",
        name="CE Last",
        marker=dict(color="turquoise", size=8, symbol="circle")
    ))

    # 3) Red PE ΔOI line
    fig.add_trace(go.Scatter(
        x=df_intraday["Time"],
        y=df_intraday["PE_OI"],
        mode="lines",
        name="PE ΔOI",
        line=dict(color="red", width=2)
    ))

    # 4) Black dashed Futures line on secondary axis
    fig.add_trace(go.Scatter(
        x=df_intraday["Time"],
        y=df_intraday["Futures"],
        mode="lines",
        name="Futures",
        line=dict(color="black", width=2, dash="dash"),
        yaxis="y2"
    ))

    # 5) Configure axes, title, legend, layout
    tick_vals = df_intraday["Time"][:: max(1, len(df_intraday)//8)]
    fig.update_layout(
        title="Change in OI",
        xaxis=dict(
            title="Time",
            tickmode="array",
            tickvals=tick_vals
        ),
        yaxis=dict(
            title="ΔOI",
            range=[-40000, 160000]
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
    st.title("📈 Change in OI Clone Dashboard")

    symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    df_chain, spot = fetch_option_chain(symbol)

    if df_chain.empty:
        st.error("Option-chain data unavailable. Displaying only intraday ΔOI chart.")

    df_intraday = generate_intraday_3min(symbol)
    fig = make_change_in_oi_lookalike(df_intraday)
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
