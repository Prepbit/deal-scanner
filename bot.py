import time
import requests
import feedparser
import re
import os

TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

RSS_FEEDS = [
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://nitter.net/DealintCB/rss"
]

def send_telegram(msg):
    print("📤 sending:", msg)

    if not TOKEN or not CHAT_ID:
        print("⚠️ missing TELEGRAM_TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def hedge_filter(text):
    score = 0

    keywords = {
        "acquisition": 25,
        "take-private": 30,
        "merger": 20,
        "deal": 10,
        "buyout": 25,
        "SEC": 15,
        "investigation": 10,
        "rumor": -10
    }

    t = text.lower()

    for k, v in keywords.items():
        if k.lower() in t:
            score += v

    return score


def parse(text):
    tickers = re.findall(r"\$([A-Z]+)", text)

    return {
        "raw": text,
        "ticker": tickers[0] if tickers else None,
        "score": hedge_filter(text),
        "spread": 0.10
    }


def run():
    seen = set()

    print("🟢 BOT STARTED OK")

    while True:
        for url in RSS_FEEDS:
            print("🔄 checking:", url)

            feed = feedparser.parse(url)

            for entry in feed.entries:
                if entry.title in seen:
                    continue

                seen.add(entry.title)

                d = parse(entry.title)

                prob = 0.6
                ev = (prob * d["spread"]) - ((1 - prob) * 0.05)

                print("🧠 signal:", entry.title, "| score:", d["score"])

                if d["score"] > 25 and ev > 0.03:
                    send_telegram(
                        f"🚨 DEAL SIGNAL\n\n{entry.title}\nScore:{d['score']}\nEV:{ev:.3f}"
                    )

        time.sleep(60)


if __name__ == "__main__":
    run()
