"""Install authored Stage3 film props. Run from the Unreal editor, not Blender.

The Level Instances keep their original puzzle actors and references. All of
these additions are non-colliding dressing in the persistent world.
"""
from pathlib import Path
import unreal as u

root = Path(r'C:/LHH/Epic_AI_MegaJam/MegaJam/SourceAssets/Stage3PuzzleArt')
exec(compile((root / 'import_props.py').read_text(encoding='utf-8'), str(root / 'import_props.py'), 'exec'))

level = u.get_editor_subsystem(u.LevelEditorSubsystem)
api = u.get_editor_subsystem(u.EditorActorSubsystem)
world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name() == '/Game/DirectorCut/Stage/Stage3_.Stage3_', world.get_path_name()

actors = {a.get_actor_label(): a for a in api.get_all_level_actors()}
folder = '/Game/Stage3Integrated/Archive/'
plan = [
    # Focus camera and archive shelf flank, rather than obscure, the key.
    ('Stage3 Focus Film Camera', 'SM_Stage3_ArchiveCamera', (75,-190,0), (1,1,1)),
    ('Stage3 Focus Film Shelf', 'SM_Stage3_FilmRack', (975,-205,0), (.88,1,1)),
    ('Stage3 Focus Film Cans', 'SM_Stage3_FilmCanStack', (160,-210,0), (.9,.9,.9)),
    # The lanterns sit in the gaps between star, moon and sun clue signs.
    ('Stage3 Bloom Spotlight 1', 'SM_Stage3_StageSpotlight', (2070,-200,0), (.9,.9,.9)),
    ('Stage3 Bloom Spotlight 2', 'SM_Stage3_StageSpotlight', (2620,-200,0), (.9,.9,.9)),
    ('Stage3 Bloom Spotlight 3', 'SM_Stage3_StageSpotlight', (3170,-200,0), (.9,.9,.9)),
    ('Stage3 Film Editing Console', 'SM_Stage3_EditConsole', (3900,-180,0), (.85,.8,.85)),
    ('Stage3 Editing Film Cans', 'SM_Stage3_FilmCanStack', (3680,-185,0), (1,1,1)),
    ('Stage3 Archive Exit Film Shelf', 'SM_Stage3_FilmRack', (7180,-180,0), (.85,.85,.9)),
    ('Stage3 Archive Exit Film Cans', 'SM_Stage3_FilmCanStack', (6680,-200,0), (.8,.8,.8)),
]
for label, name, location, scale in plan:
    actor = actors.get(label)
    if not actor:
        actor=api.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*location),u.Rotator())
        assert actor,label
        actor.set_actor_label(label)
    actor.set_folder_path('Stage3/Film Archive/Puzzle Props')
    actor.set_actor_location(u.Vector(*location),False,True)
    actor.set_actor_scale3d(u.Vector(*scale))
    component=actor.static_mesh_component
    mesh=u.EditorAssetLibrary.load_asset(folder+name)
    assert mesh, name
    component.set_static_mesh(mesh)
    component.set_collision_profile_name('NoCollision')
    component.set_cast_shadow(False)
    component.set_editor_property('affect_distance_field_lighting',False)

assert level.save_current_level()
print('STAGE3 FILM PUZZLE PROPS PLACED',len(plan))
