"""Replace the prologue's Cascade breath with the procedural Niagara breath."""
import unreal

lib = unreal.EditorAssetLibrary
effect = unreal.load_asset('/Game/DirectorCut/Prologue/Cinematic/NS_DragonBreath')
seq = unreal.load_asset('/Game/DirectorCut/Prologue/LS_BossPrologue_Cinematic')
assert effect and seq
actors = unreal.EditorLevelLibrary.get_all_level_actors()
dragon = next(a for a in actors if a.get_actor_label() == 'Prologue Dragon')
hero = next(a for a in actors if a.get_actor_label() == 'BossIntro_Hero')
mesh = dragon.get_component_by_class(unreal.SkeletalMeshComponent)
assert mesh and mesh.does_socket_exist('Head')

for binding in seq.get_bindings():
    if any(word in binding.get_name() for word in ('Flame', 'Breath', 'Niagara')):
        binding.remove()
for actor in actors:
    if actor.get_actor_label() in ('BossIntro_Dragon_Flame', 'BossIntro_Dragon_Flamethrower', 'BossIntro_Dragon_NiagaraBreath'):
        unreal.EditorLevelLibrary.destroy_actor(actor)

# During the shot the head rises about 150 cm. Start just outside its jaws.
mouth = mesh.get_socket_location('Head') + unreal.Vector(-90, 5, -115)
hero_chest = hero.get_actor_location() + unreal.Vector(0, 0, 95)
aim = hero_chest - (mouth + unreal.Vector(0, 0, 150))
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.NiagaraActor, mouth, unreal.MathLibrary.make_rot_from_x(aim))
actor.set_actor_label('BossIntro_Dragon_NiagaraBreath')
component = actor.get_component_by_class(unreal.NiagaraComponent)
component.set_asset(effect)
component.set_auto_activate(False)
component.deactivate()
actor.attach_to_component(mesh, 'Head', unreal.AttachmentRule.KEEP_WORLD,
                          unreal.AttachmentRule.KEEP_WORLD,
                          unreal.AttachmentRule.KEEP_WORLD, False)

parent_binding = seq.add_possessable(actor)
binding = seq.add_possessable(component)
binding.set_parent(parent_binding)
track = binding.add_track(unreal.MovieSceneNiagaraSystemTrack)
section = track.add_section()
section.set_range(200, 250)
section.set_editor_property('section_start_behavior', unreal.NiagaraSystemSpawnSectionStartBehavior.ACTIVATE)
section.set_editor_property('section_end_behavior', unreal.NiagaraSystemSpawnSectionEndBehavior.DEACTIVATE)
lib.save_loaded_asset(seq)
assert unreal.EditorLevelLibrary.save_current_level()
unreal.log('NIAGARA_FIRE_INSTALLED mouth=' + str(mouth) + ' target=' + str(hero_chest))

