"""Post a day's 10-question quiz to a Telegram channel as native quiz polls.
Env: TG_TOKEN (bot token), TG_CHAT (@channelusername or -100... id), QUIZ_LANG (te|en|both, default te).
Usage: python3 tools/telegram/post_quiz.py days/YYYY-MM-DD.json
"""
import json, os, sys, time, urllib.request, urllib.parse

SITE = 'https://raghucse99-collab.github.io/sulabham'
TOKEN = os.environ['TG_TOKEN'].strip()
CHAT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chat_id.txt')
CHAT = (os.environ.get('TG_CHAT') or '').strip() or (open(CHAT_FILE).read().strip() if os.path.exists(CHAT_FILE) else '')
LAB = {'te': {'h': '📝 *సులభం · నేటి క్విజ్*', 'n': '10 ప్రశ్నలు · APPSC విధానం. జవాబుపై నొక్కండి — సరైనదో కాదో వెంటనే తెలుస్తుంది 👇',
              'end': '✅ వివరణలతో పూర్తి క్విజ్ & మీ స్కోరు:', 'see': '(పై వాక్యాలు చూడండి)'},
       'en': {'h': '📝 *SULABHAM · DAILY QUIZ*', 'n': '10 questions · APPSC pattern. Tap an answer — you see at once if it is right 👇',
              'end': '✅ Full quiz with explanations & your score:', 'see': '(see statements above)'}}

def api(method, **p):
    data = urllib.parse.urlencode({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v) for k, v in p.items()}).encode()
    for t in range(4):
        try:
            r = json.load(urllib.request.urlopen(f'https://api.telegram.org/bot{TOKEN}/{method}', data, timeout=30))
            if r.get('ok'): return r
        except urllib.error.HTTPError as e:
            r = json.load(e)
            if e.code == 429: time.sleep(r.get('parameters', {}).get('retry_after', 5) + 1); continue
            raise SystemExit(f'{method} failed: {r}')
    raise SystemExit(f'{method} failed after retries')

def cut(s, n): return s if len(s) <= n else s[:n - 1] + '…'

def post(D, m):
    L = lambda o: o[m]; Lb = LAB[m]
    y, mo, d = D['date'].split('-')
    url = f"{SITE}/today.html?d={D['date']}&tab=quiz" + ('&m=te' if m == 'te' else '')
    api('sendMessage', chat_id=CHAT, parse_mode='Markdown', text=f"{Lb['h']} | {int(d)}-{int(mo)}-{y}\n{Lb['n']}")
    for i, q in enumerate(D['quiz']):
        st = [L(x) for x in q.get('st', [])]
        full = f"{i+1}. {L(q['q'])}" + ('\n' + '\n'.join(st) if st else '')
        if len(full) <= 300:
            ques = full
        else:
            api('sendMessage', chat_id=CHAT, text=full)
            ques = cut(f"{i+1}. {L(q['q'])} {Lb['see']}", 300)
        why = ' '.join(L(q['why']).split())
        api('sendPoll', chat_id=CHAT, question=ques, type='quiz', is_anonymous='true',
            options=[cut(f"({'abcd'[j]}) {L(o)}", 100) for j, o in enumerate(q['o'])],
            correct_option_id=q['a'], explanation=cut(why, 200))
        time.sleep(1.5)
    api('sendMessage', chat_id=CHAT, text=f"{Lb['end']}\n👉 {url}\n\n#APPSC #Group1 #Group2 #DailyQuiz")

def find_chat():
    # the group/channel the bot was added to (Telegram keeps updates for 24 h)
    r = json.load(urllib.request.urlopen(f'https://api.telegram.org/bot{TOKEN}/getUpdates', timeout=30))
    found = None
    for u in r.get('result', []):
        for k in ('my_chat_member', 'message', 'channel_post'):
            c = (u.get(k) or {}).get('chat')
            if c and c.get('type') in ('group', 'supergroup', 'channel'): found = c
    if not found:
        me = json.load(urllib.request.urlopen(f'https://api.telegram.org/bot{TOKEN}/getMe', timeout=30))['result']
        print('bot username: @' + me['username'], '| updates seen:', len(r.get('result', [])), '| chats:', [((u.get('message') or u.get('my_chat_member') or {}).get('chat') or {}).get('type') for u in r.get('result', [])])
    if not found: raise SystemExit('Bot is not in any group/channel yet: add it, send /start@<botname> in the group, then run again.')
    print('found chat', found['id'], found.get('title'))
    open(CHAT_FILE, 'w').write(str(found['id']))
    return str(found['id'])

if not CHAT: CHAT = find_chat()
D = json.load(open(sys.argv[1], encoding='utf-8'))
assert D.get('quiz'), 'no quiz in this day'
lang = os.environ.get('QUIZ_LANG', 'both').strip() or 'both'
for m in (['te', 'en'] if lang == 'both' else [lang]): post(D, m)
print('posted', D['date'], lang)
