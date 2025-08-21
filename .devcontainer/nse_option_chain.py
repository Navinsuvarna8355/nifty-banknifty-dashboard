import pandas as pd
import os

def fetch_live_chart_data(index_name):
    csv_file = f"{index_name.lower()}.csv"
    
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)

    # Simulate full-day data: 09:15 to 15:30 (375 minutes)
    timestamps = pd.date_range("2025-08-21 09:15", "2025-08-21 15:30", freq="1min").strftime("%H:%M:%S")
    base = 24800 if index_name == "NIFTY" else 55200

    data = {
        "timestamp": timestamps,
        "open": [base + i for i in range(len(timestamps))],
        "high": [base + i + 20 for i in range(len(timestamps))],
        "low": [base + i - 20 for i in range(len(timestamps))],
        "close": [base + i + 10 for i in range(len(timestamps))],
        "volume": [10000 + i * 10 for i in range(len(timestamps))]
    }

    return pd.DataFrame(data)
