"""Import and place decorative 3D theatre architecture into Stage3_.

Run from Unreal Python on the already open Stage3_ map, after saving work.
The script is idempotent, does not delete existing actors, and saves the map.
All dressing is NoCollision so the authored puzzle interaction remains intact.
"""
from pathlib import Path
import unreal as u

world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name() == '/Game/DirectorCut/Stage/Stage3_.Stage3_', world.get_path_name()
actor_api = u.get_editor_subsystem(u.EditorActorSubsystem)
level_api = u.get_editor_subsystem(u.LevelEditorSubsystem)
asset_api = u.EditorAssetLibrary
asset_tools = u.AssetToolsHelpers.get_asset_tools()
folder = '/Game/Stage3Integrated/Archive'
exports = Path(u.Paths.project_dir()).resolve() / 'SourceAssets/Stage3Archive/Exports'

names = ['SM_Stage3_TheatreCurtains', 'SM_Stage3_CameraBanner',
         'SM_Stage3_GothicWindow', 'SM_Stage3_StudioTruss', 'SM_Stage3_StoneProscenium']
material_paths = asset_api.list_assets('/Game/Stage4Integrated/Theatre', False)
mats = {p.rsplit('/', 1)[-1].split('.')[0]: asset_api.load_asset(p)
        for p in material_paths if p.rsplit('/', 1)[-1].startswith('M')}
tasks = []
for name in names:
    if asset_api.does_asset_exist(folder + '/' + name):
        continue
    task = u.AssetImportTask()
    task.filename = str(exports / (name + '.fbx'))
    task.destination_path = folder
    task.destination_name = name
    task.automated = True
    task.save = False
    task.options = u.FbxImportUI()
    task.options.import_as_skeletal = False
    task.options.import_materials = False
    task.options.import_textures = False
    task.options.static_mesh_import_data.combine_meshes = True
    task.options.static_mesh_import_data.auto_generate_collision = False
    tasks.append(task)
if tasks:
    asset_tools.import_asset_tasks(tasks)
meshes = {}
for name in names:
    mesh = asset_api.load_asset(folder + '/' + name)
    assert mesh, name
    for i, slot in enumerate(mesh.get_editor_property('static_materials')):
        key = str(slot.get_editor_property('imported_material_slot_name'))
        assert key in mats and mats[key], (name, key)
        mesh.set_material(i, mats[key])
    assert asset_api.save_loaded_asset(mesh, only_if_is_dirty=False)
    meshes[name] = mesh

existing = {a.get_actor_label(): a for a in actor_api.get_all_level_actors()}
def add(label, mesh, x, y, z, scale=1):
    name = 'Archive Theatre ' + label
    actor = existing.get(name)
    if not actor:
        actor = actor_api.spawn_actor_from_class(u.StaticMeshActor, u.Vector(x, y, z), u.Rotator())
        assert actor, name
        actor.set_actor_label(name)
        actor.set_folder_path('Stage3/Film Archive/Theatre Architecture')
    actor.set_actor_location(u.Vector(x, y, z), False, True)
    actor.set_actor_scale3d(u.Vector(scale, scale, scale))
    comp = actor.static_mesh_component
    comp.set_static_mesh(meshes[mesh])
    comp.set_collision_profile_name('NoCollision')
    comp.set_cast_shadow(False)
    comp.set_editor_property('affect_distance_field_lighting', False)

# Back wall is approximately y=-308; the puzzle signs are at y=-210.
# The decorations are sandwiched between those planes, away from the playable x-axis.
# Top curtain height is 682 cm and the truss is centered at 650 cm so they enter
# the top of the player's 2.5D camera rather than filling the gameplay space.
for i, x in enumerate((450, 2100, 3350, 5200, 6500), 1):
    add('Curtain %02d' % i, 'SM_Stage3_TheatreCurtains', x, -268, 0)
for i, x in enumerate((450, 2600, 5450, 6750), 1):
    add('Proscenium %02d' % i, 'SM_Stage3_StoneProscenium', x, -278, 0, .8)
for i, x in enumerate((50, 1070, 4500, 6700), 1):
    add('Window %02d' % i, 'SM_Stage3_GothicWindow', x, -278, 165, .88)
for i, x in enumerate((0, 1200, 2400, 3600, 4800, 6000, 7200), 1):
    add('Truss %02d' % i, 'SM_Stage3_StudioTruss', x, -250, 650)
for i, x in enumerate((0, 1200, 2400, 3600, 4800, 6000, 7100), 1):
    add('Banner %02d' % i, 'SM_Stage3_CameraBanner', x, -238, 425, .75)

assert level_api.save_current_level()
u.log('STAGE3 THEATRE ARCHITECTURE IMPORTED AND SAVED')
