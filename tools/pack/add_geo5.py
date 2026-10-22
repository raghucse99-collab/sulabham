# Incrementally add Geography Vol 5 (Andhra Pradesh) + Mock Test 5 to the existing pack WITHOUT changing the code or salt.
# usage: PACK_CODE=G12-XXXXXX python3 add_geo5.py <repo root> <dir with source PDFs + mt5.json>   (code is never stored in the repo)
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
pe, pt = os.path.join(SRC, 'APPSC_Geography_Vol5_Andhra_Pradesh.pdf'), os.path.join(SRC, 'APPSC_Geography_Vol5_Andhra_Pradesh_Telugu.pdf')
geo = next(s for s in pack['subjects'] if s['id'] == 'geo')
geo['vols'] = [v for v in geo['vols'] if v['n'] != 5]
v = {'n': 5, 'title': B('Volume 5 — Andhra Pradesh Geography (complete handbook)', 'సంపుటి 5 — ఆంధ్రప్రదేశ్ భూగోళం (సమగ్ర గ్రంథం)'),
 'desc': B('Location & 28 districts, geology & relief, rivers & projects, climate & hazards, soils & wildlife, agriculture & fisheries, minerals & power, industry & corridors, transport, ports & tourism, people & tribes, environment · 11 chapters, 10 maps, 10 diagrams, 2025–26 data, self-test', 'స్థానం & 28 జిల్లాలు, భూగర్భం, నదులు & ప్రాజెక్టులు, శీతోష్ణం & విపత్తులు, నేలలు & వన్యప్రాణులు, వ్యవసాయం & మత్స్యం, ఖనిజాలు & విద్యుత్, పరిశ్రమలు, రవాణా, ఓడరేవులు & పర్యాటకం, ప్రజలు & గిరిజనులు, పర్యావరణం · 11 అధ్యాయాలు, 10 పటాలు, 10 చిత్రాలు, 2025–26 గణాంకాలు, స్వీయ పరీక్ష'),
 'free': False, 'pages': {'en': len(PdfReader(pe).pages), 'te': len(PdfReader(pt).pages)}, 'sample': {}}
for m, s in (('en', pe), ('te', pt)):
    dst = f'pk/sample/geo-vol5-{m}-sample.pdf'; sample(s, dst); v['sample'][m] = dst
v['enc'] = {'en': locked_file(pe, 'geo-vol5-en'), 'te': locked_file(pt, 'geo-vol5-te')}
geo['vols'].append(v); geo['vols'].sort(key=lambda x: x['n'])
qs = json.load(open(os.path.join(SRC, 'mt5.json'), encoding='utf-8')); assert len(qs) == 50
geo['tests'] = [t for t in geo['tests'] if t['id'] != 'geo-mt5']
geo['tests'].append({'id': 'geo-mt5', 'title': B('Geography Mock Test 5 — Andhra Pradesh', 'భూగోళం మాక్ టెస్ట్ 5 — ఆంధ్రప్రదేశ్'), 'n': 50, 'free_all': False, 'enc': locked_file(os.path.join(SRC, 'APPSC_Geography_MockTest5_AP_ExamPattern_Bilingual.pdf'), 'geo-mt5')})
pack['tests']['geo-mt5'] = qs[:pack['free_q']]; locked['tests']['geo-mt5'] = qs[pack['free_q']:]
geo['status'] = B('Complete — 5 volumes (incl. full Andhra Pradesh handbook) + 5 mock tests', 'పూర్తి — 5 సంపుటాలు (ఆంధ్రప్రదేశ్ సమగ్ర గ్రంథంతో) + 5 మాక్ టెస్ట్\u200cలు')
for m, nm in (('en', 'English'), ('te', 'Telugu')):
    shutil.copy(os.path.join(SRC, f'APPSC_Geography_Syllabus_Coverage_{nm}.pdf'), os.path.join(R, f'pk/free/geo-syllabus-coverage-{m}.pdf'))
pack['enc'] = b64(enc(json.dumps(locked, ensure_ascii=False).encode()))
json.dump(pack, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('ok; vols', [x['n'] for x in geo['vols']], 'tests', [t['id'] for t in geo['tests']])
