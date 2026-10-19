"""Post Sulabham content to the Telegram group.
Env: TG_TOKEN, TG_CHAT (optional; else tools/telegram/chat_id.txt or auto-find), QUIZ_LANG (te|en|both, default both).
usage: python3 tools/telegram/post_quiz.py <file>
  days/<date>.json   morning Today page  -> headline message with link (+ quiz polls only if the file has a quiz)
  cad/<date>.json    evening current affairs -> poster photo + headlines, then 10 quiz polls (Telugu, then English)
  caw/<id>.json      weekly -> poster photo + link to the 25-question weekly test
  ca/<YYYY-MM>.json  monthly -> announcement with link (₹29 month, free preview)
"""
import json, os, sys, time, uuid, urllib.request, urllib.parse, urllib.error

SITE = 'https://raghucse99-collab.github.io/sulabham'
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
TOKEN = os.environ['TG_TOKEN'].strip()
CHAT_FILE = os.path.join(HERE, 'chat_id.txt')
CHAT = (os.environ.get('TG_CHAT') or '').strip() or (open(CHAT_FILE).read().strip() if os.path.exists(CHAT_FILE) else '')
CATS = {'ap': '🏛️', 'polity': '⚖️', 'economy': '💰', 'schemes': '📋', 'reports': '📊', 'ir': '🌏', 'science': '🔬', 'env': '🌿',
        'defence': '🛡️', 'health': '🩺', 'awards': '🏆', 'sports': '🏅', 'days': '🗓️'}
LAB = {'te': {'h': '📝 *సులభం · నేటి క్విజ్*', 'n': '10 ప్రశ్నలు · APPSC విధానం. జవాబుపై నొక్కండి — సరైనదో కాదో వెంటనే తెలుస్తుంది 👇',
              'end': '✅ వివరణలతో పూర్తి క్విజ్ & మీ స్కోరు:', 'see': '(పై వాక్యాలు చూడండి)'},
       'en': {'h': '📝 *SULABHAM · DAILY QUIZ*', 'n': '10 questions · APPSC pattern. Tap an answer — you see at once if it is right 👇',
              'end': '✅ Full quiz with explanations & your score:', 'see': '(see statements above)'}}

def call(method, data=None, files=None):
    url = f'https://api.telegram.org/bot{TOKEN}/{method}'
    for _ in range(5):
        try:
            if files:
                bd = uuid.uuid4().hex; body = b''
                for k, v in (data or {}).items():
                    body += f'--{bd}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
                for k, path in files.items():
                    body += f'--{bd}\r\nContent-Disposition: form-data; name="{k}"; filename="{os.path.basename(path)}"\r\nContent-Type: image/png\r\n\r\n'.encode() + open(path, 'rb').read() + b'\r\n'
                body += f'--{bd}--\r\n'.encode()
                req = urllib.request.Request(url, body, {'Content-Type': f'multipart/form-data; boundary={bd}'})
            else:
                req = urllib.request.Request(url, urllib.parse.urlencode({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v) for k, v in (data or {}).items()}).encode())
            r = json.load(urllib.request.urlopen(req, timeout=60))
            if r.get('ok'): return r
        except urllib.error.HTTPError as e:
            r = json.load(e)
            if e.code == 429: time.sleep(r.get('parameters', {}).get('retry_after', 5) + 1); continue
            raise SystemExit(f'{method} failed: {r}')
    raise SystemExit(f'{method} failed after retries')

def api(method, **p): return call(method, p)
def msg(text, md=False):
    p = {'chat_id': CHAT, 'text': text[:4096], 'disable_web_page_preview': 'true'}
    if md: p['parse_mode'] = 'Markdown'
    try: return call('sendMessage', p)
    except SystemExit:
        if md: p.pop('parse_mode'); return call('sendMessage', p)
        raise
def photo(path, caption):
    if not os.path.exists(path): return msg(caption)
    return call('sendPhoto', {'chat_id': CHAT, 'caption': caption[:1024]}, {'photo': path})
def cut(s, n): return s if len(s) <= n else s[:n - 1] + '…'

def find_chat():
    r = json.load(urllib.request.urlopen(f'https://api.telegram.org/bot{TOKEN}/getUpdates', timeout=30))
    found = None
    for u in r.get('result', []):
        for k in ('my_chat_member', 'message', 'channel_post'):
            c = (u.get(k) or {}).get('chat')
            if c and c.get('type') in ('group', 'supergroup', 'channel'): found = c
    if not found: raise SystemExit('Bot is not in any group/channel yet: add it, send /start@<botname> in the group, then run again.')
    open(CHAT_FILE, 'w').write(str(found['id'])); print('found chat', found['id'], found.get('title'))
    return str(found['id'])

def polls(D, m, url):
    L = lambda o: o[m]; Lb = LAB[m]
    y, mo, d = D['date'].split('-')
    msg(f"{Lb['h']} | {int(d)}-{int(mo)}-{y}\n{Lb['n']}", md=True)
    for i, q in enumerate(D['quiz']):
        st = [L(x) for x in q.get('st', [])]
        full = f"{i+1}. {L(q['q'])}" + ('\n' + '\n'.join(st) if st else '')
        if len(full) <= 300: ques = full
        else: msg(full); ques = cut(f"{i+1}. {L(q['q'])} {Lb['see']}", 300)
        api('sendPoll', chat_id=CHAT, question=ques, type='quiz', is_anonymous='true',
            options=[cut(f"({'abcd'[j]}) {L(o)}", 100) for j, o in enumerate(q['o'])],
            correct_option_id=q['a'], explanation=cut(' '.join(L(q['why']).split()), 200))
        time.sleep(1.5)
    msg(f"{Lb['end']}\n👉 {url}\n\n#APPSC #Group1 #Group2 #DailyQuiz")

def langs():
    l = (os.environ.get('QUIZ_LANG') or 'both').strip()
    return ['te', 'en'] if l == 'both' else [l]

def do_days(D):
    url = f"{SITE}/today.html?d={D['date']}"
    dd = [i for i in D['items'] if i['kind'] == 'day']; aa = [i for i in D['items'] if i['kind'] == 'article']
    for m in langs():
        if m == 'te':
            t = f"🌅 *సులభం · నేటి ప్రత్యేకం* | {D['day']['te']}\n\n🗓️ *నేటి ప్రాముఖ్యత*\n" + '\n'.join('• ' + i['title']['te'] for i in dd) + \
                "\n\n📰 *సంపాదకీయాలు — సులభ వివరణ*\n" + '\n'.join('• ' + i['title']['te'] for i in aa) + f"\n\n📖 చదవండి 👉 {url}&m=te\n📝 క్విజ్ ఈ సాయంత్రం 7 గంటలకు!"
        else:
            t = f"🌅 *TODAY IN SULABHAM* | {D['day']['en']}\n\n🗓️ *Today's importance*\n" + '\n'.join('• ' + i['title']['en'] for i in dd) + \
                "\n\n📰 *Editorials — explained*\n" + '\n'.join('• ' + i['title']['en'] for i in aa) + f"\n\n📖 Read 👉 {url}\n📝 Quiz this evening at 7 PM!"
        msg(t, md=True)
    if D.get('quiz'):
        for m in langs(): polls(D, m, f"{SITE}/today.html?d={D['date']}&tab=quiz" + ('&m=te' if m == 'te' else ''))

def do_cad(D):
    for m in langs():
        url = f"{SITE}/current.html?d={D['date']}" + ('&m=te' if m == 'te' else '')
        head = {'te': f"📰 నేటి కరెంట్ అఫైర్స్ | {D['day']['te']}", 'en': f"📰 Daily Current Affairs | {D['day']['en']}"}[m]
        lines = '\n'.join(f"{CATS.get(i['cat'], '•')} {i['title'][m]}" for i in D['items'])
        tail = {'te': f"📖 సులభ పాయింట్లు + పరీక్ష పాయింట్ 👉 {url}\n📝 10 ప్రశ్నల క్విజ్ కింద 👇", 'en': f"📖 Easy points + exam point 👉 {url}\n📝 10-question quiz below 👇"}[m]
        photo(os.path.join(ROOT, 'cards', 'cad', D['date'], f'summary-{m}.png'), f"{head}\n\n{lines}\n\n{tail}")
    for m in langs(): polls(D, m, f"{SITE}/current.html?d={D['date']}&q=1" + ('&m=te' if m == 'te' else ''))

def do_caw(W):
    for m in langs():
        url = f"{SITE}/current.html?tab=week&w={W['id']}" + ('&m=te' if m == 'te' else '')
        rev = '\n'.join('⭐ ' + r[m] for r in W['rev'][:6])
        cap = {'te': f"🗞️ *వారపు కరెంట్ అఫైర్స్* | {W['label']['te']}\n\n{rev}\n\n📝 25 ప్రశ్నల వారపు టెస్ట్ + వారం రివిజన్ 👉 {url}",
               'en': f"🗞️ *Weekly Current Affairs* | {W['label']['en']}\n\n{rev}\n\n📝 25-question weekly test + week revision 👉 {url}"}[m]
        photo(os.path.join(ROOT, 'cards', 'caw', W['id'], f'week-{m}.png'), cap.replace('*', ''))

def do_month(C):
    url = f"{SITE}/ca.html?m={C['id']}"
    for m in langs():
        t = {'te': f"📚 *{C['label']['te']} కరెంట్ అఫైర్స్ సిద్ధం!*\n\n✅ వారాల వారీ పూర్తి నోట్స్\n✅ 50 ప్రశ్నల నెలవారీ టెస్ట్ (APPSC విధానం)\n✅ PDFలు — తెలుగు + ఇంగ్లీష్\n\n🎁 వారం 1 నోట్స్ + మొదటి 10 ప్రశ్నలు ఉచితం\n🔓 పూర్తి నెల కేవలం ₹29\n\n👉 {url}&m=te",
             'en': f"📚 *{C['label']['en']} Current Affairs is ready!*\n\n✅ Full week-wise notes\n✅ 50-question monthly test (APPSC pattern)\n✅ PDFs — Telugu + English\n\n🎁 Week 1 notes + first 10 questions free\n🔓 Full month only ₹29\n\n👉 {url}"}[m]
        msg(t, md=True)

if not CHAT: CHAT = find_chat()
path = sys.argv[1]; D = json.load(open(path, encoding='utf-8'))
kind = path.replace('\\', '/').split('/')[-2]
{'days': do_days, 'cad': do_cad, 'caw': do_caw, 'ca': do_month}[kind](D)
print('posted', path, langs())
