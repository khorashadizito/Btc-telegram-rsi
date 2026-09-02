import json
import os
import urllib.parse
import urllib.request

PRODUCT = "BTC-USD"
GRANULARITY = 300
RSI_PERIOD = 14

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


def get_candles():
    url = (
        f"https://api.exchange.coinbase.com/products/{PRODUCT}/candles?"
        + urllib.parse.urlencode({
            "granularity": GRANULARITY
        })
    )

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode())


def calculate_rsi(closes, period=14):
    gains = []
    losses = []

    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message
    }).encode()

    request = urllib.request.Request(url, data=data)

    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read().decode()


def main():
    candles = get_candles()

    candles.sort(key=lambda x: x[0])

    # حذف کندل در حال تشکیل
    closed_candles = candles[:-1]

    closes = [float(candle[4]) for candle in closed_candles]

    if len(closes) < RSI_PERIOD + 1:
        print("Not enough data.")
        return

    rsi = calculate_rsi(closes, RSI_PERIOD)
    price = closes[-1]

    message = (
        "📊 BTC RSI\n\n"
        f"💰 Price: {price:,.2f}\n"
        f"📈 RSI(14): {rsi:.2f}\n"
        "⏱ Timeframe: 5m"
    )

    send_telegram(message)

    print(message)


if __name__ == "__main__":
    main()
