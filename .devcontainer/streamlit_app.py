import streamlit as st
import pandas as pd
import os
import altair as alt

st.set_page_config(layout="wide", page_title="NIFTY & BANKNIFTY Signal Dashboard")

st.title("📊 NIFTY & BANKNIFTY Signal Dashboard")

# Load data with error handling
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error(f"❌ File not found: {file_path}")
        return pd.DataFrame()

nifty_data = load_data("data/nifty.csv")
banknifty_data = load_data("data/banknifty.csv")

# Check if data is loaded
if not nifty_data.empty and not banknifty_data.empty:
    # Convert time column to datetime
    nifty_data['Time'] = pd.to_datetime(nifty_data['Time'])
    banknifty_data['Time'] = pd.to_datetime(banknifty_data['Time'])

    # Create charts
    def create_chart(df, title, color):
        chart = alt.Chart(df).mark_line(color=color).encode(
            x='Time:T',
            y='Price:Q',
            tooltip=['Time:T', 'Price:Q']
        ).properties(
            title=title,
            width=600,
            height=400
        )
        return chart

    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(create_chart(nifty_data, "NIFTY Chart", "green"), use_container_width=True)
    with col2:
        st.altair_chart(create_chart(banknifty_data, "BANKNIFTY Chart", "blue"), use_container_width=True)

    # Optional: Show raw data
    with st.expander("📄 Show Raw Data"):
        st.subheader("NIFTY")
        st.dataframe(nifty_data)
        st.subheader("BANKNIFTY")
        st.dataframe(banknifty_data)
else:
    st.warning("Please upload both 'nifty.csv' and 'banknifty.csv' in the /data folder.")
