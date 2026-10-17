# Build the Group 1 & 2 Prelims Pack data: public pk/pack.json + encrypted PDFs and locked test questions.
# usage: python3 build_pk.py <repo root>
import json, os, sys, base64, secrets, re, shutil
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from pypdf import PdfReader, PdfWriter
import qrcode

H = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1]; SITE = os.path.join(H, '..', 'site')
ITER = 150000; FREE_Q = 10; PRICE = 499; UPI = 'raghu.cse999@axl'
CP = os.path.join(H, 'codes.json'); codes = json.load(open(CP)) if os.path.exists(CP) else {}
if 'pack' not in codes: codes['pack'] = 'G12-' + ''.join(secrets.choice('ABCDEFGHJKMNPQRSTUVWXYZ23456789') for _ in range(6))
json.dump(codes, open(CP, 'w'), indent=1)
norm = lambda c: re.sub(r'[^A-Z0-9]', '', c.upper())
salt = secrets.token_bytes(16)
KEY = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(norm(codes['pack']).encode())
def enc(b): n = secrets.token_bytes(12); return n + AESGCM(KEY).encrypt(n, b, None)
b64 = lambda b: base64.b64encode(b).decode()
B = lambda en, te: {'en': en, 'te': te}
for d in ('pk/files', 'pk/sample', 'pk/free'): os.makedirs(os.path.join(OUT, d), exist_ok=True)

def pages(p): return len(PdfReader(p).pages)
def sample(src, dst, n=3):
    r = PdfReader(src); w = PdfWriter()
    for i in range(min(n, len(r.pages))): w.add_page(r.pages[i])
    w.write(dst)
def free_file(src, name):
    shutil.copy(src, os.path.join(OUT, 'pk/free', name)); return 'pk/free/' + name
def locked_file(src, fid):
    raw = open(src, 'rb').read(); fn = f'pk/files/{fid}.bin'
    open(os.path.join(OUT, fn), 'wb').write(enc(raw)); return {'file': fn, 'kb': round(len(raw) / 1024)}

S = os.path.join(SITE); P = os.path.join(H, 'pdf'); SR = os.path.join(H, 'src')
VOLS = {
 'geo': [
  (1, B('Volume 1 — General & World Geography', 'సంపుటి 1 — సాధారణ & ప్రపంచ భూగోళశాస్త్రం'),
   B('Universe, Earth, time, interior, plates, rocks, atmosphere, winds, cyclones, oceans · 10 chapters', 'విశ్వం, భూమి, కాలం, అంతర్భాగం, ఫలకాలు, శిలలు, వాతావరణం, పవనాలు, తుఫానులు, సముద్రాలు · 10 అధ్యాయాలు'),
   True, os.path.join(S, 'Geography_Vol1_General_Basics.pdf'), os.path.join(S, 'Geography_Vol1_Telugu.pdf')),
  (2, B('Volume 2 — Physical India & AP', 'సంపుటి 2 — భారత్ & ఏపీ భౌతిక భూగోళం'),
   B('Location, physiography, drainage, monsoon, soils, vegetation & wildlife, hazards · 7 chapters', 'ఉనికి, భౌతిక స్వరూపం, నదీ వ్యవస్థ, రుతుపవనాలు, నేలలు, వృక్ష & వన్యప్రాణులు, విపత్తులు · 7 అధ్యాయాలు'),
   False, os.path.join(S, 'Geography_Vol2_Physical_India_AP.pdf'), os.path.join(S, 'Geography_Vol2_Telugu.pdf')),
  (3, B('Volume 3 — Andhra Pradesh', 'సంపుటి 3 — ఆంధ్రప్రదేశ్'),
   B('Regions, districts, water, agriculture, minerals, energy, industry, transport, people · 8 chapters', 'ప్రాంతాలు, జిల్లాలు, నీరు, వ్యవసాయం, ఖనిజాలు, శక్తి, పరిశ్రమలు, రవాణా, ప్రజలు · 8 అధ్యాయాలు'),
   False, os.path.join(S, 'Geography_Vol3_Andhra_Pradesh.pdf'), os.path.join(S, 'Geography_Vol3_Telugu.pdf')),
  (4, B('Volume 4 — Social, Economic & Environmental', 'సంపుటి 4 — సామాజిక, ఆర్థిక & పర్యావరణ భూగోళం'),
   B('World climate regions, population, agriculture, minerals & energy, industries, transport & trade, ecology, pollution & laws · 8 chapters', 'ప్రపంచ శీతోష్ణ మండలాలు, జనాభా, వ్యవసాయం, ఖనిజాలు & శక్తి, పరిశ్రమలు, రవాణా & వాణిజ్యం, జీవావరణం, కాలుష్యం & చట్టాలు · 8 అధ్యాయాలు'),
   False, os.path.join(P, 'APPSC_Geography_Vol4_Social_Economic_Environment.pdf'), os.path.join(P, 'APPSC_Geography_Vol4_Social_Economic_Environment_Telugu.pdf')),
 ],
 'his': [
  (1, B('Volume 1 — Ancient India', 'సంపుటి 1 — ప్రాచీన భారతదేశం'),
   B('Sources, prehistory, Indus, Vedic, Mahajanapadas, Buddhism & Jainism, Mauryas, Satavahanas, Ikshvakus, Sangam, Guptas, Harsha, early Andhra dynasties · 12 chapters, 6 maps', 'ఆధారాలు, చరిత్రపూర్వం, సింధు, వేద కాలం, మహాజనపదాలు, బౌద్ధ & జైన మతాలు, మౌర్యులు, శాతవాహనులు, ఇక్ష్వాకులు, సంగం, గుప్తులు, హర్షుడు, తొలి ఆంధ్ర రాజవంశాలు · 12 అధ్యాయాలు, 6 మ్యాప్‌లు'),
   False, os.path.join(P, 'APPSC_History_Vol1_Ancient_India.pdf'), os.path.join(P, 'APPSC_History_Vol1_Ancient_India_Telugu.pdf')),
 ]}
TESTS = [
 ('geo-mt1', 'geo', B('Geography Mock Test 1 — Volume 1', 'భూగోళం మాక్ టెస్ట్ 1 — సంపుటి 1'), ('old', '1'), os.path.join(S, 'Geography_MockTest1_ExamPattern.pdf'), True),
 ('geo-mt2', 'geo', B('Geography Mock Test 2 — Volume 2', 'భూగోళం మాక్ టెస్ట్ 2 — సంపుటి 2'), ('old', '2'), os.path.join(S, 'Geography_MockTest2_ExamPattern.pdf'), False),
 ('geo-mt3', 'geo', B('Geography Mock Test 3 — Volume 3', 'భూగోళం మాక్ టెస్ట్ 3 — సంపుటి 3'), ('old', '3'), os.path.join(S, 'Geography_MockTest3_ExamPattern.pdf'), False),
 ('geo-mt4', 'geo', B('Geography Mock Test 4 — Volume 4', 'భూగోళం మాక్ టెస్ట్ 4 — సంపుటి 4'), ('new', '4'), os.path.join(P, 'APPSC_Geography_MockTest4_ExamPattern_Bilingual.pdf'), False),
 ('his-mt1', 'his', B('History Mock Test 1 — Ancient India', 'చరిత్ర మాక్ టెస్ట్ 1 — ప్రాచీన భారతదేశం'), ('new', '5'), os.path.join(P, 'APPSC_History_MockTest1_ExamPattern_Bilingual.pdf'), False),
]
OLD = json.load(open(os.path.join(H, '..', 'tests', 'mock.json'), encoding='utf-8'))
NEW = json.load(open(os.path.join(H, 'newmock.json'), encoding='utf-8'))

pack = {'price': PRICE, 'salt': b64(salt), 'iter': ITER, 'free_q': FREE_Q, 'subjects': [], 'tests': {}}
locked = {'tests': {}}
SUBJ = {
 'geo': {'name': B('Geography', 'భూగోళశాస్త్రం'), 'icon': '🌍', 'color': '#1f6f4a',
         'status': B('Complete — all 4 volumes + 4 mock tests', 'పూర్తి — 4 సంపుటాలు + 4 మాక్ టెస్ట్‌లు'), 'done': True,
         'cov': (os.path.join(SR, 'APPSC_Geography_Syllabus_Coverage_English.pdf'), os.path.join(SR, 'APPSC_Geography_Syllabus_Coverage_Telugu.pdf')),
         'marks': B('Prelims Paper I Part D — 30 of 120 questions', 'ప్రిలిమ్స్ పేపర్ I పార్ట్ D — 120లో 30 ప్రశ్నలు')},
 'his': {'name': B('History & Culture', 'చరిత్ర & సంస్కృతి'), 'icon': '🏛️', 'color': '#8a3b12',
         'status': B('Volume 1 ready · Volumes 2–5 coming', 'సంపుటి 1 సిద్ధం · సంపుటాలు 2–5 త్వరలో'), 'done': False,
         'cov': (os.path.join(SR, 'APPSC_History_Syllabus_Coverage_English.pdf'), os.path.join(SR, 'APPSC_History_Syllabus_Coverage_Telugu.pdf')),
         'marks': B('Prelims Paper I Part A — 30 of 120 questions', 'ప్రిలిమ్స్ పేపర్ I పార్ట్ A — 120లో 30 ప్రశ్నలు'),
         'soon': [B('Vol 2 — Medieval India', 'సంపుటి 2 — మధ్యయుగ భారతం'), B('Vol 3 — Modern India', 'సంపుటి 3 — ఆధునిక భారతం'), B('Vol 4 — History & Culture of AP', 'సంపుటి 4 — ఏపీ చరిత్ర & సంస్కృతి'), B('Vol 5', 'సంపుటి 5')]},
}
for sid in ('geo', 'his'):
    s = SUBJ[sid]; o = {'id': sid, 'name': s['name'], 'icon': s['icon'], 'color': s['color'], 'status': s['status'], 'done': s['done'], 'marks': s['marks'], 'vols': [], 'tests': []}
    o['coverage'] = {'en': free_file(s['cov'][0], f'{sid}-syllabus-coverage-en.pdf'), 'te': free_file(s['cov'][1], f'{sid}-syllabus-coverage-te.pdf')}
    if 'soon' in s: o['soon'] = s['soon']
    for n, t, d, free, pe, pt in VOLS[sid]:
        v = {'n': n, 'title': t, 'desc': d, 'free': free, 'pages': {'en': pages(pe), 'te': pages(pt)}}
        if free:
            v['pdf'] = {'en': free_file(pe, f'{sid}-vol{n}-en.pdf'), 'te': free_file(pt, f'{sid}-vol{n}-te.pdf')}
        else:
            v['sample'] = {}
            for m, src in (('en', pe), ('te', pt)):
                dst = f'pk/sample/{sid}-vol{n}-{m}-sample.pdf'; sample(src, os.path.join(OUT, dst)); v['sample'][m] = dst
            v['enc'] = {'en': locked_file(pe, f'{sid}-vol{n}-en'), 'te': locked_file(pt, f'{sid}-vol{n}-te')}
        o['vols'].append(v)
    pack['subjects'].append(o)
for tid, sid, title, (which, k), pdf, free_all in TESTS:
    qs = (OLD if which == 'old' else NEW)[k]['q']
    t = {'id': tid, 'title': title, 'n': len(qs), 'free_all': free_all}
    if free_all:
        t['pdf'] = free_file(pdf, f'{tid}.pdf'); pack['tests'][tid] = qs
    else:
        t['enc'] = locked_file(pdf, tid); pack['tests'][tid] = qs[:FREE_Q]; locked['tests'][tid] = qs[FREE_Q:]
    next(s for s in pack['subjects'] if s['id'] == sid)['tests'].append(t)
pack['enc'] = b64(enc(json.dumps(locked, ensure_ascii=False).encode()))
upi = f'upi://pay?pa={UPI}&pn=Sulabham&am={PRICE}&cu=INR&tn=Sulabham%20Group%201%20and%202%20Prelims%20Pack'
pack['upi'] = upi; qrcode.make(upi, box_size=8, border=2).save(os.path.join(OUT, 'pk/qr.png')); pack['qr'] = 'pk/qr.png'
json.dump(pack, open(os.path.join(OUT, 'pk/pack.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('code', codes['pack'], 'pack.json KB', os.path.getsize(os.path.join(OUT, 'pk/pack.json')) // 1024)
