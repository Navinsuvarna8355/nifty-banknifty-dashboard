from flask import Flask, jsonify, request
from strategy_engine import fetch_option_chain, derive_strategy
from datetime import datetime

app = Flask(__name__)

@app.route("/api/strategy")
def strategy_api():
    symbol = request.args.get("symbol", "NIFTY").upper()
    if symbol not in ["NIFTY", "BANKNIFTY"]:
        return jsonify({"error": "Invalid symbol"}), 400

    df, expiry, fut_price = fetch_option_chain(symbol)
    strategy = derive_strategy(df)

    response = {
        "symbol": symbol,
        "strategy": strategy,
        "expiry": expiry,
        "futures": fut_price,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return jsonify(response)

@app.route("/api/health")
def health_check():
    return jsonify({
        "status": "OK",
        "symbols": ["NIFTY", "BANKNIFTY"],
        "timestamp": datetime.now().isoformat()
    })

@app.route("/")
def home():
    return """
    <h2>NIFTY & BANKNIFTY Strategy API</h2>
    <p>Use <code>/api/strategy?symbol=NIFTY</code> or <code>/api/strategy?symbol=BANKNIFTY</code> to get strategy insights.</p>
    <p>Health check: <code>/api/health</code></p>
    """

if __name__ == "__main__":
    app.run(debug=True, port=8501)
