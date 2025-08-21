import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

def generate_combined_chart(data, expiry, symbol):
    # Extract CE/PE OI per strike
    strike_data = []
    for item in data["records"]["data"]:
        if item["expiryDate"] == expiry:
            strike = item["strikePrice"]
            ce_oi = item.get("CE", {}).get("openInterest", 0)
            pe_oi = item.get("PE", {}).get("openInterest", 0)
            strike_data.append((strike, ce_oi, pe_oi))
    df = pd.DataFrame(strike_data, columns=["Strike", "Call OI", "Put OI"])
    df.sort_values("Strike", inplace=True)

    # Simulate Futures Price per strike (for visual alignment)
    df["Futures Price"] = [
        random.randint(24500, 25500) if symbol == "NIFTY" else random.randint(55000, 56000)
        for _ in range(len(df))
    ]

    # Create combined chart with dual y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # CE/PE OI on primary y-axis
    fig.add_trace(go.Scatter(x=df["Strike"], y=df["Call OI"], mode='lines+markers', name='Call OI'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["Strike"], y=df["Put OI"], mode='lines+markers', name='Put OI'), secondary_y=False)

    # Futures Price on secondary y-axis
    fig.add_trace(go.Scatter(x=df["Strike"], y=df["Futures Price"], mode='lines+markers', name='Futures Price'), secondary_y=True)

    fig.update_layout(
        title=f"{symbol} CE/PE Open Interest + Futures Price Trend ({expiry})",
        xaxis_title="Strike Price",
        legend=dict(x=0.01, y=0.99),
        margin=dict(t=60, b=40)
    )
    fig.update_yaxes(title_text="Open Interest", secondary_y=False)
    fig.update_yaxes(title_text="Futures Price", secondary_y=True)

    return fig
