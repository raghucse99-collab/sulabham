# Sulabham daily: validate a day JSON, update days/index.json, make poster cards + captions.
# usage (from repo root): python3 tools/daily/make_day.py days/YYYY-MM-DD.json
# output: cards/YYYY-MM-DD/<id>-en.png, <id>-te.png, captions-en.txt, captions-te.txt
import asyncio, base64, html, json, os, sys
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FS = os.path.join(HERE, 'fonts')
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SITE_URL = 'raghucse99-collab.github.io/sulabham'

def f64(p): return 'data:font/woff2;base64,' + base64.b64encode(open(os.path.join(FS, p), 'rb').read()).decode()
FONTS = f"""
@font-face{{font-family:AK;src:url({f64('anek-telugu-latin-800-normal.woff2')});font-weight:800}}
@font-face{{font-family:AK;src:url({f64('anek-telugu-telugu-800-normal.woff2')});font-weight:800}}
@font-face{{font-family:AK;src:url({f64('anek-telugu-latin-700-normal.woff2')});font-weight:700}}
@font-face{{font-family:AK;src:url({f64('anek-telugu-telugu-700-normal.woff2')});font-weight:700}}
@font-face{{font-family:NS;src:url({f64('noto-sans-latin-400-normal.woff2')});font-weight:400}}
@font-face{{font-family:NS;src:url({f64('noto-sans-latin-600-normal.woff2')});font-weight:600}}
@font-face{{font-family:NT;src:url({f64('noto-sans-telugu-telugu-400-normal.woff2')});font-weight:400}}
@font-face{{font-family:NT;src:url({f64('noto-sans-telugu-telugu-600-normal.woff2')});font-weight:600}}
"""
LOGO = 'data:image/svg+xml;base64,' + base64.b64encode(open(os.path.join(ROOT, 'sulabham-icon.svg'), 'rb').read()).decode()

W = 'stroke="#fff" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"'
ART = {
 'sirsyed': f'<path d="M40 300 Q120 260 200 300 Q280 260 360 300 V120 Q280 80 200 120 Q120 80 40 120 Z" {W}/><path d="M200 120V300" {W}/><path d="M70 150q50-20 100 0M70 190q50-20 100 0M70 230q50-20 100 0M230 150q50-20 100 0M230 190q50-20 100 0" {W} opacity=".7"/><path d="M300 40 Q380 10 370 90 L250 250" {W}/><path d="M250 250l-12 26 26-12" {W}/>',
 'poverty': f'<path d="M60 200 L200 80 L340 200" {W}/><path d="M90 180V340H310V180" {W}/><path d="M200 300c-60-40-70-80-40-100 20-12 40 0 40 16 0-16 20-28 40-16 30 20 20 60-40 100z" {W}/><path d="M270 120V80h30v66" {W}/>',
 'food': f'<path d="M80 250h240q-10 90-120 90T80 250z" {W}/><path d="M120 250V120M120 140l-24-18M120 140l24-18M120 175l-24-18M120 175l24-18M120 210l-24-18M120 210l24-18" {W}/><path d="M200 250V90M200 110l-24-18M200 110l24-18M200 145l-24-18M200 145l24-18M200 180l-24-18M200 180l24-18M200 215l-24-18M200 215l24-18" {W}/><path d="M280 250V130M280 150l-24-18M280 150l24-18M280 185l-24-18M280 185l24-18" {W}/>',
 'ghats': f'<path d="M10 320 L110 150 L170 230 L250 90 L390 320" {W}/><path d="M220 140l30-50 28 46" {W} opacity=".7"/><path d="M60 360 Q140 320 200 350 T360 340" {W}/><circle cx="330" cy="80" r="30" {W}/><path d="M70 300l40-60 30 40" {W} opacity=".6"/>',
 'unsc': f'<path d="M80 300 A120 120 0 1 1 320 300" {W}/><path d="M120 300 A80 80 0 1 1 280 300" {W} opacity=".6"/><circle cx="200" cy="200" r="42" {W}/><path d="M158 200h84M200 158c-20 26-20 58 0 84M200 158c20 26 20 58 0 84" {W}/><g fill="#fff"><circle cx="80" cy="330" r="10"/><circle cx="320" cy="330" r="10"/><circle cx="96" cy="140" r="10"/><circle cx="304" cy="140" r="10"/><circle cx="200" cy="66" r="10"/></g>',
 'law': f'<path d="M200 60V330M120 330h160M90 120h220" {W}/><path d="M90 120l-40 100h80zM310 120l-40 100h80z" {W}/><circle cx="200" cy="60" r="14" {W}/>',
 'rocket': f'<path d="M200 40c60 50 70 140 40 220h-80c-30-80-20-170 40-220z" {W}/><circle cx="200" cy="150" r="26" {W}/><path d="M160 260l-40 50 50-10M240 260l40 50-50-10M180 300l20 60 20-60" {W}/>',
 'trophy': f'<path d="M130 60h140v80a70 70 0 0 1-140 0z" {W}/><path d="M130 90H80q0 70 60 80M270 90h50q0 70-60 80M200 210v60M150 330h100l-10-60h-80z" {W}/>',
 'rupee': f'<path d="M120 80h170M120 140h170M120 80h50a60 60 0 0 1 0 120h-50l140 130" {W}/>',
 'leaf': f'<path d="M80 320C80 160 200 70 340 70c0 150-90 250-260 250z" {W}/><path d="M80 320L260 140" {W}/>',
 'shield': f'<path d="M200 50l130 50v90c0 80-60 140-130 170-70-30-130-90-130-170v-90z" {W}/><path d="M150 200l35 35 70-80" {W}/>',
 'calendar': f'<rect x="70" y="90" width="260" height="240" rx="20" {W}/><path d="M70 150h260M140 60v60M260 60v60" {W}/><path d="M130 210h40M190 210h40M250 210h40M130 270h40M190 270h40" {W}/>',
 'oci': f'<rect x="100" y="60" width="200" height="280" rx="18" {W}/><circle cx="200" cy="170" r="50" {W}/><path d="M200 120v100M150 170h100" {W} opacity=".7"/><path d="M140 270h120M160 300h80" {W}/>',
}

CSS = """
*{box-sizing:border-box}html,body{margin:0}
body{width:1080px;height:1350px;font-family:NS,NT,sans-serif;color:#16324a;background:#f6f8f9}
.te body,body.te{font-family:NT,NS,sans-serif}
.card{width:1080px;height:1350px;display:flex;flex-direction:column}
.top{position:relative;background:var(--c);color:#fff;padding:46px 56px 44px;overflow:hidden}
.top::after{content:"";position:absolute;inset:0;background:radial-gradient(circle at 85% 20%,rgba(255,255,255,.18),transparent 55%),linear-gradient(180deg,transparent 60%,rgba(0,0,0,.18));pointer-events:none}
.art{position:absolute;right:28px;top:120px;width:330px;height:330px;opacity:.33}
.brand{display:flex;align-items:center;gap:14px;font-family:AK;font-weight:800;font-size:38px;position:relative;z-index:1}
.brand img{width:58px;height:58px;background:#16324a;border-radius:14px;padding:4px}
.brand b{color:#ffd45c}
.date{position:absolute;right:56px;top:50px;z-index:1;background:#fff;color:var(--c);font-weight:600;font-size:26px;border-radius:999px;padding:8px 22px}
.tag{display:inline-block;margin-top:40px;font-size:28px;font-weight:600;background:rgba(255,255,255,.2);border-radius:999px;padding:6px 22px;position:relative;z-index:1}
.src{display:block;margin-top:32px;font-size:26px;opacity:.92;position:relative;z-index:1}
.src+.tag{margin-top:12px}
h1{font-family:AK;font-weight:800;font-size:var(--h,92px);line-height:1.04;margin:22px 0 0;max-width:820px;position:relative;z-index:1;text-shadow:0 2px 0 rgba(0,0,0,.12)}
.line{font-size:var(--l,33px);line-height:1.4;margin:20px 0 0;max-width:900px;position:relative;z-index:1}
.bot{flex:1;display:flex;flex-direction:column;padding:34px 56px 0;min-height:0}
.facts{flex:1;min-height:0;overflow:hidden;font-size:var(--f,29px);line-height:1.38}
.row{display:flex;gap:22px;padding:13px 0;border-bottom:2px solid #e3e9ee}
.row:first-child{padding-top:0}
.k{flex:0 0 31%;font-weight:600;color:#52677a}
.v{flex:1}
.trap{margin-top:22px;background:#fbe9e7;border-left:10px solid #b3322b;border-radius:12px;padding:16px 22px;font-size:var(--t,27px);line-height:1.4}
.trap b{color:#b3322b}
.foot{display:flex;justify-content:space-between;align-items:center;gap:20px;background:#16324a;color:#fff;padding:24px 56px;margin-top:28px;font-size:24px}
.foot b{color:#ffd45c;font-size:27px}
.foot .r{text-align:right;opacity:.9}
"""

LAB = {'en': {'trap': 'Exam trap:', 'more': 'Full explanation + practice MCQ', 'join': 'Telegram · WhatsApp: Sulabham'},
       'te': {'trap': 'పరీక్ష ఉచ్చు:', 'more': 'పూర్తి వివరణ + ప్రాక్టీస్ MCQ', 'join': 'టెలిగ్రామ్ · వాట్సాప్: సులభం'}}
MON = {'en': ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'],
       'te': ['జనవరి','ఫిబ్రవరి','మార్చి','ఏప్రిల్','మే','జూన్','జూలై','ఆగస్టు','సెప్టెంబర్','అక్టోబర్','నవంబర్','డిసెంబర్']}

def e(s): return html.escape(s, quote=False)

def page(D, it, m):
    L = lambda o: o[m] if o else ''
    y, mo, d = D['date'].split('-')
    date = f"{int(d)} {MON[m][int(mo)-1]} {y}"
    facts = ''.join(f'<div class="row"><div class="k">{e(L(k))}</div><div class="v">{e(L(v))}</div></div>' for k, v in [it['facts'][i] for i in it.get('cf', range(min(5, len(it.get('facts', [])))))])
    src = f'<span class="src">{e(L(it["src"]))}</span>' if it.get('src') else ''
    trap = f'<div class="trap"><b>{LAB[m]["trap"]}</b> {e(L(it["trap"]))}</div>' if it.get('trap') else ''
    return f"""<!doctype html><html class="{m}"><head><meta charset="utf-8"><style>{FONTS}{CSS}</style></head>
<body class="{m}"><div class="card" style="--c:{it['color']}">
<div class="top"><svg class="art" viewBox="0 0 400 400">{ART.get(it.get('icon') or it['id'], ART['calendar'])}</svg>
<div class="brand"><img src="{LOGO}" alt="">{'<span>సులభం</span>' if m=='te' else '<span>Sula<b>bham</b></span>'}</div><div class="date">{date}</div>
{src}<span class="tag">{e(L(it['tag']))}</span><h1>{e(L(it['title']))}</h1><p class="line">{e(L(it['line']))}</p></div>
<div class="bot"><div class="facts">{facts}</div>{trap}</div>
<div class="foot"><div><b>{LAB[m]['more']}</b><br>{SITE_URL}/today.html</div><div class="r">{LAB[m]['join']}</div></div>
</div>
<script>
// shrink fonts until everything fits
(function(){{var r=document.documentElement.style,f=document.querySelector('.facts'),h1=document.querySelector('h1');
var hs=92;
var fs=29,ts=27,ls=33;
function over(){{return f.scrollHeight>f.clientHeight+2}}
while(h1.getBoundingClientRect().height>hs*2.2&&hs>64){{hs-=4;r.setProperty('--h',hs+'px')}}
var n=0;while(over()&&n<12){{n++;if(fs>25){{fs-=1;r.setProperty('--f',fs+'px')}}if(ts>24&&n%2){{ts-=1;r.setProperty('--t',ts+'px')}}if(ls>29&&n%3==0){{ls-=1;r.setProperty('--l',ls+'px')}}}}
while(over()&&f.children.length>2){{f.removeChild(f.lastElementChild)}}
window.__fit={{hs:hs,fs:fs,ts:ts,ls:ls,over:over()}};}})();
</script></body></html>"""

def caption(D, m):
    L = lambda o: o[m] if o else ''
    y, mo, d = D['date'].split('-')
    head = {'en': f"📅 TODAY IN SULABHAM | {int(d)} {MON['en'][int(mo)-1].title()} {y}",
            'te': f"📅 సులభం · నేటి ప్రత్యేకం | {int(d)} {MON['te'][int(mo)-1]} {y}"}[m]
    out = [head, '']
    for it in D['items']:
        icon = '🗓️' if it['kind'] == 'day' else '📰'
        block = [f"{icon} {L(it['title'])}", L(it['line'])]
        if it.get('trap'): block.append(f"⚠️ {LAB[m]['trap']} {L(it['trap'])}")
        url = f"https://{SITE_URL}/today.html?d={D['date']}&m={m}#{it['id']}"
        block.append(('👉 Full explanation + MCQ: ' if m == 'en' else '👉 పూర్తి వివరణ + MCQ: ') + url)
        short = [block[0], block[1], block[-1]]
        out.append('\n'.join(short)); out.append('')
        # one caption per card too
        os.makedirs(CAPDIR, exist_ok=True)
        cap = head + '\n\n' + '\n'.join(block) + '\n\n#APPSC #Group2 #Group1 #CurrentAffairs #Sulabham'
        if len(cap) > 1000: cap = head + '\n\n' + '\n'.join(short) + '\n\n#APPSC #CurrentAffairs #Sulabham'  # Telegram photo caption limit 1024
        open(os.path.join(CAPDIR, f"{it['id']}-{m}.txt"), 'w', encoding='utf-8').write(cap)
    out.append('#APPSC #Group1 #Group2 #APDSC #APPolice #CurrentAffairs #Sulabham')
    open(os.path.join(CAPDIR, f"all-{m}.txt"), 'w', encoding='utf-8').write('\n'.join(out))

REQ = ['id', 'kind', 'color', 'tag', 'title', 'line', 'easy', 'facts']
def validate(D):
    assert D['date'] and D['day']['en'] and D['day']['te']
    ids = set()
    for it in D['items']:
        for k in REQ: assert k in it, f"{it.get('id')}: missing {k}"
        assert it['id'] not in ids, 'duplicate id ' + it['id']; ids.add(it['id'])
        assert it['kind'] in ('day', 'article')
        def bi(o, where):
            assert isinstance(o, dict) and o.get('en') and o.get('te'), f"{it['id']}: {where} needs en+te"
        for k in ('tag', 'title', 'line', 'trap', 'tip', 'mains', 'src'):
            if k in it: bi(it[k], k)
        for p in it['easy']: bi(p, 'easy')
        for r in it['facts']: bi(r[0], 'fact key'); bi(r[1], 'fact value')
        if 'chain' in it: bi(it['chain']['h'], 'chain'); [bi(x, 'chain item') for x in it['chain']['l']]
        for pc in it.get('pics', []):
            assert pc['type'] in ('timeline', 'flow', 'compare', 'dots', 'bars'), f"{it['id']}: bad pic type"
            if 'h' in pc: bi(pc['h'], 'pic h')
            if 'cap' in pc: bi(pc['cap'], 'pic cap')
            if pc['type'] in ('timeline', 'flow', 'bars'): [bi(x['t'], 'pic item') for x in pc['items']]
            if pc['type'] == 'bars': assert all(isinstance(x['v'], (int, float)) for x in pc['items'])
            if pc['type'] == 'compare': [bi(c['h'], 'pic') or [bi(x, 'pic') for x in c['l']] for c in (pc['a'], pc['b'])]
            if pc['type'] == 'dots': [bi(g['t'], 'pic') for g in pc['groups']]
        if 'mcq' in it:
            q = it['mcq']; bi(q['q'], 'mcq'); [bi(x, 'mcq st') for x in q['st']]; assert len(q['o']) == 4; [bi(x, 'mcq option') for x in q['o']]
            assert 0 <= q['a'] < 4; bi(q['why'], 'mcq why')

async def main(src):
    global CAPDIR
    D = json.load(open(src, encoding='utf-8'))
    validate(D)
    idx_p = os.path.join(ROOT, 'days', 'index.json')
    idx = json.load(open(idx_p)) if os.path.exists(idx_p) else []
    if D['date'] not in idx: idx.append(D['date'])
    idx.sort(reverse=True); json.dump(idx, open(idx_p, 'w'), separators=(',', ':'))
    cdir = os.path.join(ROOT, 'cards', D['date']); os.makedirs(cdir, exist_ok=True)
    CAPDIR = cdir + '/_cap'
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1080, 'height': 1350})
        for it in D['items']:
            for m in ('en', 'te'):
                await pg.set_content(page(D, it, m)); await pg.wait_for_timeout(250)
                await pg.screenshot(path=os.path.join(cdir, f"{it['id']}-{m}.png"))
        await b.close()
    for m in ('en', 'te'): caption(D, m)
    # merge captions into one file per language
    for m in ('en', 'te'):
        parts = []
        for it in D['items']:
            parts.append(f"===== Photo: {it['id']}-{m}.png =====\n" + open(os.path.join(CAPDIR, f"{it['id']}-{m}.txt"), encoding='utf-8').read())
        parts.append('===== One text post with all topics =====\n' + open(os.path.join(CAPDIR, f'all-{m}.txt'), encoding='utf-8').read())
        open(os.path.join(cdir, f'captions-{m}.txt'), 'w', encoding='utf-8').write('\n\n'.join(parts))
    import shutil; shutil.rmtree(CAPDIR)
    print('done', D['date'], len(D['items']), 'items ->', cdir)

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1]))
