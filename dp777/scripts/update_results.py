#!/usr/bin/env python3
"""Fetch public historical chart tables for DP 777.
This archives published records only; it does not generate predictions.
"""
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "results.json"
SOURCES = {
    "sridevi-day": ("Sridevi Day", "https://dpbossss.com/panel-chart-record/sridevi-day.php"),
    "time-bazar": ("Time Bazar", "https://dpbosss.tax/panel-chart-record/time-bazar.php"),
    "milan-day": ("Milan Day", "https://dpbossss.net/panel-chart-record/milan-day.php"),
    "rajdhani-day": ("Rajdhani Day", "https://dpbossss.net/panel-chart-record/rajdhani-day.php"),
    "kalyan": ("Kalyan", "https://dpboss.direct/panel-chart-record/kalyan"),
    "sridevi": ("Sridevi Night", "https://dpbossss.com/panel-chart-record/sridevi-night.php"),
    "milan-night": ("Milan Night", "https://dpboss247.com/chart/panel/milan-night"),
    "kalyan-night": ("Kalyan Night", "https://dpboss247.com/chart/panel/kalyan-night"),
    "rajdhani-night": ("Rajdhani Night", "https://dpboss247.com/chart/panel/rajdhani-night"),
    "main-bazar": ("Main Bazar", "https://dpboss247.com/chart/panel/main-bazar"),
}
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def text_of(cell):
    return re.sub(r"\s+", " ", cell.get_text(" ", strip=True)).strip()

def fetch_html(url):
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urlopen(req, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        return response.read().decode("utf-8", errors="replace")

def extract_table(html, chart_id=None):
    soup = BeautifulSoup(html, "html.parser")
    best = None
    best_score = 0
    for table in soup.find_all("table"):
        txt = text_of(table).lower()
        score = int("date" in txt) + sum(day.lower() in txt for day in ["mon", "tue", "wed", "thu", "fri"])
        if score > best_score and ("20" in txt or "19" in txt):
            best, best_score = table, score
    if not best:
        raise RuntimeError("Could not find the historical date/week table; source layout may have changed")
    trs = best.find_all("tr")
    header = []
    raw_rows = []
    for tr in trs:
        cells = tr.find_all(["th", "td"], recursive=False)
        vals = [text_of(c) for c in cells]
        if not vals:
            continue
        joined = " ".join(vals).lower()
        if not raw_rows and ("date" in joined or any(d.lower() in joined for d in DAYS)):
            header = vals
            continue
        if (chart_id == "sridevi" and len(vals) >= 5 and (re.search(r"\d{2}[-/]\d{2}[-/]\d{2,4}", vals[0]) or vals[0].strip().lower() == "to")) or (chart_id != "sridevi" and re.search(r"\d{2}[-/]\d{2}[-/]\d{2,4}", vals[0])):
            raw_rows.append(vals)
    if not raw_rows:
        # Some layouts place the range in a nested element or use a separate header row.
        for tr in trs:
            cells = tr.find_all(["th", "td"], recursive=False)
            vals = [text_of(c) for c in cells]
            if vals and re.search(r"\d{2}[-/]\d{2}[-/]\d{2,4}", vals[0]) and len(vals) > 1:
                raw_rows.append(vals)
    if not raw_rows:
        raise RuntimeError("Found chart table but no dated records")
    # A weekly panel chart stores THREE cells per weekday: open panna, jodi, close panna.
    # Keep each cell separate; never infer one value by splitting another cell's text.
    max_cells = max(len(row) for row in raw_rows)
    day_headers = []
    for value in header[1:]:
        match = re.search(r"mon|tue|wed|thu|fri|sat|sun", value, re.I)
        if match:
            day = match.group(0).title()
            if day not in day_headers:
                day_headers.append(day)
    if not day_headers:
        day_headers = DAYS[:min(7, max(1, (max_cells - 1) // 3))]
    keys = ["date"]
    for day in day_headers:
        keys.extend([f"{day} Open", f"{day} Jodi", f"{day} Close"])
    rows = []
    for raw in raw_rows:
        item = {"date": raw[0]}
        for i, key in enumerate(keys[1:], start=1):
            value = raw[i] if i < len(raw) else ""
            value = re.sub(r"\s+", "", value) if key.endswith(("Open", "Close")) and re.fullmatch(r"[\d\s]+", value or "") else value.strip()
            # Star/asterisk placeholders are preserved as missing-result markers.
            if value in ("*", "**", "***"):
                value = "***"
            item[key] = value
        rows.append(item)
    # Some source pages repeat the final weekday column because their HTML
    # table has a merged/duplicated cell. Detect a systematic copy of the
    # previous day's complete Open/Jodi/Close triple and blank that suspicious
    # column rather than presenting false duplicate results as real data.
    day_names = [d for d in DAYS if any(k.startswith(d + " ") for k in rows[0])]
    if len(day_names) >= 2 and len(rows) >= 4:
        for idx in range(1, len(day_names)):
            prev_day, day = day_names[idx - 1], day_names[idx]
            comparable = 0
            same_triples = 0
            for item in rows:
                prev = tuple(item.get(f"{prev_day} {part}", "").strip() for part in ("Open", "Jodi", "Close"))
                cur = tuple(item.get(f"{day} {part}", "").strip() for part in ("Open", "Jodi", "Close"))
                if all(v and not re.fullmatch(r"\*+", v) for v in prev + cur):
                    comparable += 1
                    if cur == prev:
                        same_triples += 1
            if comparable >= 4 and same_triples / comparable >= 0.75:
                print(f"WARN {chart_id or 'chart'}: {day} column duplicates {prev_day} in {same_triples}/{comparable} rows; blanking suspicious copied values")
                for item in rows:
                    for part in ("Open", "Jodi", "Close"):
                        item[f"{day} {part}"] = ""
    # Keep original source order, but reject accidental non-chart rows.
    return header, rows

LIVE_URL = "https://dpbossg.mobi/"
LIVE_MARKETS = {
    "time-bazar": ("Time Bazar", ["TIME BAZAR"]),
    "milan-day": ("Milan Day", ["MILAN DAY"]),
    "main-mumbai": ("Main Mumbai", ["OLD MAIN MUMBAI", "MAIN MUMBAI"]),
    "sridevi": ("Sridevi Night", ["SRIDEVI NIGHT"]),
    "milan-night": ("Milan Night", ["MILAN NIGHT"]),
    "rajdhani-day": ("Rajdhani Day", ["RAJDHANI DAY"]),
    "rajdhani-night": ("Rajdhani Night", ["RAJDHANI NIGHT"]),
}

def extract_live_results(html):
    """Extract only complete published open-jodi-close triples from labelled cards."""
    soup = BeautifulSoup(html, "html.parser")
    found = {}
    result_re = re.compile(r"(?<!\d)(\d{3}\s*[-–]\s*\d{1,2}(?:\s*[-–]\s*\d{3})?)(?!\d)")
    for chart_id, (name, aliases) in LIVE_MARKETS.items():
        for alias in aliases:
            for label in soup.find_all(string=lambda s: s and re.sub(r"\s+", " ", s).strip().upper() == alias):
                node = label.parent
                for _ in range(5):
                    if node is None:
                        break
                    text = re.sub(r"\\s+", " ", node.get_text(" ", strip=True))
                    match = result_re.search(text)
                    # Avoid grabbing a result from a large page/container with many markets.
                    if match and len(text) <= 700:
                        found[chart_id] = {
                            "name": name,
                            "result": re.sub(r"\s*[-–]\s*", "-", match.group(1)),
                            "source": LIVE_URL,
                            "source_label": alias,
                        }
                        break
                    node = node.parent
                if chart_id in found:
                    break
            if chart_id in found:
                break
    return found

def fetch_live_results():
    html = fetch_html(LIVE_URL)
    results = extract_live_results(html)
    if not results:
        raise RuntimeError("Public page returned no labelled complete results; live values were not guessed")
    return results

def main():
    old = {}
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            old = {}
    charts = dict(old.get("charts", {}))
    updated_count = 0
    for chart_id, (name, url) in SOURCES.items():
        try:
            html = fetch_html(url)
            header, rows = extract_table(html, chart_id)
            charts[chart_id] = {
                "title": f"{name} historical records",
                "source": url,
                "rows": rows,
                "columns": list(rows[0].keys()) if rows else [],
                "record_count": len(rows),
                "status": "ok",
            }
            print(f"OK {name}: {len(rows)} rows")
            updated_count += 1
        except (HTTPError, URLError, TimeoutError, RuntimeError, ValueError) as exc:
            print(f"WARN {name}: {exc}")
            # Keep the last successful data instead of replacing it with empty data.
            if chart_id in charts:
                charts[chart_id]["status"] = "stale"
                charts[chart_id]["last_error"] = str(exc)
            else:
                charts[chart_id] = {
                    "title": f"{name} historical records",
                    "source": url,
                    "rows": [],
                    "columns": [],
                    "record_count": 0,
                    "status": "unavailable",
                    "last_error": str(exc),
                }
        time.sleep(1)  # be considerate to the source website
    # Avoid a commit every hour when source rows have not changed.
    previous_charts = old.get("charts", {})
    changed = any(
        previous_charts.get(chart_id, {}).get("rows") != charts.get(chart_id, {}).get("rows")
        or previous_charts.get(chart_id, {}).get("source") != charts.get(chart_id, {}).get("source")
        for chart_id in SOURCES
    )
    updated_at = datetime.now(timezone.utc).isoformat(timespec="seconds") if changed or not old.get("updated_at") else old["updated_at"]
    payload = {
        "site": "DP 777",
        "updated_at": updated_at,
        "updated_charts": updated_count,
        "latest_results": old.get("latest_results", {}),
        "live_fetched_at": old.get("live_fetched_at"),
        "live_source": old.get("live_source", "https://dpbossg.mobi/"),
        "live_status": old.get("live_status", "unknown"),
        "charts": charts,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if updated_count == 0:
        raise SystemExit("No source charts could be updated; existing data was preserved where available")

if __name__ == "__main__":
    main()

# Recovery run: rebuild the ten configured charts after repairing the JSON archive.
