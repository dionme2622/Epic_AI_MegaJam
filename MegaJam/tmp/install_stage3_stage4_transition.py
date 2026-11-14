import unreal as u

STAGE3 = '/Game/DirectorCut/Stage/Stage3_'
STAGE4 = '/Game/DirectorCut/Stage/Stage4'
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
library = u.EditorAssetLibrary

def link_crate():
    destination = library.load_asset(STAGE4)
    assert isinstance(destination, u.World)
    crate = next(a for a in actors.get_all_level_actors() if a.get_actor_label() == 'Archive Empty Crate')
    crate.set_editor_property('DestinationLevel', destination)
    assert crate.get_editor_property('DestinationLevel').get_path_name() == STAGE4 + '.Stage4'
    assert levels.save_current_level()

def add_entry_fade():
    fade = library.load_blueprint_class('/Game/DirectorCut/Transitions/BP_StageFadeIn')
    assert fade
    if not any(a.get_class() == fade for a in actors.get_all_level_actors()):
        new_fade = actors.spawn_actor_from_class(fade, u.Vector(), u.Rotator())
        assert new_fade
        new_fade.set_actor_label('Stage4_EntryFade')
        assert levels.save_current_level()

# Unreal Python keeps wrapped World/Actor objects alive. Release local references
# before switching maps so editor garbage collection can unload the old World.
import gc
link_crate()
gc.collect()
assert levels.load_level(STAGE4)
add_entry_fade()
gc.collect()
assert levels.load_level(STAGE3)
u.log('STAGE3 CRATE TRANSITION AND STAGE4 ENTRY FADE SAVED')
