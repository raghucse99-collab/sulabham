# Incrementally add Polity Vol 3 + Mock Test 3 to the existing pack WITHOUT changing the code or salt.
# usage: PACK_CODE=G12-XXXXXX python3 add_pol3.py <repo root> <dir with source PDFs + mt4.json>   (code is never stored in the repo)
import json, os, sys, base64, re, shutil, secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from pypdf import PdfReader, PdfWriter
R, SRC = sys.argv[1], sys.argv[2]
pj = os.path.join(R, 'pk/pack.json'); pack = json.load(open(pj, encoding='utf-8'))
code = re.sub(r'[^A-Z0-9]', '', os.environ['PACK_CODE'].upper())
KEY = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=base64.b64decode(pack['salt']), iterations=pack['iter']).derive(code.encode())
g = AESGCM(KEY); b64 = lambda b: base64.b64encode(b).decode()
def enc(b): n = secrets.token_bytes(12); return n + g.encrypt(n, b, None)
raw = base64.b64decode(pack['enc']); locked = json.loads(g.decrypt(raw[:12], raw[12:], None))  # raises if code wrong
def locked_file(src, fid):
    d = open(src, 'rb').read(); fn = f'pk/files/{fid}.bin'; open(os.path.join(R, fn), 'wb').write(enc(d)); return {'file': fn, 'kb': round(len(d) / 1024)}
def sample(src, dst, n=3):
    r = PdfReader(src); w = PdfWriter()
    for i in range(min(n, len(r.pages))): w.add_page(r.pages[i])
    w.write(os.path.join(R, dst))
B = lambda en, te: {'en': en, 'te': te}
B = lambda en, te: {'en': en, 'te': te}
pe, pt = os.path.join(SRC, 'APPSC_Polity_Vol3_Federalism_Local_Govt_Elections.pdf'), os.path.join(SRC, 'APPSC_Polity_Vol3_Federalism_Local_Govt_Elections_Telugu.pdf')
pol = next(s for s in pack['subjects'] if s['id'] == 'pol')
pol['vols'] = [v for v in pol['vols'] if v['n'] != 3]
v = {'n': 3, 'title': B('Volume 3 — Federalism, Local Government and Elections', 'సంపుటి 3 — సమాఖ్య, స్థానిక పాలన, ఎన్నికలు'),
 'desc': B('Centre–State relations, Finance Commission and GST, Sarkaria and Punchhi, Panchayati Raj (73rd), urban government (74th), Union Territories, Fifth and Sixth Schedules, elections, parties, reforms, AP links · picture-led, 8 chapters, 11 diagrams, mini-MCQs', 'కేంద్ర–రాష్ట్ర సంబంధాలు, ఆర్థిక సంఘం, GST, సర్కారియా, పూంఛీ, పంచాయతీ రాజ్, పురపాలక, కేంద్రపాలిత ప్రాంతాలు, 5వ, 6వ షెడ్యూళ్లు, ఎన్నికలు, పార్టీలు, సంస్కరణలు, ఏపీ లింకులు · చిత్రాలతో, 8 అధ్యాయాలు, 11 రేఖాచిత్రాలు'),
 'free': False, 'pages': {'en': len(PdfReader(pe).pages), 'te': len(PdfReader(pt).pages)}, 'sample': {}}
for m, s in (('en', pe), ('te', pt)):
    dst = f'pk/sample/pol-vol3-{m}-sample.pdf'; sample(s, dst); v['sample'][m] = dst
v['enc'] = {'en': locked_file(pe, 'pol-vol3-en'), 'te': locked_file(pt, 'pol-vol3-te')}
pol['vols'].append(v); pol['vols'].sort(key=lambda x: x['n'])
qs = json.load(open(os.path.join(SRC, 'pmt3.json'), encoding='utf-8')); assert len(qs) == 50
pol['tests'] = [t for t in pol['tests'] if t['id'] != 'pol-mt3']
pol['tests'].append({'id': 'pol-mt3', 'title': B('Polity Mock Test 3 — Federalism, Local Government and Elections', 'పాలిటీ మాక్ టెస్ట్ 3 — సమాఖ్య, స్థానిక పాలన, ఎన్నికలు'), 'n': 50, 'free_all': False, 'enc': locked_file(os.path.join(SRC, 'APPSC_Polity_MockTest3_ExamPattern_Bilingual.pdf'), 'pol-mt3')})
pack['tests']['pol-mt3'] = qs[:pack['free_q']]; locked['tests']['pol-mt3'] = qs[pack['free_q']:]
pol['status'] = B('Volumes 1–3 ready · Volumes 4–5 coming', 'సంపుటాలు 1–3 సిద్ధం · సంపుటాలు 4–5 త్వరలో')
pol['soon'] = [s for s in pol['soon'] if not s['en'].startswith('Vol 3')]
for m, nm in (('en', 'English'), ('te', 'Telugu')):
    shutil.copy(os.path.join(SRC, f'APPSC_Polity_Syllabus_Coverage_{nm}.pdf'), os.path.join(R, f'pk/free/pol-syllabus-coverage-{m}.pdf'))
pack['enc'] = b64(enc(json.dumps(locked, ensure_ascii=False).encode()))
json.dump(pack, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('ok; vols', [x['n'] for x in pol['vols']], 'tests', [t['id'] for t in pol['tests']], 'soon', [s['en'][:5] for s in pol['soon']])
