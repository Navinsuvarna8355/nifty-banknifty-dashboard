import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from signal_strategy import get_signals

st.set_page_config(layout="wide")
st.title("📊 NIFTY & BANKNIFTY Signal Dashboard")

col1, col2 = st.columns(2)

# Load your live data (replace with actual API or CSV)
nifty_data = pd.read_csv("nifty.csv")
banknifty_data = pd.read_csv("banknifty.csv")

nifty_signal = get_signals(nifty_data, "NIFTY")
banknifty_signal = get_signals(banknifty_data, "BANKNIFTY")

def plot_chart(df, signal, index_name):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price'
    ))

    for i in signal['breakout_indices']:
        fig.add_trace(go.Scatter(
            x=[df['timestamp'][i]],
            y=[df['high'][i]],
            mode='markers',
            marker=dict(color='yellow', size=12),
            name='Breakout'
        ))

    if signal['action'] == 'BUY CE':
        fig.add_annotation(text=f"✅ BUY CE {signal['strike']} @ ₹{signal['cmp']}",
                           x=df['timestamp'][signal['breakout_indices'][-1]],
                           y=df['high'][signal['breakout_indices'][-1]] + 20,
                           showarrow=True, arrowhead=2, bgcolor="green")
    elif signal['action'] == 'BUY PE':
        fig.add_annotation(text=f"✅ BUY PE {signal['strike']} @ ₹{signal['cmp']}",
                           x=df['timestamp'][signal['breakout_indices'][-1]],
                           y=df['low'][signal['breakout_indices'][-1]] - 20,
                           showarrow=True, arrowhead=2, bgcolor="red")

    fig.update_layout(title=f"{index_name} Chart", xaxis_rangeslider_visible=False)
    return fig

with col1:
    st.subheader("📈 NIFTY")
    st.plotly_chart(plot_chart(nifty_data, nifty_signal, "NIFTY"), use_container_width=True)

with col2:
    st.subheader("📈 BANKNIFTY")
    st.plotly_chart(plot_chart(banknifty_data, banknifty_signal, "BANKNIFTY"), use_container_width=True)
