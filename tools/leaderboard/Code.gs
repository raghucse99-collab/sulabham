/* Sulabham mock-test leaderboard — Google Apps Script (paste into Extensions → Apps Script of a Google Sheet).
   The website sends: mock id, name, place, device number, answers, minutes.
   This script re-checks the answers against the public answer key on the website (so a typed score cannot be faked),
   keeps only the FIRST attempt from each device for each mock, writes a row to the "Scores" sheet,
   and returns the top 100 (name, place, score, minutes — never the device number). */
const SITE = 'https://raghucse99-collab.github.io/sulabham/';

function sheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName('Scores');
  if (!sh) {
    sh = ss.insertSheet('Scores');
    sh.appendRow(['Time', 'Mock', 'Name', 'Place', 'Device', 'Score', 'Correct', 'Wrong', 'Unanswered', 'Minutes']);
    sh.setFrozenRows(1);
  }
  return sh;
}

function key_(id) {
  const cache = CacheService.getScriptCache();
  let s = cache.get('k_' + id);
  if (!s) {
    const r = UrlFetchApp.fetch(SITE + 'mocks/' + id + '.json', { muteHttpExceptions: true });
    if (r.getResponseCode() !== 200) return null;
    s = JSON.stringify(JSON.parse(r.getContentText()).qs.map(function (q) { return q.a; }));
    cache.put('k_' + id, s, 21600);
  }
  return JSON.parse(s);
}

function out_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

function clean_(s, n) {
  return String(s || '').replace(/[<>"'`\\=+@]/g, '').replace(/\s+/g, ' ').trim().slice(0, n);
}

function board_(id, dev, rows) {
  rows = rows || sheet_().getDataRange().getValues();
  const L = rows.slice(1).filter(function (r) { return r[1] === id; }).map(function (r) {
    return { name: r[2], place: r[3], dev: r[4], score: Number(r[5]), mins: Number(r[9]) };
  });
  L.sort(function (a, b) { return b.score - a.score || a.mins - b.mins; });
  let you = null;
  L.forEach(function (x, i) { if (!you && dev && x.dev === dev) you = { r: i + 1, score: x.score }; });
  const top = L.slice(0, 100).map(function (x, i) {
    return { r: i + 1, name: x.name, place: x.place, score: x.score, mins: x.mins, me: !!dev && x.dev === dev };
  });
  return { n: L.length, top: top, you: you };
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(15000);
  try {
    const d = JSON.parse(e.postData.contents);
    const id = String(d.mock || '');
    if (!/^(G2-M\d{2,3}|CA-\d{4}-\d{2})$/.test(id)) return out_({ ok: false, err: 'mock' });
    const name = clean_(d.name, 40), place = clean_(d.place, 40), dev = clean_(d.dev, 12);
    if (name.length < 2 || !/^[A-Z0-9]{6}$/.test(dev)) return out_({ ok: false, err: 'name' });
    const key = key_(id);
    if (!key) return out_({ ok: false, err: 'mock' });
    const sh = sheet_();
    const rows = sh.getDataRange().getValues();
    const dup = rows.some(function (r, i) { return i && r[1] === id && r[4] === dev; });
    if (dup) return out_(Object.assign({ ok: false, err: 'dup' }, board_(id, dev, rows)));
    let c = 0, w = 0;
    const ans = d.ans || {};
    Object.keys(ans).forEach(function (k) {
      const i = Number(k), j = Number(ans[k]);
      if (i >= 0 && i < key.length && j >= 0 && j < 4) { if (j === key[i]) c++; else w++; }
    });
    const u = key.length - c - w;
    const score = Math.round((c - w / 3) * 100) / 100;
    const mins = Math.max(0, Math.min(600, Math.round(Number(d.mins) || 0)));
    sh.appendRow([new Date(), id, name, place, dev, score, c, w, u, mins]);
    return out_(Object.assign({ ok: true, score: score }, board_(id, dev)));
  } finally {
    lock.releaseLock();
  }
}

function doGet(e) {
  const id = String((e.parameter || {}).mock || '');
  if (!/^(G2-M\d{2,3}|CA-\d{4}-\d{2})$/.test(id)) return out_({ ok: false });
  return out_(Object.assign({ ok: true }, board_(id, clean_(e.parameter.dev, 12))));
}
