KEYWORDS = {
    "acquisition": 40,
    "acquire": 40,
    "takeover": 50,
    "take-private": 60,
    "merger": 40,
    "buyout": 50,
    "activist": 30,
    "13d": 40,
    "tender offer": 50,
    "strategic review": 30,
    "spin-off": 25,
}

def score(text):
    total = 0

    t = text.lower()

    for k, v in KEYWORDS.items():
        if k in t:
            total += v

    return total
