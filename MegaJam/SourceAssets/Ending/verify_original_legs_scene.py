"""PIE check: choose original legs, observe bone motion, subtitles' time windows and final hold."""
import unreal,json,gc,types,sys
from pathlib import Path
world=unreal.EditorLevelLibrary.get_game_world()
for f in gc.get_objects():
    if isinstance(f,types.FunctionType) and f.__name__=='tick' and f.__code__.co_filename.endswith('verify_original_legs_scene.py'):
        try: unreal.unregister_slate_post_tick_callback(f.__globals__['handle'])
        except Exception: pass
a=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.DirectorCutEnding)[0]
assert a.get_ending_state()==unreal.DirectorCutEndingState.CHOOSING
seqactor=a.get_editor_property('OriginalLegsSequenceActor'); assert seqactor
assert len([t for t in seqactor.get_sequence().get_tracks() if isinstance(t,unreal.MovieSceneAudioTrack)])==2
mesh=a.get_editor_property('FullDragon').get_component_by_class(unreal.SkeletalMeshComponent)
samples=[]; seen=set(); timer={'t':0,'last':-1,'capture':0}
capture=len(sys.argv)>1 and sys.argv[1]=='capture'
a.choose_lower_body(0)
def tick(delta):
    timer['t']+=delta
    state=a.get_ending_state();seen.add(str(state))
    if state==unreal.DirectorCutEndingState.ORIGINAL_LEGS_SCENE:
        qt=seqactor.get_editor_property('sequence_player').get_current_time()
        time=(qt.time.frame_number.value+qt.time.sub_frame)*qt.rate.denominator/qt.rate.numerator
        if capture and ((timer['capture']==0 and time>=7.1) or (timer['capture']==1 and time>=10.1)):
            timer['capture']+=1
            unreal._original_test_player=seqactor.get_editor_property('sequence_player')
            unreal._original_test_player.pause()
            unreal.log('ORIGINAL_SUBTITLE_PAUSED '+str(timer['capture']))
        if time-timer['last']>.15:
            timer['last']=time
            l=mesh.get_socket_transform('Foot_L',unreal.RelativeTransformSpace.RTS_COMPONENT).translation
            r=mesh.get_socket_transform('Foot_R',unreal.RelativeTransformSpace.RTS_COMPONENT).translation
            samples.append({'time':time,'x':a.get_editor_property('FullDragon').get_actor_location().x,'left':list(l.to_tuple()),'right':list(r.to_tuple())})
    if state==unreal.DirectorCutEndingState.READY_FOR_CONTINUATION:
        unreal.unregister_slate_post_tick_callback(handle)
        assert any('ORIGINAL_LEGS_SCENE' in s for s in seen), seen
        assert len(samples)>10,len(samples)
        assert max(s['x'] for s in samples)-min(s['x'] for s in samples)>390
        assert max(s['left'][0] for s in samples)-min(s['left'][0] for s in samples)>1
        assert max(s['right'][0] for s in samples)-min(s['right'][0] for s in samples)>1
        standing=[s for s in samples if s['time']>=6.5]
        assert standing and all(abs(s['left'][0]-3.1)<.1 and abs(s['right'][0]-3.1)<.1 for s in standing), standing[:2]
        assert abs(a.get_editor_property('FullDragon').get_actor_location().x-870)<.01
        Path(unreal.Paths.project_saved_dir(),'original_legs_verify.json').write_text(json.dumps({'pass':True,'states':list(seen),'samples':samples},indent=2),encoding='utf8')
        unreal.log('ORIGINAL_LEGS_RUNTIME_PASS')
    elif timer['t']>(120 if capture else 35):
        unreal.unregister_slate_post_tick_callback(handle)
        raise AssertionError('Branch did not finish')
handle=unreal.register_slate_post_tick_callback(tick)
