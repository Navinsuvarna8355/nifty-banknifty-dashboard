import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import numpy as np
import time
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

# ------------------ FETCH OPTION CHAIN (with retry + fallback) ------------------

@st.cache_data(ttl=60)
def fetch_option_chain(symbol: str):
    session = requests.Session()
    for attempt in (1, 2):
        try:
            # 1) hit homepage to set cookies
            session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
            # 2) fetch the JSON
            url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
            res = session.get(url, headers=HEADERS, timeout=10)
            # if status not OK, retry once more
            if res.status_code != 200:
                if attempt == 1:
                    time.sleep(1)
                    continue
                else:
                    st.warning(f"⚠️ NSE returned {res.status_code}. Using fallback data.")
                    return pd.DataFrame(), SPOT_FALLBACK[symbol]
            data = res.json()
            # validate structure
            if "records" not in data or "data" not in data["records"]:
                st.warning("⚠️ Unexpected JSON shape. Using fallback.")
                return pd.DataFrame(), SPOT_FALLBACK[symbol]
            records = data["records"]["data"]
            df = pd.json_normalize(records)
            df["expiryDate"] = pd.to_datetime(df["expiryDate"], format="%d-%b-%Y")
            spot = data["records"].get("underlyingValue", SPOT_FALLBACK[symbol])
            return df, spot
        except Exception as e:
            if attempt == 2:
                st.warning(f"⚠️ Error fetching option chain: {e}. Using fallback.")
                return pd.DataFrame(), SPOT_FALLBACK[symbol]
            time.sleep(1)
    # should never reach here
    return pd.DataFrame(), SPOT_FALLBACK[symbol]


# ------------------ FETCH LIVE FUTURES PRICE ------------------

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


# ------------------ INTRADAY 3-MIN DATA GENERATOR ------------------

@st.cache_data(ttl=60)
def generate_intraday_3min(symbol: str):
    times = pd.date_range("09:15", "15:30", freq="3T")
    n = len(times)
    ce = np.random.randint(20000, 160000, size=n)   # replace with real CE OI
    pe = np.random.randint(20000, 160000, size=n)   # replace with real PE OI
    fut = [fetch_futures_price(symbol) for _ in range(n)]
    return pd.DataFrame({
        "Time": times.strftime("%H:%M"),
        "CE_OI": ce,
        "PE_OI": pe,
        "Futures": fut
    })


# ------------------ MAIN ------------------

def main():
    st.title("📊 NIFTY/BANKNIFTY: ΔOI & 3-Min Intraday Chart")

    # 1) Select index
    symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])

    # 2) Fetch option chain + spot
    df, spot = fetch_option_chain(symbol)
    if df.empty:
        st.error("No option-chain data. Displaying only intraday chart.")
    else:
        # 3) Choose expiry
        expiries = sorted(df["expiryDate"].dt.date.unique())
        expiry_date = st.selectbox(
            "Select Expiry", options=expiries,
            format_func=lambda d: d.strftime("%d-%m-%Y")
        )
        df_exp = df[df["expiryDate"].dt.date == expiry_date]

        # 4) Compute total ΔOI in K
        ce_k = df_exp["CE.changeinOpenInterest"].fillna(0).sum() / 1e3
        pe_k = df_exp["PE.changeinOpenInterest"].fillna(0).sum() / 1e3

        # 5) Caption
        now = datetime.now().strftime("%H:%M")
        st.markdown(f"**As of {now}  Expiry {expiry_date.strftime('%d-%m-%Y')}**")

        # 6) Bar + 3-min line layout
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
        df_intraday = generate_intraday_3min(symbol)
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
                    overlaying="y", side="right", showgrid=False
                ),
                height=500, margin=dict(t=50, b=40)
            )
            st.plotly_chart(line_fig, use_container_width=True)

    # Always show intraday data even if option chain failed
    if df.empty:
        st.subheader("⏱️ Intraday OI & Futures (3-Min Interval)")
        df_intraday = generate_intraday_3min(symbol)
        intraday_fig = go.Figure([
            go.Scatter(x=df_intraday["Time"], y=df_intraday["CE_OI"],
                       mode="lines+markers", name="CE OI", line=dict(color="green")),
            go.Scatter(x=df_intraday["Time"], y=df_intraday["PE_OI"],
                       mode="lines+markers", name="PE OI", line=dict(color="red")),
            go.Scatter(x=df_intraday["Time"], y=df_intraday["Futures"],
                       mode="lines+markers", name="Futures", line=dict(color="yellow", dash="dash"),
                       yaxis="y2")
        ])
        intraday_fig.update_layout(
            template="plotly_dark",
            xaxis_title="Time (HH:MM)",
            yaxis=dict(title="OI"),
            yaxis2=dict(title="Futures", overlaying="y", side="right", showgrid=False),
            height=450
        )
        st.plotly_chart(intraday_fig, use_container_width=True)


if __name__ == "__main__":
    main()
