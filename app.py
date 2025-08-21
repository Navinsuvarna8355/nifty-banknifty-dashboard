import requests
import pandas as pd
import time
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# NSE headers to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
    "Connection": "keep-alive"
}

def fetch_option_chain(symbol: str = "NIFTY") -> tuple[pd.DataFrame, str, float]:
    """
    Fetches option chain data from NSE for the given symbol.
    Returns:
        - DataFrame with strike, CE OI, PE OI
        - Nearest expiry date
        - Underlying index value
    """
    session = requests.Session()
    try:
        # Warm-up request to set cookies
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
        time.sleep(1)

        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        response = session.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
        data = response.json()

        expiry = data["records"]["expiryDates"][0]
        underlying = data["records"].get("underlyingValue", 0.0)

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

        df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df["Underlying"] = underlying

        logging.info(f"Fetched {len(df)} rows for {symbol} - Expiry: {expiry}")
        return df, expiry, underlying

    except Exception as e:
        logging.error(f"Error fetching option chain for {symbol}: {e}")
        return pd.DataFrame(), "—", 0.0

def derive_strategy(df: pd.DataFrame) -> str:
    """
    Derives market sentiment based on open interest.
    Returns:
        - "Bullish", "Bearish", or "Neutral"
    """
    if df.empty:
        return "No Data"

    total_ce = df["Call_OI"].sum()
    total_pe = df["Put_OI"].sum()

    logging.info(f"Total CE OI: {total_ce}, Total PE OI: {total_pe}")

    if total_pe > total_ce * 1.2:
        return "Bullish"
    elif total_ce > total_pe * 1.2:
        return "Bearish"
    else:
        return "Neutral"

# Optional: Run as script
if __name__ == "__main__":
    symbol = "BANKNIFTY"  # You can change this to "NIFTY" or others
    df, expiry, underlying = fetch_option_chain(symbol)
    strategy = derive_strategy(df)

    print(f"\nSymbol: {symbol}")
    print(f"Expiry Date: {expiry}")
    print(f"Underlying Index Value: {underlying}")
    print(f"Market Sentiment: {strategy}")
    print("\nOption Chain Snapshot:")
    print(df.head())
