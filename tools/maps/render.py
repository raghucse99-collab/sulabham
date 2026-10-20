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
 "cap": {en,te}}
"""
import json, math, os, html
HERE = os.path.dirname(os.path.abspath(__file__))
B = json.load(open(os.path.join(HERE, 'base.json')))
STATES = sorted(B['states'])
VIEWS = {'india': [66.5, 6, 98.5, 37.6], 'north': [72.5, 25.8, 97.8, 37.4], 'northeast': [87.5, 21.5, 97.8, 29.7],
         'south': [72.5, 7.5, 88.5, 21.5], 'ap': [76.4, 12.4, 85.2, 19.6], 'southasia': [57, 1, 103, 41],
         'world': [-170, -56, 190, 78]}
W = 560

def validate(p):
    v = p.get('view', 'india')
    assert v in VIEWS or (isinstance(v, list) and len(v) == 4), f'map view must be one of {list(VIEWS)} or [lon_min,lat_min,lon_max,lat_max]'
    for s in p.get('hl', []): assert s in B['states'], f'map hl: unknown state "{s}". Use one of: {STATES}'
    names = set(B['nb']) | set(B['world'])
    for c in p.get('ctry', []): assert c in names, f'map ctry: unknown country "{c}"'
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
                pts = [P(a, b) for a, b in ring]
                out.append('M' + 'L'.join(f'{a},{b}' for a, b in pts) + 'Z')
        return ''.join(out)
    hlc = p.get('hlc', '#b3322b'); fam = "'Noto Sans Telugu','Noto Sans',sans-serif" if m == 'te' else "'Noto Sans','Noto Sans Telugu',sans-serif"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{fam}">',
         '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="context-stroke"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#dcebf5"/>']
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
        o.append(f'<path d="{path(B["india"])}" fill="none" stroke="#16324a" stroke-width="1.8" stroke-linejoin="round"/>')
    for ln in p.get('lines', []):
        d = 'M' + 'L'.join('%s,%s' % P(b, a) for a, b in ln['ll'])
        o.append(f'<path d="{d}" fill="none" stroke="{ln.get("c", "#b3322b")}" stroke-width="3" stroke-linecap="round"' + (' stroke-dasharray="8 6"' if ln.get('dash') else '') + (' marker-end="url(#ah)"' if ln.get('arrow') else '') + '/>')
    def label(x, y, t, a, size, bold, col='#16324a'):
        anc = 'end' if a == 'l' else 'start'; dx = -10 if a == 'l' else 10
        return (f'<text x="{x + dx}" y="{y + 5}" text-anchor="{anc}" font-size="{size}" font-weight="{700 if bold else 600}" fill="{col}" '
                f'stroke="#fff" stroke-width="4" paint-order="stroke" stroke-linejoin="round">{html.escape(t)}</text>')
    for lb in p.get('labels', []):
        x, y = P(lb['ll'][1], lb['ll'][0])
        o.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="20" font-weight="600" fill="#5a4d38" font-style="italic" stroke="#fff" stroke-width="3" paint-order="stroke" opacity=".9">{html.escape(lb["t"][m])}</text>')
    for pt in p.get('pts', []):
        x, y = P(pt['ll'][1], pt['ll'][0]); c = pt.get('c', '#b3322b')
        o.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{c}" stroke="#fff" stroke-width="2.5"/>')
        o.append(label(x, y, pt['t'][m], pt.get('a', 'r' if x < W * 0.7 else 'l'), 26, True))
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
