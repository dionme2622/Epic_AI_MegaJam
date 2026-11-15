"""PIE regression: original stage stays level; cart alone uses the right-side ramp."""
import unreal, json, math, sys
from pathlib import Path
option=int(sys.argv[1]) if len(sys.argv)>1 else 1
pause_preview=len(sys.argv)>2 and sys.argv[2]=='preview'
root=Path(unreal.Paths.project_dir())/'SourceAssets'/'Ending'
baseline=json.loads((root/'stage_baseline.json').read_text(encoding='utf-8-sig'))
stage=[r for r in baseline if r['label'] not in ('Ending Hero','Ending Dragon Upper')]
data={'elapsed':0,'chosen':False,'intro':False,'pauses':0,'samples':[],'max_stage_error':0,'max_seam':0}
unreal._right_ramp_test=data

def tick(dt):
    data['elapsed']+=dt
    world=unreal.EditorLevelLibrary.get_game_world()
    if not world:return
    controllers=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.DirectorCutEnding)
    if not controllers:return
    c=controllers[0]
    actors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor)}
    state=c.get_ending_state()
    ramp=actors['Ending_CartScene_StartRamp']
    for r in stage:
        actor=actors[r['label']]
        error=unreal.MathLibrary.vector_distance(actor.get_actor_location(),unreal.Vector(*r['pos']))
        data['max_stage_error']=max(data['max_stage_error'],error)
        assert error<.01 and abs(actor.get_actor_rotation().pitch-r['rot'][0])<.001, r['label']
    hero=actors['Ending Hero']
    assert abs(hero.get_actor_location().z-19.2743233)<.01
    if state==unreal.DirectorCutEndingState.DIALOGUE:
        data['intro']=True
        assert ramp.get_editor_property('hidden')
        assert abs(c.get_editor_property('UpperDragon').get_actor_location().z+17.8)<.01
    if state==unreal.DirectorCutEndingState.CHOOSING and not data['chosen']:
        c.choose_lower_body(option);data['chosen']=True
        assert ramp.get_editor_property('hidden')==(option!=1)
    if state==unreal.DirectorCutEndingState.REVEALING:
        cam=c.get_editor_property('EndingCamera').get_actor_location()
        data['reveal_camera']=cam.to_tuple()
    if state==unreal.DirectorCutEndingState.CART_SCENE:
        assert option==1 and not ramp.get_editor_property('hidden')
        p=c.get_editor_property('CartSequenceActor').get_editor_property('sequence_player')
        unreal._right_ramp_player=p
        q=p.get_current_time();t=(q.time.frame_number.value+q.time.sub_frame)*q.rate.denominator/q.rate.numerator
        cart=c.get_editor_property('CartBody');upper=c.get_editor_property('UpperDragon');rig=cart.get_attach_parent_actor()
        assert ramp.get_attach_parent_actor() is None
        waist=unreal.MathLibrary.transform_location(upper.get_actor_transform(),unreal.Vector(14.1,0,43.75))
        deck=unreal.MathLibrary.transform_location(cart.get_actor_transform(),unreal.Vector(0,0,31.9))
        seam=unreal.MathLibrary.vector_distance(waist,deck);data['max_seam']=max(data['max_seam'],seam)
        assert seam<3.1,seam
        cam=c.get_editor_property('EndingCamera').get_actor_location()
        if data['samples']:assert cam.x<=data['samples'][-1]['camera'][0]+.01
        else:assert unreal.MathLibrary.vector_distance(cam,unreal.Vector(*data['reveal_camera']))<2
        data['samples'].append(dict(time=t,pos=rig.get_actor_location().to_tuple(),pitch=rig.get_actor_rotation().pitch,camera=cam.to_tuple()))
        if pause_preview and data['pauses']<2 and t>=[.1,3.3][data['pauses']]:
            data['pauses']+=1;p.pause();unreal.log('RIGHT_RAMP_PREVIEW_PAUSED '+str(data['pauses']))
    if state==unreal.DirectorCutEndingState.READY_FOR_CONTINUATION and data['chosen']:
        unreal.unregister_slate_post_tick_callback(handle)
        if option==1:
            def at(t):return min(data['samples'],key=lambda s:abs(s['time']-t))
            assert at(.2)['pos'][2]>379
            assert at(3.3)['pos'][2]<300 and at(3.3)['pitch']>10
            assert abs(at(4.7)['pos'][2]-20.07)<.5
            assert at(4.5)['pos'][0]<110
            early=abs(at(1.75)['pos'][0]-at(.75)['pos'][0])
            fast=abs(at(4.5)['pos'][0]-at(3.5)['pos'][0])
            assert fast>early*5,(early,fast)
            data.update(early_cm=early,fast_cm=fast)
        else:assert ramp.get_editor_property('hidden')
        data['pass']=True
        Path(unreal.Paths.project_saved_dir(),f'right_ramp_verify_{option}.json').write_text(json.dumps(data,indent=2),encoding='utf8')
        unreal.log('RIGHT_RAMP_RUNTIME_PASS '+str(option))
    elif data['elapsed']>(240 if pause_preview else 60):
        unreal.unregister_slate_post_tick_callback(handle)
        raise AssertionError('Right ramp test timed out')
handle=unreal.register_slate_post_tick_callback(tick)
