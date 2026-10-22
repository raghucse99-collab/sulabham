# Incrementally add Polity Vol 1 (Constitution) + Mock Test 1 (creates the 'pol' subject if missing) to the existing pack WITHOUT changing the code or salt.
# usage: PACK_CODE=G12-XXXXXX python3 add_pol1.py <repo root> <dir with source PDFs + mt4.json>   (code is never stored in the repo)
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
pe, pt = os.path.join(SRC, 'APPSC_Polity_Vol1_Constitution.pdf'), os.path.join(SRC, 'APPSC_Polity_Vol1_Constitution_Telugu.pdf')
pol = next((s for s in pack['subjects'] if s['id'] == 'pol'), None)
if pol is None:
    pol = {'id': 'pol', 'name': B('Polity', 'పాలిటీ'), 'icon': '\u2696\ufe0f', 'color': '#7b1fa2', 'done': False,
      'marks': B('Prelims Paper I Part B — Indian Polity and Governance; Group 2 Paper I Section B; Mains Paper III', 'ప్రిలిమ్స్ పేపర్ I పార్ట్ B — భారత పాలిటీ, పాలన; గ్రూప్ 2 పేపర్ I సెక్షన్ B; మెయిన్స్ పేపర్ III'),
      'coverage': {'en': 'pk/free/pol-syllabus-coverage-en.pdf', 'te': 'pk/free/pol-syllabus-coverage-te.pdf'}, 'vols': [], 'tests': [], 'soon': []}
    pack['subjects'].append(pol)
pol['vols'] = [v for v in pol['vols'] if v['n'] != 1]
v = {'n': 1, 'title': B('Volume 1 — The Constitution', 'సంపుటి 1 — భారత రాజ్యాంగం'),
 'desc': B('Making of the Constitution, sources, salient features, Preamble, Union and citizenship, Fundamental Rights and writs, DPSP, Duties, amendments, basic structure, key cases, master list of Parts, Articles and Schedules · 10 chapters, 7 diagrams', 'రాజ్యాంగ రూపకల్పన, లక్షణాలు, ప్రవేశిక, యూనియన్, పౌరసత్వం, ప్రాథమిక హక్కులు, రిట్లు, DPSP, విధులు, సవరణలు, ప్రాథమిక స్వరూపం, కేసులు, ఆర్టికల్స్ జాబితా · 10 అధ్యాయాలు, 7 రేఖాచిత్రాలు'),
 'free': False, 'pages': {'en': len(PdfReader(pe).pages), 'te': len(PdfReader(pt).pages)}, 'sample': {}}
for m, s in (('en', pe), ('te', pt)):
    dst = f'pk/sample/pol-vol1-{m}-sample.pdf'; sample(s, dst); v['sample'][m] = dst
v['enc'] = {'en': locked_file(pe, 'pol-vol1-en'), 'te': locked_file(pt, 'pol-vol1-te')}
pol['vols'].append(v); pol['vols'].sort(key=lambda x: x['n'])
qs = json.load(open(os.path.join(SRC, 'pmt1.json'), encoding='utf-8')); assert len(qs) == 50
pol['tests'] = [t for t in pol['tests'] if t['id'] != 'pol-mt1']
pol['tests'].append({'id': 'pol-mt1', 'title': B('Polity Mock Test 1 — The Constitution', 'పాలిటీ మాక్ టెస్ట్ 1 — రాజ్యాంగం'), 'n': 50, 'free_all': False, 'enc': locked_file(os.path.join(SRC, 'APPSC_Polity_MockTest1_ExamPattern_Bilingual.pdf'), 'pol-mt1')})
pack['tests']['pol-mt1'] = qs[:pack['free_q']]; locked['tests']['pol-mt1'] = qs[pack['free_q']:]
pol['status'] = B('Volume 1 ready · Volumes 2–5 coming', 'సంపుటి 1 సిద్ధం · సంపుటాలు 2–5 త్వరలో')
pol['soon'] = [B('Vol 2 — Union and State Government', 'సంపుటి 2 — కేంద్ర, రాష్ట్ర ప్రభుత్వం'), B('Vol 3 — Federalism, Local Government, Elections', 'సంపుటి 3 — సమాఖ్య, స్థానిక పాలన, ఎన్నికలు'), B('Vol 4 — Constitutional and Statutory Bodies, Governance', 'సంపుటి 4 — రాజ్యాంగ, చట్టబద్ధ సంస్థలు, పాలన'), B('Vol 5 — Cases, Laws and Current Polity', 'సంపుటి 5 — కేసులు, చట్టాలు, తాజా పాలిటీ')] if not pol['soon'] else [s for s in pol['soon'] if not s['en'].startswith('Vol 1')]
for m, nm in (('en', 'English'), ('te', 'Telugu')):
    shutil.copy(os.path.join(SRC, f'APPSC_Polity_Syllabus_Coverage_{nm}.pdf'), os.path.join(R, f'pk/free/pol-syllabus-coverage-{m}.pdf'))
pack['enc'] = b64(enc(json.dumps(locked, ensure_ascii=False).encode()))
json.dump(pack, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('ok; vols', [x['n'] for x in pol['vols']], 'tests', [t['id'] for t in pol['tests']])
