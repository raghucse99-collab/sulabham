"""One-off: build tools/maps/base.json (simplified outlines) from
 - DataMeet India maps (CC BY 4.0): Country/india-composite.geojson (official boundary of India) + States/Admin2.shp
 - Natural Earth via world-atlas 2.0.2 (public domain): countries-50m / 110m
usage: python3 build_base.py <datameet dir> <world50.geojson> <world110.geojson> <out base.json>"""
import json, sys, shapefile
from shapely.geometry import shape, mapping, box
from shapely.ops import unary_union
dm, w50, w110, out = sys.argv[1:5]
r6 = lambda g: json.loads(json.dumps(mapping(g)), parse_float=lambda x: round(float(x), 3))
india = unary_union([shape(f['geometry']) for f in json.load(open(f'{dm}/Country/india-composite.geojson'))['features']]).buffer(0)
R = shapefile.Reader(f'{dm}/States/Admin2.shp')
states = {}
for sr in R.shapeRecords():
    g = shape(sr.shape.__geo_interface__).buffer(0).simplify(0.015, preserve_topology=True)
    states[sr.record[0]] = r6(g)
# official outline adds PoK / Aksai Chin / Shaksgam: keep as 'india' outline
india_s = india.simplify(0.015, preserve_topology=True)
BB = box(55, -2, 105, 42)
nb = {}
for f in json.load(open(w50))['features']:
    g = shape(f['geometry']).buffer(0)
    nm = f['properties']['name']
    if nm == 'India' or not g.intersects(BB): continue
    g = g.intersection(BB).difference(india).simplify(0.03, preserve_topology=True)
    if not g.is_empty: nb[nm] = r6(g)
world = {}
for f in json.load(open(w110))['features']:
    nm = f['properties']['name']
    g = shape(f['geometry']).buffer(0)
    if nm != 'India': g = g.difference(india)
    else: continue
    g = g.simplify(0.25, preserve_topology=True)
    if not g.is_empty: world[nm] = json.loads(json.dumps(mapping(g)), parse_float=lambda x: round(float(x), 2))
json.dump({'india': r6(india_s), 'india_lo': json.loads(json.dumps(mapping(india.simplify(0.2))), parse_float=lambda x: round(float(x), 2)),
           'states': states, 'nb': nb, 'world': world,
           'credit': 'Map data: DataMeet India (CC BY 4.0), Natural Earth'}, open(out, 'w'), separators=(',', ':'))
print('ok', len(states), len(nb), len(world))
