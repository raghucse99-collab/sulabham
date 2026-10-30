# Sulabham — daily "Today" page (instructions for the daily run)

> **First read `tools/CONTENT_STANDARD.md`** — the owner's charter (UNDERSTAND. CONNECT. REMEMBER. APPLY.): Group 2 first, teaching / exam / bilingual / accuracy / website rules and the quality-control checklist. Follow it for everything below.


Every morning (IST) one new day is added to https://raghucse99-collab.github.io/sulabham/today.html
Audience: Andhra Pradesh exam aspirants (APPSC Group 1/2, AP DSC, AP Police SI/PC). Bilingual: every text field has English (`en`) and Telugu (`te`).

## Steps
1. Work in the repo root (clone `raghucse99-collab/sulabham` if needed). Use today's date in Asia/Kolkata (`TZ=Asia/Kolkata date +%F`).
2. Research with web search (use the current year in queries):
   - **Today's importance**: 2–3 items — birth/death anniversaries of important persons (Indian freedom fighters, reformers, scientists, AP/Telangana personalities get priority), national/international days with the **official theme for this year**. Verify the theme from an official or reliable source; if no theme is announced, don't invent one — say so or omit the theme row.
   - **In the news — explained**: 3 current topics from the last 1–3 days that matter for exams (editorials and "Explained" pieces of The Hindu / Indian Express, PIB, government schemes, reports & indices, environment, polity, IR, economy, science, AP news). Prefer topics with static-GK links.
   - Every fact, number and date must come from a source you actually read. If two sources conflict, use the official one or leave the fact out.
   - Record every source you used in the item's `refs` (title + exact https URL of the page you read). Required — make_day.py rejects items without refs.

## Choosing topics (APPSC Group 1/2 value first)
- **Priority order:** (1) Andhra Pradesh — AP government schemes, G.O.s, budget/economy figures, AP history, AP & Telugu personalities and literature, AP geography/environment news; (2) national polity & governance — constitutional bodies, ECI, Census, Supreme Court judgments, new Acts/rules; (3) economy — RBI, budget, schemes, indices & reports; (4) international relations involving India; (5) science & tech, environment, health; (6) awards, sports (only major events: Olympics, Asian/Commonwealth Games, World Cups).
- **Persons of the day:** prefer people asked in APPSC — freedom fighters, social reformers, AP/Telugu personalities, scientists, constitution makers. ALSO always check world-famous personalities whose birth/death anniversary is today and who are standard GK (e.g. Alfred Nobel 21 Oct, Gandhi, Einstein, Newton, Nelson Mandela, Martin Luther King, Marie Curie, Shakespeare) — include them; they are frequently asked. Search "born on <date>" and "died on <date>" before choosing. Skip figures who are rarely asked in APPSC (distant regional rulers, celebrities) unless nothing better exists that day.
- **Avoid filler:** celebrity/film news, minor sports, crime stories, political party quarrels, stock-market moves.
- **Source priority:** PIB (pib.gov.in), official ministry/ECI/RBI/AP government sites and gazettes, The Hindu & The Indian Express (editorial / Explained), All India Radio (newsonair.gov.in), UN/WHO pages for days and themes; for AP news also Eenadu / Sakshi / The Hindu AP edition. Coaching sites (Drishti, Vajiram, GKToday) only to cross-check, never as the only source for a number.
3. Write `days/YYYY-MM-DD.json` (schema below). Use `days/2026-10-17.json` as the model for depth and style.
4. Run `python3 tools/daily/make_day.py days/YYYY-MM-DD.json` — it validates the JSON, updates `days/index.json`, and makes `cards/YYYY-MM-DD/summary-en.png`, `summary-te.png` (one-page poster of the whole edition — post this first on WhatsApp/Telegram; look at it to check nothing is cut off) and `cards/YYYY-MM-DD/<id>-en.png`, `<id>-te.png`, `captions-en.txt`, `captions-te.txt`. Fix any validation error and re-run.
5. Look at 2 or 3 of the PNG cards (one Telugu) to check they render properly (no overflow, Telugu shaping fine).
6. Commit and push to `main` (message: `Today: YYYY-MM-DD`). GitHub Pages publishes in ~2 minutes.
7. Do NOT change any other file of the site.

## Writing rules
- Simple language "from basics": what it is → why it matters → exam point. Short sentences. No jargon without explaining it.
- Telugu: natural, simple Telugu as used in AP exam material (ఈనాడు/సాక్షి style); keep official names, acronyms and English theme titles in English where students expect them.
- Practice question per item (`mcq`): APPSC Group 1 Prelims pattern — statement-based "which of the statements given above is/are correct" with 3–4 statements (I, II, III, IV) and 4 combination options; at least one statement must be a common trap. Never a one-line recall question.
- `trap`: the mistake examiners expect (similar dates, similar names, wrong Act, etc.).
- Neutral on politics; describe news facts, no opinions about parties or persons. For people in the news, focus on the law/issue, not on the person.
- Colors: pick a distinct dark color per item (white text must be readable), e.g. #9b2c2c, #1f6f6a, #a86b00, #2f6b2f, #1d4f91, #7a3b8f, #8a4b14, #2c5d63.
- `icon` (poster artwork): one of sirsyed(book), poverty(house), food(wheat), ghats(mountains), unsc(globe/UN), oci(passport), law, rocket, trophy, rupee, leaf, shield, calendar.

## Pictures (required — aspirants understand faster with pictures)
Every item must have at least one picture in `pics` (articles: 1–2). Choose the type that best explains the idea:
- `timeline` — life of a person, history of an event/law: `{"type":"timeline","h":{..},"items":[{"y":"1864","t":{..},"hl":1}],"cap":{..}}` (`hl` = bold, most-asked dates)
- `flow` — process / cause → effect / how something works / old law → new law: `{"type":"flow","h":{..},"items":[{"i":"🌾","t":{..}}]}` (2–6 steps, one emoji each)
- `compare` — A vs B (committee vs committee, citizen vs OCI, old vs new): `{"type":"compare","h":{..},"a":{"h":{..},"l":[{..}]},"b":{"h":{..},"l":[{..}]}}`
- `dots` — composition / counts (UNSC 5 + 10, seats): `{"type":"dots","h":{..},"groups":[{"n":5,"color":"#b3322b","t":{..}}]}` (keep n ≤ 30)
- `bars` — numbers to compare (ranks, areas, votes, budget): `{"type":"bars","h":{..},"items":[{"t":{..},"v":20668,"vl":"20,668 km²"}]}`
- `map` — WHERE something is or happened (wars, borders, places in the news, projects, disasters, rivers, summits, state-wise news, other countries):
  `{"type":"map","h":{..},"view":"india|north|northeast|south|ap|southasia|world" or [lon_min,lat_min,lon_max,lat_max],"hl":["Ladakh","Arunachal Pradesh"],"hlc":"#b3322b","ctry":["China"],"pts":[{"ll":[27.59,91.86],"t":{..},"a":"l"}],"labels":[{"ll":[32.3,88.0],"t":{..}}],"lines":[{"ll":[[lat,lon],[lat,lon]],"dash":1,"arrow":1}],"cap":{..}}`
  - `hl` = Indian states/UTs to colour (exact names, e.g. "Andhra Pradesh", "Jammu & Kashmir", "Ladakh", "Tamil Nadu"); `ctry` = other countries to colour (Natural Earth names, e.g. "China", "Pakistan", "New Zealand").
  - `pts` = places with a dot (lat, lon — take coordinates from a reliable source; if unsure leave the place out); `a`:"l" puts the label on the left. Max 6 dots, labels short (1–3 words) so they do not overlap.
  - `labels` = region / sea / country names without a dot; `lines` = routes, movements (arrow) or lines (dash).
  - PHYSICAL layers (Geography — rivers, mountains, plateaus, seas): `"rivers":["Godavari","Krishna"]`, `"regions":["Western Ghats","Deccan Plateau"]`, `"peaks":["Mount Everest","Arma Konda"]`, `"seas":true` (or "all" for every river/region/peak).
    Available: rivers Ganga, Yamuna, Brahmaputra, Tsangpo, Indus, Sutlej, Beas, Ravi, Chenab, Jhelum, Chambal, Betwa, Son, Gandak, Ghaghara, Kosi, Teesta, Lohit, Narmada, Tapi, Mahi, Banas, Godavari, Krishna, Bhima, Tungabhadra, Penna, Kaveri, Mahanadi, Brahmani, Wainganga, Indravati, Palar;
    regions Himalayas, Karakoram, Shivalik Hills, Hindu Kush, Aravalli Range, Vindhya Range, Satpura Range, Western Ghats, Eastern Ghats, Khasi Hills, Naga Hills, Deccan Plateau, Chota Nagpur Plateau, Tibetan Plateau, Thar Desert, Ganga Plain, Ganga Delta, Sundarbans, Kashmir Valley, Malabar Coast, Coromandel Coast, Kathiawar Peninsula;
    peaks Mount Everest, K2 (Godwin-Austen), Kanchenjunga, Nanda Devi, Nanga Parbat, Namcha Barwa, Mount Kailash, Anamudi, Doddabetta, Mahendragiri, Guru Shikhar, Saramati, Arma Konda.
    Show only the 2–6 features the topic needs (e.g. a dam news item → that river + state; a cyclone → seas + coast state) — fewer features = easier to grasp.
  - India is always drawn with its official boundary. Use "ap" for Andhra Pradesh news, "north" for Ladakh/J&K/Himalaya/China border, "northeast" for NE states, "world" zooms automatically to the dots.
  - Model: days/2026-10-20.json (1962 war map) and cad/2026-10-20.json (ulbpolls, sco, nzfta, dengue).
Use a map whenever the topic involves places — it is the fastest way for aspirants to understand "where". Only verified numbers in pictures. Look at the Today page pictures of 2026-10-17 as the model.

## Quiz (required — made in the morning, together with the page)
Aspirants read the day's importance and articles first, then take the quiz. So `days/YYYY-MM-DD.json` MUST contain a `"quiz"` array of exactly **10 questions** based ONLY on that day's items (about 2 per item, spread across all items).
- Format of each question: `{"topic":"<item id>","q":{..},"st":[{..} x3-4],"o":[{..} x4],"a":0-3,"why":{..}}` (all text en + te). `topic` must be an item id of the same file.
- APPSC Group 1 Prelims pattern: statement-based "which of the statements is/are correct" (I/II/III/IV with combination options), incorrect-statement, application questions; at least one trap statement per question; NEVER one-line recall. Options like "I and II only". Spread correct answers over a–d.
- Use only facts written in the item (easy / facts / chain / trap) — nothing new. Explain the wrong statement in `why`.
- `make_day.py` validates the quiz and makes `cards/<date>/quiz-en.png`, `quiz-te.png`, `quiz-en.txt`, `quiz-te.txt`, `quiz-polls-en.txt`, `quiz-polls-te.txt`.
- The quiz page link to share: https://raghucse99-collab.github.io/sulabham/today.html?d=<date>&tab=quiz (add `&m=te` for the Telugu medium). The Telegram post (automatic) sends the headline plus quiz polls.
- The evening current-affairs run makes a separate 10-question quiz for the evening news.

## Schema (every text = {"en": "...", "te": "..."})
```
{ "date": "YYYY-MM-DD",
  "day": {"en":"Sunday, 18 October 2026","te":"ఆదివారం, 18 అక్టోబర్ 2026"},
  "items": [
    { "id": "short-id", "kind": "day" | "article", "color": "#hex", "icon": "law",
      "src":  {..}            // articles only: "The Hindu · Editorial · 15 Oct 2026" / "In the news · Economy"
      "tag":  {..},           // "Birth anniversary · 18 Oct 1890" / "Explained · GS-II Polity"
      "title":{..}, "line": {..},          // one-line why it matters
      "easy": [ {..}, {..} ],              // 1–3 short paragraphs
      "facts": [ [ {key}, {value} ], ... ],// 4–8 rows
      "cf": [0,2,3,5],                     // optional: which fact rows go on the poster (max 5)
      "chain": {"h": {..}, "l": [ {..}, ... ]},   // link to static GK, AP link if any
      "trap": {..}, "tip": {..},           // tip optional
      "mcq": {"q": {..}, "st": [ {..} x3-4 ], "o": [ {..} x4 ], "a": 0-3, "why": {..}},
      "pics": [ {picture}, ... ],          // REQUIRED, see Pictures above
      "refs": [ {"t":"PIB — <title>, 16 Oct 2026","u":"https://pib.gov.in/..."} ],   // REQUIRED: sources actually read
      "mains": {..}                        // articles: one Group 1 Mains style question
    } ] }
```
Usually: 2–3 `day` items first, then 3 `article` items.
