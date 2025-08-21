import pandas as pd

def fetch_live_chart_data(index_name):
    # Replace with actual API or CSV fetch
    return pd.read_csv(f"{index_name.lower()}.csv")

def get_option_price(index_name, strike, option_type):
    df = pd.read_csv(f"{index_name.lower()}_option_chain.csv")
    row = df[(df['strikePrice'] == strike) & (df['type'] == option_type)]
    if not row.empty:
        return float(row['lastPrice'].values[0])
    return None
