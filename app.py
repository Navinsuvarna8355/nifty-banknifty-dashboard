# app.py
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

# Fallback spot if NSE API returns nothing
SPOT_FALLBACK = None

# Common headers for NSE requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/option-chain"
}

@st.cache_data(ttl=60, show_spinner=False)
def fetch_option_chain(symbol: str):
    """
    Returns a tuple (df, spot_price) where:
    - df: DataFrame of raw option-chain records
    - spot_price: underlying value or SPOT_FALLBACK
    """
    session = requests.Session()
    try:
        # 1) Preload cookies
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)

        # 2) Fetch option-chain JSON
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        res = session.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()

        records = data["records"]["data"]
        spot = data["records"].get("underlyingValue", SPOT_FALLBACK)

        # Normalize into flat DataFrame
        df = pd.json_normalize(records)
        # Convert expiry dates to datetime for sorting/filter UI
        df["expiryDate"] = pd.to_datetime(df["expiryDate"], format="%d-%b-%Y")
        return df, spot

    except Exception as e:
        st.error(f"❌ Failed to fetch option chain: {e}")
        return pd.DataFrame(), SPOT_FALLBACK


def plot_oi_chart(df: pd.DataFrame, spot: float):
    """
    Builds and returns a Plotly Figure:
    - Bars for CE and PE open interest by strike
    - Vertical line at 'spot'
    """
    strikes = df["strikePrice"]
    ce_oi = df["CE.openInterest"].fillna(0)
    pe_oi = df["PE.openInterest"].fillna(0)

    fig = go.Figure()

    # CE bars (left axis)
    fig.add_trace(go.Bar(
        x=strikes, y=ce_oi, name="CE OI",
        marker_color="#2ca02c",
        offsetgroup=0
    ))

    # PE bars (left axis)
    fig.add_trace(go.Bar(
        x=strikes, y=pe_oi, name="PE OI",
        marker_color="#d62728",
        offsetgroup=1
    ))

    # Spot marker (vertical line)
    if spot is not None:
        fig.add_vline(
            x=spot,
            line=dict(color="#1f77b4", width=2, dash="dash"),
            annotation_text=f"Spot: {spot:.2f}",
            annotation_position="top right"
        )

    fig.update_layout(
        title="Option Chain Open Interest by Strike",
        xaxis_title="Strike Price",
        yaxis_title="Open Interest",
        barmode="relative",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40)
    )
    return fig


def main():
    st.set_page_config(page_title="NIFTY Option Chain Dashboard", layout="wide")
    st.title("📈 NIFTY Option Chain Dashboard")

    # Symbol selector
    symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"], index=0)

    # Fetch data
    df, spot = fetch_option_chain(symbol)
    if df.empty:
        st.stop()

    # Display spot price
    if spot is not None:
        st.metric(label="Spot Price", value=f"{spot:.2f}")
    else:
        st.warning("⚠️ No valid spot data—using fallback logic.")

    # Expiry filter
    expiries = df["expiryDate"].dt.date.unique()
    expiry = st.selectbox(
        "Select Expiry Date",
        options=sorted(expiries),
        format_func=lambda x: x.strftime("%d %b %Y")
    )
    df_exp = df[df["expiryDate"].dt.date == expiry]

    # Chart
    fig = plot_oi_chart(df_exp, spot)
    st.plotly_chart(fig, use_container_width=True)

    # Raw data table
    with st.expander("Show raw data"):
        display_cols = [
            "strikePrice",
            "CE.openInterest", "CE.changeinOpenInterest", "CE.lastPrice",
            "PE.openInterest", "PE.changeinOpenInterest", "PE.lastPrice"
        ]
        st.dataframe(df_exp[display_cols].rename(columns={
            "strikePrice": "Strike",
            "CE.openInterest": "CE OI",
            "CE.changeinOpenInterest": "Δ CE OI",
            "CE.lastPrice": "CE LTP",
            "PE.openInterest": "PE OI",
            "PE.changeinOpenInterest": "Δ PE OI",
            "PE.lastPrice": "PE LTP"
        }), height=400)


if __name__ == "__main__":
    main()
