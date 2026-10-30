"""Sulabham Visual Library builder.
usage: python3 tools/vlib/build.py
Validates every lesson file vlib/<area>/<ID>.json against tools/CONTENT_STANDARD.md (7 parts, bilingual,
5-10 MCQs, sources, syllabus links) and writes vlib/index.json from tools/vlib/plan.py."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from plan import AREAS

SYL = set()
def walk(o):
    if isinstance(o, dict):
        if isinstance(o.get('id'), str): SYL.add(o['id'])
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(json.load(open(os.path.join(ROOT, 'syllabus', 'group2.json'), encoding='utf-8')))
IDS = {it[0] for a in AREAS for s in a['subs'] for it in s['items']}
TEL = re.compile('[ఀ-౿]')
ERR = []

def bi(o, w, opt=False):
    if o is None and opt: return
    if not (isinstance(o, dict) and str(o.get('en', '')).strip() and str(o.get('te', '')).strip()):
        ERR.append(f'{w}: needs en + te'); return
    if re.search('[a-z]{3,}', o['en']) and not TEL.search(o['te']) and (o['te'] == o['en'] or re.search('[a-z]{3,}', o['te'])): ERR.append(f'{w}: te looks untranslated: {o["te"][:40]}')

def node(n, w, needy=True):
    bi(n.get('t'), w + ' t'); bi(n.get('s'), w + ' s', True)
    if needy: bi(n.get('n'), w + ' n (tap note)')
    for k, x in enumerate(n.get('items', [])): bi(x, f'{w} item{k}')

def vis(v, w):
    ty = v.get('type')
    if ty == 'hub':
        bi(v.get('c'), w + ' centre'); bi(v.get('cs'), w + ' centre sub', True)
        assert 3 <= len(v['nodes']) <= 10, f'{w}: hub needs 3-10 nodes'
        for i, n in enumerate(v['nodes']): node(n, f'{w} node{i}')
    elif ty in ('flow', 'timeline'):
        assert 3 <= len(v['items']) <= 10, f'{w}: {ty} needs 3-10 items'
        for i, n in enumerate(v['items']):
            node(n, f'{w} item{i}')
            if ty == 'timeline': assert str(n.get('y', '')).strip(), f'{w} item{i}: year y'
    elif ty == 'compare':
        h = v['h']; assert 2 <= len(h) <= 3, f'{w}: compare needs 2-3 column heads'
        for i, x in enumerate(h): bi(x, f'{w} head{i}')
        assert 3 <= len(v['rows']) <= 12, f'{w}: compare needs 3-12 rows'
        for i, r in enumerate(v['rows']):
            bi(r.get('k'), f'{w} row{i} k'); bi(r.get('n'), f'{w} row{i} n', True)
            assert len(r['v']) == len(h), f'{w} row{i}: {len(h)} values needed'
            for j, x in enumerate(r['v']): bi(x, f'{w} row{i} v{j}')
    elif ty == 'tree':
        L = v['levels']; assert 2 <= len(L) <= 5, f'{w}: tree needs 2-5 levels'
        for i, lev in enumerate(L):
            assert 1 <= len(lev) <= 3, f'{w}: level{i} 1-3 boxes'
            for j, n in enumerate(lev):
                node(n, f'{w} L{i}.{j}')
                if i: assert 0 <= n.get('p', 0) < len(L[i-1]), f'{w} L{i}.{j}: bad parent p'
    else: raise AssertionError(f'{w}: unknown visual type {ty}')
    bi(v.get('cap'), w + ' caption', True)

def lesson(path, item):
    iid, title, syl, ty = item
    D = json.load(open(path, encoding='utf-8')); w = iid
    try:
        assert D.get('id') == iid, f'{w}: id mismatch'
        assert re.fullmatch(r'\d{4}-\d\d-\d\d', D.get('checked', '')), f'{w}: checked date'
        bi(D.get('lead'), w + ' lead'); vis(D['vis'], w + ' visual')
        assert D['vis']['type'] == ty, f'{w}: plan says {ty}'
        for k, n in (('explain', (3, 7)), ('conn', (2, 6)), ('memory', (1, 3)), ('apply', (2, 5)), ('mcq', (5, 10)), ('refs', (1, 6))):
            assert n[0] <= len(D.get(k, [])) <= n[1], f'{w}: {k} needs {n[0]}-{n[1]} entries'
        for i, x in enumerate(D['explain']): bi(x, f'{w} explain{i}')
        for i, x in enumerate(D['memory']): bi(x, f'{w} memory{i}')
        for i, x in enumerate(D['apply']): bi(x, f'{w} apply{i}')
        for i, c in enumerate(D['conn']):
            bi(c.get('t'), f'{w} conn{i}')
            assert c.get('to') in IDS or c.get('to') in SYL, f'{w} conn{i}: "to" must be a VL id or syllabus id ({c.get("to")})'
        for i, q in enumerate(D['mcq']):
            bi(q.get('q'), f'{w} mcq{i} q'); bi(q.get('why'), f'{w} mcq{i} why')
            for k, s in enumerate(q.get('st', [])): bi(s, f'{w} mcq{i} st{k}')
            assert len(q['o']) == 4 and q['a'] in (0, 1, 2, 3), f'{w} mcq{i}: 4 options + a 0-3'
            for k, o in enumerate(q['o']): bi(o, f'{w} mcq{i} o{k}')
        for r in D['refs']: assert r.get('t') and str(r.get('u', '')).startswith('https://'), f'{w}: ref t + https u'
    except (AssertionError, KeyError, TypeError) as e: ERR.append(f'{w}: {e}')
    return len(D.get('mcq', []))

def main():
    for s in {x for it in (i for a in AREAS for su in a['subs'] for i in su['items']) for x in it[2]}:
        if s not in SYL: ERR.append(f'plan: unknown syllabus id {s}')
    out, nr, npl = [], 0, 0
    for a in AREAS:
        A = {'id': a['id'], 'em': a['em'], 'phase': a['phase'], 't': a['t'], 'subs': []}
        for s in a['subs']:
            S = {'id': s['id'], 't': s['t'], 'items': []}
            for it in s['items']:
                p = os.path.join(ROOT, 'vlib', a['id'], it[0] + '.json'); npl += 1
                e = {'id': it[0], 't': it[1], 'syl': it[2], 'type': it[3], 'ready': os.path.exists(p)}
                if e['ready']: e['nq'] = lesson(p, it); nr += 1
                S['items'].append(e)
            A['subs'].append(S)
        out.append(A)
    if ERR:
        print('\n'.join(ERR)); sys.exit(1)
    json.dump({'areas': out, 'ready': nr, 'planned': npl}, open(os.path.join(ROOT, 'vlib', 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'vlib ok: {nr} ready of {npl} planned')

if __name__ == '__main__': main()
