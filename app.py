import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Intraday OI Tracker", layout="wide")

# ------------------ CONFIG ------------------
INDEX = st.selectbox("Choose Index", ["NIFTY", "BANKNIFTY"])
SPOT_PRICE = 25075.05 if INDEX == "NIFTY" else 55698.50

# ------------------ MOCK INTRADAY DATA ------------------
def generate_intraday_data():
    times = pd.date_range("09:15", "15:30", freq="15min").strftime("%H:%M")
    ce_oi = np.random.randint(20000, 160000, len(times))
    pe_oi = np.random.randint(20000, 160000, len(times))
    fut_price = np.linspace(SPOT_PRICE - 50, SPOT_PRICE + 50, len(times))

    df = pd.DataFrame({
        "Time": times,
        "CE_OI": ce_oi,
        "PE_OI": pe_oi,
        "Futures": fut_price
    })
    return df

df_intraday = generate_intraday_data()

# ------------------ CHART ------------------
st.subheader("📈 Intraday OI vs Futures")

fig = go.Figure()

# CE Line
fig.add_trace(go.Scatter(
    x=df_intraday["Time"], y=df_intraday["CE_OI"],
    mode="lines+markers", name="CE",
    line=dict(color="blue", width=2)
))

# PE Line
fig.add_trace(go.Scatter(
    x=df_intraday["Time"], y=df_intraday["PE_OI"],
    mode="lines+markers", name="PE",
    line=dict(color="red", width=2)
))

# Futures Line (secondary y-axis)
fig.add_trace(go.Scatter(
    x=df_intraday["Time"], y=df_intraday["Futures"],
    mode="lines", name="Futures",
    line=dict(color="black", dash="dot"),
    yaxis="y2"
))

fig.update_layout(
    template="plotly_dark",
    title="Change in OI vs Time",
    xaxis_title="Time",
    yaxis=dict(title="OI (Contracts)", side="left"),
    yaxis2=dict(
        title="Futures Price",
        overlaying="y",
        side="right",
        range=[SPOT_PRICE - 100, SPOT_PRICE + 100],
        showgrid=False
    ),
    legend=dict(x=0.01, y=0.99),
    height=600,
    margin=dict(l=50, r=50, t=50, b=50)
)

st.plotly_chart(fig, use_container_width=True)
