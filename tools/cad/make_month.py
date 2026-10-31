"""Sulabham — build a monthly current affairs package for ca.html (₹29, free preview) from the daily files.
usage: python3 tools/cad/make_month.py YYYY-MM /path/outside/repo/test.json [/path/outside/repo/codes.json] [--extra /path/outside/repo/extra.json]
- extra.json (optional, NEVER commit — paid-only notes): [{date, id, cat, title, pts, facts, exam}] in the cad item format, for
  verified topics of the month that the daily files missed (e.g. days before the evening CA started). They are merged by date.
- test.json: {"test": [50 questions in the daily-quiz format {q,st?,o,a,why}]}  — NEVER commit it (locked content).
- Notes are compiled from cad/<date>.json (evening current affairs) and the 'article' items of days/<date>.json.
- Week 1 notes + first 10 questions are free; the rest + 4 PDFs are AES-GCM encrypted with a new random code.
- The code is printed and saved to the codes file (outside the repo). Give it ONLY to the owner.
"""
import asyncio, base64, calendar, html, json, os, re, secrets, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import qrcode
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'daily'))
import make_day as M
from make_cad import CATS, bi
from make_week import validate_test
from playwright.async_api import async_playwright

ROOT = M.ROOT; ITER = 150000; FREE_Q = 10; UPI = 'raghu.cse999@axl'
ALPH = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
EN_M = ['January','February','March','April','May','June','July','August','September','October','November','December']
TE_M = ['జనవరి','ఫిబ్రవరి','మార్చి','ఏప్రిల్','మే','జూన్','జూలై','ఆగస్టు','సెప్టెంబర్','అక్టోబర్','నవంబర్','డిసెంబర్']
E = lambda s: html.escape(str(s))

def norm(c): return re.sub(r'[^A-Z0-9]', '', c.upper())
def key_for(code, salt): return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(norm(code).encode())
def enc(key, data): n = secrets.token_bytes(12); return n + AESGCM(key).encrypt(n, data, None)
b64 = lambda b: base64.b64encode(b).decode()

EXTRA = []

def topics_for(mid, m):
    y, mo = map(int, mid.split('-')); last = calendar.monthrange(y, mo)[1]
    ex = {'en': '🎯 Exam point: ', 'te': '🎯 పరీక్ష పాయింట్: '}[m]
    weeks = {1: [], 2: [], 3: [], 4: []}
    for d in range(1, last + 1):
        ds = f'{mid}-{d:02d}'; wk = min(4, (d - 1) // 7 + 1); dl = f"{d} {(EN_M if m=='en' else TE_M)[mo-1]}"
        p = os.path.join(ROOT, 'cad', ds + '.json')
        cad_items = json.load(open(p, encoding='utf-8'))['items'] if os.path.exists(p) else []
        if True:
            for it in [x for x in EXTRA if x.get('date') == ds] + cad_items:
                h = '<ul>' + ''.join(f'<li>{E(x[m])}</li>' for x in it['pts']) + '</ul>'
                if it.get('facts'): h += '<ul>' + ''.join(f'<li><b>{E(r[0][m])}: </b>{E(r[1][m])}</li>' for r in it['facts']) + '</ul>'
                h += f'<p><b>{ex}</b>{E(it["exam"][m])}</p><p class="small">{CATS[it["cat"]][0]} {E(CATS[it["cat"]][1 if m=="en" else 2])} · {dl}</p>'
                weeks[wk].append({'t': it['title'][m], 'html': h})
        p = os.path.join(ROOT, 'days', ds + '.json')
        if os.path.exists(p):
            for it in json.load(open(p, encoding='utf-8'))['items']:
                if it['kind'] != 'article': continue
                h = ''.join(f'<p>{E(x[m])}</p>' for x in it['easy'])
                h += '<ul>' + ''.join(f'<li><b>{E(r[0][m])}: </b>{E(r[1][m])}</li>' for r in it['facts']) + '</ul>'
                if it.get('trap'): h += f'<p><b>⚠️ </b>{E(it["trap"][m])}</p>'
                h += f'<p class="small">📰 {dl}</p>'
                weeks[wk].append({'t': it['title'][m], 'html': h})
    n = 0; secs = []
    for wk in (1, 2, 3, 4):
        if not weeks[wk]: continue
        for t in weeks[wk]: n += 1; t['n'] = n
        a = (wk - 1) * 7 + 1; b = last if wk == 4 else wk * 7
        mn = (EN_M if m == 'en' else TE_M)[mo - 1]
        secs.append({'h': (f'Week {wk} · {a}–{b} {mn}' if m == 'en' else f'వారం {wk} · {a}–{b} {mn}'), 'wk': wk, 'topics': weeks[wk]})
    return secs

def conv(q, i, m):
    return {'n': i + 1, 'body': [q['q'][m]] + [x[m] for x in q.get('st', [])], 'o': [o[m] for o in q['o']], 'a': q['a'], 'x': q['why'][m]}

def pdf_html(title, body, m):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{M.FONTS}
@page{{size:A4;margin:14mm 12mm}} body{{font-family:{'NT,NS' if m=='te' else 'NS,NT'},sans-serif;font-size:10.5pt;line-height:1.45;color:#16324a}}
h1{{font-family:AK;font-size:20pt;margin:0 0 2mm}} h2{{font-family:AK;font-size:14pt;margin:5mm 0 2mm;border-bottom:2px solid #e3a400}}
h3{{font-size:11pt;margin:3mm 0 1mm}} ul{{margin:1mm 0;padding-left:5mm}} p{{margin:1mm 0}} .small{{color:#52677a;font-size:8.5pt}}
.q{{break-inside:avoid;margin:0 0 3mm}} .o{{margin-left:4mm}} .k{{background:#e6f1f6;padding:1.5mm 3mm;border-radius:2mm;margin-top:1mm}}
</style></head><body><h1>{E(title)}</h1><p class="small">Sulabham · raghucse99-collab.github.io/sulabham</p>{body}</body></html>"""

async def main(mid, test_p, codes_p):
    y, mo = map(int, mid.split('-'))
    T = json.load(open(test_p, encoding='utf-8'))['test']; validate_test(T, 50)
    codes = json.load(open(codes_p)) if codes_p and os.path.exists(codes_p) else {}
    code = codes.get(mid) or (EN_M[mo-1][:3].upper() + '-' + ''.join(secrets.choice(ALPH) for _ in range(6)))
    codes[mid] = code
    salt = secrets.token_bytes(16); key = key_for(code, salt)
    lab = {'en': f'{EN_M[mo-1]} {y}', 'te': f'{TE_M[mo-1]} {y}'}
    pub = {'id': mid, 'label': lab, 'salt': b64(salt), 'iter': ITER, 'free_q': FREE_Q, 'notes': {}, 'test': {}}
    locked = {'notes': {}, 'test': {}}
    secs_all = {}
    for m in ('en', 'te'):
        secs = topics_for(mid, m); secs_all[m] = secs
        assert secs, 'no daily files for this month'
        out, lk = [], {}
        for i, s in enumerate(secs):
            free = (i == 0)
            e = {'h': s['h'], 'n': len(s['topics']), 'free': free, 'titles': [[t['n'], t['t']] for t in s['topics']]}
            if free: e['topics'] = s['topics']
            else: lk[str(i)] = s['topics']
            out.append(e)
        title = {'en': f'CURRENT AFFAIRS — {EN_M[mo-1].upper()} {y}', 'te': f'కరెంట్ అఫైర్స్ — {TE_M[mo-1]} {y}'}[m]
        intro = {'en': '<b>💡 In simple words: </b>Week-wise notes compiled from Sulabham daily current affairs, with exam points.',
                 'te': '<b>💡 సులభంగా: </b>సులభం రోజువారీ కరెంట్ అఫైర్స్ నుంచి వారాల వారీగా నోట్స్, పరీక్ష పాయింట్లతో.'}[m]
        pub['notes'][m] = {'title': title, 'intro': intro, 'sections': out, 'total': sum(len(s['topics']) for s in secs)}
        locked['notes'][m] = lk
        Q = [conv(q, i, m) for i, q in enumerate(T)]
        tt = {'en': (f'APPSC Group-1 Prelims Style Monthly Test — {lab["en"]} Current Affairs', 'General Studies · Current Affairs', f'Questions: 50  |  Time: 50 minutes  |  Marks: +1 each, −1/3 for each wrong answer'),
              'te': (f'APPSC గ్రూప్-1 ప్రిలిమ్స్ తరహా నెలవారీ టెస్ట్ — {lab["te"]} కరెంట్ అఫైర్స్', 'జనరల్ స్టడీస్ · కరెంట్ అఫైర్స్', 'ప్రశ్నలు: 50  |  సమయం: 50 నిమిషాలు  |  మార్కులు: ఒక్కోదానికి +1, తప్పుకు −1/3')}[m]
        pub['test'][m] = {'title': tt[0], 'sub': tt[1], 'info': tt[2], 'n': 50, 'free': Q[:FREE_Q]}
        locked['test'][m] = Q[FREE_Q:]
    pub['enc'] = b64(enc(key, json.dumps(locked, ensure_ascii=False).encode()))
    # PDFs
    pdfs = []
    os.makedirs(os.path.join(ROOT, 'ca', 'files'), exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        for m in ('en', 'te'):
            nb = ''.join(f'<h2>{E(s["h"])}</h2>' + ''.join(f'<h3>{t["n"]}. {E(t["t"])}</h3>{t["html"]}' for t in s['topics']) for s in secs_all[m])
            Q = [conv(q, i, m) for i, q in enumerate(T)]
            tb = ''.join(f'<div class="q"><p><b>{q["n"]}.</b> ' + '<br>'.join(E(x) for x in q['body']) + '</p>' + ''.join(f'<p class="o">({"abcd"[j]}) {E(o)}</p>' for j, o in enumerate(q['o'])) + f'<p class="k"><b>{"Answer" if m=="en" else "జవాబు"}: ({"abcd"[q["a"]]})</b> {E(q["x"])}</p></div>' for q in Q)
            for pid, title, body, le, lt in ((f'notes-{m}', pub['notes'][m]['title'], nb, f'Full notes — {"English" if m=="en" else "Telugu"}', f'పూర్తి నోట్స్ — {"ఇంగ్లీష్" if m=="en" else "తెలుగు"}'),
                                             (f'mock-{m}', pub['test'][m]['title'], tb, f'Monthly test with answers — {"English" if m=="en" else "Telugu"}', f'నెలవారీ టెస్ట్ + జవాబులు — {"ఇంగ్లీష్" if m=="en" else "తెలుగు"}')):
                await pg.set_content(pdf_html(title, body, m)); await pg.wait_for_timeout(300)
                raw = await pg.pdf(format='A4', print_background=True)
                fn = f'ca/files/{mid}-{pid}.bin'
                open(os.path.join(ROOT, fn), 'wb').write(enc(key, raw))
                pdfs.append({'id': pid, 'label': {'en': le, 'te': lt}, 'file': fn, 'kb': round(len(raw) / 1024), 'name': f'Sulabham_{lab["en"].replace(" ", "_")}_{pid}.pdf'})
        await b.close()
    order = ['notes-en', 'notes-te', 'mock-en', 'mock-te']
    pub['pdfs'] = sorted(pdfs, key=lambda x: order.index(x['id']))
    upi = f'upi://pay?pa={UPI}&pn=Sulabham&am=29&cu=INR&tn=Sulabham%20{lab["en"].replace(" ", "%20")}'
    pub['upi'] = upi; qp = f'ca/qr-{mid}.png'; qrcode.make(upi, box_size=8, border=2).save(os.path.join(ROOT, qp)); pub['qr'] = qp
    json.dump(pub, open(os.path.join(ROOT, 'ca', mid + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    ip = os.path.join(ROOT, 'ca', 'index.json'); idx = json.load(open(ip, encoding='utf-8'))
    idx = [x for x in idx if x['id'] != mid] + [{'id': mid, 'label': lab, 'topics': pub['notes']['en']['total'], 'q': 50, 'pdfs': 4}]
    idx.sort(key=lambda x: x['id'], reverse=True)
    json.dump(idx, open(ip, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    if codes_p: json.dump(codes, open(codes_p, 'w'), indent=1)
    print('MONTH', mid, 'topics', pub['notes']['en']['total'], 'UNLOCK CODE:', code)

if __name__ == '__main__':
    a = sys.argv[1:]
    if '--extra' in a:
        i = a.index('--extra'); EXTRA.extend(json.load(open(a[i + 1], encoding='utf-8'))); del a[i:i + 2]
        for x in EXTRA:
            assert x['cat'] in CATS and x['date'].startswith(a[0]) and x['pts'] and x['exam'], x.get('id')
    asyncio.run(main(a[0], a[1], a[2] if len(a) > 2 else None))
