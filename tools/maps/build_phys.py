"""One-off: build tools/maps/phys.json (rivers, ranges/plateaus/deserts, peaks, seas) for India + neighbours
from Natural Earth 10m (public domain): rivers_lake_centerlines, geography_regions_polys, geography_regions_elevation_points, geography_marine_polys.
usage: python3 build_phys.py <natural-earth geojson dir> <out phys.json>"""
import json, sys
from shapely.geometry import shape, mapping, box
from shapely.ops import unary_union, linemerge
ne, out = sys.argv[1:3]
BB = box(60, 4, 100, 40)
rd = lambda g, n=3: json.loads(json.dumps(mapping(g)), parse_float=lambda x: round(float(x), n))
RIV = {'Ganges': ('Ganga', 'గంగా'), 'Yamuna': ('Yamuna', 'యమునా'), 'Brahmaputra': ('Brahmaputra', 'బ్రహ్మపుత్ర'), 'Dihang': ('Brahmaputra', 'బ్రహ్మపుత్ర'),
       'Yarlung': ('Tsangpo', 'సాంగ్‌పో'), 'Indus': ('Indus', 'సింధు'), 'Sutlej': ('Sutlej', 'సట్లెజ్'), 'Beas': ('Beas', 'బియాస్'), 'Ravi': ('Ravi', 'రావి'),
       'Chenab': ('Chenab', 'చీనాబ్'), 'Jhelum': ('Jhelum', 'జీలం'), 'Chambal': ('Chambal', 'చంబల్'), 'Betwa': ('Betwa', 'బెత్వా'), 'Son': ('Son', 'సోన్'),
       'Gandak': ('Gandak', 'గండక్'), 'Ghäghara': ('Ghaghara', 'ఘాఘ్రా'), 'Sapt': ('Kosi', 'కోసి'), 'Tista': ('Teesta', 'తీస్తా'),
       'Narmada': ('Narmada', 'నర్మదా'), 'Tapi': ('Tapi', 'తపతి'), 'Mahi': ('Mahi', 'మాహి'), 'Godävari': ('Godavari', 'గోదావరి'),
       'Krishna': ('Krishna', 'కృష్ణా'), 'Bhima': ('Bhima', 'భీమా'), 'Tungabhadra': ('Tungabhadra', 'తుంగభద్ర'), 'Penner': ('Penna', 'పెన్నా'),
       'Cauvery': ('Kaveri', 'కావేరి'), 'Kolidam': ('Kaveri', 'కావేరి'), 'Mahäna Nadï': ('Mahanadi', 'మహానది'), 'Brahmani': ('Brahmani', 'బ్రాహ్మణి'),
       'Wainganga': ('Wainganga', 'వైన్‌గంగా'), 'Indravati': ('Indravati', 'ఇంద్రావతి'), 'Palar': ('Palar', 'పాలార్'), 'Banas': ('Banas', 'బనాస్'),
       'Luhit': ('Lohit', 'లోహిత్')}
REG = {'HIMALAYAS': ('Himalayas', 'హిమాలయాలు'), 'KARAKORAM RA.': ('Karakoram', 'కారకోరం'), 'Siwalik Hills': ('Shivalik Hills', 'శివాలిక్ కొండలు'),
       'Arvalli Ra.': ('Aravalli Range', 'ఆరావళి పర్వతాలు'), 'Vindhya Range': ('Vindhya Range', 'వింధ్య పర్వతాలు'), 'Satpura Range': ('Satpura Range', 'సాత్పురా పర్వతాలు'),
       'WESTERN GHATS': ('Western Ghats', 'పశ్చిమ కనుమలు'), 'EASTERN GHATS': ('Eastern Ghats', 'తూర్పు కనుమలు'), 'Khasi Hills': ('Khasi Hills', 'ఖాసీ కొండలు'),
       'Naga Hills': ('Naga Hills', 'నాగా కొండలు'), 'HINDU KUSH': ('Hindu Kush', 'హిందూకుష్'), 'Chota Nägpur Plateau': ('Chota Nagpur Plateau', 'ఛోటానాగ్‌పూర్ పీఠభూమి'),
       'DECCAN PLATEAU': ('Deccan Plateau', 'దక్కన్ పీఠభూమి'), 'THAR DESERT': ('Thar Desert', 'థార్ ఎడారి'), 'GANGES PLAIN': ('Ganga Plain', 'గంగా మైదానం'),
       'PLATEAU OF TIBET': ('Tibetan Plateau', 'టిబెట్ పీఠభూమి'), 'Sundarbans': ('Sundarbans', 'సుందర్బన్స్'), 'Vale of Kashmir': ('Kashmir Valley', 'కశ్మీర్ లోయ'),
       'Malabar Coast': ('Malabar Coast', 'మలబార్ తీరం'), 'Coromandel Coast': ('Coromandel Coast', 'కోరమండల్ తీరం'), 'Kathiawar Pen.': ('Kathiawar Peninsula', 'కథియావాడ్ ద్వీపకల్పం'),
       'Ganges Delta': ('Ganga Delta', 'గంగా డెల్టా')}
PK = {'Mount Everest': ('Mount Everest', 'ఎవరెస్ట్'), 'K2': ('K2 (Godwin-Austen)', 'K2 (గాడ్విన్ ఆస్టిన్)'), 'Kanchenjunga': ('Kanchenjunga', 'కాంచనజంగా'),
      'Nanda Devi': ('Nanda Devi', 'నందాదేవి'), 'Nanga Parbat': ('Nanga Parbat', 'నంగా పర్వత్'), 'Namcha Barwa': ('Namcha Barwa', 'నామ్చా బర్వా'),
      'Anai Mudi': ('Anamudi', 'ఆనైముడి'), 'Doda Betta': ('Doddabetta', 'దొడ్డబెట్ట'), 'Mahendra Giri': ('Mahendragiri', 'మహేంద్రగిరి'),
      'Guru Sikhar': ('Guru Shikhar', 'గురుశిఖర్'), 'Saramati': ('Saramati', 'సారామతి'), 'Kailash': ('Mount Kailash', 'కైలాస పర్వతం')}
SEA = {'Bay of Bengal': ('Bay of Bengal', 'బంగాళాఖాతం'), 'Arabian Sea': ('Arabian Sea', 'అరేబియా సముద్రం'), 'INDIAN OCEAN': ('Indian Ocean', 'హిందూ మహాసముద్రం'),
       'Laccadive Sea': ('Laccadive Sea', 'లక్షదీవుల సముద్రం'), 'Andaman Sea': ('Andaman Sea', 'అండమాన్ సముద్రం'), 'Gulf of Mannar': ('Gulf of Mannar', 'మన్నార్ సింధుశాఖ'),
       'Palk Strait': ('Palk Strait', 'పాక్ జలసంధి'), 'Gulf of Kutch': ('Gulf of Kutch', 'కచ్ సింధుశాఖ'), 'Gulf of Khambhät': ('Gulf of Khambhat', 'ఖంబాత్ సింధుశాఖ')}
rivers = {}
for f in json.load(open(f'{ne}/ne_10m_rivers_lake_centerlines.geojson'))['features']:
    n = f['properties'].get('name')
    if n in RIV:
        g = shape(f['geometry']).intersection(BB)
        if not g.is_empty: rivers.setdefault(RIV[n], []).append(g)
R = {}
for (en, te), gs in rivers.items():
    g = unary_union(gs); g = linemerge(g) if g.geom_type == 'MultiLineString' else g
    R[en] = {'te': te, 'g': rd(g.simplify(0.02))}
G = {}
for f in json.load(open(f'{ne}/ne_10m_geography_regions_polys.geojson'))['features']:
    n = f['properties']['NAME']
    if n in REG:
        g = shape(f['geometry']).buffer(0).intersection(BB).simplify(0.03)
        lp = g.representative_point()
        G[REG[n][0]] = {'te': REG[n][1], 'k': f['properties']['FEATURECLA'], 'g': rd(g), 'lp': [round(lp.y, 2), round(lp.x, 2)]}
P = {}
for f in json.load(open(f'{ne}/ne_10m_geography_regions_elevation_points.geojson'))['features']:
    n = f['properties'].get('name')
    if n in PK:
        c = f['geometry']['coordinates']
        P[PK[n][0]] = {'te': PK[n][1], 'll': [round(c[1], 3), round(c[0], 3)], 'm': f['properties'].get('elevation')}
P['Arma Konda'] = {'te': 'అరమకొండ', 'll': [18.224, 82.725], 'm': 1680}   # highest peak of Andhra Pradesh (Eastern Ghats)
S = {}
for f in json.load(open(f'{ne}/ne_10m_geography_marine_polys.geojson'))['features']:
    n = f['properties'].get('name')
    if n in SEA:
        g = shape(f['geometry']).buffer(0).intersection(BB)
        if g.is_empty: continue
        lp = g.representative_point(); S[SEA[n][0]] = {'te': SEA[n][1], 'll': [round(lp.y, 2), round(lp.x, 2)]}
json.dump({'rivers': R, 'regions': G, 'peaks': P, 'seas': S}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('rivers', sorted(R), '\nregions', sorted(G), '\npeaks', sorted(P), '\nseas', sorted(S))
