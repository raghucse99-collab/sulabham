# Sulabham health checker

This read-only script checks the static website for missing local HTML links/assets, missing HTML anchors (warnings), and daily JSON index inconsistencies. It uses only Python's standard library and does not modify or publish website files.

## Run

From the repository root:

```bash
python3 tools/health_check.py
```

If running elsewhere, pass the repository root:

```bash
python3 tools/health_check.py --root /path/to/sulabham
```

## Checks

- Local `href`, `src`, and `poster` paths referenced in HTML.
- HTML fragment/anchor targets (reported as warnings).
- `days/index.json` JSON shape, date format, duplicates, newest-first order, freshness, and matching `days/YYYY-MM-DD.json` files.
- Valid JSON and recognizable `YYYY-MM` month fields under `months/`.
- Stale homepage `New this week` announcement dates and a current-affairs index that trails the current calendar month.

Exit codes: `0` means no errors (warnings may remain), `1` means errors were found, and `2` means the root path is invalid.

## Limitations

It does not verify external URLs, execute JavaScript, confirm that a job notification is factually current, or test payment flows. Run it locally first and review its output before adding it to a publish workflow.
