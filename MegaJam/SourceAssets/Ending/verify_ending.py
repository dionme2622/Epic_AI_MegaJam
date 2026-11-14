"""Run during PIE, while the ending choice is visible, with an optional 0/1/2 argument."""
import unreal, json, sys
from pathlib import Path
world=unreal.EditorLevelLibrary.get_game_world()
assert world, 'Start PIE before verifying'
actor=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.DirectorCutEnding)[0]
option=int(sys.argv[1]) if len(sys.argv)>1 else 0
observe_only=len(sys.argv)>2 and sys.argv[2]=='observe'
assert len(actor.get_editor_property('OptionImages'))==3
if not observe_only:
    assert actor.get_ending_state()==unreal.DirectorCutEndingState.CHOOSING
    assert actor.get_selected_lower_body()==-1
    assert actor.get_editor_property('UpperDragon').get_editor_property('hidden') is False
    # Invalid indices must leave the choice open.
    actor.choose_lower_body(-1); actor.choose_lower_body(3)
    assert actor.get_ending_state()==unreal.DirectorCutEndingState.CHOOSING
    actor.choose_lower_body(option)
assert actor.get_selected_lower_body()==option
assert actor.get_ending_state() in (unreal.DirectorCutEndingState.REVEALING,unreal.DirectorCutEndingState.READY_FOR_CONTINUATION)
expected={'FullDragon':option==0,'UpperDragon':option!=0,'CartBody':option==1,'HeroLegs':option==2}
for prop,visible in expected.items():
    assert actor.get_editor_property(prop).get_editor_property('hidden') != visible, prop
for wheel in actor.get_editor_property('CartAccessories'):
    assert wheel.get_editor_property('hidden') != (option==1)
actor.choose_lower_body((option+1)%3)
assert actor.get_selected_lower_body()==option, 'Duplicate input must not change selection'
result={'option':option,'model_visibility_pass':True,'duplicate_input_pass':True,'selection_input':'UI' if observe_only else 'API with invalid-index checks'}
data={'elapsed':0.0}
def tick(delta):
    data['elapsed']+=delta
    if actor.get_ending_state()==unreal.DirectorCutEndingState.READY_FOR_CONTINUATION:
        unreal.unregister_slate_post_tick_callback(handle)
        cam=actor.get_editor_property('EndingCamera')
        p=cam.get_actor_location(); r=cam.get_actor_rotation()
        expected_camera=(710,2450,470,-3) if option==0 and actor.get_editor_property('OriginalLegsSequenceActor') else (390,1150,245,-2)
        if option==1 and actor.get_editor_property('CartSequenceActor'):expected_camera=(110,850,165,-5)
        assert abs(p.x-expected_camera[0])<.01 and abs(p.y-expected_camera[1])<.01 and abs(p.z-expected_camera[2])<.01, str(p)
        assert abs(r.pitch-expected_camera[3])<.01 and abs(r.yaw+90)<.01, str(r)
        pc=unreal.GameplayStatics.get_player_controller(world,0)
        assert pc.get_view_target()==cam
        result.update({'camera_return_pass':True,'choice_persisted':actor.get_selected_lower_body()==option,
            'state':'ReadyForContinuation','camera':[p.x,p.y,p.z,r.pitch,r.yaw,r.roll]})
        Path(unreal.Paths.project_saved_dir(),f'ending_verify_{option}.json').write_text(json.dumps(result,indent=2),encoding='utf8')
        unreal.log('ENDING_VERIFY_PASS '+str(option))
    elif data['elapsed']>30:
        unreal.unregister_slate_post_tick_callback(handle)
        raise AssertionError('Reveal did not finish within 30 seconds')
handle=unreal.register_slate_post_tick_callback(tick)
tick(0.0)
