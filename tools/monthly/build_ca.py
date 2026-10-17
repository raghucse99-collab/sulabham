# Build Sulabham monthly pages data: public JSON + AES-GCM encrypted locked parts and PDFs.
# usage: python3 build_ca.py <out_dir (repo root)>
import json, os, sys, base64, secrets, hashlib, re
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import qrcode

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
ITER = 150000
FREE_Q = 10
UPI = 'raghu.cse999@axl'
CODES_P = os.path.join(HERE, 'codes.json')
codes = json.load(open(CODES_P)) if os.path.exists(CODES_P) else {}
ALPH = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'

MONTHS = [
 {'id': '2026-09', 'en': 'September 2026', 'te': 'సెప్టెంబర్ 2026', 'pre': 'SEP',
  'notes': None, 'test': 'September2026',
  'pdfs': [('digest-bi', 'Current affairs digest — Telugu + English', 'కరెంట్ అఫైర్స్ డైజెస్ట్ — తెలుగు + ఇంగ్లీష్', '../pdfbuild/Sulabham_September_2026_Current_Affairs.pdf'),
           ('digest-te', 'Current affairs digest — Telugu medium', 'కరెంట్ అఫైర్స్ డైజెస్ట్ — తెలుగు మీడియం', '../pdfbuild/Sulabham_September_2026_Current_Affairs_Telugu.pdf'),
           ('mock-en', 'Mock test with answers — English', 'మాక్ టెస్ట్ + జవాబులు — ఇంగ్లీష్', 'pdf/MockTest_September2026_English.pdf'),
           ('mock-te', 'Mock test with answers — Telugu', 'మాక్ టెస్ట్ + జవాబులు — తెలుగు', 'pdf/MockTest_September2026_Telugu.pdf')]},
 {'id': '2026-08', 'en': 'August 2026', 'te': 'ఆగస్టు 2026', 'pre': 'AUG',
  'notes': 'August_2026', 'test': 'August2026',
  'pdfs': [('notes-en', 'Full notes — English', 'పూర్తి నోట్స్ — ఇంగ్లీష్', 'pdf/CA_August_2026_English.pdf'),
           ('notes-te', 'Full notes — Telugu', 'పూర్తి నోట్స్ — తెలుగు', 'pdf/CA_August_2026_Telugu.pdf'),
           ('mock-en', 'Mock test with answers — English', 'మాక్ టెస్ట్ + జవాబులు — ఇంగ్లీష్', 'pdf/MockTest_August2026_English.pdf'),
           ('mock-te', 'Mock test with answers — Telugu', 'మాక్ టెస్ట్ + జవాబులు — తెలుగు', 'pdf/MockTest_August2026_Telugu.pdf')]},
 {'id': '2026-07', 'en': 'July 2026', 'te': 'జూలై 2026', 'pre': 'JUL',
  'notes': 'July_2026', 'test': 'July2026',
  'pdfs': [('notes-en', 'Full notes — English', 'పూర్తి నోట్స్ — ఇంగ్లీష్', 'pdf/CA_July_2026_English.pdf'),
           ('notes-te', 'Full notes — Telugu', 'పూర్తి నోట్స్ — తెలుగు', 'pdf/CA_July_2026_Telugu.pdf'),
           ('mock-en', 'Mock test with answers — English', 'మాక్ టెస్ట్ + జవాబులు — ఇంగ్లీష్', 'pdf/MockTest_July2026_English.pdf'),
           ('mock-te', 'Mock test with answers — Telugu', 'మాక్ టెస్ట్ + జవాబులు — తెలుగు', 'pdf/MockTest_July2026_Telugu.pdf')]},
]

def norm(c): return re.sub(r'[^A-Z0-9]', '', c.upper())
def key_for(code, salt):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(norm(code).encode())
def enc(key, data):
    n = secrets.token_bytes(12); return n + AESGCM(key).encrypt(n, data, None)
b64 = lambda b: base64.b64encode(b).decode()

def notes_sections(month, med):
    d = json.load(open(os.path.join(HERE, f'CA_{month}_{med}.json'), encoding='utf-8'))
    secs = d['sections']
    if len(secs) == 1 and secs[0]['wk'] == 0:   # no weeks in the docx -> parts of ~27 topics
        T = secs[0]['topics']; size = (len(T) + 3) // 4; secs = []
        for i in range(0, len(T), size):
            k = i // size + 1; part = T[i:i + size]
            secs.append({'h': (f'Part {k} · Topics {part[0]["n"]}–{part[-1]["n"]}' if med == 'English' else f'భాగం {k} · అంశాలు {part[0]["n"]}–{part[-1]["n"]}'), 'wk': k, 'topics': part})
    return d, secs

index = []
os.makedirs(os.path.join(OUT, 'ca', 'files'), exist_ok=True)
for M in MONTHS:
    mid = M['id']
    if mid not in codes:
        codes[mid] = M['pre'] + '-' + ''.join(secrets.choice(ALPH) for _ in range(6))
    code = codes[mid]
    salt = secrets.token_bytes(16); key = key_for(code, salt)
    pub = {'id': mid, 'label': {'en': M['en'], 'te': M['te']}, 'salt': b64(salt), 'iter': ITER, 'free_q': FREE_Q}
    locked = {'notes': {}, 'test': {}}
    # notes
    if M['notes']:
        pub['notes'] = {}
        for med, mk in (('English', 'en'), ('Telugu', 'te')):
            d, secs = notes_sections(M['notes'], med)
            out = []; lk = {}
            for i, s in enumerate(secs):
                free = (s['wk'] == 1)
                e = {'h': s['h'], 'n': len(s['topics']), 'free': free, 'titles': [[t['n'], t['t']] for t in s['topics']]}
                if free: e['topics'] = s['topics']
                else: lk[str(i)] = s['topics']
                out.append(e)
            pub['notes'][mk] = {'title': d['title'], 'intro': d['intro'], 'sections': out,
                                'total': sum(len(s['topics']) for s in secs)}
            locked['notes'][mk] = lk
    else:
        pub['notes_link'] = 'index.html#digest'
    # test
    pub['test'] = {}
    for med, mk in (('English', 'en'), ('Telugu', 'te')):
        t = json.load(open(os.path.join(HERE, f'MockTest_{M["test"]}_{med}.json'), encoding='utf-8'))
        pub['test'][mk] = {'title': t['title'], 'sub': t['sub'], 'info': t['info'], 'n': len(t['q']), 'free': t['q'][:FREE_Q]}
        locked['test'][mk] = t['q'][FREE_Q:]
    pub['enc'] = b64(enc(key, json.dumps(locked, ensure_ascii=False).encode()))
    # pdfs
    pub['pdfs'] = []
    for pid, le, lt, src in M['pdfs']:
        raw = open(os.path.join(HERE, src), 'rb').read()
        fn = f'ca/files/{mid}-{pid}.bin'
        open(os.path.join(OUT, fn), 'wb').write(enc(key, raw))
        pub['pdfs'].append({'id': pid, 'label': {'en': le, 'te': lt}, 'file': fn, 'kb': round(len(raw) / 1024),
                            'name': f'Sulabham_{M["en"].replace(" ", "_")}_{pid}.pdf'})
    # UPI QR
    upi = f'upi://pay?pa={UPI}&pn=Sulabham&am=29&cu=INR&tn=Sulabham%20{M["en"].replace(" ", "%20")}'
    pub['upi'] = upi
    img = qrcode.make(upi, box_size=8, border=2); qp = f'ca/qr-{mid}.png'; img.save(os.path.join(OUT, qp)); pub['qr'] = qp
    json.dump(pub, open(os.path.join(OUT, 'ca', mid + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    nt = pub['notes']['en']['total'] if M['notes'] else 91
    index.append({'id': mid, 'label': pub['label'], 'topics': nt, 'q': pub['test']['en']['n'], 'pdfs': len(pub['pdfs'])})
    print(mid, code, 'enc', len(pub['enc']) // 1024, 'KB')
json.dump(index, open(os.path.join(OUT, 'ca', 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(codes, open(CODES_P, 'w'), indent=1)
