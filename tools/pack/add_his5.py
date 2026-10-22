# Incrementally add History Vol 5 (Art, Architecture and Culture) + Mock Test 5 to the existing pack WITHOUT changing the code or salt.
# usage: PACK_CODE=G12-XXXXXX python3 add_his5.py <repo root> <dir with source PDFs + mt5.json>   (code is never stored in the repo)
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
pe, pt = os.path.join(SRC, 'APPSC_History_Vol5_Art_Culture.pdf'), os.path.join(SRC, 'APPSC_History_Vol5_Art_Culture_Telugu.pdf')
his = next(s for s in pack['subjects'] if s['id'] == 'his')
his['vols'] = [v for v in his['vols'] if v['n'] != 5]
v = {'n': 5, 'title': B('Volume 5 — Art, Architecture and Culture', 'సంపుటి 5 — కళలు, వాస్తు, సంస్కృతి'),
 'desc': B('Harappan to Mauryan art, Buddhist and Jain art, caves and stupas, temple styles, AP and Telangana temples (all regions), Indo-Islamic and colonial architecture, painting, crafts and GI products, music, dance, folk arts, languages, literature, religion, festivals, UNESCO sites, institutions · 9 chapters, maps and diagrams', 'హరప్పా నుండి మౌర్య కళ, బౌద్ధ, జైన కళ, గుహలు, స్తూపాలు, ఆలయ శైలులు, ఆంధ్ర, తెలంగాణ ఆలయాలు (అన్ని ప్రాంతాలు), ఇండో-ఇస్లామిక్, చిత్రకళ, హస్తకళలు, GI ఉత్పత్తులు, సంగీతం, నృత్యం, జానపద కళలు, భాషలు, సాహిత్యం, మతం, పండుగలు, యునెస్కో, సంస్థలు · 9 అధ్యాయాలు'),
 'free': False, 'pages': {'en': len(PdfReader(pe).pages), 'te': len(PdfReader(pt).pages)}, 'sample': {}}
for m, s in (('en', pe), ('te', pt)):
    dst = f'pk/sample/his-vol5-{m}-sample.pdf'; sample(s, dst); v['sample'][m] = dst
v['enc'] = {'en': locked_file(pe, 'his-vol5-en'), 'te': locked_file(pt, 'his-vol5-te')}
his['vols'].append(v); his['vols'].sort(key=lambda x: x['n'])
qs = json.load(open(os.path.join(SRC, 'mt5.json'), encoding='utf-8')); assert len(qs) == 50
his['tests'] = [t for t in his['tests'] if t['id'] != 'his-mt5']
his['tests'].append({'id': 'his-mt5', 'title': B('History Mock Test 5 — Art, Architecture and Culture', 'చరిత్ర మాక్ టెస్ట్ 5 — కళలు, వాస్తు, సంస్కృతి'), 'n': 50, 'free_all': False, 'enc': locked_file(os.path.join(SRC, 'APPSC_History_MockTest5_ExamPattern_Bilingual.pdf'), 'his-mt5')})
pack['tests']['his-mt5'] = qs[:pack['free_q']]; locked['tests']['his-mt5'] = qs[pack['free_q']:]
his['status'] = B('Complete — 5 volumes + 5 mock tests', 'పూర్తి — 5 సంపుటాలు + 5 మాక్ టెస్ట్‌లు')
his['soon'] = []
his['done'] = True
for m, nm in (('en', 'English'), ('te', 'Telugu')):
    shutil.copy(os.path.join(SRC, f'APPSC_History_Syllabus_Coverage_{nm}.pdf'), os.path.join(R, f'pk/free/his-syllabus-coverage-{m}.pdf'))
pack['enc'] = b64(enc(json.dumps(locked, ensure_ascii=False).encode()))
json.dump(pack, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('ok; vols', [x['n'] for x in his['vols']], 'tests', [t['id'] for t in his['tests']])
