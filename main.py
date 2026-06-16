import os
import time
import re
import requests
import feedparser
import yfinance as yf

from flask import Flask

# =====================
# CONFIG
# =====================
TOKEN = os.getenv("TELEGRAM_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

CHECK_INTERVAL = 60

RSS_FEEDS = [
    "https://feeds.bloomberg.com/markets/news.rss",
]

# =====================
# FLASK (KEEP ALIVE)
# =====================
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

# =====================
# TELEGRAM
# =====================
def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("Missing Telegram credentials")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# =====================
# PARSER
# =====================
def parse(text):

    tickers = re.findall(r"\$([A-Z]+)", text)

    return {
        "raw": text,
        "ticker": tickers[0] if tickers else None,
        "is_mna": any(x in text.lower() for x in ["acquisition", "merger", "buyout"]),
        "rumor": "rumor" in text.lower()
    }

# =====================
# SCORE
# =====================
def score(d):

    s = 0

    if d["is_mna"]:
        s += 30

    if d["ticker"]:
        s += 10

    if d["rumor"]:
        s -= 15

    return s

# =====================
# PROBABILITY
# =====================
def probability(d):

    p = 0.55

    if d["is_mna"]:
        p += 0.2

    if d["rumor"]:
        p -= 0.1

    return max(0.05, min(0.95, p))

# =====================
# EV ENGINE
# =====================
def expected_value(prob, spread):

    downside = 0.05

    return (prob * spread) - ((1 - prob) * downside)

# =====================
# ENGINE LOOP
# =====================
def run_engine():

    seen = set()

    while True:

        for url in RSS_FEEDS:

            feed = feedparser.parse(url)

            for entry in feed.entries:

                if entry.title in seen:
                    continue

                seen.add(entry.title)

                d = parse(entry.title)

                s = score(d)
                p = probability(d)

                spread = 0.10  # placeholder (luego lo mejoramos con precios reales)

                ev = expected_value(p, spread)

                if s > 35 and ev > 0.03:

                    send_telegram(
                        f"🚨 DEAL SIGNAL\n\n"
                        f"{entry.title}\n\n"
                        f"Score: {s}\n"
                        f"Prob: {p:.2f}\n"
                        f"EV: {ev:.3f}"
                    )

        time.sleep(CHECK_INTERVAL)

# =====================
# MAIN
# =====================
if __name__ == "__main__":

    from threading import Thread

    t1 = Thread(target=lambda: app.run(host="0.0.0.0", port=3000))
    t2 = Thread(target=run_engine)

    t1.start()
    t2.start()
