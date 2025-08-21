from nse_option_chain import get_option_price

def get_signals(df, index_name):
    breakout_indices = []
    action = None
    strike = None
    cmp = None

    for i in range(2, len(df)):
        if df['close'][i] > df['high'][i-1] and df['volume'][i] > df['volume'][i-1]:
            breakout_indices.append(i)

    pcr = 1.28 if index_name == "NIFTY" else 0.76
    ema_signal = "BUY" if df['close'].iloc[-1] > df['close'].rolling(10).mean().iloc[-1] else "SELL"

    if pcr > 1 and ema_signal == "BUY":
        action = "BUY CE"
        strike = round(df['close'].iloc[-1] + 150, -2)
        cmp = get_option_price(index_name, strike, "CE")
    elif pcr < 0.7 and ema_signal == "SELL":
        action = "BUY PE"
        strike = round(df['close'].iloc[-1] - 150, -2)
        cmp = get_option_price(index_name, strike, "PE")

    return {
        "breakout_indices": breakout_indices,
        "action": action,
        "strike": strike,
        "cmp": cmp
    }
