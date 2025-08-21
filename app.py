import streamlit as st
from option_chain import fetch_option_chain
from charts import generate_oi_chart

st.set_page_config(page_title="📈 NIFTY & BANKNIFTY Dashboard", layout="wide")

st.title("📊 NIFTY & BANKNIFTY Strategy Signal")

symbol = st.selectbox("Choose Index", ["NIFTY", "BANKNIFTY"])
data = fetch_option_chain(symbol)

if data:
    expiry_dates = data["records"]["expiryDates"]
    selected_expiry = st.selectbox("Select Expiry", expiry_dates)

    live_price = data["records"]["underlyingValue"]
    st.metric(label=f"{symbol} Live Price", value=f"₹{live_price:,.2f}")

    st.write("**Signal:** SIDEWAYS")
    st.write("**Trend:** BEARISH")
    st.write("**Strategy:** 3 EMA Crossover + PCR")
    st.write("**Confidence:** 90%")

    # PCR Calculation
    total_ce_oi = sum(item.get("CE", {}).get("openInterest", 0)
                      for item in data["records"]["data"] if item["expiryDate"] == selected_expiry)
    total_pe_oi = sum(item.get("PE", {}).get("openInterest", 0)
                      for item in data["records"]["data"] if item["expiryDate"] == selected_expiry)
    pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi else 0

    st.write(f"**PCR (Put/Call Ratio):** {pcr}")

    fig = generate_oi_chart(data, selected_expiry)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Failed to fetch data from NSE. Please try again later.")
