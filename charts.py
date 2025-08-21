import pandas as pd
import plotly.express as px

def generate_oi_chart(data, expiry):
    strike_data = []
    for item in data["records"]["data"]:
        if item["expiryDate"] == expiry:
            strike = item["strikePrice"]
            ce_oi = item.get("CE", {}).get("openInterest", 0)
            pe_oi = item.get("PE", {}).get("openInterest", 0)
            strike_data.append((strike, ce_oi, pe_oi))
    df = pd.DataFrame(strike_data, columns=["Strike", "Call OI", "Put OI"])
    fig = px.bar(df, x="Strike", y=["Call OI", "Put OI"], barmode="group",
                 title=f"Open Interest - {expiry}", labels={"value": "OI", "Strike": "Strike Price"})
    return fig
