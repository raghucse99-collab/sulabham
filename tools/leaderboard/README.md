# Mock-test leaderboard (Google Sheet + Apps Script)

- `mock.html` reads `mocks/lb.json` (`{"url":"https://script.google.com/macros/s/…/exec"}`). If that file is missing, the leaderboard is hidden.
- When a test is submitted in timed mode, the page sends: name, place, device number, answers and minutes. The `Code.gs` web app then:
  - re-scores the answers against the public answer key (`mocks/<id>.json`), so a typed-in score cannot be faked;
  - keeps only the FIRST attempt from each device for each mock;
  - adds a row to the "Scores" sheet;
  - returns the top 100 (name, place, score, minutes). The device number is never shown.
- The owner sees every entry in the Google Sheet and can delete fake or rude rows there; they disappear from the board straight away.
- Setup, done once by the owner from their Google account:
  1. Make a new Google Sheet.
  2. Go to Extensions → Apps Script and paste `Code.gs`.
  3. Deploy → New deployment → Web app. Set "Execute as: Me" and "Who has access: Anyone", then deploy and authorise.
  4. Put the web-app URL in `mocks/lb.json`.
