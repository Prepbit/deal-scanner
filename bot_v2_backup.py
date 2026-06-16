import time
import requests
import feedparser
import sqlite3
from datetime import datetime

# =========================
# CONFIG
# =========================

TELEGRAM_TOKEN = None
TELEGRAM_CHAT_ID = None

try:
    import os
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
except:
    pass

RSS_FEEDS = [
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://www.reuters.com/rssFeed/businessNews",
]

DB = "data/events.db"

# =========================
# INIT DB
# =========================

conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS seen (title TEXT PRIMARY KEY)")
conn.commit()

# =========================
# TELEGRAM
# =========================

def send(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ missing TELEGRAM_TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# =========================
# SCORING (simple hedge fund style)
# =========================

KEYWORDS = {
    "acquisition": 50,
    "merger": 50,
    "buyout": 60,
    "stake": 40,
    "sec": 30,
    "investigation": 35,
    "bankruptcy": 45,
    "deal": 30,
    "partnership": 25,
    "earnings": 10,
}

def score(text):
    t = text.lower()
    s = 0
    for k, v in KEYWORDS.items():
        if k in t:
            s += v
    return s

# =========================
# FETCH RSS
# =========================

def fetch_rss():
    out = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for e in feed.entries:
            out.append(e.title)
    return out

# =========================
# MAIN LOOP
# =========================

print("🚀 Hedge Fund Scanner v2 started")

while True:

    events = fetch_rss()

    print(f"📡 events: {len(events)}")

    for title in events:

        c.execute("SELECT 1 FROM seen WHERE title=?", (title,))
        if c.fetchone():
            continue

        c.execute("INSERT INTO seen VALUES (?)", (title,))
        conn.commit()

        s = score(title)

        print("NEWS:", title)
        print("SCORE:", s)

        if s >= 40:
            msg = f"🚨 EVENT\n\n{title}\n\nScore: {s}"
            print("SEND:", msg)
            send(msg)

    time.sleep(60)
