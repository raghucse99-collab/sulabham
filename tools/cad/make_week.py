"""Sulabham — weekly current affairs + 25-question weekly test.
usage: python3 tools/cad/make_week.py caw/YYYY-Www.json
The run writes caw/<id>.json with {"id": "2026-W43", "rev": [...5-10 {en,te}], "test": [25 questions]}.
This script fills in from/to/label and the subject-wise groups from cad/<date>.json files of that week,
updates caw/index.json and writes cards/caw/<id>/week-en.png, week-te.png, week-en.txt, week-te.txt.
"""
import asyncio, datetime as dt, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'daily'))
import make_day as M
from make_cad import CATS, bi, esc
from playwright.async_api import async_playwright
ROOT = M.ROOT
TE_MON = M.MON['te']; EN_MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def week_days(wid):
    y, w = wid.split('-W'); mon = dt.date.fromisocalendar(int(y), int(w), 1)
    return [mon + dt.timedelta(days=i) for i in range(7)]

def lab(d1, d2, m):
    mo = EN_MON if m == 'en' else TE_MON
    return f"{d1.day} {mo[d1.month-1]} – {d2.day} {mo[d2.month-1]} {d2.year}"

def validate_test(T, n=25):
    assert len(T) == n, f'test: exactly {n} questions'
    from collections import Counter
    for i, q in enumerate(T):
        w = f'test Q{i+1}'
        bi(q.get('q'), w); bi(q.get('why'), w + ' why')
        for x in q.get('st', []): bi(x, w + ' st')
        assert len(q['o']) == 4, w + ': 4 options'; [bi(o, w + ' option') for o in q['o']]
        assert 0 <= q['a'] < 4
    c = Counter(q['a'] for q in T); assert max(c.values()) <= n // 3 + 1, f'answers not spread: {dict(c)}'

def build(W):
    days = week_days(W['id'])
    groups = {}
    used = []
    for d in days:
        p = os.path.join(ROOT, 'cad', d.isoformat() + '.json')
        if not os.path.exists(p): continue
        used.append(d.isoformat())
        for it in json.load(open(p, encoding='utf-8'))['items']:
            groups.setdefault(it['cat'], []).append({'d': d.isoformat(), 'id': it['id'], 't': it['title'], 'x': it['exam']})
    assert used, 'no daily current affairs found for this week'
    W['from'], W['to'] = days[0].isoformat(), days[-1].isoformat()
    W['label'] = {m: lab(days[0], days[-1], m) for m in ('en', 'te')}
    W['days'] = used
    W['groups'] = [{'cat': c, 'items': groups[c]} for c in CATS if c in groups]
    return W

def poster(W, m):
    h = {'en': ('Weekly Current Affairs', W['label']['en'], 'Revise the week + 25-question weekly test'),
         'te': ('వారపు కరెంట్ అఫైర్స్', W['label']['te'], 'వారం రివిజన్ + 25 ప్రశ్నల వారపు టెస్ట్')}[m]
    rows = ''.join(f'<li><span class="em">{CATS[g["cat"]][0]}</span><b>{esc(CATS[g["cat"]][1 if m=="en" else 2])}</b><i>{len(g["items"])}</i></li>' for g in W['groups'])
    rev = ''.join(f'<li>{esc(r[m])}</li>' for r in W['rev'][:6])
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{M.FONTS}
*{{box-sizing:border-box}}html,body{{margin:0}}
body{{width:1080px;height:1350px;font-family:{'NT,NS' if m=='te' else 'NS,NT'},sans-serif;color:#16324a;background:#f6f8f9}}
.card{{width:1080px;height:1350px;display:flex;flex-direction:column}}
.top{{padding:44px 56px 34px;color:#fff;background:radial-gradient(circle at 88% 12%,rgba(255,212,92,.4),transparent 45%),linear-gradient(135deg,#3b1d5e,#7a3b8f)}}
.brand{{display:flex;align-items:center;gap:14px;font-family:AK;font-weight:800;font-size:36px}}
.brand img{{width:58px;height:58px;background:#fff;border-radius:14px;padding:4px}}
h1{{font-family:AK;font-weight:800;font-size:74px;line-height:1.05;margin:22px 0 6px}}
.sub{{font-size:34px;font-weight:600;color:#ffd45c}}
.bot{{flex:1;min-height:0;padding:26px 56px 0;overflow:hidden;font-size:var(--f,30px)}}
ul.g{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:10px 18px}}
ul.g li{{display:flex;align-items:center;gap:12px;background:#fff;border:2px solid #d6dfe5;border-radius:16px;padding:10px 14px}}
ul.g b{{flex:1;font-weight:600;font-size:.9em}} ul.g i{{font-style:normal;font-family:AK;font-weight:800;color:#7a3b8f;font-size:1.2em}}
h3{{font-family:AK;font-weight:800;margin:22px 0 8px;font-size:1.1em}}
ul.r{{margin:0;padding-left:1.1em;line-height:1.35}} ul.r li{{margin:0 0 8px}}
.foot{{display:flex;justify-content:space-between;align-items:center;gap:20px;background:#16324a;color:#fff;padding:24px 56px;margin-top:16px;font-size:24px}}
.foot b{{color:#ffd45c;font-size:28px}}
</style></head><body><div class="card">
<div class="top"><div class="brand"><img src="{M.LOGO}" alt="">{'<span>సులభం</span>' if m=='te' else '<span>Sulabham</span>'}</div>
<h1>🗞️ {h[0]}</h1><div class="sub">{h[1]}</div></div>
<div class="bot" id="bx"><ul class="g">{rows}</ul><h3>{'⭐ Must-revise this week' if m=='en' else '⭐ ఈ వారం తప్పక రివైజ్ చేయండి'}</h3><ul class="r">{rev}</ul></div>
<div class="foot"><div><b>{h[2]}</b><br>{M.SITE_URL}/current.html?tab=week</div><div style="font-size:50px">👉</div></div>
</div><script>(function(){{var b=document.getElementById('bx'),f=30;while(b.scrollHeight>b.clientHeight+2&&f>18){{f--;document.documentElement.style.setProperty('--f',f+'px')}}}})();</script></body></html>"""

def text(W, m, cdir):
    url = f"https://{M.SITE_URL}/current.html?tab=week&w={W['id']}" + ('&m=te' if m == 'te' else '')
    head = {'en': f"🗞️ *SULABHAM · WEEKLY CURRENT AFFAIRS* | {W['label']['en']}", 'te': f"🗞️ *సులభం · వారపు కరెంట్ అఫైర్స్* | {W['label']['te']}"}[m]
    parts = [head, '']
    for g in W['groups']:
        parts.append(f"{CATS[g['cat']][0]} *{CATS[g['cat']][1 if m=='en' else 2]}*")
        parts += [f"• {x['t'][m]}" for x in g['items']]
        parts.append('')
    parts.append({'en': '⭐ *Must-revise*', 'te': '⭐ *తప్పక రివైజ్ చేయండి*'}[m])
    parts += [f"• {r[m]}" for r in W['rev']]
    parts += ['', {'en': f"📝 25-question WEEKLY TEST (APPSC pattern) + score:\n👉 {url}", 'te': f"📝 25 ప్రశ్నల వారపు టెస్ట్ (APPSC విధానం) + మీ స్కోరు:\n👉 {url}"}[m],
              '', '#APPSC #Group1 #Group2 #WeeklyCurrentAffairs #Sulabham']
    open(os.path.join(cdir, f'week-{m}.txt'), 'w', encoding='utf-8').write('\n'.join(parts))

async def main(src):
    W = json.load(open(src, encoding='utf-8'))
    assert W.get('id') and '-W' in W['id'], 'id like 2026-W43'
    assert 4 <= len(W.get('rev', [])) <= 10, 'rev: 4-10 must-revise points'; [bi(r, 'rev') for r in W['rev']]
    validate_test(W['test'])
    build(W)
    json.dump(W, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    idx_p = os.path.join(ROOT, 'caw', 'index.json')
    idx = json.load(open(idx_p, encoding='utf-8')) if os.path.exists(idx_p) else []
    idx = [x for x in idx if x['id'] != W['id']] + [{'id': W['id'], 'label': W['label'], 'n': sum(len(g['items']) for g in W['groups']), 'q': len(W['test'])}]
    idx.sort(key=lambda x: x['id'], reverse=True)
    json.dump(idx, open(idx_p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    cdir = os.path.join(ROOT, 'cards', 'caw', W['id']); os.makedirs(cdir, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1080, 'height': 1350})
        for m in ('en', 'te'):
            await pg.set_content(poster(W, m)); await pg.wait_for_timeout(300)
            await pg.screenshot(path=os.path.join(cdir, f'week-{m}.png'))
        await b.close()
    for m in ('en', 'te'): text(W, m, cdir)
    print('done week', W['id'], W['days'], '->', cdir)

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1]))
