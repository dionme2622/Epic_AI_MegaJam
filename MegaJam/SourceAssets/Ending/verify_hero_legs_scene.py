"""Run before PIE. Exercise the hero-leg choice and optionally pause for visual review."""
import unreal,json,sys,math
from pathlib import Path
preview=len(sys.argv)>1 and sys.argv[1]=='preview'
data={'elapsed':0,'chosen':False,'samples':[],'pauses':0,'max_seam':0,'foot_samples':[],'standing_feet':[]}
unreal._hero_legs_test=data

def tick(dt):
 data['elapsed']+=dt
 world=unreal.EditorLevelLibrary.get_game_world()
 if not world:return
 cs=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.DirectorCutEnding)
 if not cs:return
 c=cs[0];state=c.get_ending_state()
 if state==unreal.DirectorCutEndingState.CHOOSING and not data['chosen']:
  c.choose_lower_body(2);data['chosen']=True
 if state==unreal.DirectorCutEndingState.HERO_LEGS_SCENE:
  player=c.get_editor_property('HeroLegsSequenceActor').get_editor_property('sequence_player');unreal._hero_legs_player=player
  q=player.get_current_time();time=(q.time.frame_number.value+q.time.sub_frame)*q.rate.denominator/q.rate.numerator
  upper=c.get_editor_property('UpperDragon');legs=c.get_editor_property('HeroLegs');rig=legs.get_attach_parent_actor()
  assert upper.get_attach_parent_actor()==rig
  assert not legs.get_editor_property('hidden') and not upper.get_editor_property('hidden')
  assert c.get_editor_property('CartBody').get_editor_property('hidden')
  for accessory in c.get_editor_property('CartAccessories'):assert accessory.get_editor_property('hidden')
  waist=unreal.MathLibrary.transform_location(upper.get_actor_transform(),unreal.Vector(14.1,0,43.75))
  belt=unreal.MathLibrary.transform_location(legs.get_actor_transform(),unreal.Vector(0,0,40.5))
  seam=unreal.MathLibrary.vector_distance(waist,belt);data['max_seam']=max(data['max_seam'],seam)
  assert seam<3.1,seam
  data['samples'].append({'time':time,'x':rig.get_actor_location().x,'z':rig.get_actor_location().z})
  if .7<time<2.8:
   foot=legs.skeletal_mesh_component.get_socket_transform('LeftFoot',unreal.RelativeTransformSpace.RTS_COMPONENT).translation
   data['foot_samples'].append(foot.to_tuple())
  if time>=3.2:
   data['standing_feet'].append([legs.skeletal_mesh_component.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT).translation.to_tuple() for n in ['LeftFoot','RightFoot']])
  if preview and data['pauses']<2 and time>=[1.7,4.1][data['pauses']]:
   data['pauses']+=1;player.pause();unreal.log('HERO_LEGS_PREVIEW_PAUSED '+str(data['pauses']))
 if state==unreal.DirectorCutEndingState.READY_FOR_CONTINUATION and data['chosen']:
  if 'ready_at' not in data:data['ready_at']=data['elapsed']
  legs=c.get_editor_property('HeroLegs')
  data['standing_feet'].append([legs.skeletal_mesh_component.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT).translation.to_tuple() for n in ['LeftFoot','RightFoot']])
  if data['elapsed']-data['ready_at']<.7:return
  unreal.unregister_slate_post_tick_callback(handle)
  for foot in range(2):
   for axis in range(3):
    values=[p[foot][axis] for p in data['standing_feet']]
    assert max(values)-min(values)<.001, 'Foot moves during the final hold'
  assert len(data['samples'])>20
  assert max(s['z'] for s in data['samples'])-min(s['z'] for s in data['samples'])<.01, 'Body must not vibrate vertically'
  assert abs(data['samples'][-1]['x']-650)<.1
  assert max(p[1] for p in data['foot_samples'])-min(p[1] for p in data['foot_samples'])>3
  assert c.get_selected_lower_body()==2
  data['pass']=True
  Path(unreal.Paths.project_saved_dir(),'hero_legs_runtime.json').write_text(json.dumps(data,indent=2),encoding='utf8')
  unreal.log('HERO_LEGS_RUNTIME_PASS')
 elif data['elapsed']>(240 if preview else 50):
  unreal.unregister_slate_post_tick_callback(handle);raise AssertionError('Hero legs branch did not finish')
handle=unreal.register_slate_post_tick_callback(tick)
