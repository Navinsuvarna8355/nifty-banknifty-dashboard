import requests, json, time
import pandas as pd
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
    "Connection": "keep-alive"
}

def fetch_option_chain(symbol):
    session = requests.Session()
    try:
        # Set cookies
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
        time.sleep(1)

        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        response = session.get(url, headers=HEADERS, timeout=5)
        data = response.json()

        expiry = data["records"]["expiryDates"][0]
        strikes, ce_oi, pe_oi = [], [], []

        for item in data["records"]["data"]:
            if item.get("expiryDate") == expiry:
                strike = item.get("strikePrice")
                ce = item.get("CE", {}).get("openInterest", 0)
                pe = item.get("PE", {}).get("openInterest", 0)
                strikes.append(strike)
                ce_oi.append(ce)
                pe_oi.append(pe)

        df = pd.DataFrame({
            "Strike": strikes,
            "Call_OI": ce_oi,
            "Put_OI": pe_oi
        })

        fut_price = round(sum(strikes) / len(strikes), 2)
        df["Futures"] = fut_price

        return df, expiry, fut_price

    except Exception as e:
        return pd.DataFrame(), "—", 0

def derive_strategy(df):
    if df.empty:
        return "No Data"

    total_ce = df["Call_OI"].sum()
    total_pe = df["Put_OI"].sum()

    if total_pe > total_ce * 1.2:
        return "Bullish"
    elif total_ce > total_pe * 1.2:
        return "Bearish"
    else:
        return "Neutral"
