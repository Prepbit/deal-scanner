import feedparser

SEC_FEED = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-k&output=atom"

def get_events():
    results = []

    try:
        feed = feedparser.parse(SEC_FEED)

        for entry in feed.entries:
            results.append(entry.title)

    except Exception as e:
        print(e)

    return results
