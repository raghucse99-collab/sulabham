#!/usr/bin/env python3
"""Append today's published results into each market's dated weekly chart row."""
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FEED = DATA / "latest_results.json"
CHARTS = DATA / "charts"
TZ = ZoneInfo("Asia/Kolkata")
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MARKET_TO_CHART = {
    "sridevi": "sridevi-day",
    "sridevi-night": "sridevi",
    "time-bazar": "time-bazar",
    "milan-day": "milan-day",
    "rajdhani-day": "rajdhani-day",
    "kalyan": "kalyan",
    "milan-night": "milan-night",
    "kalyan-night": "kalyan-night",
    "rajdhani-night": "rajdhani-night",
    "main-bazar": "main-bazar",
}
MARKET_TIMES = {
    "sridevi": ("11:25", "12:25"), "time-bazar": ("13:00", "14:00"),
    "milan-day": ("15:00", "17:00"), "rajdhani-day": ("15:15", "17:15"),
    "kalyan": ("15:45", "17:45"), "sridevi-night": ("19:30", "20:30"),
    "milan-night": ("20:55", "22:55"), "kalyan-night": ("21:20", "23:20"),
    "rajdhani-night": ("21:20", "23:30"), "main-bazar": ("21:00", "23:00"),
}
RESULT_RE = re.compile(r"^(\d{3})-(\d{1,2})-(\d{3})$")
PARTIAL_RE = re.compile(r"^(\d{3})-(\d{1,2})$")
OPEN_RE = re.compile(r"^(?:OPEN:)?(\d{3})$")

def _within_market_window(market_id, now):
    bounds = MARKET_TIMES.get(market_id)
    if not bounds:
        return False
    if now.weekday() == 6 and market_id not in ("sridevi", "sridevi-night"):
        return False
    minutes = now.hour * 60 + now.minute
    to_minutes = lambda value: int(value[:2]) * 60 + int(value[3:])
    return to_minutes(bounds[0]) <= minutes <= to_minutes(bounds[1])

def week_bounds(today):
    monday = today - timedelta(days=today.weekday())
    return monday, monday + timedelta(days=6)

def date_label(start, end):
    return f"{start:%d-%m-%Y} to {end:%d-%m-%Y}"

def _is_placeholder(value):
    value = str(value or "").strip()
    return not value or bool(re.fullmatch(r"[★☆*\s—-]+", value))

def _real_value_count(row):
    return sum(1 for key, value in row.items() if key != "date" and not _is_placeholder(value))

def _collapse_rows_by_week(rows):
    """Merge rows with the same week-start date, keeping all real results."""
    merged = {}
    order = []
    for incoming in rows:
        row = dict(incoming)
        key = _row_start(row)
        if key == datetime.min.date():
            key = ("raw", str(row.get("date", "")))
        if key not in merged:
            merged[key] = row
            order.append(key)
            continue
        current = merged[key]
        # Keep the date label belonging to the row with more actual results.
        if _real_value_count(row) > _real_value_count(current):
            preferred, other = row, current
        else:
            preferred, other = current, row
        # Merge day fields without replacing a real value with a star/blank.
        for field, value in other.items():
            if field == "date":
                continue
            if _is_placeholder(preferred.get(field)) and not _is_placeholder(value):
                preferred[field] = value
        merged[key] = preferred
    result = [merged[key] for key in order]
    result.sort(key=lambda row: _row_start(row))
    return result

def row_for_week(rows, start, end):
    # Historical source charts may label the same week as ending Friday,
    # Saturday, or Sunday. Match by Monday/week-start, not the exact end date.
    rows[:] = _collapse_rows_by_week(rows)
    for row in rows:
        if _row_start(row) == start:
            return row
    row = {"date": date_label(start, end)}
    for day in DAYS:
        row[f"{day} Open"] = "★"
        row[f"{day} Jodi"] = "★"
        row[f"{day} Close"] = "★"
    rows.append(row)
    rows.sort(key=lambda r: _row_start(r))
    return row

def _row_start(row):
    dates = re.findall(r"(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})", str(row.get("date", "")))
    if not dates:
        return datetime.min.date()
    d, m, y = dates[0]
    year = int(y) + (2000 if int(y) < 100 else 0)
    try:
        return datetime(year, int(m), int(d)).date()
    except ValueError:
        return datetime.min.date()

def _result_trading_date(stamp, market_id):
    """Night-market results posted shortly after midnight belong to prior session day."""
    local = stamp.astimezone(TZ)
    if market_id in {"milan-night", "kalyan-night", "rajdhani-night", "main-bazar", "sridevi-night"} and local.hour < 6:
        return local.date() - timedelta(days=1)
    return local.date()

def main():
    today = datetime.now(TZ).date()
    start, end = week_bounds(today)
    feed = json.loads(FEED.read_text(encoding="utf-8"))
    latest = feed.get("latest_results", {})
    updated = 0
    for market_id, chart_key in MARKET_TO_CHART.items():
        path = CHARTS / f"{chart_key}.json"
        if not path.exists():
            print(f"Skip missing chart file: {path.name}")
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            chart = doc.get("charts", {}).get(chart_key, doc)
            rows = chart.get("rows")
            if not isinstance(rows, list):
                print(f"Skip chart without rows: {path.name}")
                continue
            row = row_for_week(rows, start, end)
            # Always keep the current dated week visible, even before a result is published.
            day = DAYS[today.weekday()]
            item = latest.get(market_id, {})
            posted = str(item.get("telegram_posted_at", ""))
            # Telegram items must carry a post timestamp from today. For non-Telegram
            # live cards, the current fetch timestamp can date the observation.
            # Only place homepage results into today's chart when the observed
            # result actually changed today. A routine fetch timestamp does not
            # prove that the displayed result is today's result.
            source_stamp = posted if str(item.get("source", "")).startswith("https://t.me/") else str(item.get("result_changed_at") or "")
            try:
                stamp = _result_trading_date(datetime.fromisoformat(source_stamp.replace("Z", "+00:00")), market_id)
            except (ValueError, TypeError):
                stamp = None
            result_text = str(item.get("result", "")).strip()
            # Only a complete result with evidence that it changed today may
            # enter the historical chart. Partial Open/Jodi values belong in Live
            # only and must never be written into chart cells.
            match = RESULT_RE.fullmatch(result_text)
            if item and stamp == today and match:
                op, jodi, cl = match.groups()
                row[f"{day} Open"] = op
                row[f"{day} Jodi"] = jodi.zfill(2)
                row[f"{day} Close"] = cl
                updated += 1
            chart["rows"] = rows
            chart["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            if "charts" in doc:
                doc["charts"][chart_key] = chart
            else:
                doc = chart
            doc["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            path.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            print(f"Could not update {path.name}: {exc}")
            raise
    # Keep the separate Milan Day 1992–2026 Jodi archive synchronized with the
    # authoritative Milan Day weekly chart. This adds/updates the current week
    # while preserving all older archive rows and never fabricating unpublished Jodis.
    source_path = CHARTS / "milan-day.json"
    archive_path = CHARTS / "milan-day-archive.json"
    if source_path.exists() and archive_path.exists():
        source_doc = json.loads(source_path.read_text(encoding="utf-8"))
        source_chart = source_doc.get("charts", {}).get("milan-day", source_doc)
        archive_doc = json.loads(archive_path.read_text(encoding="utf-8"))
        archive_chart = archive_doc.get("charts", {}).get("milan-day-archive", archive_doc)
        source_rows = source_chart.get("rows", [])
        archive_rows = archive_chart.get("rows", [])
        def week_key(row):
            return _row_start(row).isoformat()
        positions = {week_key(row): i for i, row in enumerate(archive_rows) if week_key(row) != datetime.min.date().isoformat()}
        for source_row in source_rows:
            key = week_key(source_row)
            if key == datetime.min.date().isoformat():
                continue
            archive_row = archive_rows[positions[key]] if key in positions else {"date": source_row.get("date", "")}
            for day in DAYS:
                value = str(source_row.get(f"{day} Jodi", "") or "").strip()
                if value and not re.fullmatch(r"[*★☆—-]+", value):
                    archive_row[f"{day} Jodi"] = value.zfill(2)
                else:
                    archive_row.setdefault(f"{day} Jodi", "")
            if key not in positions:
                positions[key] = len(archive_rows)
                archive_rows.append(archive_row)
        archive_rows.sort(key=_row_start)
        archive_chart["rows"] = archive_rows
        archive_chart["record_count"] = len(archive_rows)
        archive_chart["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if "charts" in archive_doc:
            archive_doc["charts"]["milan-day-archive"] = archive_chart
        else:
            archive_doc = archive_chart
        archive_doc["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        archive_path.write_text(json.dumps(archive_doc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        print(f"Synchronized Milan Day archive: {len(archive_rows)} weekly rows.")
    print(f"Ensured dated week {date_label(start, end)} exists for all charts; wrote {updated} complete results.")

if __name__ == "__main__":
    main()
