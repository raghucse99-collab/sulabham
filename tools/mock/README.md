# Group 2 Prelims weekly mock tests

The page is `mock.html`. The tests are in `mocks/G2-Mxx.json`, and `mocks/index.json` lists them with the newest first. Everything is free and is not encrypted.

## Pattern (APPSC Group 2 Screening Test, Notification 37/2026)
- 150 questions, 150 marks, 150 minutes.
- Each wrong answer loses 1/3 mark (G.O.Ms.No.235, 2016).
- There are 5 sections of 30 questions each, in this order: `his` Indian History, `geo` Geography, `soc` Indian Society, `ca` Current Affairs, `men` Mental Ability.
- The topic ids (`tp`) are the screening-test topic ids in `syllabus/group2.json`, for example `his-anc-1` or `men-num-8`. The result page links weak topics to `syllabus.html?t=<tp>`.

## Question standard (the owner's "most important" rule)
Questions must be at the level of the real APPSC papers. Do not write easy one-line recall questions.

Mix of question types in every section:
- About 35% statement-based ("Which of the above is/are correct / NOT correct"), with 2–4 statements.
- About 15% match List-I with List-II, using codes.
- About 10% Assertion–Reason, using the standard 4 options from `mk.AR`.
- About 10% chronology or arrange-in-order.
- About 10% correctly / incorrectly matched pairs.
- The rest are concept or application questions.

Mental Ability uses real problems. Check every answer by computing it in Python before you build.

Difficulty: about 15% easy (`e`), 65% medium (`m`), 20% hard (`h`).

Every question needs:
- An `en` and a `te` version of the question, every statement and every option.
- A `why` in both languages. It must say why the right answer is right and why each wrong statement is wrong, and name the trap.

Accuracy:
- Static facts come from NCERT, the Constitution, Census 2011 or official sources.
- Current-affairs questions come only from facts already verified in the site's own `cad/`, `caw/` and `days/` files from the last 4–5 weeks.
- Andhra Pradesh content gives all regions equal weight.

Do not repeat a question from an earlier mock. Rotate through the syllabus topics so that over 4–5 mocks every topic in the screening syllabus is covered.

## How to add the next mock (example: Mock 2, file prefix `m2`)
1. Write `tools/mock/m2_his.py`, `m2_geo.py`, `m2_soc.py`, `m2_ca.py` and `m2_men.py`, with 30 questions each. Use the helpers in `mk.py`:
   - `q()` builds a question.
   - `co()` gives the statement-combination options.
   - `AR` gives the Assertion–Reason options.
   - `M()` gives code options.
   - For a figure, wrap the question as `dict(q(...), fig=SVG)`.
2. Run `python3 tools/mock/build.py G2-M02 m2 YYYY-MM-DD 2`.
   - It checks that each section has 30 questions, every field is in both languages and there are no duplicate options.
   - It balances the answer key (a/b/c/d) by moving the correct option where the order is free (code options or single-answer options). Statement-combination and A–R options keep their usual order.
   - It writes `mocks/G2-M02.json` and updates `mocks/index.json`.
3. Test `mock.html` at a phone width of 360 px in both languages, then commit.

## How answers feed the rest of the site
- Every answer in a submitted mock is passed to `sulRev("g:<MOCK>:<i>", ok, pick)`.
- A wrong answer goes to My revision (Leitner schedule) and to `revise.html?tab=mis` (My mistakes, with your pick, the correct answer, the explanation and a re-test).
- `qsrc.js` turns the `g:` ids back into the full question.
