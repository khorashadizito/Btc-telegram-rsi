import os
import urllib.parse
import urllib.request

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


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
    send_telegram("✅ تست ربات BTC RSI با موفقیت انجام شد")
    print("Telegram test message sent successfully.")


if __name__ == "__main__":
    main()
