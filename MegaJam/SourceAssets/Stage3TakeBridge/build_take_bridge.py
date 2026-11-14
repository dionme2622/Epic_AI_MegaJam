"""Build Stage3 theatre props with the project's shared centimetre-scale FBX palette.

Run Blender in background mode with this script and an export folder after `--`.
"""

import json
import math
from pathlib import Path

import bpy


toolbox = Path(__file__).resolve().parents[1] / "Stage4ShadowTheatre" / "build_theatre.py"
scope = {"__file__": str(toolbox)}
head = toolbox.read_text(encoding="utf-8-sig").split("# Courses are staggered")[0]
exec(compile(head, str(toolbox), "exec"), scope)
box = scope["box"]
prism = scope["prism"]
rod = scope["rod"]
ring = scope["ring"]
finish = scope["finish"]
out = scope["OUT"]
manifest = {}


def export(name, note):
    finish(name)
    obj = scope["EXPORTS"][-1]
    # Read the restored model coordinates. Blender may retain the reflected FBX
    # bounds from its evaluated object after the exporter runs.
    corners = [vertex.co for vertex in obj.data.vertices]
    manifest[name] = {
        "bounds_cm": [[round(fn(v[i] for v in corners) * 100, 1) for i in range(3)] for fn in (min, max)],
        "material_slots": [m.name for m in obj.data.materials],
        "vertices": len(obj.data.vertices),
        "placement": note,
    }


def eyelet(x, y, z, radius=3, vertical=True):
    if vertical:
        rod((x, y - 1.5, z), (x, y + 1.5, z), radius, "09", 10)
        rod((x, y + 1, z), (x, y + 2.1, z), radius * .52, "08", 10)
    else:
        rod((x, y, z - 1.5), (x, y, z + 1.5), radius, "09", 10)
        rod((x, y, z + 1), (x, y, z + 2.1), radius * .52, "08", 10)


# Low brass stage switch. The inset reeds and the oval step mark read from
# above, while the front fascia looks like perforated film from a side camera.
box(0, 0, -13, 174, 148, 13, "03", 3)
box(0, 0, -6, 178, 150, 9, "07", 2)
box(0, 0, -.75, 148, 119, 1.5, "12", .5)
for y in (-66, 66):
    box(0, y, -.7, 167, 6, 1.5, "06", .5)
for x in (-79, 79):
    box(x, 0, -.7, 5, 129, 1.5, "06", .5)
for x in (-79, 79):
    for y in (-66, 66):
        eyelet(x, y, -1, 3.6, vertical=False)
for x in (-60, -47, -34, 34, 47, 60):
    box(x, 74, -6, 7, 3, 4, "13", .5)
ring(0, 0, .1, 32, 1.8, "06", vertical=False, steps=24)
for x, y in ((-11, -8), (12, 11)):
    box(x, y, .3, 15, 24, .8, "06", .3)
    box(x, y + 4, .7, 11, 4, .8, "08", .4)
box(0, 75.5, -6, 44, 4, 7, "09", 1)
box(0, 78, -6, 33, 1.5, 3, "14", .5)
export("SM_S3Take_PressurePlate", "Pivot centred on the walkable surface. Put Z at floor height, use NoCollision. Indicator lens faces +Y at (0, 78, -6).")


# A low-profile theatre cue lamp with a protective brow and a recessed lens.
# This uses matte dark steel in the lens so the runtime cyan state reads alone.
box(0, 0, 3, 40, 28, 6, "09", 1.5)
box(0, 0, 9, 32, 21, 8, "07", 1.5)
box(0, 0, 35, 12, 10, 47, "09", 1.2)
box(0, 1, 15, 22, 17, 7, "06", 1)
ring(0, 0, 24, 6.1, 1.15, "06", vertical=False, steps=20)
ring(0, 0, 42, 6.1, 1.15, "07", vertical=False, steps=20)
for x in (-13, 13):
    rod((x, -1, 42), (x, 0, 65), 2.4, "07", 10)
rod((0, -8, 66), (0, 6, 66), 17, "07", 26)
rod((0, 5, 66), (0, 12, 66), 15.4, "09", 26)
ring(0, 13, 66, 14.8, 2, "06", steps=28)
rod((0, 11.8, 66), (0, 13.1, 66), 12.5, "18", 26)
prism([(-18, 73), (-14, 82), (14, 82), (18, 73)], 10, 16, "09", 1.4)
box(0, 19, 81, 29, 2.5, 2, "06", .6)
for x in (-10, 10):
    eyelet(x, 15, 66, 2.3)
export("SM_S3Take_CueLamp", "Floor pivot, 40 cm wide and ~83 cm tall, use NoCollision. Cyan runtime overlay can sit on the lens face, local (0, 16, 66), with 11 cm radius.")


# The transport deck has a level top at z=0. Its front shows a film edge,
# with guide-wheel bearings and a plum stone tread to match the archive.
box(0, 0, -14, 200, 148, 28, "04", 3)
box(0, 0, -34, 188, 135, 15, "02", 3)
for y in (-69, 69):
    box(0, y, -4, 197, 8, 8, "07", 2)
for x in (-95, 95):
    box(x, 0, -4, 8, 142, 8, "06", 2)
for x in range(-80, 81, 20):
    box(x, 0, -.8, 17, 125, 1.6, "05", .7)
box(0, 75, -19, 195, 4, 24, "09", 1.4)
for z in (-12, -27):
    for x in range(-83, 84, 12):
        box(x, 78, z, 7, 2, 4, "06", .5)
for x in (-67, 67):
    rod((x, 62, -41), (x, 84, -41), 16, "09", 24)
    ring(x, 83, -41, 12, 2, "06", steps=24)
    eyelet(x, 87, -41, 5)
export("SM_S3Bridge_Platform", "200 cm wide before edge details, deck top at Z=0, wheel bottoms at -57 cm. Use movable/blocking collision on a separate box covering the flat tread.")


# The silver screen uses a dark canvas for projected contrast. Registration
# marks frame the usable rectangle and are kept out of the central diagram.
box(0, 0, 0, 750, 8, 248, "11", 3)
box(0, 3.7, 0, 720, 1, 224, "19", .3)
for x in (-365, 365):
    box(x, 7, 0, 12, 14, 236, "07", 2)
    box(x, 15, 0, 3, 3, 232, "08", .6)
for z in (-119, 119):
    box(0, 7, z, 749, 14, 14, "06", 2)
    box(0, 15, z, 729, 3, 3, "08", .6)
    for x in range(-338, 340, 34):
        box(x, 15, z - 4, 13, 3, 4, "09", .65)
for x in (-371, 371):
    for z in (-119, 119):
        rod((x, 7, z), (x, 18, z), 12, "07", 18)
        eyelet(x, 19, z, 6)
for x in (-207, 207):
    box(x, -1, 141, 14, 10, 32, "09", 1.25)
    eyelet(x, 6, 137, 3)
export("SM_S3Bridge_ProjectionScreen", "Pivot centre of the 720 × 224 cm usable canvas. Canvas faces +Y and ends at Y=4.2 cm. Put diagram on +Y=8 or closer.")


def film_wheel(x, y, z, radius):
    rod((x, y - 3, z), (x, y + 3, z), radius, "09", 26)
    ring(x, y + 4, z, radius - 2, 1.5, "07", steps=28)
    for index in range(5):
        angle = index * 2 * math.pi / 5
        rod((x, y + 5, z), (x + (radius - 4) * math.cos(angle), y + 5,
                              z + (radius - 4) * math.sin(angle)), 2, "06", 8)
    eyelet(x, y + 7, z, 4)


# Splicing apparatus: two separate numbered feed lanes, exposed reels and a
# recessed strip across the work surface. The player stands in front of it.
box(0, 0, 5, 152, 69, 10, "11", 3)
for x in (-66, 66):
    box(x, 0, 44, 15, 57, 79, "10", 2)
    box(x, 29, 43, 8, 4, 73, "07", .7)
    for z in (15, 69):
        eyelet(x, 32, z, 2.7)
box(0, 1, 37, 120, 10, 14, "11", 1)
box(0, 0, 86, 152, 70, 17, "07", 3)
box(0, 0, 97, 147, 65, 9, "10", 2)
box(0, -21, 103, 136, 23, 5, "09", 1)
for x in (-43, 43):
    box(x, 1, 104, 54, 48, 5, "06", 1.7)
    box(x, 2, 107, 43, 42, 1.6, "09", .8)
    for y in range(-15, 20, 7):
        for dx in (-19, 19):
            box(x + dx, y, 108, 2.4, 2.5, 1, "08", .25)
    rod((x, 5, 108), (x, 16, 125), 2.6, "07", 12)
    rod((x - 7, 16, 125), (x + 7, 16, 125), 4, "08", 14)
    film_wheel(x, -23, 128, 19)
box(0, 35, 85, 124, 4, 7, "11", 1)
for x in (-43, 43):
    box(x, 38, 85, 26, 2, 4, "14", .5)
    box(x, 38, 72, 23, 6, 108, "09", 1.5)
    for dx in (-9, 9):
        box(x + dx, 42, 72, 3, 3, 105, "07", .7)
    for z in (30, 51, 72, 93, 114):
        box(x - 14, 42, z, 5, 3, 2, "08", .4)
box(0, 39, 85, 15, 2, 5, "06", 1)
export("SM_S3Bridge_SpliceDesk", "Ground pivot, facing +Y. Position behind the movement path so the controls stay visible.")


# Brass slider rides the desk face. The textured film strip and polished
# leading edge stay legible when the camera is zoomed out.
box(0, 0, 0, 19, 6, 23, "07", 1.1)
box(0, 4, 0, 13, 3, 15, "13", .7)
for x in (-5, 5):
    for z in (-5, 0, 5):
        box(x, 6, z, 2.3, 1.2, 2.2, "08", .3)
box(0, 5.8, 8.8, 21, 3.4, 4.8, "08", .7)
export("SM_S3Bridge_FilmClip", "Moving clips. Home pivots at desk-relative X=-43/+43, Y=45, Z=72. Five positions are separated by 21 cm along Z.")


# Reusable rail section below the opening; the rails are intentionally narrow
# and separated from the character floor.
for x in (-108, -72, -36, 0, 36, 72, 108):
    box(x, 0, -10, 14, 143, 11, "10", 1.4)
    for y in (-50, 50):
        box(x, y, -.5, 13, 19, 7, "09", 1.2)
        eyelet(x, y, 3.1, 2.1, vertical=False)
for y in (-50, 50):
    box(0, y, 4, 240, 9, 8, "09", 1)
    box(0, y, 9, 240, 3, 2, "07", .5)
export("SM_S3Bridge_Rail", "240 cm repeat along X. Use NoCollision and place about 70 cm below the platform top, with scale adjusted to the section gaps.")

manifest_file = out / "mesh_manifest.json"
manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
bpy.ops.wm.save_as_mainfile(filepath=str(out / "Stage3TakeBridge.blend"))
print("STAGE3 TAKE BRIDGE FBX READY", manifest_file)
