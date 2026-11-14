import unreal,json,traceback
out={}
try:
 worlds=unreal.EditorLevelLibrary.get_pie_worlds(False);out['worlds']=[str(w) for w in worlds]
 world=worlds[0]
 actors=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_class(None,'/Game/Level/Character/BP_Dragon.BP_Dragon_C'))
 actor=actors[0];mesh=actor.get_editor_property('mesh');anim=mesh.get_anim_instance();movement=actor.get_character_movement()
 out.update({'actor':str(actor),'anim':str(anim),'initial':anim.get_editor_property('is_moving'),'velocity':str(actor.get_velocity())})
 state={'i':0}; movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING); movement.set_editor_property('velocity',unreal.Vector(0,0,0))
 def tick(dt):
  try:
   state['i']+=1
   if state['i']==4:
    out['idle']=anim.get_editor_property('is_moving');movement.set_editor_property('velocity',unreal.Vector(300,0,0))
   if state['i']==5:out['moving_velocity']=str(actor.get_velocity())
   if state['i']==6:
    out['moving']=anim.get_editor_property('is_moving');movement.set_editor_property('velocity',unreal.Vector(0,0,0))
   if state['i']==10:
    out['stopped']=anim.get_editor_property('is_moving');unreal.unregister_slate_post_tick_callback(state['handle']);open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/runtime_abp.json','w').write(json.dumps(out,indent=2))
  except:
   out['callback_error']=traceback.format_exc();unreal.unregister_slate_post_tick_callback(state['handle']);open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/runtime_abp.json','w').write(json.dumps(out,indent=2))
 state['handle']=unreal.register_slate_post_tick_callback(tick)
except:
 out['error']=traceback.format_exc();open('C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/runtime_abp.json','w').write(json.dumps(out,indent=2))
