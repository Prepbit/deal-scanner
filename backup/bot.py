import os
import re
import time
import requests
import feedparser

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

FEEDS = [
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
]

KEYWORDS = {
    "acquisition": 40,
    "acquire": 40,
    "takeover": 50,
    "take-private": 60,
    "merger": 40,
    "buyout": 50,
    "activist": 25,
    "spin-off": 30,
    "spinoff": 30,
    "asset sale": 25,
    "strategic review": 35,
    "bankruptcy": 20,
    "chapter 11": 25,
    "offer": 20,
    "bid": 25,
}

SEEN = set()


def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("Telegram no configurado")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": msg,
            },
            timeout=15,
        )
    except Exception as e:
        print("telegram error:", e)


def score_title(title):
    score = 0
    lower = title.lower()

    for word, pts in KEYWORDS.items():
        if word in lower:
            score += pts

    return score


def process_entry(title):
    score = score_title(title)

    if score < 40:
        return

    message = (
        "🚨 EVENT DRIVEN SIGNAL\n\n"
        f"{title}\n\n"
        f"Score: {score}"
    )

    print(message)
    send_telegram(message)


def scan_feed(feed_url):
    try:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:

            title = entry.title.strip()

            if title in SEEN:
                continue

            SEEN.add(title)

            process_entry(title)

    except Exception as e:
        print(feed_url, e)


def main():
    print("Scanner iniciado")

    while True:

        for feed in FEEDS:
            scan_feed(feed)

        time.sleep(60)


if __name__ == "__main__":
    main()
