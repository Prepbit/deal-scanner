#!/bin/bash

set -e

echo "🚀 Installing Hedge Fund Scanner v3..."

cd ~/deal-scanner

pip3 install feedparser requests beautifulsoup4 lxml

mkdir -p modules data

cat > bot.py << 'EOF'
import time
import requests
import feedparser
import sqlite3

# =========================
# CONFIG
# =========================

import os
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")

RSS_FEEDS = [
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://www.reuters.com/rssFeed/businessNews",
]

X_FEED = "https://rss.app/feeds/REPLACE_WITH_X_FEED.xml"  # <- DealintCB aquí

SEC_FEED = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-k&count=40&output=atom"

DB = "data/scanner.db"

# =========================
# DB
# =========================

conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)")
conn.commit()

# =========================
# TELEGRAM
# =========================

def send(msg):
    if not TOKEN or not CHAT:
        print("⚠️ Missing Telegram env vars")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT, "text": msg}, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# =========================
# SCORING v3 (hedge fund style)
# =========================

WEIGHTS = {
    "merger": 60,
    "acquisition": 60,
    "buyout": 70,
    "takeover": 65,
    "stake": 45,
    "sec": 35,
    "form 8-k": 50,
    "bankruptcy": 55,
    "investigation": 40,
    "guidance": 20,
    "earnings": 15,
    "ceo": 10,
    "lawsuit": 35,
}

def score(text):
    t = text.lower()
    s = 0
    for k, v in WEIGHTS.items():
        if k in t:
            s += v
    return s

# =========================
# FETCHERS
# =========================

def fetch_rss(urls):
    out = []
    for u in urls:
        feed = feedparser.parse(u)
        for e in feed.entries:
            out.append(e.title)
    return out

def fetch_sec():
    feed = feedparser.parse(SEC_FEED)
    return [e.title for e in feed.entries]

# =========================
# MAIN LOOP
# =========================

print("🚀 Hedge Fund Scanner v3 started")

while True:

    events = []
    events += fetch_rss(RSS_FEEDS)
    events += fetch_rss([X_FEED])
    events += fetch_sec()

    print("📡 events:", len(events))

    for e in events:

        c.execute("SELECT 1 FROM seen WHERE id=?", (e,))
        if c.fetchone():
            continue

        c.execute("INSERT INTO seen VALUES (?)", (e,))
        conn.commit()

        s = score(e)

        print("NEWS:", e)
        print("SCORE:", s)

        if s >= 40:

            if s >= 70:
                level = "🔥 HIGH"
            elif s >= 50:
                level = "⚠️ MID"
            else:
                level = "ℹ️ LOW"

            msg = f"{level} EVENT\n\n{e}\n\nScore: {s}"
            print("SEND:", msg)
            send(msg)

    time.sleep(60)
EOF

echo "✅ v3 installed"
