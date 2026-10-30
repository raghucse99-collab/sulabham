"""Sulabham — course launch posters (English + Telugu), 1080x1350.
usage: python3 tools/launch/make_launch.py   ->  cards/launch/launch-en.png, launch-te.png"""
import asyncio, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'daily'))
import make_day as M
from playwright.async_api import async_playwright
ROOT = M.ROOT
OUT = os.path.join(ROOT, 'cards', 'launch')

T = {
 'en': dict(eb='NOW LIVE ON SULABHAM', h='Courses launched!', sub='APPSC preparation in Telugu & English — try free, then unlock',
   c1k='APPSC Group 1 & Group 2', c1h='Prelims Pack 2026–27', c1p='₹499', c1s='whole Prelims',
   c1l=['Geography — 5 volumes', 'History — Volumes 1–2', '7 exam-pattern mock tests', 'Syllabus coverage maps', 'Polity · Economy · Science — coming'],
   c2k='APPSC ASO · Notification 20/2026', c2h='ASO Paper II — Full Course', c2p='₹299', c2s='full course',
   c2l=['7 volumes · 51 chapters', '937 practice questions', 'Full 150-question mock', 'Statistics · Economics · Accounting · Computers'],
   free='🎁 Free part in every course — start free today', also='Also: Monthly Current Affairs ₹29 · Daily CA + quiz, Visual Library, Syllabus Tracker — FREE',
   how='How to join', steps=['Open the course and try the free part', 'Pay by UPI and send the screenshot on Telegram', 'Enter your unlock code — done!'],
   cta='Start free →'),
 'te': dict(eb='సులభంలో ఇప్పుడు అందుబాటులో', h='కోర్సులు ప్రారంభం!', sub='తెలుగు & ఇంగ్లీష్‌లో APPSC సన్నద్ధత — ముందు ఉచితంగా, తర్వాత అన్‌లాక్',
   c1k='APPSC గ్రూప్ 1 & గ్రూప్ 2', c1h='ప్రిలిమ్స్ ప్యాక్ 2026–27', c1p='₹499', c1s='పూర్తి ప్రిలిమ్స్',
   c1l=['భూగోళం — 5 సంపుటాలు', 'చరిత్ర — సంపుటాలు 1–2', '7 పరీక్షా విధాన మాక్ టెస్ట్‌లు', 'సిలబస్ కవరేజ్ మ్యాప్‌లు', 'పాలిటీ · ఎకానమీ · సైన్స్ — త్వరలో'],
   c2k='APPSC ASO · నోటిఫికేషన్ 20/2026', c2h='ASO పేపర్ II — పూర్తి కోర్సు', c2p='₹299', c2s='పూర్తి కోర్సు',
   c2l=['7 సంపుటాలు · 51 అధ్యాయాలు', '937 ప్రాక్టీస్ ప్రశ్నలు', 'పూర్తి 150 ప్రశ్నల మాక్', 'గణాంకాలు · ఆర్థికం · అకౌంటింగ్ · కంప్యూటర్స్'],
   free='🎁 ప్రతి కోర్సులో ఉచిత భాగం — ఈ రోజే ఉచితంగా మొదలుపెట్టండి', also='అదనంగా: నెలవారీ కరెంట్ అఫైర్స్ ₹29 · రోజువారీ CA + క్విజ్, విజువల్ లైబ్రరీ, సిలబస్ ట్రాకర్ — ఉచితం',
   how='ఎలా చేరాలి', steps=['కోర్సు తెరిచి ఉచిత భాగం చూడండి', 'UPIతో చెల్లించి, స్క్రీన్‌షాట్ టెలిగ్రామ్‌లో పంపండి', 'అన్‌లాక్ కోడ్ నమోదు చేయండి — పూర్తి!'],
   cta='ఇప్పుడే చేరండి →'),
}

def page(m):
    x = T[m]; e = M.e
    li = lambda L: ''.join(f'<li>{e(i)}</li>' for i in L)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{M.FONTS}
*{{box-sizing:border-box}}html,body{{margin:0}}
body{{width:1080px;height:1350px;font-family:{'NT,NS' if m=='te' else 'NS,NT'},sans-serif;color:#16324a;background:#f6f8f9}}
.card{{width:1080px;height:1350px;display:flex;flex-direction:column;background:radial-gradient(circle at 85% 6%,rgba(255,212,92,.55),transparent 32%),linear-gradient(180deg,#0c2238 0,#1a3d5c 560px,#f6f8f9 560px)}}
.top{{padding:44px 56px 0;color:#fff;position:relative}}
.brand{{display:flex;align-items:center;gap:14px;font-family:AK;font-weight:800;font-size:38px}}
.brand img{{width:60px;height:60px;background:#fff;border-radius:14px;padding:4px}}
.eb{{display:inline-block;margin-top:26px;background:#ffd45c;color:#1b1500;font-weight:800;font-size:24px;letter-spacing:.08em;border-radius:999px;padding:8px 22px}}
h1{{font-family:AK;font-weight:800;font-size:{'92' if m=='en' else '84'}px;line-height:1.05;margin:16px 0 8px}}
h1 span{{color:#ffd45c}}
.sub{{font-size:28px;opacity:.92;max-width:900px}}
.rocket{{position:absolute;right:56px;top:120px;font-size:120px}}
.cards{{display:grid;grid-template-columns:1fr 1fr;gap:24px;padding:34px 56px 0}}
.c{{border-radius:28px;padding:26px 26px 22px;color:#fff;box-shadow:0 18px 40px rgba(12,34,56,.25);display:flex;flex-direction:column}}
.c1{{background:radial-gradient(circle at 90% 8%,rgba(255,224,138,.45),transparent 40%),linear-gradient(140deg,#7a2d0c,#b8580f 60%,#d98a12)}}
.c2{{background:radial-gradient(circle at 90% 8%,rgba(185,243,223,.4),transparent 40%),linear-gradient(140deg,#06303a,#0d4f57 55%,#137168)}}
.k{{font-size:20px;font-weight:800;letter-spacing:.05em;opacity:.95;text-transform:uppercase}}
.ch{{font-family:AK;font-weight:800;font-size:{'40' if m=='en' else '36'}px;line-height:1.1;margin:8px 0 12px}}
.price{{display:flex;align-items:baseline;gap:10px;margin:0 0 12px}}
.price b{{font-family:AK;font-size:84px;line-height:1;color:#ffe08a}}.c2 .price b{{color:#9ff0d3}}
.price span{{font-size:22px;font-weight:700;opacity:.9}}
.c ul{{margin:0;padding:0;list-style:none;font-size:{'23' if m=='en' else '22'}px;line-height:1.35}}
.c li{{padding:5px 0 5px 34px;position:relative}}.c li::before{{content:"✓";position:absolute;left:0;top:5px;width:24px;height:24px;border-radius:50%;background:rgba(255,255,255,.22);font-size:16px;font-weight:800;display:flex;align-items:center;justify-content:center}}
.free{{margin:26px 56px 0;background:#fff3cf;border:3px dashed #e3a400;border-radius:22px;padding:16px 24px;font-size:28px;font-weight:800;text-align:center}}
.how{{margin:22px 56px 0;display:grid;grid-template-columns:auto 1fr 1fr 1fr;gap:14px;align-items:stretch}}
.how h3{{margin:0;writing-mode:horizontal-tb;font-family:AK;font-size:30px;display:flex;align-items:center;max-width:150px;line-height:1.1}}
.st{{background:#fff;border-radius:18px;padding:14px 16px;font-size:{'21' if m=='en' else '20'}px;font-weight:600;box-shadow:0 6px 16px rgba(12,34,56,.08);display:flex;gap:12px;align-items:flex-start}}
.st i{{font-style:normal;flex:none;width:38px;height:38px;border-radius:50%;background:#16324a;color:#ffd45c;font-weight:800;font-size:22px;display:flex;align-items:center;justify-content:center}}
.also{{margin:20px 56px 0;font-size:21px;color:#52677a;text-align:center;font-weight:600}}
.foot{{margin-top:auto;display:flex;justify-content:space-between;align-items:center;gap:20px;background:#16324a;color:#fff;padding:26px 48px;font-size:23px;font-weight:700;white-space:nowrap}}
.foot b{{background:#ffd45c;color:#1b1500;border-radius:999px;padding:12px 26px;font-size:26px}}
</style></head><body><div class="card">
<div class="top"><div class="brand"><img src="{M.LOGO}" alt="">{'సులభం' if m=='te' else 'Sulabham'}</div><div class="rocket">🚀</div>
<div class="eb">{e(x['eb'])}</div><h1>{e(x['h'])}</h1><div class="sub">{e(x['sub'])}</div></div>
<div class="cards">
 <div class="c c1"><div class="k">{e(x['c1k'])}</div><div class="ch">{e(x['c1h'])}</div><div class="price"><b>{x['c1p']}</b><span>{e(x['c1s'])}</span></div><ul>{li(x['c1l'])}</ul></div>
 <div class="c c2"><div class="k">{e(x['c2k'])}</div><div class="ch">{e(x['c2h'])}</div><div class="price"><b>{x['c2p']}</b><span>{e(x['c2s'])}</span></div><ul>{li(x['c2l'])}</ul></div>
</div>
<div class="free">{e(x['free'])}</div>
<div class="how"><h3>{e(x['how'])}</h3>{''.join(f'<div class="st"><i>{i+1}</i><span>{e(s)}</span></div>' for i, s in enumerate(x['steps']))}</div>
<div class="also">{e(x['also'])}</div>
<div class="foot"><span>👉 {M.SITE_URL}/courses.html</span><b>{e(x['cta'])}</b></div>
</div></body></html>"""

async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1080, 'height': 1350})
        for m in ('en', 'te'):
            await pg.set_content(page(m)); await pg.wait_for_timeout(500)
            over = await pg.evaluate('document.querySelector(".card").scrollHeight>1352')
            if over: print('WARNING: content taller than poster for', m)
            await pg.screenshot(path=os.path.join(OUT, f'launch-{m}.png'))
        await b.close()
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'compress_cards.py'), OUT], check=False)
    print('done', OUT)

if __name__ == '__main__':
    asyncio.run(main())
