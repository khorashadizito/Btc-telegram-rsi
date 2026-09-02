import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

PRODUCT = "BTC-USD"
GRANULARITY = 300  # 5 دقیقه
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
    if len(closes) < period + 1:
        return []

    gains = []
    losses = []

    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]

        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-change)

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    rsi_values = []

    if avg_loss == 0:
        rsi_values.append(100.0)
    else:
        rs = avg_gain / avg_loss
        rsi_values.append(100 - (100 / (1 + rs)))

    for i in range(period, len(gains)):
        avg_gain = (
            (avg_gain * (period - 1)) + gains[i]
        ) / period

        avg_loss = (
            (avg_loss * (period - 1)) + losses[i]
        ) / period

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

    request = urllib.request.Request(
        url,
        data=data
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode())


def main():
    candles = get_candles()

    if len(candles) < RSI_PERIOD + 2:
        print("Not enough candle data.")
        return

    # مرتب‌سازی کندل‌ها از قدیمی به جدید
    candles.sort(key=lambda x: x[0])

    # آخرین کندل ممکن است هنوز در حال تشکیل باشد
    closed_candles = candles[:-1]

    closes = [
        float(candle[4])
        for candle in closed_candles
    ]

    rsi_values = calculate_rsi(
        closes,
        RSI_PERIOD
    )

    if not rsi_values:
        print("Could not calculate RSI.")
        return

    rsi = rsi_values[-1]
    price = closes[-1]

    print(f"BTC-USD Price: {price:,.2f}")
    print(f"RSI(14): {rsi:.2f}")

    if rsi > 70:
        message = (
            "🔴 BTC RSI ALERT\n\n"
            f"BTC-USD: {price:,.2f}\n"
            f"RSI(14): {rsi:.2f}\n"
            "⏱ Timeframe: 5m\n\n"
            "⚠️ RSI بالای 70 قرار گرفت."
        )

        send_telegram(message)
        print("Telegram alert sent.")

    elif rsi < 30:
        message = (
            "🟢 BTC RSI ALERT\n\n"
            f"BTC-USD: {price:,.2f}\n"
            f"RSI(14): {rsi:.2f}\n"
            "⏱ Timeframe: 5m\n\n"
            "⚠️ RSI زیر 30 قرار گرفت."
        )

        send_telegram(message)
        print("Telegram alert sent.")

    else:
        print("No alert. RSI is between 30 and 70.")


if __name__ == "__main__":
    main()
