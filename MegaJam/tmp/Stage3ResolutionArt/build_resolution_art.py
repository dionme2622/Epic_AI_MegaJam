"""Decorative, collision-free pieces for the Stage 3 projection corridor.

Centimetre-sized assets with pivots at the centre of the ring/window and on
the top of the tile. Existing theatre material-slot names are used for easy
mapping in Unreal; the centre of the ring intentionally contains no geometry.
"""
from pathlib import Path

source = Path('SourceAssets/Stage4ShadowTheatre/build_theatre.py')
namespace = {'__file__': str(source.resolve())}
exec(compile(source.read_text(encoding='utf-8-sig').split('# Courses are staggered')[0], str(source), 'exec'), namespace)
globals().update({key: value for key, value in namespace.items() if not key.startswith('__')})

# Large hollow proscenium ring: every element stays outside radius 121 cm.
ring(0, 0, 0, 128, 3.0, '07', True, 64)
ring(0, 3, 0, 134, 1.8, '08', True, 64)
ring(0, -1, 0, 122, 1.4, '06', True, 64)
for i in range(48):
    angle = 2 * math.pi * i / 48
    x, z = 128 * math.cos(angle), 128 * math.sin(angle)
    rod((x, 4, z), (x, 8, z), 2.2 if i % 4 else 3.2, '08' if i % 4 == 0 else '06', 8)
for angle in (math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4):
    x, z = 141 * math.cos(angle), 141 * math.sin(angle)
    rod((x, 0, z), (x, 6, z), 4, '07', 10)
finish('SM_S3_DotRing')

# Independent narrow stained-glass panel. Two copies can flank a ring or a
# passage, without placing any geometry across the player's numeric clues.
box(0, 0, 0, 62, 7, 154, '07', 2)
box(0, 5, 0, 54, 3, 146, '09', 1)
palette = ['12', '04', '15', '08', '05', '14']
for row in range(10):
    for col in range(4):
        mat = palette[(row * 3 + col * 5) % len(palette)]
        box(-19.5 + col * 13, 8, -65 + row * 14.5, 11, 2.5, 12, mat, .35)
for x in (-28, 28):
    box(x, 10, 0, 3, 4, 150, '06', .5)
for z in (-73, 0, 73):
    box(0, 10, z, 58, 4, 3, '06', .5)
for z in (-77, 77):
    rod((-22, 7, z), (22, 7, z), 2.3, '08', 8)
finish('SM_S3_StainedGlass')

# Tile edge only: the centre remains open so the existing tile surface and its
# gameplay state remain visible. Place at the actual top height of each tile.
for x in (-69, 69):
    box(x, 0, 0, 4, 154, 3, '06', .4)
    box(x, 0, 2, 1.3, 151, 1, '08', .2)
for y in (-75, 75):
    box(0, y, 0, 142, 4, 3, '06', .4)
    box(0, y, 2, 138, 1.3, 1, '08', .2)
for x in (-64, 64):
    for y in (-69, 69):
        rod((x, y, 1), (x, y, 4), 2, '09', 8)
finish('SM_S3_TileRim')
print('S3 RESOLUTION ART EXPORTED:', [obj.name for obj in EXPORTS])
