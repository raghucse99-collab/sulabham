# Incrementally add Polity Vol 2 (Union and State Government) + Mock Test 2 to the existing pack WITHOUT changing the code or salt.
# usage: PACK_CODE=G12-XXXXXX python3 add_pol2.py <repo root> <dir with source PDFs + mt4.json>   (code is never stored in the repo)
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
pe, pt = os.path.join(SRC, 'APPSC_Polity_Vol2_Union_State_Govt.pdf'), os.path.join(SRC, 'APPSC_Polity_Vol2_Union_State_Govt_Telugu.pdf')
pol = next(s for s in pack['subjects'] if s['id'] == 'pol')
pol['vols'] = [v for v in pol['vols'] if v['n'] != 2]
v = {'n': 2, 'title': B('Volume 2 — Union and State Government', 'సంపుటి 2 — కేంద్ర, రాష్ట్ర ప్రభుత్వం'),
 'desc': B('President and Vice-President, Prime Minister and Council, Parliament, Bills and Budget, committees, Governor and Chief Minister, State Legislature, Supreme Court, High Courts, PIL and judicial review, Emergency, AP links · 10 chapters, 6 diagrams', 'రాష్ట్రపతి, ఉపరాష్ట్రపతి, ప్రధాని, మంత్రి మండలి, పార్లమెంటు, బిల్లులు, బడ్జెట్, కమిటీలు, గవర్నర్, ముఖ్యమంత్రి, శాసనసభ, సుప్రీంకోర్టు, హైకోర్టులు, PIL, న్యాయ సమీక్ష, అత్యవసర పరిస్థితి, ఏపీ లింకులు · 10 అధ్యాయాలు, 6 రేఖాచిత్రాలు'),
 'free': False, 'pages': {'en': len(PdfReader(pe).pages), 'te': len(PdfReader(pt).pages)}, 'sample': {}}
for m, s in (('en', pe), ('te', pt)):
    dst = f'pk/sample/pol-vol2-{m}-sample.pdf'; sample(s, dst); v['sample'][m] = dst
v['enc'] = {'en': locked_file(pe, 'pol-vol2-en'), 'te': locked_file(pt, 'pol-vol2-te')}
pol['vols'].append(v); pol['vols'].sort(key=lambda x: x['n'])
qs = json.load(open(os.path.join(SRC, 'pmt2.json'), encoding='utf-8')); assert len(qs) == 50
pol['tests'] = [t for t in pol['tests'] if t['id'] != 'pol-mt2']
pol['tests'].append({'id': 'pol-mt2', 'title': B('Polity Mock Test 2 — Union and State Government', 'పాలిటీ మాక్ టెస్ట్ 2 — కేంద్ర, రాష్ట్ర ప్రభుత్వం'), 'n': 50, 'free_all': False, 'enc': locked_file(os.path.join(SRC, 'APPSC_Polity_MockTest2_ExamPattern_Bilingual.pdf'), 'pol-mt2')})
pack['tests']['pol-mt2'] = qs[:pack['free_q']]; locked['tests']['pol-mt2'] = qs[pack['free_q']:]
pol['status'] = B('Volumes 1–2 ready · Volumes 3–5 coming', 'సంపుటాలు 1–2 సిద్ధం · సంపుటాలు 3–5 త్వరలో')
pol['soon'] = [s for s in pol['soon'] if not s['en'].startswith('Vol 2')]
for m, nm in (('en', 'English'), ('te', 'Telugu')):
    shutil.copy(os.path.join(SRC, f'APPSC_Polity_Syllabus_Coverage_{nm}.pdf'), os.path.join(R, f'pk/free/pol-syllabus-coverage-{m}.pdf'))
pack['enc'] = b64(enc(json.dumps(locked, ensure_ascii=False).encode()))
json.dump(pack, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('ok; vols', [x['n'] for x in pol['vols']], 'tests', [t['id'] for t in pol['tests']], 'soon', [s['en'][:5] for s in pol['soon']])
