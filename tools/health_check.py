#!/usr/bin/env python3
"""Read-only health checks for the Sulabham static website. Standard library only."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

SKIP = ("http:", "https:", "mailto:", "tel:", "data:", "javascript:", "blob:")

class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids = [], set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"): self.ids.add(a["id"])
        for key in ("href", "src", "poster"):
            if a.get(key): self.refs.append((a[key].strip(), key))

def scan_html(root, path, errors, warnings):
    try: text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as e:
        errors.append(f"{path.relative_to(root)}: cannot read: {e}"); return
    parser = Links()
    try: parser.feed(text)
    except Exception as e:
        errors.append(f"{path.relative_to(root)}: HTML parse error: {e}"); return
    for raw, attr in parser.refs:
        if not raw or raw.startswith("//") or raw.lower().startswith(SKIP): continue
        parts = urlsplit(raw)
        rel = unquote(parts.path)
        target = path.parent / rel if rel else path
        try: target = target.resolve(); target.relative_to(root.resolve())
        except ValueError:
            warnings.append(f"{path.relative_to(root)}: {attr} points outside repository: {raw}"); continue
        if rel.endswith("/"): target = target / "index.html"
        if not target.exists():
            errors.append(f"{path.relative_to(root)}: missing {attr}: {raw}"); continue
        if parts.fragment and target.suffix.lower() in (".html", ".htm"):
            try:
                dest = Links(); dest.feed(target.read_text(encoding="utf-8", errors="replace"))
                if parts.fragment not in dest.ids:
                    warnings.append(f"{path.relative_to(root)}: missing anchor #{parts.fragment} in {rel or path.name}")
            except OSError: pass

def scan_daily(root, errors, warnings):
    index = root / "days" / "index.json"
    if not index.exists():
        warnings.append("days/index.json not found; daily-content check skipped"); return
    try: dates = json.loads(index.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"days/index.json invalid: {e}"); return
    if not isinstance(dates, list):
        errors.append("days/index.json must be a JSON array"); return
    seen, parsed = set(), []
    for value in dates:
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            errors.append(f"invalid date in days/index.json: {value!r}"); continue
        try: date = dt.date.fromisoformat(value)
        except ValueError:
            errors.append(f"impossible date in days/index.json: {value}"); continue
        if value in seen: warnings.append(f"duplicate date in days/index.json: {value}")
        seen.add(value); parsed.append(date)
        file = root / "days" / f"{value}.json"
        if not file.exists():
            errors.append(f"index references missing file: days/{value}.json"); continue
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            if not isinstance(data, dict): errors.append(f"days/{value}.json must contain an object")
            elif data.get("date") and data["date"] != value:
                warnings.append(f"days/{value}.json date field does not match filename")
        except (OSError, json.JSONDecodeError) as e: errors.append(f"days/{value}.json invalid: {e}")
    if parsed:
        if parsed != sorted(parsed, reverse=True): warnings.append("days/index.json is not sorted newest-first")
        newest = max(parsed); age = (dt.date.today() - newest).days
        if age > 7: warnings.append(f"newest daily content is {age} days old ({newest})")
        if age < 0: warnings.append(f"newest daily content date is in the future ({newest})")

def scan_home_announcements(root, warnings):
    """Warn when the homepage's manually maintained 'New this week' dates are stale."""
    home = root / "index.html"
    if not home.exists():
        return
    try:
        text = home.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as e:
        warnings.append(f"index.html: cannot inspect announcement dates: {e}")
        return
    match = re.search(r"var NEW\\s*=\\s*\\[(.*?)\\];", text, re.S)
    if not match:
        warnings.append("index.html: could not find the manually maintained NEW announcement list")
        return
    months = {name: number for number, name in enumerate(
        ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), 1)}
    today = dt.date.today()
    for day_text, month_text in re.findall(r'\\bd:"(\\d{1,2}) ([A-Z][a-z]{2})"', match.group(1)):
        day, month = int(day_text), months.get(month_text)
        if month is None:
            warnings.append(f"index.html: unrecognized announcement date month: {month_text}")
            continue
        year = today.year
        try:
            date = dt.date(year, month, day)
            # If a December announcement is viewed in January, treat it as last year.
            if date - today > dt.timedelta(days=180):
                date = dt.date(year - 1, month, day)
        except ValueError:
            warnings.append(f"index.html: invalid announcement date: {day_text} {month_text}")
            continue
        age = (today - date).days
        if age > 7:
            warnings.append(f"index.html: 'New this week' announcement date {day_text} {month_text} is {age} days old")
        elif age < 0:
            warnings.append(f"index.html: announcement date {day_text} {month_text} is in the future")

def main():
    ap = argparse.ArgumentParser(description="Read-only Sulabham site health check")
    ap.add_argument("--root", default=".", help="repository root")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr); return 2
    errors, warnings = [], []
    html = [p for p in root.rglob("*.html") if ".git" not in p.parts and "node_modules" not in p.parts]
    jsons = [p for p in root.rglob("*.json") if ".git" not in p.parts and "node_modules" not in p.parts]
    for path in html: scan_html(root, path, errors, warnings)
    scan_daily(root, errors, warnings)
    scan_home_announcements(root, warnings)
    for path in jsons:
        if "months" not in path.parts: continue
        try: data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"{path.relative_to(root)} invalid JSON: {e}"); continue
        if isinstance(data, dict):
            for key in ("id", "month", "date"):
                value = data.get(key)
                if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}", value):
                    try: dt.date.fromisoformat(value + "-01")
                    except ValueError: errors.append(f"{path.relative_to(root)} invalid month: {value}")
    print("SULABHAM WEBSITE HEALTH CHECK")
    print(f"HTML files scanned: {len(html)} | JSON files scanned: {len(jsons)}")
    print(f"Errors: {len(errors)} | Warnings: {len(warnings)}")
    for heading, items in (("ERRORS", errors), ("WARNINGS", warnings)):
        if items:
            print(f"\n{heading}:")
            for item in sorted(set(items)): print(f" - {item}")
    if not errors and not warnings: print("\nPASS: no issues found by these checks.")
    elif not errors: print("\nPASS WITH WARNINGS: review before publishing.")
    else: print("\nFAIL: fix errors before publishing.")
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
