import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import numpy as np

# ------------------ CONFIG & CONSTANTS ------------------
st.set_page_config(page_title="NIFTY/BANKNIFTY Dashboard", layout="wide")

SPOT_FALLBACK = {"NIFTY": 25050.55, "BANKNIFTY": 55698.50}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/option-chain"
}

# ------------------ FETCH OPTION CHAIN WITH COOKIE PRELOAD ------------------
@st.cache_data(ttl=60)
def fetch_option_chain(symbol: str):
    session = requests.Session()
    try:
        # Prime cookies
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        res = session.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()

        df = pd.json_normalize(data["records"]["data"])
        df["expiryDate"] = pd.to_datetime(df["expiryDate"], format="%d-%b-%Y")
        spot = data["records"].get("underlyingValue", SPOT_FALLBACK[symbol])
        return df, spot

    except Exception as e:
        st.error(f"❌ Failed to fetch option chain: {e}")
        return pd.DataFrame(), SPOT_FALLBACK[symbol]

# ------------------ INTRADAY DATA GENERATOR ------------------
@st.cache_data(ttl=60)
def generate_intraday_data(symbol: str, spot_price: float):
    times = pd.date_range("09:15", "15:30", freq="15Min").strftime("%H:%M")
    ce = np.random.randint(20000, 160000, len(times))
    pe = np.random.randint(20000, 160000, len(times))
    fut = np.linspace(spot_price - 50, spot_price + 50, len(times))
    return pd.DataFrame({"Time": times, "CE_OI": ce, "PE_OI": pe, "Futures": fut})

# ------------------ MAIN APP ------------------
def main():
    # User Inputs
    symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
    df, spot_price = fetch_option_chain(symbol)
    if df.empty:
        return  # stop if fetch failed

    # Spot Metric
    st.metric(label=f"{symbol} Spot Price", value=f"{spot_price:.2f}")

    # Expiry Filter
    expiries = df["expiryDate"].dt.date.unique()
    expiry = st.selectbox(
        "Select Expiry",
        options=sorted(expiries),
        format_func=lambda d: d.strftime("%d %b %Y")
    )
    df_exp = df[df["expiryDate"].dt.date == expiry]

    # Extract Strike-wise OI Change
    if "CE.changeinOpenInterest" in df_exp.columns:
        df_chg = df_exp[[
            "strikePrice",
            "CE.changeinOpenInterest",
            "PE.changeinOpenInterest"
        ]].rename(columns={
            "strikePrice": "Strike",
            "CE.changeinOpenInterest": "CE_ChgOI",
            "PE.changeinOpenInterest": "PE_ChgOI"
        })
    else:
        df_chg = pd.DataFrame(columns=["Strike", "CE_ChgOI", "PE_ChgOI"])

    # Clean and Sort
    df_chg = df_chg.fillna(0).sort_values("Strike")

    # PCR Calculation
    total_ce = df_chg["CE_ChgOI"].sum()
    total_pe = df_chg["PE_ChgOI"].sum()
    pcr = round(total_pe / total_ce, 2) if total_ce else None

    # EMA Signal on Synthetic History
    history = pd.Series([spot_price - i * 10 for i in range(30)][::-1])
    ema_fast = history.ewm(span=9).mean().iloc[-1]
    ema_slow = history.ewm(span=21).mean().iloc[-1]
    ema_signal = "BULLISH" if ema_fast > ema_slow else "BEARISH"

    # Strategy Decision
    if pcr and pcr > 1.2 and ema_signal == "BULLISH":
        strategy = "BUY CALL"
    elif pcr and pcr < 0.8 and ema_signal == "BEARISH":
        strategy = "BUY PUT"
    else:
        strategy = "SIDEWAYS"

    # Display Strategy Metrics
    st.subheader("📊 Strategy Insights")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Expiry", expiry.strftime("%d %b %Y"))
    c2.metric("PCR", pcr)
    c3.metric("EMA Signal", ema_signal)
    c4.metric("Strategy", strategy)

    # ------------------ Strike-Wise Charts ------------------
    st.subheader("📈 Strike-wise OI Overview")
    left, right = st.columns([1, 2])

    # Bar Chart
    with left:
        bar_fig = go.Figure()
        bar_fig.add_trace(go.Bar(
            x=["CALL"], y=[total_ce/100000],
            name="CALL", marker_color="green"
        ))
        bar_fig.add_trace(go.Bar(
            x=["PUT"], y=[total_pe/100000],
            name="PUT", marker_color="red"
        ))
        bar_fig.update_layout(
            template="plotly_dark",
            title="Δ OI (in Lakhs)",
            xaxis_title="Option Type",
            yaxis_title="OI Change (L)",
            height=350, margin=dict(l=30, r=30, t=40, b=30)
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    # Line Chart
    with right:
        max_oi = max(df_chg["CE_ChgOI"].max(), df_chg["PE_ChgOI"].max(), 1)
        line_fig = go.Figure()
        line_fig.add_trace(go.Scatter(
            x=df_chg["Strike"], y=df_chg["CE_ChgOI"],
            mode="lines+markers", name="CE",
            line=dict(color="green", width=2), marker=dict(size=5)
        ))
        line_fig.add_trace(go.Scatter(
            x=df_chg["Strike"], y=df_chg["PE_ChgOI"],
            mode="lines+markers", name="PE",
            line=dict(color="red", width=2), marker=dict(size=5)
        ))
        line_fig.add_trace(go.Scatter(
            x=df_chg["Strike"], y=[spot_price]*len(df_chg),
            mode="lines", name="Future",
            line=dict(color="gray", dash="dot", width=1),
            opacity=0.6, yaxis="y2"
        ))
        line_fig.update_layout(
            template="plotly_dark",
            title="Δ OI vs Strike",
            xaxis_title="Strike",
            yaxis=dict(title="OI Change", side="left"),
            yaxis2=dict(
                title="Futures Price",
                overlaying="y",
                side="right",
                range=[spot_price-200, spot_price+200],
                showgrid=False
            ),
            shapes=[dict(
                type="line", x0=spot_price, x1=spot_price,
                y0=0, y1=max_oi, line=dict(color="yellow", dash="dash")
            )],
            annotations=[dict(
                x=spot_price, y=max_oi*0.1,
                text=f"Spot @ {spot_price:.2f}",
                showarrow=False, font=dict(color="yellow"),
                xanchor="left"
            )],
            legend=dict(x=0.01, y=0.99),
            height=550, margin=dict(l=50, r=50, t=50, b=50)
        )
        st.plotly_chart(line_fig, use_container_width=True)

    # ------------------ Intraday OI Tracker ------------------
    st.subheader("⏱️ Intraday OI & Futures")
    df_intraday = generate_intraday_data(symbol, spot_price)
    intraday_fig = go.Figure()
    intraday_fig.add_trace(go.Scatter(
        x=df_intraday["Time"], y=df_intraday["CE_OI"],
        mode="lines+markers", name="CE OI",
        line=dict(color="green", width=2), marker=dict(size=4)
    ))
    intraday_fig.add_trace(go.Scatter(
        x=df_intraday["Time"], y=df_intraday["PE_OI"],
        mode="lines+markers", name="PE OI",
        line=dict(color="red", width=2), marker=dict(size=4)
    ))
    intraday_fig.add_trace(go.Scatter(
        x=df_intraday["Time"], y=df_intraday["Futures"],
        mode="lines", name="Futures Price",
        line=dict(color="gray", dash="dash", width=1),
        yaxis="y2"
    ))
    intraday_fig.update_layout(
        template="plotly_dark",
        title="Intraday OI vs Time",
        xaxis_title="Time",
        yaxis=dict(title="Open Interest"),
        yaxis2=dict(
            title="Futures Price",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        legend=dict(x=0.01, y=0.99),
        height=450, margin=dict(l=50, r=50, t=40, b=40)
    )
    st.plotly_chart(intraday_fig, use_container_width=True)


if __name__ == "__main__":
    main()
