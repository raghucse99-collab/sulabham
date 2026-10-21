"""Render a 'map' picture (from a day / current-affairs JSON) to SVG, using tools/maps/base.json.
India is always drawn with its official boundary (Survey of India claim: whole of J&K and Ladakh incl. PoK, Aksai Chin).

Picture spec (inside "pics" / "pic"):
{"type": "map", "h": {en,te},
 "view": "india" | "north" | "northeast" | "south" | "ap" | "southasia" | "world" | [lon_min, lat_min, lon_max, lat_max],
 "hl":  ["Ladakh", "Arunachal Pradesh"],          // Indian states/UTs to colour (names as in STATES below)
 "hlc": "#b3322b",                                 // optional colour for hl (default red)
 "ctry": ["China"],                                // optional neighbouring/world countries to colour (Natural Earth names)
 "pts": [{"ll": [34.17, 77.58], "t": {en,te}, "c": "#1d4f91", "a": "l"|"r"}],   // places: dot + label (a = label side)
 "labels": [{"ll": [33, 85], "t": {en,te}}],       // plain labels (regions, seas, countries) without a dot
 "lines": [{"ll": [[lat,lon], [lat,lon], ...], "c": "#b3322b", "dash": 1, "arrow": 1}],   // routes / movements / borders
 "rivers": ["Godavari", "Krishna"] | "all",   // physical layers (names in tools/maps/phys.json; English names)
 "regions": ["Western Ghats", "Deccan Plateau"] | "all",   // mountain ranges, plateaus, deserts, plains, coasts, deltas
 "peaks": ["Mount Everest", "Anamudi"] | "all",
 "seas": true,                                     // names of seas / bays / gulfs
 "cap": {en,te}}
"""
import json, math, os, html
HERE = os.path.dirname(os.path.abspath(__file__))
B = json.load(open(os.path.join(HERE, 'base.json')))
PH = json.load(open(os.path.join(HERE, 'phys.json'), encoding='utf-8'))
KC = {'Range/mtn': ('#9a6a3a', .42), 'Plateau': ('#c49a5e', .30), 'Desert': ('#e3b94f', .45), 'Plain': ('#8fbf6a', .35),
      'Delta': ('#4fa592', .45), 'Wetlands': ('#4fa592', .45), 'Coast': ('#3f93b0', .40), 'Valley': ('#6fae5c', .45), 'Pen/cape': ('#cdb48a', .30)}
STATES = sorted(B['states'])
VIEWS = {'india': [66.5, 6, 98.5, 37.6], 'north': [72.5, 25.8, 97.8, 37.4], 'northeast': [87.5, 21.5, 97.8, 29.7],
         'south': [72.5, 7.5, 88.5, 21.5], 'ap': [76.4, 12.4, 85.2, 19.6], 'southasia': [57, 1, 103, 41],
         'world': [-170, -56, 190, 78]}
W = 560

def validate(p):
    v = p.get('view', 'india')
    assert (isinstance(v, list) and len(v) == 4) or v in VIEWS, f'map view must be one of {list(VIEWS)} or [lon_min,lat_min,lon_max,lat_max]'
    for s in p.get('hl', []): assert s in B['states'], f'map hl: unknown state "{s}". Use one of: {STATES}'
    names = set(B['nb']) | set(B['world'])
    for c in p.get('ctry', []): assert c in names, f'map ctry: unknown country "{c}"'
    for k in ('rivers', 'regions', 'peaks'):
        v = p.get(k); src = PH[k]
        if v and v != 'all':
            for n in v: assert n in src, f'map {k}: unknown "{n}". Use one of: {sorted(src)}'
    for x in p.get('pts', []) + p.get('labels', []):
        assert len(x['ll']) == 2 and -90 <= x['ll'][0] <= 90, 'map ll must be [lat, lon]'
        assert x['t'].get('en') and x['t'].get('te'), 'map label needs en+te'

def svg(p, m):
    v = p.get('view', 'india'); bb = VIEWS[v] if isinstance(v, str) else v
    if v == 'world' and p.get('pts'):   # zoom to the places shown (with padding)
        la = [x['ll'][0] for x in p['pts']]; lo = [x['ll'][1] for x in p['pts']]
        cx0, cx1, cy0, cy1 = min(lo) - 18, max(lo) + 18, min(la) - 14, max(la) + 14
        if cx1 - cx0 < 70: d = (70 - (cx1 - cx0)) / 2; cx0 -= d; cx1 += d
        if cy1 - cy0 < 45: d = (45 - (cy1 - cy0)) / 2; cy0 -= d; cy1 += d
        bb = [max(-180, cx0), max(-60, cy0), min(190, cx1), min(80, cy1)]
    x0, y0, x1, y1 = bb; world = (v == 'world')
    kx = math.cos(math.radians((y0 + y1) / 2)) if not world else 0.85
    sc = W / ((x1 - x0) * kx); H = round((y1 - y0) * sc)
    P = lambda lon, lat: (round((lon - x0) * kx * sc, 1), round((y1 - lat) * sc, 1))
    def path(g):
        polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        out = []
        for poly in polys:
            for ring in poly:
                seg = []; prev = None
                for a, b in ring:   # break the ring where it jumps across the date line (avoids stray lines)
                    if prev is not None and abs(a - prev) > 180:
                        if len(seg) > 1: out.append('M' + 'L'.join(f'{u},{w}' for u, w in seg))
                        seg = []
                    seg.append(P(a, b)); prev = a
                if len(seg) > 1: out.append('M' + 'L'.join(f'{u},{w}' for u, w in seg) + 'Z')
        return ''.join(out)
    hlc = p.get('hlc', '#b3322b'); fam = "'Noto Sans Telugu','Noto Sans',sans-serif" if m == 'te' else "'Noto Sans','Noto Sans Telugu',sans-serif"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{fam}">',
         '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="context-stroke"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#dcebf5"/>']
    sel = lambda k: (list(PH[k]) if p.get(k) == 'all' else (p.get(k) or []))
    RL = []
    others = B['world'] if world else B['nb']
    ct = set(p.get('ctry', []))
    for nm, g in others.items():
        o.append(f'<path d="{path(g)}" fill="{"#f3d9a4" if nm in ct else "#ece8df"}" stroke="#b9b2a5" stroke-width="0.8"/>')
    if world:
        o.append(f'<path d="{path(B["india_lo"])}" fill="#fff6e0" stroke="#16324a" stroke-width="1.2"/>')
    else:
        hl = set(p.get('hl', []))
        for nm, g in B['states'].items():
            o.append(f'<path d="{path(g)}" fill="{hlc if nm in hl else "#fffaf0"}" fill-opacity="{0.85 if nm in hl else 1}" stroke="#c4b49a" stroke-width="0.7"/>')
        for n in sel('regions'):
            r = PH['regions'][n]; c, op = KC.get(r['k'], ('#9a6a3a', .35))
            o.append(f'<path d="{path(r["g"])}" fill="{c}" fill-opacity="{op}" stroke="{c}" stroke-opacity=".6" stroke-width="0.8"/>')
        def lpath(g):
            ls = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
            return ''.join('M' + 'L'.join('%s,%s' % P(a, b) for a, b in l) for l in ls), ls
        for n in sel('rivers'):
            d, ls = lpath(PH['rivers'][n]['g'])
            o.append(f'<path d="{d}" fill="none" stroke="#2f7fc1" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
            # label at the middle of the longest visible part
            best = None
            for l in ls:
                vis = [P(a, b) for a, b in l if x0 <= a <= x1 and y0 <= b <= y1]
                if best is None or len(vis) > len(best): best = vis
            if best: RL.append((best[len(best) // 2], n))
        o.append(f'<path d="{path(B["india"])}" fill="none" stroke="#16324a" stroke-width="1.8" stroke-linejoin="round"/>')
    for ln in p.get('lines', []):
        d = 'M' + 'L'.join('%s,%s' % P(b, a) for a, b in ln['ll'])
        o.append(f'<path d="{d}" fill="none" stroke="{ln.get("c", "#b3322b")}" stroke-width="3" stroke-linecap="round"' + (' stroke-dasharray="8 6"' if ln.get('dash') else '') + (' marker-end="url(#ah)"' if ln.get('arrow') else '') + '/>')
    # ---- labels: placed in priority order, skipping/shifting to avoid overlaps and edges ----
    boxes = []
    def tw(t, size):
        n = 0
        for ch in t:
            c = ord(ch)
            if 0x0C3E <= c <= 0x0C56 or c in (0x0C4D, 0x0C01, 0x0C02, 0x0C03): n += 0.15   # Telugu vowel signs / virama: little width
            elif 0x0C00 <= c <= 0x0C7F: n += 0.78
            else: n += 0.56
        return n * size + 6
    def hit(b):
        return any(not (b[2] < c[0] or b[0] > c[2] or b[3] < c[1] or b[1] > c[3]) for c in boxes)
    def put(x, y, t, size, cands, style, must=False):
        w = tw(t, size); h = size * 1.15
        for dx, dy, anc in cands:
            ax = x + dx; ay = y + dy
            l = ax - w / 2 if anc == 'middle' else (ax - w if anc == 'end' else ax)
            if l < 3: ax += 3 - l; l = 3
            if l + w > W - 3: ax -= l + w - (W - 3); l = W - 3 - w
            b = (l, ay - h * 0.8, l + w, ay + h * 0.25)
            if b[1] < 2 or b[3] > H - 2: continue
            if hit(b) and not (must and (dx, dy, anc) == cands[-1]): continue
            boxes.append(b)
            T.append(f'<text x="{round(ax,1)}" y="{round(ay,1)}" text-anchor="{anc}" font-size="{size}" {style} paint-order="stroke" stroke-linejoin="round">{html.escape(t)}</text>')
            return True
        return False
    T = []
    side = lambda x: [(11, 6, 'start'), (-11, 6, 'end'), (0, -12, 'middle'), (0, 26, 'middle')] if x < W * 0.7 else [(-11, 6, 'end'), (11, 6, 'start'), (0, -12, 'middle'), (0, 26, 'middle')]
    for pt in p.get('pts', []):
        x, y = P(pt['ll'][1], pt['ll'][0]); c = pt.get('c', '#b3322b')
        o.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{c}" stroke="#fff" stroke-width="2.5"/>')
        boxes.append((x - 8, y - 8, x + 8, y + 8))
    for pt in p.get('pts', []):
        x, y = P(pt['ll'][1], pt['ll'][0]); cs = side(x)
        if pt.get('a') == 'l': cs = [(-11, 6, 'end')] + cs
        elif pt.get('a') == 'r': cs = [(11, 6, 'start')] + cs
        put(x, y, pt['t'][m], 24, cs, 'font-weight="700" fill="#16324a" stroke="#fff" stroke-width="4"', must=True)
    if not world:
        for n in sel('peaks'):
            k = PH['peaks'][n]; x, y = P(k['ll'][1], k['ll'][0])
            if 0 < x < W and 0 < y < H:
                o.append(f'<path d="M{x},{y - 9}L{x + 8},{y + 5}L{x - 8},{y + 5}Z" fill="#6b3d16" stroke="#fff" stroke-width="1.5"/>')
                boxes.append((x - 8, y - 9, x + 8, y + 5))
                put(x, y, f'{n if m == "en" else k["te"]} {k["m"]:,} m', 16, side(x), 'font-weight="700" fill="#5b3a17" stroke="#fff" stroke-width="3.5"')
    for lb in p.get('labels', []):
        x, y = P(lb['ll'][1], lb['ll'][0])
        put(x, y, lb['t'][m], 19, [(0, 0, 'middle'), (0, -20, 'middle'), (0, 20, 'middle')], 'font-weight="600" font-style="italic" fill="#5a4d38" stroke="#fff" stroke-width="3"', must=True)
    if not world:
        for n in sel('regions'):
            r = PH['regions'][n]; x, y = P(r['lp'][1], r['lp'][0])
            if 0 < x < W and 0 < y < H:
                put(x, y, n if m == 'en' else r['te'], 16, [(0, 0, 'middle'), (0, -18, 'middle'), (0, 18, 'middle'), (0, -36, 'middle'), (0, 36, 'middle')], 'font-weight="700" font-style="italic" fill="#5b3a17" stroke="#fff" stroke-width="3.5"')
        for (x, y), n in RL:
            put(x, y, n if m == 'en' else PH['rivers'][n]['te'], 15, [(6, -6, 'start'), (-6, -6, 'end'), (6, 16, 'start'), (-6, 16, 'end')], 'font-weight="700" font-style="italic" fill="#1d5f9a" stroke="#fff" stroke-width="3.5"')
        if p.get('seas'):
            for n, k in PH['seas'].items():
                x, y = P(k['ll'][1], k['ll'][0])
                if 0 < x < W and 0 < y < H:
                    put(x, y, n if m == 'en' else k['te'], 16, [(0, 0, 'middle'), (0, -20, 'middle'), (0, 20, 'middle')], 'font-weight="600" font-style="italic" fill="#2b6d96" stroke="#dcebf5" stroke-width="3"')
    o += T
    o.append(f'<text x="{W - 8}" y="{H - 8}" text-anchor="end" font-size="9" fill="#6b7b88">{B["credit"]}</text>')
    o.append('</svg>')
    return ''.join(o)

def build(pics_owner_list, outdir, prefix, rel):
    """For every map pic: validate, write <outdir>/<prefix>-<k>-<m>.svg and set pic['src'] = '<rel>/<prefix>-<k>-{m}.svg'."""
    os.makedirs(outdir, exist_ok=True)
    k = 0
    for p in pics_owner_list:
        if not p or p.get('type') != 'map': continue
        validate(p); k += 1
        for m in ('en', 'te'):
            open(os.path.join(outdir, f'{prefix}-{k}-{m}.svg'), 'w', encoding='utf-8').write(svg(p, m))
        p['src'] = f'{rel}/{prefix}-{k}-{{m}}.svg'
    return k
