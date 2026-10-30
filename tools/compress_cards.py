"""Shrink poster PNGs (about 85% smaller, same file names) — 128-colour palette PNG.
usage: python3 tools/compress_cards.py <dir> [<dir> ...]   (skips files already compressed)"""
import os, sys
from PIL import Image
saved = 0
for root in sys.argv[1:]:
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith('.png'): continue
            p = os.path.join(dp, f)
            im = Image.open(p)
            if im.mode == 'P': continue
            b = os.path.getsize(p)
            im.convert('RGB').quantize(colors=128, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(p, optimize=True)
            saved += b - os.path.getsize(p)
print(f'compressed posters, saved {saved // 1024} KB')
