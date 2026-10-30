# Sulabham — Current Affairs: daily (evening), weekly (Sunday), monthly (1st)

> **First read `tools/CONTENT_STANDARD.md`** — the owner's 7-step content standard (research from official sources → easy concepts → meaningful visuals → memory codes & recall → exam-pattern original questions → website lessons → quality control). Follow it for everything below; finish with its quality-control checklist before pushing.


Page: https://raghucse99-collab.github.io/sulabham/current.html (tabs Daily / Weekly / Monthly).
Audience: Andhra Pradesh aspirants — APPSC Group 1 & Group 2 first. Every text field is bilingual `{"en": "...", "te": "..."}`.
Telegram posting is automatic (GitHub Action) when a NEW file is pushed — never post yourself.

## General rules (all three)
- Research with web search using the current date. Every fact, number and date must come from a page you actually read.
  Source priority: PIB (pib.gov.in), official ministry / RBI / ECI / AP government sites and gazettes, The Hindu & The Indian Express,
  All India Radio (newsonair.gov.in); for AP news also Eenadu / Sakshi / The Hindu AP edition. Coaching sites only to cross-check.
- Topic priority (APPSC value): (1) Andhra Pradesh — schemes, G.O.s, budget/economy, AP persons, AP geography/environment;
  (2) national polity & governance — constitutional bodies, SC judgments, new Acts/rules; (3) economy — RBI, budget, schemes, indices & reports;
  (4) international relations involving India; (5) science & tech, defence, environment, health; (6) awards, persons, important days, major sports.
  No filler: no celebrity/film news, minor sports, crime, party quarrels, stock-market moves. Neutral on politics.
- Simple language: short sentences, explain any term. Telugu: natural, simple Telugu like Eenadu/Sakshi exam pages; keep official names/acronyms in English.
- Quizzes/tests follow the APPSC Group 1 Prelims pattern: mostly statement-based ("Consider the following statements… I/II/III" with
  combination options), match List-I/List-II, chronological order, "which is INCORRECT", application questions. Max 20% simple one-liners.
  Spread correct answers across (a)–(d). Every option plausible. Each `why` explains the answer and names the trap.
  Question format: `{"topic":"<item id>","q":{..},"st":[{..},...optional],"o":[{..}x4],"a":0-3,"why":{..}}`
  Keep options under 100 characters and question + statements under 300 characters where possible (Telegram quiz poll limits).

## 1. Daily current affairs — every evening → `cad/YYYY-MM-DD.json`
Today's date: `TZ=Asia/Kolkata date +%F`. If the file exists, stop. Cover news of the last 24–36 hours that is NOT already
explained in this morning's `days/<today>.json` articles (read it first; you may build quiz questions on its topics too).
```
{ "date": "YYYY-MM-DD", "day": {"en": "Monday, 19 October 2026", "te": "సోమవారం, 19 అక్టోబర్ 2026"},
  "items": [   // 8-10 items (6-12 allowed), AP items first
    { "id": "short-id", "cat": "ap|polity|economy|schemes|reports|ir|science|env|defence|health|awards|sports|days",
      "title": {..},                        // short headline
      "pts": [ {..}, {..}, {..} ],          // 2-5 easy points: what happened → why → key detail
      "facts": [ [ {key}, {value} ], ... ], // optional 2-5 rows: dates, numbers, places, heads, HQ
      "exam": {..},                         // one line: what the examiner can ask / static-GK link / trap
      "pics": [ { ... } ],                  // pictures: same types as tools/daily/README.md (timeline/flow/compare/dots/bars/MAP).
                                            // Give a picture whenever it helps understanding; a MAP for every place-based news item (AP districts, borders, countries, summits, disasters).
      "refs": [ {"t": "PIB — <title>, 19 Oct 2026", "u": "https://..."} ] } ],   // REQUIRED
  "quiz": [ 10 questions ] }               // based on today's items (topic = item id)
```
Run `python3 tools/cad/make_cad.py cad/<date>.json`, fix errors, look at `cards/cad/<date>/summary-te.png` and `quiz-te.png`.
Commit `cad/` + `cards/cad/` with message `Current affairs: <date>` and push.

## 2. Weekly — every Sunday evening (after that day's daily file) → `caw/YYYY-Www.json`
Week id = ISO week of today: `python3 -c "import datetime;y,w,_=datetime.date.today().isocalendar();print(f'{y}-W{w:02d}')"`.
Read all `cad/<date>.json` of Monday–Sunday of this week (and the morning `days/` articles). Write ONLY:
```
{ "id": "2026-W43",
  "rev": [ 5-8 {..} ],     // "must-revise" one-liners: the most exam-worthy facts of the week
  "test": [ 25 questions ] }   // mixed across the week's topics; no copy-paste of the daily quizzes — new angles, combine topics
```
Run `python3 tools/cad/make_week.py caw/<id>.json` (it adds dates, labels and subject-wise groups automatically), check
`cards/caw/<id>/week-te.png`, commit `caw/` + `cards/caw/` with message `Weekly current affairs: <id>` and push.

## 3. Monthly — on the 1st of every month, for the PREVIOUS month → `ca/YYYY-MM.json` (₹29, free preview)
1. Read all `cad/` files (and `days/` articles) of last month. Write a 50-question monthly test to a file OUTSIDE the repo,
   e.g. `/tmp/month-test.json` = `{"test": [50 questions]}` (all subjects of the month, APPSC pattern, answers spread a–d).
   NEVER commit the test file — questions 11–50 are paid content.
2. Run `python3 tools/cad/make_month.py <YYYY-MM> /tmp/month-test.json /tmp/month-codes.json`.
   It builds week-wise notes (week 1 free), the test (first 10 free), 4 encrypted PDFs, the UPI QR, and prints `UNLOCK CODE: XXX-XXXXXX`.
3. Commit `ca/` with message `Monthly current affairs: <YYYY-MM>` and push.
4. In your final message, give the owner the UNLOCK CODE clearly (it is the code paid students receive). Never write it in the repo.
