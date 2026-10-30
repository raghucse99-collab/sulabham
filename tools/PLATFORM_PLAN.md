# Sulabham learning platform — inventory and phased plan (30 Oct 2026)

Goal: bilingual, syllabus-complete, concept-oriented APPSC platform (Group 2 first, Group 1 depth), built INCREMENTALLY on the existing site
without breaking anything. Follow tools/CONTENT_STANDARD.md for all content.

## A. What exists today (inventory, checked 30 Oct 2026)
Static site on GitHub Pages (raghucse99-collab/sulabham), no server/login; per-device progress in localStorage.

| Area | Files | Working features |
|---|---|---|
| Home | index.html (1,673 lines) | Our courses banners (Prelims ₹499, ASO ₹299), Today / Daily CA / Monthly tiles, search, jobs & notifications, exam sections (Group 1/2, DSC, SI, PC, AEE), digest, explainers, words, quiz, PDFs, visit counter, en/te toggle (`sul_med`/`sul_lang`) |
| Today page | today.html, days/*.json, tools/daily | Morning edition 7:35 AM (scheduled task): importance + editorials, pictures & maps, MCQ per item, 10-Q quiz (`sul_quiz_<date>`), posters/captions, summary poster |
| Current affairs | current.html, cad/, caw/, tools/cad | Evening daily CA + 10-Q quiz (`sul_cq_`), Sunday weekly revision + 25-Q test (`sul_wq_`), monthly tab, streak & scores (`sul_cad_done`), back-to-weekly |
| Monthly CA (paid ₹29) | ca.html, ca/, tools/monthly, tools/cad/make_month.py | Jul–Sep packs, encrypted notes/tests/PDFs, `sul_code_<month>`, UPI QR; auto-build on the 1st |
| Prelims Pack (paid ₹499) | prelims.html, pk/ (63 MB), tools/pack | Geography Vol 1–5, History Vol 1–2, 7 mock tests, coverage maps, notification viewer; `sul_pack`, `sul_pk_` progress |
| ASO Paper II (paid ₹299) | aso.html, aso/, tools/aso | 7 volumes, 51 chapters, 937 Q, 150-Q mock; `sul_aso*` |
| DSC / AEE / Geography tests | dsc-*.html, AEE_*, Geography_* | Study guides & tests (separate older pages) |
| Maps | tools/maps | Official-boundary India/state/world maps + rivers, ranges, peaks, seas (bilingual SVG) |
| Integrations | .github/workflows/telegram-quiz.yml, tools/telegram | Telegram bot posts posters + quiz polls (te+en) on every new day/cad/caw/ca file |
| Scheduled tasks | (claude.ai) | Morning 7:35, evening 6:40, Sunday 8:10 PM weekly, 1st 10:20 AM monthly |
| NOT Sulabham | dp777/, dp777-*.yml workflows | Third-party project — to be moved out by the owner (see chat 27 Oct) |

## B. Risks found
1. **Repo size**: cards/ = 126 MB and grows ~5–8 MB/day (PNG posters). GitHub Pages limit is 1 GB → full in ~4 months. Fix: compress posters (JPEG/WebP, smaller) and keep only the last ~60 days of posters in the repo.
2. **Usage limits**: heavy chats before 7:35 AM / 6:40 PM make the daily runs fail.
3. **Shared unlock codes**: one code per pack (decision pending: personal codes).
4. **Progress is per device** (no login) — dashboard shows this phone's progress only.

## C. New components (phased; each phase = small, tested, published, verified)
| Phase | Component | What it does | Built from | New/changed files |
|---|---|---|---|---|
| 1 | **Student dashboard** `me.html` | One page: streak, quizzes taken, scores trend, weak subjects, pack/ASO progress, "continue where you left off" | existing localStorage keys (no content work) | me.html; nav link in index/today/current |
| 1 | **Group 2 syllabus tracker** `syllabus.html` | Every official Group 2 syllabus line (en/te), tick ✓ studied / ★ revise, % per section, links to the lesson/volume/CA that covers it | Group2_Notification_37_2026.pdf syllabus + mapping to existing content | syllabus.html, syllabus/group2.json, tools/syllabus |
| 2 | **Question bank** `qbank.html` | All questions on the site in one place: filter by subject/topic/type/level, practice mode, explanations | days/cad/caw quizzes + free pack/ASO questions (paid ones only after unlock) | qbank.html, tools/qbank/build.py, qbank/*.json (built daily by the runs) |
| 2 | **Revision engine** | Every wrong answer anywhere goes into "My revision" with spaced repetition (1-3-7-15 days) | shared localStorage key `sul_rev` written by all quiz engines | small additions to today/current/prelims/aso quiz code; me.html |
| 3 | **Memory Lab** `memory.html` | All memory codes, traps and look-alike pairs as flashcards + closed-book recall drills | `tip`/`trap` fields of days/cad items + new memory sets | memory.html, tools/memory |
| 3 | **Visual library** `visuals.html` | All maps/diagrams by subject; new mind-map picture type | pics in days/cad + tools/maps | visuals.html; mind-map type in pic renderers |
| 4 | **Group 2 mock tests** | 150-Q full-length screening mocks in Group 2 pattern (timer, negative marking, analysis) | new questions (question-setter standard) | mocks in the existing test runner |
| 5+ | **Integrated lessons** | Syllabus-line lessons in the 17-part format, Group 2 first, unit by unit, linked from the tracker | content work, ~1 unit per session | lessons/<subject>/<unit>.json + lesson page |

Testing after every phase: navigation, search, language switch, today/current quizzes, paid unlock (Prelims, ASO, Monthly with real codes), payments (UPI/QR), Telegram workflow, phone-width screenshots, then the live site.

## D. Change log
- 30 Oct 2026 — Storage: posters compressed (cards/ 126 MB → 31 MB), generators compress automatically; maps slimmer.
- 30 Oct 2026 — Phase 1: `syllabus.html` + `syllabus/group2.json` (official Group 2 syllabus, Notification 37/2026: 3 stages, 33 units, 195 topics, en/te, ✓/★ per topic saved in `sul_syl_g2`, filters, search, links to Sulabham pages) and `me.html` (streak, quizzes completed, average, today's tasks, score trend, strong/weak areas by category, syllabus % per stage, next topic, revise list, Prelims/ASO course progress). Linked from home (nav + tiles), Today and Current Affairs. Tested at phone width: ticks, filters, language switch, dashboard with sample data, home search, Prelims unlock.
