# Parse monthly mock test docx -> {title, sub, info, q:[{n, body:[str | {"tbl":[[..]]}], o:[4], a:0-3, x:str}]}
import docx, re, json, sys
from docx.table import Table
from docx.text.paragraph import Paragraph

Q = re.compile(r'^(\d{1,3})\.\s+(.*)$', re.S)
OPT = re.compile(r'^\(([a-dA-D])\)\s*(.*)$', re.S)
EXP = re.compile(r'^(\d{1,3})\.\s*\(([A-Da-d])\)\s*(.*)$', re.S)

def rows(t):
    out = []
    for r in t.rows:
        seen = []; cs = []
        for c in r.cells:
            if c._tc in seen: continue
            seen.append(c._tc); cs.append(c.text.strip())
        out.append(cs)
    return out

def parse(path):
    d = docx.Document(path)
    title = sub = info = None
    qs = []; cur = None; mode = 'q'; key = {}; exp = {}
    for el in d.element.body.iterchildren():
        tag = el.tag.split('}')[1]
        if tag == 'tbl':
            rr = rows(Table(el, d))
            if mode == 'key' or (mode == 'q' and rr and all(re.fullmatch(r'\d{1,3}', x) for x in rr[0] if x) and len(rr[0]) >= 5):
                mode = 'key'
                for i in range(0, len(rr) - 1, 2):
                    for n, a in zip(rr[i], rr[i + 1]):
                        if n.strip().isdigit() and a.strip(): key[int(n)] = 'ABCD'.index(a.strip().upper()[0])
                continue
            if cur is not None: cur['body'].append({'tbl': rr})
            continue
        if tag != 'p': continue
        p = Paragraph(el, d); t = p.text.strip()
        if not t: continue
        if title is None: title = t; continue
        if sub is None: sub = t; continue
        if info is None and not Q.match(t): info = t; continue
        up = t.upper()
        if up.startswith('ANSWER KEY') or t.startswith('సమాధానాల కీ'):
            mode = 'key'; cur = None; continue
        if up.startswith('EXPLANATIONS') or t.startswith('వివరణలు'):
            mode = 'exp'; continue
        if mode == 'exp':
            m = EXP.match(t)
            if m: exp[int(m.group(1))] = m.group(3).strip(); last = int(m.group(1))
            elif exp: exp[last] += ' ' + t
            continue
        if mode == 'key': continue
        bolds = [r.bold for r in p.runs if r.text.strip()]
        m = Q.match(t)
        if m and bolds and bolds[0]:
            cur = {'n': int(m.group(1)), 'body': [m.group(2).strip()], 'o': []}; qs.append(cur); continue
        if cur is None: continue
        mo = OPT.match(t)
        if mo:
            cur['o'].append(mo.group(2).strip()); continue
        cur['body'].append(t)
    for q in qs:
        assert len(q['o']) == 4, (path, q['n'], q['o'])
        q['a'] = key[q['n']]
        q['x'] = exp.get(q['n'], '')
    assert [q['n'] for q in qs] == list(range(1, len(qs) + 1)), path
    return {'title': title, 'sub': sub, 'info': info, 'q': qs}

if __name__ == '__main__':
    r = parse(sys.argv[1])
    json.dump(r, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False)
    from collections import Counter
    print(sys.argv[1], len(r['q']), 'explained', sum(1 for q in r['q'] if q['x']), Counter(q['a'] for q in r['q']))
