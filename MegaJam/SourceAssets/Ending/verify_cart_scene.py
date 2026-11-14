"""Run at the PIE choice. Optional 'capture' pauses on brakes, scream, and hero reaction."""
import unreal,json,sys,gc,types,math
from pathlib import Path
for f in gc.get_objects():
    if isinstance(f,types.FunctionType) and f.__name__=='tick' and f.__code__.co_filename.endswith('verify_cart_scene.py'):
        try:unreal.unregister_slate_post_tick_callback(f.__globals__['handle'])
        except Exception:pass
world=unreal.EditorLevelLibrary.get_game_world()
assert not unreal.GameplayStatics.get_all_actors_of_class(world,unreal.DefaultPawn), 'Unexpected floating sphere pawn'
a=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.DirectorCutEnding)[0]
assert a.get_ending_state()==unreal.DirectorCutEndingState.CHOOSING
seqactor=a.get_editor_property('CartSequenceActor');assert seqactor
assert not any(isinstance(t,unreal.MovieSceneAudioTrack) for t in seqactor.get_sequence().get_tracks())
scenery=[x for x in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.StaticMeshActor) if x.get_actor_label().startswith('Ending_CartScene_') and not x.get_actor_label().endswith('_Rig')]
assert len(scenery)==34 and all(not x.get_editor_property('hidden') for x in scenery)
cart=a.get_editor_property('CartBody');upper=a.get_editor_property('UpperDragon')
rig=cart.get_attach_parent_actor();assert rig==upper.get_attach_parent_actor()
hero=next(x for x in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if x.get_actor_label()=='Ending Hero')
start_yaw=hero.get_actor_rotation().yaw;hero_pos=hero.get_actor_location()
capture=len(sys.argv)>1 and sys.argv[1]=='capture'
samples=[];data={'elapsed':0,'last':-1,'capture':0};seen=set()
pause_times=[2.0,4.5,7.6]
a.choose_lower_body(1)
def tick(delta):
    data['elapsed']+=delta
    state=a.get_ending_state();seen.add(str(state))
    if state==unreal.DirectorCutEndingState.CART_SCENE:
        p=seqactor.get_editor_property('sequence_player')
        qt=p.get_current_time();time=(qt.time.frame_number.value+qt.time.sub_frame)*qt.rate.denominator/qt.rate.numerator
        assert all(not x.get_editor_property('hidden') for x in scenery)
        if time-data['last']>.12:
            data['last']=time
            waist=unreal.MathLibrary.transform_location(upper.get_actor_transform(),unreal.Vector(14.1,0,43.75))
            deck=unreal.MathLibrary.transform_location(cart.get_actor_transform(),unreal.Vector(0,0,31.9))
            seam=unreal.MathLibrary.vector_distance(waist,deck)
            samples.append({'time':time,'x':rig.get_actor_location().x,'z':rig.get_actor_location().z,
                'hero_yaw':hero.get_actor_rotation().yaw,'seam_cm':seam})
            assert seam<3.1,seam
        if capture and data['capture']<len(pause_times) and time>=pause_times[data['capture']]:
            data['capture']+=1;unreal._cart_test_player=p;p.pause()
            unreal.log('CART_CAPTURE_PAUSED '+str(data['capture']))
    if state==unreal.DirectorCutEndingState.READY_FOR_CONTINUATION:
        unreal.unregister_slate_post_tick_callback(handle)
        assert any('CART_SCENE' in s for s in seen)
        assert len(samples)>20
        def nearest(t):return min(samples,key=lambda s:abs(s['time']-t))
        early=abs(nearest(1.5)['x']-nearest(.5)['x'])
        late=abs(nearest(5)['x']-nearest(4)['x'])
        assert late>early*2.5,(early,late)
        assert all(abs(s['z']-20.07)<.02 for s in samples if s['time']<2.5), 'Cart must start on the flat'
        assert nearest(4)['z']<nearest(2)['z']-50, 'Cart must descend ahead of the flat'
        assert rig.get_actor_location().x < -1700
        assert unreal.MathLibrary.vector_distance(hero.get_actor_location(),hero_pos)<.01
        turn=abs((hero.get_actor_rotation().yaw-start_yaw+180)%360-180)
        assert abs(turn-180)<.1,turn
        assert abs(nearest(4)['hero_yaw']-start_yaw)<.1,'Hero turns before cart passes'
        Path(unreal.Paths.project_saved_dir(),'cart_scene_verify.json').write_text(json.dumps({'pass':True,'early_travel_cm':early,
            'late_travel_cm':late,'max_seam_cm':max(s['seam_cm'] for s in samples),'hero_turn_degrees':turn,'samples':samples},indent=2),encoding='utf8')
        unreal.log('CART_SCENE_RUNTIME_PASS')
    elif data['elapsed']>(180 if capture else 35):
        unreal.unregister_slate_post_tick_callback(handle)
        raise AssertionError('Cart branch did not finish')
handle=unreal.register_slate_post_tick_callback(tick)
