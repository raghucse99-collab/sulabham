# Parse monthly CA notes docx -> {title, sub, intro, sections:[{h, wk, topics:[{n,t,html}]}]}
import docx, re, json, sys, html as H
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

def runs_html(p):
    out = []
    for r in p.runs:
        t = r.text
        if not t: continue
        e = H.escape(t)
        if r.bold and t.strip(): e = '<b>' + e + '</b>'
        out.append(e)
    s = ''.join(out).replace('</b><b>', '')
    return s.strip()

def table_html(t):
    rows = []
    for i, r in enumerate(t.rows):
        seen = []; cells = []
        for c in r.cells:
            if c._tc in seen: continue
            seen.append(c._tc); cells.append(H.escape(c.text.strip()))
        tag = 'th' if i == 0 else 'td'
        rows.append('<tr>' + ''.join(f'<{tag}>{x}</{tag}>' for x in cells) + '</tr>')
    return '<div class="tw"><table>' + ''.join(rows) + '</table></div>'

WEEK = re.compile(r'^★\s*(WEEK|వారం)', re.I)
TOPIC = re.compile(r'^(\d{1,3})\.\s+(.*)$')

def parse(path):
    d = docx.Document(path)
    title = sub = intro = None
    sections = []; cur_sec = None; cur = None
    buf = []          # html pieces for current topic
    lst = []          # pending <li>
    chain = None      # pending chain dict
    def flush_list():
        nonlocal lst
        if lst: buf.append('<ul>' + ''.join(lst) + '</ul>'); lst = []
    def flush_chain():
        nonlocal chain
        if chain:
            h = f'<b>{chain["h"]}</b>' if chain['h'] else ''
            buf.append('<div class="chain">' + h + '<ul>' + ''.join('<li>' + x + '</li>' for x in chain['l']) + '</ul></div>'); chain = None
    def flush_all():
        flush_list(); flush_chain()
    def close_topic():
        nonlocal cur, buf
        flush_all()
        if cur is not None:
            cur['html'] = ''.join(buf); cur_sec['topics'].append(cur)
        cur = None; buf = []
    for el in d.element.body.iterchildren():
        tag = el.tag.split('}')[1]
        if tag == 'tbl':
            flush_all(); buf.append(table_html(Table(el, d))); continue
        if tag != 'p': continue
        p = Paragraph(el, d); t = p.text.strip()
        if not t: continue
        is_list = el.find('.//' + qn('w:numPr')) is not None or p.style.name.startswith('List')
        bolds = [r.bold for r in p.runs if r.text.strip()]
        allbold = bool(bolds) and all(bolds)
        if title is None: title = t; continue
        if sub is None and not t.startswith('💡'): sub = t; continue
        if t.startswith('💡') and intro is None and not sections:
            intro = runs_html(p); continue
        if WEEK.match(t):
            close_topic()
            cur_sec = {'h': t.lstrip('★ ').strip(), 'topics': []}
            m = re.search(r'(\d+)', t); cur_sec['wk'] = int(m.group(1)) if m else 0
            sections.append(cur_sec); continue
        if t.startswith('★') and cur_sec is None:  # month banner like "★ JULY 2026"
            continue
        m = TOPIC.match(t)
        if m and allbold and not is_list:
            close_topic()
            if cur_sec is None:
                cur_sec = {'h': '', 'wk': 0, 'topics': []}; sections.append(cur_sec)
            cur = {'n': int(m.group(1)), 't': m.group(2).strip()}; continue
        if cur is None:
            if cur_sec is not None and t.startswith('★'):
                continue
            continue
        if t.startswith('🔗'):
            flush_list()
            txt = H.escape(t.lstrip('🔗').strip())
            if allbold and not any(r.italic for r in p.runs if r.text.strip()):
                flush_chain(); chain = {'h': '🔗 ' + txt, 'l': []}
            else:
                if chain is None: chain = {'h': '', 'l': []}
                chain['l'].append(txt)
            continue
        flush_chain()
        if t.startswith('★'):
            flush_list()
            body = t.lstrip('★').strip()
            low = body.lower()
            cls = 'trap' if ('trap' in low or 'ఉచ్చు' in body) else 'note'
            k = body.find(':')
            if 0 < k < 40: body = '<b>' + H.escape(body[:k + 1]) + '</b>' + H.escape(body[k + 1:])
            else: body = H.escape(body)
            buf.append(f'<p class="{cls}">{body}</p>'); continue
        if is_list:
            lst.append('<li>' + runs_html(p) + '</li>'); continue
        flush_list()
        if allbold:
            buf.append('<h5>' + H.escape(t) + '</h5>')
        else:
            buf.append('<p>' + runs_html(p) + '</p>')
    close_topic()
    return {'title': title, 'sub': sub, 'intro': intro, 'sections': sections}

if __name__ == '__main__':
    r = parse(sys.argv[1])
    json.dump(r, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False)
    print(sys.argv[1], [(s['h'], s['wk'], len(s['topics'])) for s in r['sections']], sum(len(s['topics']) for s in r['sections']))
