#!/usr/bin/env python3
"""Fetch only market values attached to exact DPBOSS market headings."""
import json
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "results.json"
LIVE_URL = "https://dpbossss.com/"
MARKETS = {
    "time-bazar": ("Time Bazar", ("TIME BAZAR",)),
    "milan-day": ("Milan Day", ("MILAN DAY",)),
    "rajdhani-day": ("Rajdhani Day", ("RAJDHANI DAY",)),
    "kalyan": ("Kalyan", ("KALYAN",)),
    "milan-night": ("Milan Night", ("MILAN NIGHT",)),
    "kalyan-night": ("Kalyan Night", ("KALYAN NIGHT",)),
    "rajdhani-night": ("Rajdhani Night", ("RAJDHANI NIGHT",)),
    "main-bazar": ("Main Bazar", ("MAIN BAZAR",)),
    "sridevi": ("Sridevi", ("SRIDEVI",)),
    "sridevi-night": ("Sridevi Night", ("SRIDEVI NIGHT",)),
}
RESULT_RE = re.compile(r"(?<!\d)(\d{3}\s*[-–]\s*\d{1,2}(?:\s*[-–]\s*\d{3})?)(?!\d)")
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

def fetch_html():
    request = Request(LIVE_URL, headers={
        "User-Agent": "Mozilla/5.0 (compatible; DP777PublicResults/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urlopen(request, timeout=25) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        return response.read().decode("utf-8", errors="replace")

def norm(value):
    return re.sub(r"\s+", " ", value or "").strip().upper()

def extract_results(html):
    soup = BeautifulSoup(html, "html.parser")
    results = {}
    headings = [tag for tag in soup.find_all(HEADING_TAGS)]

    for market_id, (name, aliases) in MARKETS.items():
        for heading in headings:
            label = norm(heading.get_text(" ", strip=True))
            if label not in aliases:
                continue

            # Read the complete result card text, not individual text nodes.
            # The old parser could stop at a fragment such as "366-5" when
            # the remaining digits were rendered in adjacent spans.
            value = None
            for container in heading.parents:
                if getattr(container, "name", None) in {"body", "html", "[document]"}:
                    break
                nested_headings = [
                    h for h in container.find_all(HEADING_TAGS)
                    if norm(h.get_text(" ", strip=True)) in {
                        alias for _, market_aliases in MARKETS.values()
                        for alias in market_aliases
                    }
                ]
                # A card should contain this market heading only; do not read
                # a grid/container containing several markets.
                if len(nested_headings) > 1:
                    break
                combined = norm(container.get_text(" ", strip=True))
                label_pos = combined.find(label)
                if label_pos < 0:
                    continue
                tail = combined[label_pos + len(label):]
                match = RESULT_RE.search(tail)
                if match:
                    candidate = re.sub(r"\s*[-–]\s*", "-", match.group(1))
                    # Prefer a full panel result (xxx-xx-xxx) over a partial
                    # OPEN result (xxx-x); keep searching upward only while
                    # the container remains a single-card container.
                    value = candidate
                    if candidate.count("-") == 2:
                        break

            if value:
                results[market_id] = {
                    "name": name, "result": value, "source": LIVE_URL,
                    "source_label": label,
                }
                break

    values = [item["result"] for item in results.values()]
    if len(values) >= 4 and len(set(values)) == 1:
        raise RuntimeError("Repeated-value extraction rejected; previous feed preserved")
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
    old.setdefault("site", "DP 777")
    old.setdefault("charts", {})
    old.setdefault("updated_at", None)
    old.setdefault("updated_charts", 0)
    # Mark a result as newly published only when it changes from the previous
    # observed value. A page fetch timestamp alone does NOT prove that a market
    # result belongs to today; otherwise yesterday's result can be copied into
    # today's chart cell on every refresh.
    previous = old.get("latest_results", {}) if isinstance(old.get("latest_results", {}), dict) else {}
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    india_now = datetime.now(ZoneInfo("Asia/Kolkata"))
    india_today = india_now.date()
    week_start = india_today - timedelta(days=india_today.weekday())
    day_key = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][india_today.weekday()]
    chart_keys = {"sridevi": "sridevi-day", "sridevi-night": "sridevi", **{k: k for k in MARKETS if k not in ("sridevi", "sridevi-night")}}
    market_times = {
        "sridevi": ("11:25", "12:25"), "time-bazar": ("13:00", "14:00"),
        "milan-day": ("15:00", "17:00"), "rajdhani-day": ("15:15", "17:15"),
        "kalyan": ("15:45", "17:45"), "sridevi-night": ("19:30", "20:30"),
        "milan-night": ("20:55", "22:55"), "kalyan-night": ("21:20", "23:20"),
        "rajdhani-night": ("21:20", "23:30"), "main-bazar": ("21:00", "23:00"),
    }
    def current_chart_day_is_blank(market_id):
        chart_key = chart_keys.get(market_id, market_id)
        path = ROOT / "data" / "charts" / f"{chart_key}.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            chart = payload.get("charts", {}).get(chart_key, payload)
            for row in chart.get("rows", []):
                match = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})", str(row.get("date", "")))
                if not match:
                    continue
                day, month, year = map(int, match.groups())
                if year < 100:
                    year += 2000
                try:
                    start = datetime(year, month, day).date()
                except ValueError:
                    continue
                if start != week_start:
                    continue
                values = [str(row.get(f"{day_key} {part}", "")).strip() for part in ("Open", "Jodi")]
                return all(not v or re.fullmatch(r"[★☆*\s—-]+", v) for v in values)
        except (OSError, json.JSONDecodeError, TypeError):
            pass
        return False
    def within_market_window(market_id):
        bounds = market_times.get(market_id)
        if not bounds:
            return False
        now_minutes = india_now.hour * 60 + india_now.minute
        start_minutes = int(bounds[0][:2]) * 60 + int(bounds[0][3:])
        end_minutes = int(bounds[1][:2]) * 60 + int(bounds[1][3:])
        # Allow a short grace period after scheduled close because the
        # public board may still show the current day's OPEN-only value.
        return start_minutes <= now_minutes <= end_minutes + 120
    for market_id, item in current.items():
        prior = previous.get(market_id, {}) if isinstance(previous.get(market_id, {}), dict) else {}
        value = str(item.get("result", "")).strip()
        if prior.get("result") and str(prior.get("result")) != value:
            item["result_changed_at"] = fetched_at
        elif prior.get("result") == value and prior.get("result_changed_at"):
            item["result_changed_at"] = prior["result_changed_at"]
        elif re.fullmatch(r"\d{3}-\d{1,2}", value) and within_market_window(market_id) and current_chart_day_is_blank(market_id):
            # One-time bootstrap for an already-visible OPEN result when the
            # new change tracker is first deployed. Do not bootstrap complete
            # old results into today's chart merely because the page was fetched.
            item["result_changed_at"] = fetched_at
    old["live_source"] = LIVE_URL
    old["latest_results"] = current
    old["live_fetched_at"] = fetched_at
    old["live_status"] = "ok" if len(current) == len(MARKETS) else "partial" if current else "no-labelled-results"
    print(f"Found {len(current)}/{len(MARKETS)} exact-heading markets; absent markets will display as not published.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    live_feed = {
        "latest_results": current,
        "live_fetched_at": old["live_fetched_at"],
        "live_source": LIVE_URL,
        "live_status": old["live_status"],
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (ROOT / "data" / "latest_results.json").write_text(
        json.dumps(live_feed, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("Wrote compact live feed with", len(current), "market entries.")

if __name__ == "__main__":
    main()
