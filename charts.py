import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random

def generate_oi_line_chart(data, expiry):
    strike_data = []
    for item in data["records"]["data"]:
        if item["expiryDate"] == expiry:
            strike = item["strikePrice"]
            ce_oi = item.get("CE", {}).get("openInterest", 0)
            pe_oi = item.get("PE", {}).get("openInterest", 0)
            strike_data.append((strike, ce_oi, pe_oi))
    df = pd.DataFrame(strike_data, columns=["Strike", "Call OI", "Put OI"])
    df.sort_values("Strike", inplace=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Strike"], y=df["Call OI"], mode='lines+markers', name='Call OI'))
    fig.add_trace(go.Scatter(x=df["Strike"], y=df["Put OI"], mode='lines+markers', name='Put OI'))
    fig.update_layout(title=f"CE/PE Open Interest - {expiry}",
                      xaxis_title="Strike Price", yaxis_title="Open Interest")
    return fig

def generate_mock_futures_chart(symbol):
    dates = pd.date_range(end=pd.Timestamp.today(), periods=30)
    prices = [random.randint(24500, 25500) if symbol == "NIFTY" else random.randint(55000, 56000) for _ in range(30)]
    df = pd.DataFrame({"Date": dates, "Price": prices})
    fig = px.line(df, x="Date", y="Price", title=f"{symbol} Futures Price Trend (Simulated)")
    return fig
