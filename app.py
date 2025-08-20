from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import time

# Serve frontend from Flask to avoid file:// CORS issues
app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

NSE_BASE = "https://www.nseindia.com"
OC_URL = NSE_BASE + "/api/option-chain-indices?symbol={sym}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
    "Connection": "keep-alive"
}

def fetch_option_chain(symbol: str):
    """Handshake + resilient fetch from NSE. Returns dict or raises."""
    url = OC_URL.format(sym=symbol.upper())
    s = requests.Session()
    s.headers.update(HEADERS)

    # initial cookie warm-up
    try:
        s.get(NSE_BASE + "/option-chain", timeout=8)
    except Exception:
        pass

    last_err = None
    for _ in range(5):
        try:
            r = s.get(url, timeout=12)
            if r.status_code == 200:
                return r.json()
            last_err = f"HTTP {r.status_code}"
        except Exception as e:
            last_err = str(e)
        time.sleep(0.8)
        try:
            s.get(NSE_BASE + "/option-chain", timeout=6)
        except Exception:
            pass
    raise RuntimeError(f"Failed to fetch NSE data: {last_err}")

def compute_pcr_levels(raw: dict):
    """Compute total OI PCR, top supports/resistances, ATM window."""
    records = raw.get("records", {})
    rows = records.get("data", [])
    expiry = (records.get("expiryDates") or [None])[0]
    spot = records.get("underlyingValue")

    total_ce = 0
    total_pe = 0
    strikes = []

    for row in rows:
        if expiry and row.get("expiryDate") != expiry:
            continue
        sp = row.get("strikePrice")
        ce_oi = int((row.get("CE") or {}).get("openInterest") or 0)
        pe_oi = int((row.get("PE") or {}).get("openInterest") or 0)
        total_ce += ce_oi
        total_pe += pe_oi
        strikes.append({"strike": sp, "callOI": ce_oi, "putOI": pe_oi})

    pcr = round(total_pe / total_ce, 2) if total_ce else 0.0

    top_calls = sorted(strikes, key=lambda x: x["callOI"], reverse=True)[:3]
    top_puts  = sorted(strikes, key=lambda x: x["putOI"],  reverse=True)[:3]
    resistances = [int(x["strike"]) for x in top_calls]
    supports    = [int(x["strike"]) for x in top_puts]

    # nearest 20 strikes to spot
    if spot is not None:
        window = sorted(strikes, key=lambda x: abs((x["strike"] or 0) - spot))[:20]
    else:
        window = strikes[:20]

    if pcr > 1.1:
        reco = "BUY CE (Bullish)"
    elif pcr < 0.9:
        reco = "BUY PE (Bearish)"
    else:
        reco = "SIDEWAYS / NO TRADE"

    return {
        "expiry": expiry,
        "underlying": spot,
        "pcr": pcr,
        "supports": supports,
        "resistances": resistances,
        "recommendation": reco,
        "strikesWindow": window
    }

# --------- API ---------
@app.route("/api/data")
def api_data():
    sym = (request.args.get("symbol") or "BANKNIFTY").upper()
    try:
        raw = fetch_option_chain(sym)
        res = compute_pcr_levels(raw)
        res["symbol"] = sym
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e), "symbol": sym}), 500

# --------- Serve frontend ---------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def static_front(path):
    if path == "" or path is None:
        return send_from_directory(app.static_folder, "index.html")
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
