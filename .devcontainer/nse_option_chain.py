import pandas as pd

def fetch_live_chart_data(index_name):
    # Dummy live data for testing without CSV
    if index_name == "NIFTY":
        data = {
            "timestamp": ["2025-08-21 09:15", "2025-08-21 09:16", "2025-08-21 09:17"],
            "open": [24800, 24840, 24880],
            "high": [24850, 24890, 24920],
            "low": [24780, 24830, 24870],
            "close": [24840, 24880, 24910],
            "volume": [12000, 15000, 18000]
        }
    else:  # BANKNIFTY
        data = {
            "timestamp": ["2025-08-21 09:15", "2025-08-21 09:16", "2025-08-21 09:17"],
            "open": [55200, 55240, 55280],
            "high": [55250, 55290, 55320],
            "low": [55180, 55230, 55270],
            "close": [55240, 55280, 55310],
            "volume": [11000, 14000, 17000]
        }

    return pd.DataFrame(data)

def get_option_price(index_name, strike, option_type):
    try:
        df = pd.read_csv(f"{index_name.lower()}_option_chain.csv")
        row = df[(df['strikePrice'] == strike) & (df['type'] == option_type)]
        if not row.empty:
            return float(row['lastPrice'].values[0])
    except FileNotFoundError:
        return None
    return None
