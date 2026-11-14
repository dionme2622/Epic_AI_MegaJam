"""Replace the flat storage sign with white, solid 3D block letters."""
import unreal

GLYPHS = {
    'S': ('11111','10000','10000','11111','00001','00001','11111'),
    'T': ('11111','00100','00100','00100','00100','00100','00100'),
    'O': ('11111','10001','10001','10001','10001','10001','11111'),
    'R': ('11110','10001','10001','11110','10100','10010','10001'),
    'A': ('01110','10001','10001','11111','10001','10001','10001'),
    'G': ('11111','10000','10000','10111','10001','10001','11111'),
    'E': ('11111','10000','10000','11110','10000','10000','11111'),
}
prefix = 'BossIntro_Storage_Letter_'
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    if actor.get_actor_label() == 'BossIntro_Storage_Sign' or actor.get_actor_label().startswith(prefix):
        unreal.EditorLevelLibrary.destroy_actor(actor)

lib = unreal.EditorAssetLibrary
material_path = '/Game/DirectorCut/Prologue/Cinematic/M_Storage_Letters_White'
if lib.does_asset_exist(material_path):
    white = unreal.load_asset(material_path)
else:
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    white = tools.create_asset('M_Storage_Letters_White', '/Game/DirectorCut/Prologue/Cinematic',
                               unreal.Material, unreal.MaterialFactoryNew())
    color = unreal.MaterialEditingLibrary.create_material_expression(
        white, unreal.MaterialExpressionConstant3Vector, -200, 0)
    color.set_editor_property('constant', unreal.LinearColor(1, 1, 1, 1))
    unreal.MaterialEditingLibrary.connect_material_property(color, '', unreal.MaterialProperty.MP_BASE_COLOR)
    unreal.MaterialEditingLibrary.recompile_material(white)
    assert lib.save_loaded_asset(white, False)

cube = unreal.load_asset('/Engine/BasicShapes/Cube')
assert cube and white
word = 'STORAGE'
pitch = 5.2
letter_step = 6 * pitch
left = 1600 - (len(word) * letter_step - pitch) / 2
bottom = 349
count = 0
for letter_index, letter in enumerate(word):
    for row, line in enumerate(GLYPHS[letter]):
        for column, bit in enumerate(line):
            if bit != '1':
                continue
            x = left + letter_index * letter_step + column * pitch
            z = bottom + (6 - row) * pitch
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.StaticMeshActor, unreal.Vector(x, 133, z), unreal.Rotator())
            actor.set_actor_label(f'{prefix}{letter_index:02d}_{row}_{column}')
            actor.static_mesh_component.set_static_mesh(cube)
            actor.static_mesh_component.set_material(0, white)
            actor.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
            actor.set_actor_scale3d(unreal.Vector(.047, .06, .047))
            count += 1

assert count > 100
assert unreal.EditorLevelLibrary.save_current_level()
