
import json
import os
import time
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
