# Build the ASO Paper II course (aso.html data): public aso/data.json + one encrypted file per volume.
# usage: python3 tools/aso/build_aso.py            (run from repo root)
#        python3 tools/aso/build_aso.py --export DIR  (decrypt the published files back to readable sources)
# Private, never committed: tools/aso/codes.json {"aso": "ASO-XXXXXX"} and tools/aso/src/ (course.json, vN/cK.html, vN/cK.q, vN/test.q, mock1.q).
# Keep the SAME code when rebuilding, or every buyer's code stops working.
import json, os, sys, re, base64, secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '..', '..'))
SRC = os.path.join(H, 'src'); OUT = os.path.join(ROOT, 'aso')
ITER = 150000; PRICE = 299; UPI = 'raghu.cse999@axl'; MOCK_FREE = 10
CP = os.path.join(H, 'codes.json'); codes = json.load(open(CP)) if os.path.exists(CP) else {}
norm = lambda c: re.sub(r'[^A-Z0-9]', '', c.upper())
b64 = lambda b: base64.b64encode(b).decode()

def key(salt): return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(norm(codes['aso']).encode())

def parse_quiz(path):
    """Blocks split by '---'. Q: line (repeatable) · a) b) c) d) options · ANS: x · X: explanation."""
    qs = []
    for blk in re.split(r'\n-{3,}\s*\n', open(path, encoding='utf-8').read().strip() + '\n'):
        q, o, a, x = [], [], None, ''
        for ln in blk.strip().split('\n'):
            ln = ln.rstrip()
            if not ln: continue
            m = re.match(r'^([a-d])\)\s*(.*)$', ln)
            if ln.startswith('Q:'): q.append(ln[2:].strip())
            elif m: o.append(m.group(2))
            elif ln.startswith('ANS:'): a = 'abcd'.index(ln[4:].strip().lower()[0])
            elif ln.startswith('X:'): x = ln[2:].strip()
            elif x: x += ' ' + ln.strip()
            elif q and not o: q.append(ln.strip())
            else: raise ValueError(f'{path}: stray line: {ln}')
        if not blk.strip(): continue
        if len(o) != 4 or a is None or not q: raise ValueError(f'{path}: bad block starting {q[:1]} (opts {len(o)}, ans {a})')
        qs.append(mix({'q': q, 'o': o, 'a': a, 'x': x}))
    return qs

FIXED = re.compile(r'\(A\)|\bA is\b|\bOnly one\b|\bNone\b|\bNeither\b|\bAll of the above|\bBoth\b|above', re.I)
def mix(q):
    """Deterministically reorder options so answers are spread over a-d; ordered option sets (A-R codes, 'Only one…None', 'Both/Neither') stay as written."""
    if any(FIXED.search(o) for o in q['o']): return q
    import hashlib
    r = int(hashlib.md5(' '.join(q['q']).encode()).hexdigest(), 16)
    perm = [0, 1, 2, 3]
    for i in range(3, 0, -1):
        r, j = divmod(r, i + 1); perm[i], perm[j] = perm[j], perm[i]
    return {'q': q['q'], 'o': [q['o'][k] for k in perm], 'a': perm.index(q['a']), 'x': q['x']}

def build():
    if 'aso' not in codes:
        codes['aso'] = 'ASO-' + ''.join(secrets.choice('ABCDEFGHJKMNPQRSTUVWXYZ23456789') for _ in range(6))
        json.dump(codes, open(CP, 'w'), indent=1)
    salt = secrets.token_bytes(16); K = AESGCM(key(salt))
    enc = lambda b: (lambda n: n + K.encrypt(n, b, None))(secrets.token_bytes(12))
    C = json.load(open(os.path.join(SRC, 'course.json'), encoding='utf-8'))
    os.makedirs(OUT, exist_ok=True)
    data = {'price': PRICE, 'mrp': C.get('mrp', 599), 'salt': b64(salt), 'iter': ITER, 'check': b64(enc(b'sulabham-aso')),
            'upi': f'upi://pay?pa={UPI}&pn=Sulabham&am={PRICE}&cu=INR&tn=Sulabham%20ASO%20Paper%20II', 'qr': 'aso/qr.png',
            'analysis': C['analysis'], 'vols': [], 'free': {}, 'mock': []}
    tot = {'ch': 0, 'q': 0, 'fig': 0}
    for v in C['vols']:
        vd = os.path.join(SRC, v['id']); lockv = {'ch': {}, 'test': []}
        vo = {k: v[k] for k in ('id', 'n', 'title', 'units', 'desc', 'icon', 'color')}; vo['ch'] = []
        for c in v['ch']:
            hp, qp = os.path.join(vd, c['id'] + '.html'), os.path.join(vd, c['id'] + '.q')
            if not os.path.exists(hp):
                vo['ch'].append({'id': c['id'], 'title': c['title'], 'desc': c.get('desc', ''), 'soon': True}); continue
            html = open(hp, encoding='utf-8').read(); quiz = parse_quiz(qp) if os.path.exists(qp) else []
            tot['ch'] += 1; tot['q'] += len(quiz); tot['fig'] += html.count('<svg')
            co = {'id': c['id'], 'title': c['title'], 'desc': c.get('desc', ''), 'nq': len(quiz), 'min': max(3, round(len(re.sub('<[^>]+>', ' ', html).split()) / 160)), 'free': bool(c.get('free'))}
            body = {'html': html, 'quiz': quiz}
            if co['free']: data['free'][v['id'] + c['id']] = body
            else: lockv['ch'][c['id']] = body
            vo['ch'].append(co)
        tp = os.path.join(vd, 'test.q')
        if os.path.exists(tp):
            lockv['test'] = parse_quiz(tp); vo['test'] = {'n': len(lockv['test']), 'title': v['test']}; tot['q'] += len(lockv['test'])
        fn = f'aso/{v["id"]}.bin'; open(os.path.join(ROOT, fn), 'wb').write(enc(json.dumps(lockv, ensure_ascii=False).encode()))
        vo['file'] = fn; data['vols'].append(vo)
    mp = os.path.join(SRC, 'mock1.q')
    if os.path.exists(mp):
        mq = parse_quiz(mp); tot['q'] += len(mq)
        data['mock'] = [{'id': 'mock1', 'title': C['mock1'], 'n': len(mq), 'free': mq[:MOCK_FREE], 'file': 'aso/mock1.bin'}]
        open(os.path.join(ROOT, 'aso/mock1.bin'), 'wb').write(enc(json.dumps(mq[MOCK_FREE:], ensure_ascii=False).encode()))
    data['tot'] = tot
    json.dump(data, open(os.path.join(OUT, 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    try:
        import qrcode; qrcode.make(data['upi'], box_size=8, border=2).save(os.path.join(OUT, 'qr.png'))
    except ImportError: print('qrcode missing: pip install qrcode')
    print('code', codes['aso'], '| chapters', tot['ch'], '| questions', tot['q'], '| diagrams', tot['fig'], '| data.json KB', os.path.getsize(os.path.join(OUT, 'data.json')) // 1024)

def export(dst):
    """Rebuild readable sources from the published encrypted files (backup if tools/aso/src is lost)."""
    d = json.load(open(os.path.join(OUT, 'data.json'), encoding='utf-8')); K = AESGCM(key(base64.b64decode(d['salt'])))
    dec = lambda b: K.decrypt(b[:12], b[12:], None)
    os.makedirs(dst, exist_ok=True)
    for v in d['vols']:
        lk = json.loads(dec(open(os.path.join(ROOT, v['file']), 'rb').read())); os.makedirs(os.path.join(dst, v['id']), exist_ok=True)
        for c in v['ch']:
            body = d['free'].get(v['id'] + c['id']) or lk['ch'].get(c['id'])
            if body: open(os.path.join(dst, v['id'], c['id'] + '.html'), 'w', encoding='utf-8').write(body['html']); json.dump(body['quiz'], open(os.path.join(dst, v['id'], c['id'] + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        json.dump(lk['test'], open(os.path.join(dst, v['id'], 'test.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('exported to', dst)

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--export': export(sys.argv[2])
    else: build()
