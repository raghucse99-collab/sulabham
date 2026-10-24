#!/usr/bin/env python3
"""Refresh only the latest published results from the public DPBOSS page."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "results.json"
LIVE_URL = "https://dpbossg.mobi/"
MARKETS = {
    "time-bazar": ("Time Bazar", ("TIME BAZAR",)),
    "milan-day": ("Milan Day", ("MILAN DAY",)),
    "main-mumbai": ("Main Mumbai", ("MAIN MUMBAI", "OLD MAIN MUMBAI")),
    "sridevi": ("Sridevi Night", ("SRIDEVI NIGHT",)),
    "milan-night": ("Milan Night", ("MILAN NIGHT",)),
    "rajdhani-day": ("Rajdhani Day", ("RAJDHANI DAY",)),
    "rajdhani-night": ("Rajdhani Night", ("RAJDHANI NIGHT",)),
    "sridevi-day": ("Sridevi Day", ("SRIDEVI DAY", "SRIDEVI (DAY)")),
    "puna-bazar": ("Puna Bazar", ("PUNA BAZAR",)),
    "supreme-day": ("Supreme Day", ("SUPREME DAY",)),
    "main-bazar-day": ("Main Bazar Day", ("MAIN BAZAR DAY",)),
    "central-bombay": ("Central Bombay", ("CENTRAL BOMBAY",)),
    "star-tara-day": ("Star Tara Day", ("STAR TARA DAY",)),
    "andhra-day": ("Andhra Day", ("ANDHRA DAY",)),
    "cb": ("CB", ("CB",)),
    "gama-day": ("Gama Day", ("GAMA DAY",)),
    "kalyan": ("Kalyan", ("KALYAN",)),
    "kalyan-night": ("Kalyan Night", ("KALYAN NIGHT",)),
    "main-bazar": ("Main Bazar", ("MAIN BAZAR",)),
}
# Accept formats visible on the public page: 780-5 and 188-74-220.
RESULT_RE = re.compile(r"(?<!\d)(\d{3}\s*[-–]\s*\d{1,2}(?:\s*[-–]\s*\d{3})?)(?!\d)")

def fetch_html():
    request = Request(LIVE_URL, headers={
        "User-Agent": "Mozilla/5.0 (compatible; DP777PublicResults/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urlopen(request, timeout=25) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        return response.read().decode("utf-8", errors="replace")

def extract_results(html):
    soup = BeautifulSoup(html, "html.parser")
    results = {}
    for market_id, (name, aliases) in MARKETS.items():
        matched = None
        for alias in aliases:
            labels = soup.find_all(string=lambda value: value and re.sub(r"\s+", " ", value).strip().upper() == alias)
            for label in labels:
                node = label.parent
                # Walk from the market label to nearby card containers, not the whole page.
                for _ in range(6):
                    if node is None:
                        break
                    text = re.sub(r"\s+", " ", node.get_text(" ", strip=True))
                    match = RESULT_RE.search(text)
                    if match and len(text) <= 500:
                        value = re.sub(r"\s*[-–]\s*", "-", match.group(1))
                        matched = {
                            "name": name,
                            "result": value,
                            "source": LIVE_URL,
                            "source_label": alias,
                        }
                        break
                    node = node.parent
                if matched:
                    break
            if matched:
                break
        if matched:
            results[market_id] = matched
    return results

def main():
    try:
        current = extract_results(fetch_html())
    except (HTTPError, URLError, TimeoutError, RuntimeError, ValueError) as error:
        print(f"Live source fetch failed: {error}")
        raise SystemExit(1)

    old = {}
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            old = {}
    previous = old.get("latest_results", {})
    if current != previous:
        old["latest_results"] = current
        old["live_fetched_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        old["live_source"] = LIVE_URL
        old["live_status"] = "ok" if current else "no-labelled-results"
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Live results changed: {len(current)}/{len(MARKETS)} markets matched; data saved.")
    else:
        print(f"No live result changes: {len(current)}/{len(MARKETS)} markets matched.")
        # Do not create a new commit just to update a timestamp every five minutes.
        if not old.get("live_source") or not old.get("live_status"):
            old["live_source"] = LIVE_URL
            old["live_status"] = "ok" if current else "no-labelled-results"
            OUT.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
