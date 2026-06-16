import time

from modules.scoring import score
from modules.telegram_sender import send
from modules.rss_scanner import get_events as rss_events
from modules.sec_scanner import get_events as sec_events

seen = set()

print("Scanner profesional iniciado")
print("Bot arrancado correctamente")

while True:

    print("Escaneando feeds...")

    events = []
    events.extend(rss_events())
    events.extend(sec_events())

    print(f"Eventos encontrados: {len(events)}")

    for title in events:

        if title in seen:
            continue

        seen.add(title)

        s = score(title)

        print("NEWS:", title)
        print("SCORE:", s)

        if s >= 40:

            msg = (
                "🚨 EVENT SIGNAL\n\n"
                f"{title}\n\n"
                f"Score={s}"
            )

            print("📤 sending:", msg)

            send(msg)

    time.sleep(60)
