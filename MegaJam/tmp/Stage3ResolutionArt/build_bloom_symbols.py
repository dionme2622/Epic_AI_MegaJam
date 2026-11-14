"""Three separate freestanding silhouette props for the film-editing signs.

FBX origins are at visual centre, size approx. 160 cm across. All meshes face
the +Y side in the theatre convention used by the existing Stage4 assets.
"""
from pathlib import Path

source = Path('SourceAssets/Stage4ShadowTheatre/build_theatre.py')
namespace = {'__file__': str(source.resolve())}
exec(compile(source.read_text(encoding='utf-8-sig').split('# Courses are staggered')[0], str(source), 'exec'), namespace)
globals().update({key: value for key, value in namespace.items() if not key.startswith('__')})

def border(points, y, radius=1.5, mat='08'):
    for i, a in enumerate(points):
        b = points[(i + 1) % len(points)]
        rod((a[0], y, a[1]), (b[0], y, b[1]), radius, mat, 8)

def star_points(outer, inner):
    return [(math.cos(math.pi / 2 + i * math.pi / 5) * (outer if i % 2 == 0 else inner),
             math.sin(math.pi / 2 + i * math.pi / 5) * (outer if i % 2 == 0 else inner)) for i in range(10)]

# Carved brass star around a smaller warm luminous face, dotted theatre bulbs.
star = star_points(82, 36)
prism(star, 0, 11, '07', 1.5)
prism(star_points(73, 31), 7, 4, '14', .8)
border(star, 7, 2, '08')
rod((0, 10, 0), (0, 14, 0), 7, '08', 12)
for i in range(5):
    a = math.pi / 2 + i * 2 * math.pi / 5
    x, z = 52 * math.cos(a), 52 * math.sin(a)
    rod((x, 10, z), (x, 15, z), 3.8, '08', 12)
finish('SM_S3_BloomStar')

# A hollow-looking crescent profile (the concavity is truly cut into the mesh).
outer = [(82 * math.cos(math.radians(75 + i * 210 / 28)),
          82 * math.sin(math.radians(75 + i * 210 / 28))) for i in range(29)]
tip_z = 82 * math.sin(math.radians(75))
tip_x = 82 * math.cos(math.radians(75))
inner = []
for i in range(1, 21):
    z = -tip_z + i * (2 * tip_z / 21)
    x = tip_x - 51 * (1 - (z / tip_z) ** 2)
    inner.append((x, z))
moon = outer + inner
prism(moon, 0, 12, '04', .7)
prism([(x * .94, z * .94) for x, z in moon], 7, 3, '15', .5)
border(moon, 9, 1.8, '08')
for x, z, r in [(-56, 2, 7), (-43, 28, 5), (-43, -30, 6)]:
    rod((x, 9, z), (x, 12, z), r, '05', 18)
    ring(x, 13, z, r + 1.4, .8, '08', True, 18)
finish('SM_S3_BloomMoon')

# Separate sculpted rays behind concentric discs rather than a square sign.
for i in range(12):
    a = 2 * math.pi * i / 12
    b = 2 * math.pi * (i + .5) / 12
    c = 2 * math.pi * (i + 1) / 12
    pts = [(48 * math.cos(a), 48 * math.sin(a)),
           (85 * math.cos(b), 85 * math.sin(b)),
           (48 * math.cos(c), 48 * math.sin(c))]
    prism(pts, 0, 9, '06', 1)
    border(pts, 5, 1, '08')
rod((0, -5, 0), (0, 9, 0), 52, '07', 40)
rod((0, 9, 0), (0, 14, 0), 45, '14', 40)
ring(0, 15, 0, 46, 3, '08', True, 48)
ring(0, 16, 0, 35, 1.5, '06', True, 40)
finish('SM_S3_BloomSun')
print('STAGE3 BLOOM SYMBOLS:', [obj.name for obj in EXPORTS])
