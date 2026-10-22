# Incrementally add History Vol 4 (Andhra Pradesh) + Mock Test 4 to the existing pack WITHOUT changing the code or salt.
# usage: PACK_CODE=G12-XXXXXX python3 add_his4.py <repo root> <dir with source PDFs + mt4.json>   (code is never stored in the repo)
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
pe, pt = os.path.join(SRC, 'APPSC_History_Vol4_Andhra_Pradesh.pdf'), os.path.join(SRC, 'APPSC_History_Vol4_Andhra_Pradesh_Telugu.pdf')
his = next(s for s in pack['subjects'] if s['id'] == 'his')
his['vols'] = [v for v in his['vols'] if v['n'] != 4]
v = {'n': 4, 'title': B('Volume 4 — History of Andhra Pradesh', 'సంపుటి 4 — ఆంధ్రప్రదేశ్ చరిత్ర'),
 'desc': B('Ancient Andhra, Eastern Chalukyas, Kakatiyas, Reddis, Gajapatis, Vijayanagara, Qutb Shahis, Telugu literature, Company rule, reformers, nationalist movement, Andhra State 1953, AP 1956, 2014 bifurcation · 9 chapters, 4 maps and diagrams, who\'s-who tables', 'ప్రాచీన ఆంధ్ర, తూర్పు చాళుక్యులు, కాకతీయులు, రెడ్డిలు, గజపతులు, విజయనగరం, కుతుబ్ షాహీలు, తెలుగు సాహిత్యం, కంపెనీ పాలన, సంస్కర్తలు, జాతీయోద్యమం, ఆంధ్ర రాష్ట్రం 1953, ఏపీ 1956, 2014 విభజన · 9 అధ్యాయాలు, పటాలు, రేఖాచిత్రాలు, ఎవరు-ఎవరు పట్టికలు'),
 'free': False, 'pages': {'en': len(PdfReader(pe).pages), 'te': len(PdfReader(pt).pages)}, 'sample': {}}
for m, s in (('en', pe), ('te', pt)):
    dst = f'pk/sample/his-vol4-{m}-sample.pdf'; sample(s, dst); v['sample'][m] = dst
v['enc'] = {'en': locked_file(pe, 'his-vol4-en'), 'te': locked_file(pt, 'his-vol4-te')}
his['vols'].append(v); his['vols'].sort(key=lambda x: x['n'])
qs = json.load(open(os.path.join(SRC, 'mt4.json'), encoding='utf-8')); assert len(qs) == 50
his['tests'] = [t for t in his['tests'] if t['id'] != 'his-mt4']
his['tests'].append({'id': 'his-mt4', 'title': B('History Mock Test 4 — Andhra Pradesh', 'చరిత్ర మాక్ టెస్ట్ 4 — ఆంధ్రప్రదేశ్'), 'n': 50, 'free_all': False, 'enc': locked_file(os.path.join(SRC, 'APPSC_History_MockTest4_ExamPattern_Bilingual.pdf'), 'his-mt4')})
pack['tests']['his-mt4'] = qs[:pack['free_q']]; locked['tests']['his-mt4'] = qs[pack['free_q']:]
his['status'] = B('Volumes 1, 2 and 4 ready · Volumes 3 and 5 coming', 'సంపుటాలు 1, 2, 4 సిద్ధం · సంపుటాలు 3, 5 త్వరలో')
his['soon'] = [s for s in his.get('soon', []) if not s['en'].startswith('Vol 4')]
for m, nm in (('en', 'English'), ('te', 'Telugu')):
    shutil.copy(os.path.join(SRC, f'APPSC_History_Syllabus_Coverage_{nm}.pdf'), os.path.join(R, f'pk/free/his-syllabus-coverage-{m}.pdf'))
pack['enc'] = b64(enc(json.dumps(locked, ensure_ascii=False).encode()))
json.dump(pack, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('ok; vols', [x['n'] for x in his['vols']], 'tests', [t['id'] for t in his['tests']])
