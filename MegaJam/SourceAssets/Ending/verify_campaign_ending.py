"""PIE integration test: uncleared Stage4 stays put; completion opens the ending choice."""
import unreal,json
from pathlib import Path
state={'elapsed':0,'stage_time':0,'completion_set':False,'ending_seen':False}

def tick(dt):
    state['elapsed']+=dt
    world=unreal.EditorLevelLibrary.get_game_world()
    if not world:return
    name=unreal.GameplayStatics.get_current_level_name(world,True)
    if name=='Stage4':
        state['stage_time']+=dt
        theatres=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Stage4ShadowTheatre)
        assert len(theatres)==1
        theatre=theatres[0]
        if not state['completion_set']:
            assert not theatre.get_editor_property('bRecovered'), 'Test requires uncleared Stage4'
            if state['stage_time']>=3:
                unreal.SystemLibrary.execute_console_command(world,'DirectorCut.Test.CompleteFinalStage')
                state['completion_set']=True;state['completion_time']=state['elapsed']
                unreal.log('CAMPAIGN_TEST_FINAL_CLEAR_SIGNAL')
    elif name=='L_BossEnding':
        assert state['completion_set'], 'Ending opened before final clear'
        if not state['ending_seen']:
            state['ending_seen']=True
            state['transition_delay']=state['elapsed']-state['completion_time']
            assert state['transition_delay']>=7.9
        cs=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.DirectorCutEnding)
        assert len(cs)==1
        c=cs[0]
        assert c.get_editor_property('OriginalLegsSequenceActor')
        assert c.get_editor_property('CartSequenceActor')
        assert c.get_editor_property('HeroLegsSequenceActor')
        if c.get_ending_state()==unreal.DirectorCutEndingState.CHOOSING:
            assert len(c.get_editor_property('OptionImages'))==3
            state['pass']=True
            Path(unreal.Paths.project_saved_dir(),'campaign_ending_integration.json').write_text(json.dumps(state,indent=2),encoding='utf8')
            unreal.unregister_slate_post_tick_callback(handle)
            unreal.log('CAMPAIGN_FINAL_CLEAR_TO_ENDING_CHOICE_PASS')
    else:raise AssertionError('Unexpected gameplay map '+name)
    if state['elapsed']>55:
        unreal.unregister_slate_post_tick_callback(handle)
        raise AssertionError('Campaign ending integration timed out')
handle=unreal.register_slate_post_tick_callback(tick)
