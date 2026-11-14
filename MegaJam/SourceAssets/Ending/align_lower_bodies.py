import unreal
sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors={a.get_actor_label():a for a in sub.get_all_level_actors()}
c=actors['Ending_Controller']; upper=actors['Ending Dragon Upper']
legs=actors['Ending_Hero_Legs']
legs.set_actor_rotation(unreal.Rotator(pitch=0,yaw=90,roll=0),False)
for prop,height in [('CartUpperTransform',20.07+31.9*3.4),('HeroUpperTransform',20.07+40.5*4.1)]:
    c.set_editor_property(prop,unreal.Transform(location=unreal.Vector(1271.6,3.5,height-43.75*7.5+3),rotation=unreal.Rotator(pitch=0,yaw=180,roll=0),scale=unreal.Vector(7.5,7.5,7.5)))
# Restore the dragon's reference pose when the dialogue completes, before fitting a new lower body.
intro=c.get_editor_property('IntroSequenceActor')
settings=intro.get_editor_property('playback_settings')
settings.finish_completion_state_override=unreal.MovieSceneCompletionModeOverride.FORCE_RESTORE_STATE
intro.set_editor_property('playback_settings',settings)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.log('ENDING_LOWER_ALIGNMENT_SAVED')
