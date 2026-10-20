"""Sulabham — evening Daily Current Affairs + Daily Quiz.
usage: python3 tools/cad/make_cad.py cad/YYYY-MM-DD.json
Validates the file, updates cad/index.json and writes cards/cad/<date>/:
  summary-en.png, summary-te.png  (one-page headlines poster)
  quiz-en.png, quiz-te.png        (quiz poster with Question 1)
  ca-en.txt, ca-te.txt            (WhatsApp/Telegram text post)
  quiz-en.txt, quiz-te.txt, quiz-polls-en.txt, quiz-polls-te.txt
"""
import asyncio, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'daily'))
import make_day as M
import render as MAPS
from playwright.async_api import async_playwright

ROOT = M.ROOT
CATS = {  # id: (emoji, en, te)
    'ap': ('🏛️', 'Andhra Pradesh', 'ఆంధ్రప్రదేశ్'),
    'polity': ('⚖️', 'Polity & Governance', 'రాజ్యాంగం & పాలన'),
    'economy': ('💰', 'Economy', 'ఆర్థిక వ్యవస్థ'),
    'schemes': ('📋', 'Schemes', 'పథకాలు'),
    'reports': ('📊', 'Reports & Indices', 'నివేదికలు & సూచీలు'),
    'ir': ('🌏', 'International Relations', 'అంతర్జాతీయ సంబంధాలు'),
    'science': ('🔬', 'Science & Tech', 'సైన్స్ & టెక్నాలజీ'),
    'env': ('🌿', 'Environment', 'పర్యావరణం'),
    'defence': ('🛡️', 'Defence', 'రక్షణ'),
    'health': ('🩺', 'Health', 'ఆరోగ్యం'),
    'awards': ('🏆', 'Awards & Persons', 'అవార్డులు & వ్యక్తులు'),
    'sports': ('🏅', 'Sports', 'క్రీడలు'),
    'days': ('🗓️', 'Important Days', 'ముఖ్య దినోత్సవాలు'),
}

def bi(o, w):
    assert isinstance(o, dict) and o.get('en') and o.get('te'), f'{w}: needs en+te'

def validate(D):
    assert D.get('date') and D.get('day'), 'date and day required'; bi(D['day'], 'day')
    items = D['items']; assert 6 <= len(items) <= 12, 'items: 6-12 news items'
    ids = set()
    for it in items:
        w = it.get('id', '?')
        assert it.get('id') and it['id'] not in ids, f'{w}: unique id needed'; ids.add(it['id'])
        assert it.get('cat') in CATS, f'{w}: cat must be one of {list(CATS)}'
        bi(it.get('title'), f'{w} title'); bi(it.get('exam'), f'{w} exam')
        assert 2 <= len(it.get('pts', [])) <= 5, f'{w}: 2-5 pts'
        for p in it['pts']: bi(p, f'{w} pts')
        for r in it.get('facts', []): bi(r[0], f'{w} fact'); bi(r[1], f'{w} fact')
        for pc in ([it['pic']] if it.get('pic') else []) + it.get('pics', []):
            assert pc['type'] in ('timeline', 'flow', 'compare', 'dots', 'bars', 'map'), f'{w}: bad pic'
            if pc['type'] == 'map': MAPS.validate(pc)
        assert it.get('refs'), f'{w}: refs required'
        for r in it['refs']: assert r.get('t') and str(r.get('u', '')).startswith('https://'), f'{w}: ref needs t + https u'
    M.validate_quiz(D)

def esc(s): return M.e(s)

def summary_page(D, m):
    y, mo, d = D['date'].split('-'); date = f"{int(d)} {M.MON[m][int(mo)-1]} {y}"
    h = {'en': ('Daily Current Affairs', 'Important for APPSC Group 1 & 2 · easy points', 'Full notes + 10-question quiz', 'Tonight\'s quiz'),
         'te': ('నేటి కరెంట్ అఫైర్స్', 'APPSC గ్రూప్ 1 & 2కు ముఖ్యమైనవి · సులభ పాయింట్లు', 'పూర్తి నోట్స్ + 10 ప్రశ్నల క్విజ్', 'ఈ రాత్రి క్విజ్')}[m]
    rows = ''.join(f'<li><span class="em">{CATS[it["cat"]][0]}</span><span><b>{esc(it["title"][m])}</b><small>{esc(CATS[it["cat"]][1 if m == "en" else 2])}</small></span></li>' for it in D['items'])
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{M.FONTS}
*{{box-sizing:border-box}}html,body{{margin:0}}
body{{width:1080px;height:1350px;font-family:{'NT,NS' if m=='te' else 'NS,NT'},sans-serif;color:#16324a;background:#f6f8f9}}
.card{{width:1080px;height:1350px;display:flex;flex-direction:column}}
.top{{position:relative;padding:44px 56px 36px;color:#fff;background:radial-gradient(circle at 90% 10%,rgba(255,212,92,.35),transparent 45%),linear-gradient(135deg,#0c2238,#1f5f7c)}}
.brand{{display:flex;align-items:center;gap:14px;font-family:AK;font-weight:800;font-size:36px}}
.brand img{{width:58px;height:58px;background:#fff;border-radius:14px;padding:4px}}
.date{{position:absolute;right:56px;top:48px;background:#ffd45c;color:#1b1500;font-weight:600;font-size:26px;border-radius:999px;padding:8px 22px}}
h1{{font-family:AK;font-weight:800;font-size:88px;line-height:1.05;margin:24px 0 6px}}
.sub{{font-size:30px;opacity:.92}}
.bot{{flex:1;min-height:0;padding:28px 56px 0;overflow:hidden}}
ol{{list-style:none;margin:0;padding:0;font-size:var(--f,34px);line-height:1.3}}
li{{display:flex;gap:18px;align-items:flex-start;padding:.38em 0;border-bottom:2px solid #d6dfe5}}
li .em{{flex:0 0 auto;font-size:1.15em}}
li b{{display:block;font-weight:600}}
li small{{display:block;font-size:.62em;color:#52677a;font-weight:600;letter-spacing:.03em}}
.foot{{display:flex;justify-content:space-between;align-items:center;gap:20px;background:#16324a;color:#fff;padding:24px 56px;margin-top:18px;font-size:24px}}
.foot b{{color:#ffd45c;font-size:28px}}
</style></head><body><div class="card">
<div class="top"><div class="brand"><img src="{M.LOGO}" alt="">{'<span>సులభం</span>' if m=='te' else '<span>Sulabham</span>'}</div><div class="date">{date}</div>
<h1>📰 {h[0]}</h1><div class="sub">{h[1]}</div></div>
<div class="bot" id="bx"><ol>{rows}</ol></div>
<div class="foot"><div><b>{h[2]}</b><br>{M.SITE_URL}/current.html</div><div style="font-size:50px">👉</div></div>
</div><script>(function(){{var b=document.getElementById('bx'),f=34;while(b.scrollHeight>b.clientHeight+2&&f>20){{f--;document.documentElement.style.setProperty('--f',f+'px')}}}})();</script></body></html>"""

def ca_text(D, m, cdir):
    y, mo, d = D['date'].split('-'); date = f"{int(d)} {M.MON[m][int(mo)-1]} {y}"
    url = f"https://{M.SITE_URL}/current.html?d={D['date']}" + ('&m=te' if m == 'te' else '')
    head = {'en': f"📰 *SULABHAM · DAILY CURRENT AFFAIRS* | {date}\nImportant for APPSC Group 1 & 2",
            'te': f"📰 *సులభం · నేటి కరెంట్ అఫైర్స్* | {date}\nAPPSC గ్రూప్ 1 & 2కు ముఖ్యమైనవి"}[m]
    ex = {'en': '🎯 Exam point:', 'te': '🎯 పరీక్ష పాయింట్:'}[m]
    blocks = [f"{CATS[it['cat']][0]} *{it['title'][m]}*\n{ex} {it['exam'][m]}" for it in D['items']]
    tail = {'en': f"📖 Full easy notes + 📝 10-question quiz (APPSC pattern):\n👉 {url}", 'te': f"📖 పూర్తి సులభ నోట్స్ + 📝 10 ప్రశ్నల క్విజ్ (APPSC విధానం):\n👉 {url}"}[m]
    txt = head + '\n\n' + '\n\n'.join(blocks) + '\n\n' + tail + '\n\n#APPSC #Group1 #Group2 #CurrentAffairs #Sulabham'
    open(os.path.join(cdir, f'ca-{m}.txt'), 'w', encoding='utf-8').write(txt)

async def main(src):
    D = json.load(open(src, encoding='utf-8'))
    validate(D)
    idx_p = os.path.join(ROOT, 'cad', 'index.json')
    idx = json.load(open(idx_p)) if os.path.exists(idx_p) else []
    if D['date'] not in idx: idx.append(D['date'])
    idx.sort(reverse=True); json.dump(idx, open(idx_p, 'w'), separators=(',', ':'))
    cdir = os.path.join(ROOT, 'cards', 'cad', D['date']); os.makedirs(cdir, exist_ok=True)
    nm = sum(MAPS.build(([it['pic']] if it.get('pic') else []) + it.get('pics', []), cdir, f"map-{it['id']}", f"cards/cad/{D['date']}") for it in D['items'])
    if nm: json.dump(D, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    Q = dict(D, _qurl=f"current.html?d={D['date']}", _qshort='current.html')
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1080, 'height': 1350})
        for m in ('en', 'te'):
            await pg.set_content(summary_page(D, m)); await pg.wait_for_timeout(300)
            await pg.screenshot(path=os.path.join(cdir, f'summary-{m}.png'))
            await pg.set_content(M.quiz_page(Q, m)); await pg.wait_for_timeout(300)
            await pg.screenshot(path=os.path.join(cdir, f'quiz-{m}.png'))
        await b.close()
    for m in ('en', 'te'):
        ca_text(D, m, cdir); M.quiz_texts(Q, m, cdir); M.quiz_polls(Q, m, cdir)
    print('done cad', D['date'], len(D['items']), 'items ->', cdir)

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1]))
