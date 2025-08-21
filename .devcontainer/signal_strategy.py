def determine_signal(pcr, trend, ema_signal):
    signal = "SIDEWAYS"
    suggested_option = None

    if trend == "BULLISH" and ema_signal == "BUY" and pcr >= 1:
        signal = "BUY"
        suggested_option = "CALL"
    elif trend == "BEARISH" and ema_signal == "SELL" and pcr <= 1:
        signal = "SELL"
        suggested_option = "PUT"
    return signal, suggested_option
