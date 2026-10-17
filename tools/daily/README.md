# Sulabham — daily "Today" page (instructions for the daily run)

Every morning (IST) one new day is added to https://raghucse99-collab.github.io/sulabham/today.html
Audience: Andhra Pradesh exam aspirants (APPSC Group 1/2, AP DSC, AP Police SI/PC). Bilingual: every text field has English (`en`) and Telugu (`te`).

## Steps
1. Work in the repo root (clone `raghucse99-collab/sulabham` if needed). Use today's date in Asia/Kolkata (`TZ=Asia/Kolkata date +%F`).
2. Research with web search (use the current year in queries):
   - **Today's importance**: 2–3 items — birth/death anniversaries of important persons (Indian freedom fighters, reformers, scientists, AP/Telangana personalities get priority), national/international days with the **official theme for this year**. Verify the theme from an official or reliable source; if no theme is announced, don't invent one — say so or omit the theme row.
   - **In the news — explained**: 3 current topics from the last 1–3 days that matter for exams (editorials and "Explained" pieces of The Hindu / Indian Express, PIB, government schemes, reports & indices, environment, polity, IR, economy, science, AP news). Prefer topics with static-GK links.
   - Every fact, number and date must come from a source you actually read. If two sources conflict, use the official one or leave the fact out.
3. Write `days/YYYY-MM-DD.json` (schema below). Use `days/2026-10-17.json` as the model for depth and style.
4. Run `python3 tools/daily/make_day.py days/YYYY-MM-DD.json` — it validates the JSON, updates `days/index.json`, and makes `cards/YYYY-MM-DD/<id>-en.png`, `<id>-te.png`, `captions-en.txt`, `captions-te.txt`. Fix any validation error and re-run.
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
      "mains": {..}                        // articles: one Group 1 Mains style question
    } ] }
```
Usually: 2–3 `day` items first, then 3 `article` items.
