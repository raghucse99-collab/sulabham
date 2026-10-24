#!/usr/bin/env python3
"""Supplement DP 777 live results from the public Telegram channel preview.

Only public posts are read. A result is accepted only when a market name and a
valid result pattern occur in the same Telegram message. If Telegram is
unavailable or its markup changes, the existing result feed is left untouched.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
FEED = ROOT / "data" / "latest_results.json"
ARCHIVE = ROOT / "data" / "results.json"
CHANNEL = "KMFAMILYRESULTS"
CHANNEL_URL = f"https://t.me/s/{CHANNEL}"
MARKETS = {
    "sridevi-day": ("Sridevi Day", (r"SRIDEVI\s*(?:\(\s*DAY\s*\)|DAY)",)),
    "time-bazar": ("Time Bazar", (r"TIME\s*BAZAR",)),
    "milan-day": ("Milan Day", (r"MILAN\s*DAY",)),
    "rajdhani-day": ("Rajdhani Day", (r"RAJDHANI\s*DAY",)),
    "kalyan": ("Kalyan", (r"(?<!NIGHT\s)KALYAN(?!\s*NIGHT)",)),
    "sridevi": ("Sridevi Night", (r"SRIDEVI\s*NIGHT",)),
    "milan-night": ("Milan Night", (r"MILAN\s*NIGHT",)),
    "kalyan-night": ("Kalyan Night", (r"KALYAN\s*NIGHT",)),
    "rajdhani-night": ("Rajdhani Night", (r"RAJDHANI\s*NIGHT",)),
    "main-bazar": ("Main Bazar", (r"MAIN\s*BAZAR",)),
}
RESULT_RE = re.compile(r"(?<!\d)(\d{3})\s*[-–]\s*(\d{1,2})(?:\s*[-–]\s*(\d{3}))?(?!\d)")
MARKET_PATTERNS = {key: [re.compile(p, re.I) for p in aliases] for key, (_n, aliases) in MARKETS.items()}

def fetch_page():
    request = Request(CHANNEL_URL, headers={
        "User-Agent": "Mozilla/5.0 (compatible; DP777PublicResults/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urlopen(request, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(f"Telegram returned HTTP {response.status}")
        return response.read().decode("utf-8", errors="replace")

def parse_posts(html):
    soup = BeautifulSoup(html, "html.parser")
    posts = soup.select(".tgme_widget_message_wrap")
    if not posts:
        posts = soup.select("[data-post]")
    found = {}
    for wrap in reversed(posts):
        post_node = wrap if wrap.has_attr("data-post") else wrap.select_one("[data-post]")
        if post_node is None:
            continue
        post_id = post_node.get("data-post", "")
        msg = wrap.select_one(".tgme_widget_message_text")
        if msg is None:
            continue
        body = re.sub(r"\s+", " ", msg.get_text(" ", strip=True)).strip()
        matches = list(RESULT_RE.finditer(body))
        if not body or not matches:
            continue
        link = f"https://t.me/{post_id}" if "/" in post_id else CHANNEL_URL
        time_node = wrap.select_one("time[datetime]")
        posted_at = time_node.get("datetime") if time_node else None
        for market_id, (name, _aliases) in MARKETS.items():
            if market_id in found:
                continue
            positions = [m.start() for p in MARKET_PATTERNS[market_id] for m in p.finditer(body)]
            if not positions:
                continue
            nearby = []
            for match in matches:
                distance = min(abs(match.start() - pos) for pos in positions)
                if distance <= 100:
                    nearby.append((distance, match))
            if len(nearby) == 1:
                chosen = nearby[0][1]
            elif len(matches) == 1:
                chosen = matches[0]
            elif nearby:
                nearby.sort(key=lambda x: x[0])
                if len(nearby) > 1 and nearby[0][0] == nearby[1][0]:
                    continue
                chosen = nearby[0][1]
            else:
                continue
            value = f"{chosen.group(1)}-{chosen.group(2)}"
            if chosen.group(3):
                value += f"-{chosen.group(3)}"
            found[market_id] = {
                "name": name, "result": value, "source": CHANNEL_URL,
                "source_label": f"Telegram @{CHANNEL}",
                "telegram_message_url": link, "telegram_posted_at": posted_at,
            }
    return found

def main():
    try:
        updates = parse_posts(fetch_page())
    except (HTTPError, URLError, TimeoutError, OSError, RuntimeError, ValueError) as exc:
        print(f"Telegram preview unavailable; keeping existing results: {exc}")
        return
    if not updates:
        print("No unambiguous market results found in visible Telegram posts; keeping existing results.")
        return
    try:
        feed = json.loads(FEED.read_text(encoding="utf-8"))
        archive = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Cannot read existing data; keeping it unchanged: {exc}")
        return
    feed_latest = feed.setdefault("latest_results", {})
    archive_latest = archive.setdefault("latest_results", {})
    changed = []
    for market_id, item in updates.items():
        old = feed_latest.get(market_id, {})
        if old.get("result") != item["result"] or old.get("source") != item["source"]:
            changed.append(f"{item['name']}={item['result']}")
        feed_latest[market_id] = item
        archive_latest[market_id] = item
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    feed["telegram_fetched_at"] = now
    feed["live_source"] = CHANNEL_URL
    feed["live_status"] = "telegram-updated" if changed else feed.get("live_status", "ok")
    archive["telegram_fetched_at"] = now
    archive["live_source"] = CHANNEL_URL
    if changed:
        feed["updated_at"] = now
        print("Telegram result values updated: " + ", ".join(changed))
    else:
        print(f"Telegram checked; {len(updates)} labelled results found; values unchanged.")
    FEED.write_text(json.dumps(feed, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    ARCHIVE.write_text(json.dumps(archive, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
