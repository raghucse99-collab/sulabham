#!/usr/bin/env python3
"""Refresh latest published results; report partial source coverage for diagnosis."""
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
    "sridevi-day": ("Sridevi Day", ("SRIDEVI DAY", "SRIDEVI (DAY)")),
    "time-bazar": ("Time Bazar", ("TIME BAZAR",)),
    "milan-day": ("Milan Day", ("MILAN DAY",)),
    "rajdhani-day": ("Rajdhani Day", ("RAJDHANI DAY",)),
    "kalyan": ("Kalyan", ("KALYAN",)),
    "sridevi": ("Sridevi Night", ("SRIDEVI NIGHT",)),
    "milan-night": ("Milan Night", ("MILAN NIGHT",)),
    "kalyan-night": ("Kalyan Night", ("KALYAN NIGHT",)),
    "rajdhani-night": ("Rajdhani Night", ("RAJDHANI NIGHT",)),
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
    # Reject a candidate container if it also contains another market label.
    # This prevents a nearby/first result from a multi-market section being
    # copied into several market cards.
    all_aliases = {
        alias
        for _market_id, (_name, aliases) in MARKETS.items()
        for alias in aliases
    }
    for market_id, (name, aliases) in MARKETS.items():
        matched = None
        for alias in aliases:
            labels = soup.find_all(
                string=lambda value: value and re.sub(r"\s+", " ", value).strip().upper() == alias
            )
            for label in labels:
                node = label.parent
                for _ in range(7):
                    if node is None:
                        break
                    text = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()
                    upper = text.upper()
                    # Only accept a compact container that identifies this
                    # market and does not include a different market's label.
                    other_market_found = any(
                        other != alias and re.search(r"(?<![A-Z])" + re.escape(other) + r"(?![A-Z])", upper)
                        for other in all_aliases
                    )
                    if alias in upper and not other_market_found and len(text) <= 260:
                        match = RESULT_RE.search(text)
                        if match:
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
    # Fail closed if a source layout causes one value to be copied to many
    # markets. Identical values can occur legitimately, so only reject an
    # all-markets-identical extraction (a common broad-container failure).
    values = [item["result"] for item in results.values()]
    if len(values) >= 4 and len(set(values)) == 1:
        raise RuntimeError("Live result extraction produced one repeated value across markets; preserved prior results")
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
    # Seed the JSON structure if a previous race or failed update left it empty.
    old.setdefault("site", "DP 777")
    old.setdefault("charts", {})
    old.setdefault("updated_at", None)
    old.setdefault("updated_charts", 0)
    old.setdefault("latest_results", {})
    old.setdefault("live_source", LIVE_URL)
    if current:
        # Merge only markets confidently extracted in this run. A partial source
        # response must not erase valid results already stored for other markets.
        previous = old.get("latest_results", {})
        if not isinstance(previous, dict):
            previous = {}
        old["latest_results"] = {**previous, **current}
        old["live_fetched_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        old["live_status"] = "partial" if len(current) < len(MARKETS) else "ok"
        print(f"Updated {len(current)}/{len(MARKETS)} markets; preserved existing values for {len(set(previous) - set(current))} markets not found this run.")
    else:
        old["live_status"] = "no-labelled-results"
        print("No labelled live results matched; preserved previous results.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
