import json
import os
import urllib.parse
import urllib.request

SYMBOL = "BTCUSDT"
INTERVAL = "5m"
RSI_PERIOD = 14

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


def get_klines():
    url = (
        "https://api.binance.com/api/v3/klines?"
        + urllib.parse.urlencode({
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "limit": 100
        })
    )

    with urllib.request.urlopen(url, timeout=15) as response:
        return json.loads(response.read().decode())


def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return []

    gains = []
    losses = []

    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    rsi_values = [None] * period

    if avg_loss == 0:
        rsi_values.append(100.0)
    else:
        rs = avg_gain / avg_loss
        rsi_values.append(100 - (100 / (1 + rs)))

    for i in range(period, len(gains)):
        avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period

        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        rsi_values.append(rsi)

    return rsi_values


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message
    }).encode()

    request = urllib.request.Request(url, data=data)

    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode())


def main():
    klines = get_klines()

    # آخرین کندل کامل‌شده را استفاده می‌کنیم
    closed_klines = klines[:-1]

    closes = [float(k[4]) for k in closed_klines]

    rsi_values = calculate_rsi(closes, RSI_PERIOD)

    if not rsi_values:
        print("Not enough data for RSI.")
        return

    rsi = rsi_values[-1]
    price = closes[-1]

    print(f"BTCUSDT Price: {price}")
    print(f"RSI(14): {rsi:.2f}")

    if rsi > 70:
        message = (
            "🔴 BTC RSI ALERT\n\n"
            f"BTCUSDT: {price:,.2f}\n"
            f"RSI(14): {rsi:.2f}\n"
            "⏱ Timeframe: 5m\n"
            "⚠️ RSI بالای 70 قرار گرفت."
        )

        send_telegram(message)
        print("Telegram alert sent.")

    elif rsi < 30:
        message = (
            "🟢 BTC RSI ALERT\n\n"
            f"BTCUSDT: {price:,.2f}\n"
            f"RSI(14): {rsi:.2f}\n"
            "⏱ Timeframe: 5m\n"
            "⚠️ RSI زیر 30 قرار گرفت."
        )

        send_telegram(message)
        print("Telegram alert sent.")

    else:
        print("No alert.")


if __name__ == "__main__":
    main()
