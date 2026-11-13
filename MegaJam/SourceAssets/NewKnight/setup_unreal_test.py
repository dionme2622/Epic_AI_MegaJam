import unreal

prefix = '/Game/Assets/Knight_Combat_New/'
level_path = prefix + 'L_Knight_Combat_Test'
mesh = unreal.load_asset(prefix + 'Knight_New_Combat_Idle')
anim = unreal.load_asset(prefix + 'Knight_New_Combat_Idle_Anim')
enemy_mesh = unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
assert mesh and anim and enemy_mesh
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level(level_path)

def spawn_mesh(label, skeletal_mesh, location, yaw):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkeletalMeshActor, unreal.Vector(*location), unreal.Rotator(0, yaw, 0))
    actor.set_actor_label(label)
    component = actor.get_editor_property('skeletal_mesh_component')
    component.set_skeletal_mesh_asset(skeletal_mesh)
    return actor, component

knight = next((a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label() == 'Knight_Combat_Idle_Test'), None)
if knight:
    knight_comp = knight.get_editor_property('skeletal_mesh_component')
else:
    knight, knight_comp = spawn_mesh('Knight_Combat_Idle_Test', mesh, (0, 0, 0), 0)
knight_comp.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
knight_comp.set_animation(anim)
knight_comp.play(True)
enemy, enemy_comp = spawn_mesh('Enemy_Test_Mannequin', enemy_mesh, (250, 0, 0), 180)
light = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.PointLight, unreal.Vector(100, 0, 350))
light.set_actor_label('Combat_Test_Light')
light.get_editor_property('point_light_component').set_editor_property('intensity', 50000.0)
unreal.EditorLevelLibrary.save_current_level()
unreal.log('KNIGHT_TEST_OK level=' + level_path + ' mesh=' + mesh.get_name() + ' animation=' + anim.get_name())
