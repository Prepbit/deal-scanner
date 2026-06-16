import feedparser

RSS_FEEDS = [
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
]

def get_events():
    events = []

    for url in RSS_FEEDS:

        try:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                events.append(entry.title)

        except Exception as e:
            print(e)

    return events
