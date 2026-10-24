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
    "time-bazar": ("Time Bazar", "https://khabar.bet/time-bazar-matka-chart"),
    "milan-day": ("Milan Day", "https://khabar.bet/milan-day-matka-chart"),
    "main-mumbai": ("Main Mumbai", "https://khabar.bet/main-mumbai-matka-chart"),
    "sridevi": ("Sridevi", "https://khabar.bet/sridevi-matka-chart"),
    "milan-night": ("Milan Night", "https://khabar.bet/milan-night-matka-chart"),
    "rajdhani-day": ("Rajdhani Day", "https://khabar.bet/rajdhani-day-matka-chart"),
    "rajdhani-night": ("Rajdhani Night", "https://khabar.bet/rajdhani-night-matka-chart"),
}
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def text_of(cell):
    return re.sub(r"\s+", " ", cell.get_text(" ", strip=True)).strip()

def fetch_html(url):
    req = Request(url, headers={
        "User-Agent": "DP777-Historical-Archive/1.0 (public chart archive; contact site owner through repository)",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urlopen(req, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        return response.read().decode("utf-8", errors="replace")

def extract_table(html):
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
        if re.search(r"\d{2}/\d{2}/\d{2,4}", vals[0]):
            raw_rows.append(vals)
    if not raw_rows:
        # Some layouts place the range in a nested element or use a separate header row.
        for tr in trs:
            cells = tr.find_all(["th", "td"], recursive=False)
            vals = [text_of(c) for c in cells]
            if vals and re.search(r"\d{2}/\d{2}/\d{2,4}", vals[0]) and len(vals) > 1:
                raw_rows.append(vals)
    if not raw_rows:
        raise RuntimeError("Found chart table but no dated records")
    max_cells = max(len(row) for row in raw_rows)
    # Use stable descriptive columns. Most source charts have one cell per day
    # or separate panel/Jodi cells for each day.
    sample = max(raw_rows, key=len)
    n = max_cells - 1
    keys = ["date"]
    if n <= 7:
        keys += [f"{DAYS[i]} result" for i in range(n)]
    else:
        for i in range(n):
            day = DAYS[(i // 2) % len(DAYS)]
            kind = "Panel" if i % 2 == 0 else "Jodi"
            keys.append(f"{day} {kind}")
    rows = []
    for raw in raw_rows:
        item = {"date": raw[0]}
        for i, key in enumerate(keys[1:], start=1):
            item[key] = raw[i] if i < len(raw) else ""
        rows.append(item)
    # Keep original source order, but reject accidental non-chart rows.
    return header, rows

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
            header, rows = extract_table(html)
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
        "last_checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "updated_charts": updated_count,
        "charts": charts,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if updated_count == 0:
        raise SystemExit("No source charts could be updated; existing data was preserved where available")

if __name__ == "__main__":
    main()
