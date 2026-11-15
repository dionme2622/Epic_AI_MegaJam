import unreal
ed=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert ed.load_level('/Game/DirectorCut/Prologue/L_BossPrologue')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
for i,name in enumerate(['01_Hero','02_Dragon','03_Missing','04_Protest']):
    matches=[a for a in actors if 'Subtitle_'+name in a.get_actor_label()]
    assert len(matches)==1,(name,[a.get_actor_label() for a in matches])
    a=matches[0];tags=list(a.tags);tag='PrologueCaption%02d'%(i+1)
    if tag not in [str(t) for t in tags]:tags.append(tag)
    a.set_editor_property('tags',tags)
assert ed.save_current_level()
unreal.log('PROLOGUE_SUBTITLE_UI_TAGS_SAVED')
