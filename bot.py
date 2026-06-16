import time
import requests
import feedparser
import re
import os

TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

RSS_FEEDS = [
    "https://feeds.bloomberg.com/markets/news.rss",
]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def parse(text):
    tickers = re.findall(r"\$([A-Z]+)", text)
    return {
        "raw": text,
        "ticker": tickers[0] if tickers else None,
	"type": "acquisition" if "acquisition" in text.lower() else "unknown",
        "take_private": "take-private" in text.lower(),
        "rumor": "rumor" in text.lower(),
        "spread": 0.10
    }

def run():
    seen = set()
    send_telegram("🟢 BOT STARTED OK")

    while True:
        for url in RSS_FEEDS:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                if entry.title in seen:
                    continue

                seen.add(entry.title)

                d = parse(entry.title)

		score = 50
                
		if score > 35:
                    send_telegram("🚨 TEST SIGNAL\n" + entry.title)
                if "acquisition" in entry.title.lower():
                    send_telegram(f"🚨 DEAL SIGNAL\n\n{entry.title}")

        time.sleep(60)

if __name__ == "__main__":
    run()
