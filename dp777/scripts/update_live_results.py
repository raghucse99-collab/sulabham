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
    "time-bazar": ("Time Bazar", ("TIME BAZAR",)),
    "milan-day": ("Milan Day", ("MILAN DAY",)),
    "rajdhani-day": ("Rajdhani Day", ("RAJDHANI DAY",)),
    "kalyan": ("Kalyan", ("KALYAN",)),
    "milan-night": ("Milan Night", ("MILAN NIGHT",)),
    "kalyan-night": ("Kalyan Night", ("KALYAN NIGHT",)),
    "rajdhani-night": ("Rajdhani Night", ("RAJDHANI NIGHT",)),
    "main-bazar": ("Main Bazar", ("MAIN BAZAR",)),
}
# Accept formats visible on the public page: 780-5 and 188-74-220.
RESULT_RE = re.compile(r"(?<!\d)(\d{3}\s*[-–]\s*\d{1,2}(?:\s*[-–]\s*\d{3})?)(?!\d)")

def fetch_url(url, timeout=25):
    request = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; DP777PublicResults/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} for {url}")
        return response.read().decode("utf-8", errors="replace")

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
    # Fetch Sridevi Night separately so it has the same live-result refresh path.
    sridevi_night_url = "https://dpbossss.com/panel-chart-record/sridevi-night.php?full_chart"
    try:
        request = Request(sridevi_night_url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; DP777PublicResults/1.0)",
            "Accept": "text/html,application/xhtml+xml",
        })
        with urlopen(request, timeout=20) as response:
            sridevi_night_html = response.read().decode("utf-8", errors="replace")
        night_soup = BeautifulSoup(sridevi_night_html, "html.parser")
        night_text = re.sub(r"\s+", " ", night_soup.get_text(" ", strip=True))
        # Accept the published OPEN-only value (e.g. 456-5) immediately;
        # do not wait for the CLOSE panel to appear later.
        night_match = re.search(
            r"\bSRIDEVI\s*NIGHT\b.{0,180}?(\d{3}\s*[-–]\s*\d{1,2}(?:\s*[-–]\s*\d{3})?)",
            night_text, re.I
        )
        if night_match:
            results["sridevi-night"] = {
                "name": "Sridevi Night",
                "result": re.sub(r"\s*[-–]\s*", "-", night_match.group(1)),
                "source": sridevi_night_url,
                "source_label": "SRIDEVI NIGHT",
            }
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
        print(f"Sridevi Night chart fetch failed; leaving it unpublished: {error}")
    # Sridevi Morning is published on the DPBOSS homepage every day.
    # Use its exact card label and store it under the DP 777 Sridevi market key;
    # never derive the morning result from the separate Sridevi Night card.
    sridevi_morning_url = "https://dpbossss.com/"
    try:
        morning_soup = BeautifulSoup(fetch_url(sridevi_morning_url, 20), "html.parser")
        labels = morning_soup.find_all(
            string=lambda value: value and re.sub(r"\\s+", " ", value).strip().upper() == "SRIDEVI MORNING"
        )
        for label in labels:
            node = label.parent
            for _ in range(8):
                if node is None:
                    break
                card_text = re.sub(r"\\s+", " ", node.get_text(" ", strip=True)).strip()
                upper = card_text.upper()
                other_market = re.search(r"\\b(SRIDEVI NIGHT|MAIN SRIDEVI DAY|SRIDEVI DAY)\\b", upper)
                if len(card_text) <= 1200 and not other_market and "SRIDEVI MORNING" in upper:
                    match = RESULT_RE.search(card_text)
                    if match:
                        value = re.sub(r"\\s*[-–]\\s*", "-", match.group(1))
                        results["sridevi"] = {
                            "name": "Sridevi", "result": value,
                            "source": sridevi_morning_url,
                            "source_label": "SRIDEVI MORNING on DPBOSS",
                        }
                        break
                node = node.parent
            if results.get("sridevi", {}).get("source") == sridevi_morning_url:
                break
    except (HTTPError, URLError, TimeoutError, OSError, RuntimeError, ValueError) as error:
        print(f"DPBOSS Sridevi Morning fetch failed; leaving it unpublished: {error}")

    # On Sundays, use the live-results card for Sridevi Day. The result may
    # be OPEN-only (e.g. 570-2), so do not require a completed three-part result.
    india_now = datetime.now(timezone.utc).astimezone(__import__("zoneinfo").ZoneInfo("Asia/Kolkata"))
    if india_now.weekday() == 6:
        sridevi_live_url = "https://sattamatkahub.in/"
        try:
            live_soup = BeautifulSoup(fetch_url(sridevi_live_url, 20), "html.parser")
            labels = live_soup.find_all(string=lambda value: value and value.strip().upper() == "SRIDEVI")
            for label in labels:
                node = label.parent
                for _ in range(8):
                    if node is None:
                        break
                    card_text = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()
                    # A live result card contains the JODI/PANEL labels and
                    # a valid result; keep this search local to the card.
                    if len(card_text) <= 1200 and re.search(r"\bJODI\b", card_text, re.I) and re.search(r"\bPANEL\b", card_text, re.I):
                        match = RESULT_RE.search(card_text)
                        if match:
                            value = re.sub(r"\s*[-–]\s*", "-", match.group(1))
                            results["sridevi"] = {
                                "name": "Sridevi", "result": value,
                                "source": sridevi_live_url,
                                "source_label": "Sridevi Sunday live-results card",
                            }
                            break
                    node = node.parent
                if "sridevi" in results:
                    break
        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError, ValueError) as error:
            print(f"Sunday Sridevi live card fetch failed; leaving it unpublished: {error}")
    # Sunday Sridevi Night uses the same live results card as Sridevi Day.
    # Monday-Saturday Sridevi Night remains sourced from the public Telegram channel.
    if india_now.weekday() == 6:
        sridevi_night_live_url = "https://sattamatkahub.in/"
        found_night = False
        try:
            live_soup = BeautifulSoup(fetch_url(sridevi_night_live_url, 20), "html.parser")
            labels = live_soup.find_all(
                string=lambda value: value and re.sub(r"\s+", " ", value).strip().upper() == "SRIDEVI NIGHT"
            )
            for label in labels:
                node = label.parent
                for _ in range(8):
                    if node is None:
                        break
                    card_text = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()
                    if len(card_text) <= 1200 and re.search(r"\bJODI\b", card_text, re.I) and re.search(r"\bPANEL\b", card_text, re.I):
                        match = RESULT_RE.search(card_text)
                        if match:
                            value = re.sub(r"\s*[-–]\s*", "-", match.group(1))
                            results["sridevi-night"] = {
                                "name": "Sridevi Night", "result": value,
                                "source": sridevi_night_live_url,
                                "source_label": "Sridevi Night Sunday live-results card",
                            }
                            found_night = True
                            break
                    node = node.parent
                if found_night:
                    break
        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError, ValueError) as error:
            print(f"Sunday Sridevi Night live card fetch failed: {error}")
        if not found_night:
            # Never show a stale Telegram/chart value as Sunday's live result.
            results.pop("sridevi-night", None)

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

    # These values were confirmed by the site owner as previous results,
    # not today's newly published results. Suppress them until the source
    # actually changes to a different value for that market.
    known_stale_results = {
        "milan-night": "350-88-567",
        "rajdhani-night": "369-81-245",
        "main-bazar": "240-61-380",
    }
    for market_id, stale_value in known_stale_results.items():
        if current.get(market_id, {}).get("result") == stale_value:
            current.pop(market_id, None)

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
    # Show only results actually present on the source in this fetch. Do not
    # merge missing markets from an earlier fetch: that makes yesterday's
    # numbers look like today's unpublished results.
    old["latest_results"] = current
    old["live_fetched_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    old["live_status"] = (
        "ok" if len(current) == len(MARKETS)
        else "partial" if current
        else "no-labelled-results"
    )
    print(f"Found {len(current)}/{len(MARKETS)} published markets in this source fetch; unlisted markets will display as not published.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # A compact feed lets the browser show results without downloading the full archive.
    live_feed = {
        "latest_results": old.get("latest_results", {}),
        "live_fetched_at": old.get("live_fetched_at"),
        "live_source": old.get("live_source", LIVE_URL),
        "live_status": old.get("live_status", "unknown"),
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (ROOT / "data" / "latest_results.json").write_text(
        json.dumps(live_feed, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("Wrote compact live feed with", len(live_feed["latest_results"]), "market entries.")


if __name__ == "__main__":
    main()
