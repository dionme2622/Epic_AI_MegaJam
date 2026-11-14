import unreal as u
le=u.get_editor_subsystem(u.LevelEditorSubsystem);api=u.get_editor_subsystem(u.EditorActorSubsystem)
assert le.load_level('/Game/Stage3Integrated/Sections/L_Bloom')
a={x.get_actor_label():x for x in api.get_all_level_actors()}
# Preserve the interaction controller while revealing the authored lever desk.
c=a['Bloom_Controller'].get_editor_property('ConsoleMesh');c.set_visibility(False,True);c.set_hidden_in_game(True,True)
assert le.save_current_level()
assert le.load_level('/Game/DirectorCut/Stage/Stage3_')
u.log('STAGE3 BLOOM CONTROL DESK POLISHED')
