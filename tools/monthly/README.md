# Monthly page (ca.html) — how to add a new month

> **First read `tools/CONTENT_STANDARD.md`** — the owner's charter (UNDERSTAND. CONNECT. REMEMBER. APPLY.): Group 2 first, teaching / exam / bilingual / accuracy / website rules and the quality-control checklist. Follow it for everything below.


Inputs (never commit these): CA_<Month>_<Year>_English/Telugu.docx, MockTest_<Month><Year>_English/Telugu.docx, and `codes.json`
(the private unlock codes, e.g. {"2026-07":"JUL-XXXXXX", ...} — the owner has them; never put them in the repo).

1. Put the docx files and codes.json next to these scripts.
2. `python3 parse_ca.py CA_..._English.docx CA_..._English.json` (and Telugu); `python3 parse_mock.py MockTest_..._English.docx MockTest_..._English.json` (and Telugu).
3. Convert docx to PDF with LibreOffice into `pdf/` (replace font "Nirmala UI" with "Noto Sans Telugu" inside the Telugu docx XML first).
4. Add the month to MONTHS in build_ca.py (newest first) and run `python3 build_ca.py <repo root>`.
   A new month gets a new random code, written to codes.json — give it to the owner.
5. Add the month to EXTRA in index.html's drawPdf list and to the search list; commit `ca/` + index.html.

Free preview = Week 1 (or Part 1) notes + first 10 questions. Everything else is AES-GCM encrypted with a key derived from the month's code (PBKDF2-SHA256, 150k iterations).
