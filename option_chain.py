import requests
import json

def fetch_option_chain(symbol="NIFTY"):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }
    session = requests.Session()
    session.get("https://www.nseindia.com/option-chain", headers=headers)
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    response = session.get(url, headers=headers)
    data = json.loads(response.text)
    return data
