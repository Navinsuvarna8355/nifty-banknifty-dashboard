# strategy_engine.py

import requests
import pandas as pd
from datetime import datetime
import logging

# Optional: configure logging for debugging
logging.basicConfig(level=logging.INFO)

NSE_BASE_URL = "https://www.nseindia.com/api/option-chain-indices"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

def fetch_option_chain(symbol: str = "NIFTY") -> tuple[pd.DataFrame, str, dict]:
    """
    Fetches option chain data from NSE for the given symbol.
    Returns:
        - DataFrame of CE/PE options
        - Nearest expiry date
        - Futures metadata (if available)
    """
    try:
        url = f"{NSE_BASE_URL}?symbol={symbol}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        records = data.get("records", {})
        expiry_dates = records.get("expiryDates", [])
        all_data = records.get("data", [])

        if not expiry_dates or not all_data:
            raise ValueError("Empty payload from NSE")

        nearest_expiry = expiry_dates[0]
        filtered = [d for d in all_data if d.get("expiryDate") == nearest_expiry]

        rows = []
        for entry in filtered:
            ce = entry.get("CE", {})
            pe = entry.get("PE", {})
            strike = entry.get("strikePrice")

            rows.append({
                "strike": strike,
                "CE_OI": ce.get("openInterest"),
                "CE_ChgOI": ce.get("changeinOpenInterest"),
                "CE_LTP": ce.get("lastPrice"),
                "PE_OI": pe.get("openInterest"),
                "PE_ChgOI": pe.get("changeinOpenInterest"),
                "PE_LTP": pe.get("lastPrice")
            })

        df = pd.DataFrame(rows).dropna()
        fut_meta = records.get("underlyingValue", {})

        return df, nearest_expiry, fut_meta

    except Exception as e:
        logging.error(f"Error fetching option chain: {e}")
        return pd.DataFrame(), "", {}

# Optional test block
if __name__ == "__main__":
    df, expiry, fut = fetch_option_chain("BANKNIFTY")
    print(f"Expiry: {expiry}")
    print(f"Underlying: {fut}")
    print(df.head())
