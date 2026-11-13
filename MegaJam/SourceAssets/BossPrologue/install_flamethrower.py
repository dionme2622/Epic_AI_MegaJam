import unreal
import math
actors=unreal.EditorLevelLibrary.get_all_level_actors()
for a in actors:
 if a.get_actor_label() in ['Prologue Dragon','BossIntro_Hero','BossIntro_Dragon_NiagaraBreath']:
  unreal.log('BREATH_ACTOR '+a.get_actor_label()+' '+str(a.get_actor_location()))
  c=a.get_component_by_class(unreal.SkeletalMeshComponent)
  if c:
   for i in range(c.get_num_bones()):
    n=c.get_bone_name(i)
    if any(k in str(n).lower() for k in ['head','jaw','mouth']): unreal.log('BREATH_BONE '+str(n)+' '+str(c.get_socket_location(n)))

lib=unreal.EditorAssetLibrary
source=unreal.load_asset('/Game/Realistic_Starter_VFX_Pack_Vol2/Particles/Fire/P_flamethrower')
path='/Game/DirectorCut/Prologue/Cinematic/P_DragonBreath_Short'
effect=unreal.load_asset(path) if lib.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset('P_DragonBreath_Short','/Game/DirectorCut/Prologue/Cinematic',source)
assert effect
for obj in unreal.ObjectIterator():
 if not isinstance(obj,unreal.Object): continue
 p=unreal.SystemLibrary.get_path_name(obj)
 if not p.startswith(effect.get_path_name()+':'): continue
 if 'Lifetime' in p and obj.get_class().get_name()=='DistributionFloatUniform':
  obj.set_editor_property('min',.24); obj.set_editor_property('max',.40)
 if False and ('StartSize' in p or 'ParticleModuleSize_' in p) and obj.get_class().get_name()=='DistributionVectorUniform':
  for prop in ['min','max']: obj.set_editor_property(prop,obj.get_editor_property(prop)*.6)
lib.save_loaded_asset(effect)
dragon=next(a for a in actors if a.get_actor_label()=='Prologue Dragon')
mesh=dragon.get_component_by_class(unreal.SkeletalMeshComponent)
hero=next(a for a in actors if a.get_actor_label()=='BossIntro_Hero')
mouth=mesh.get_socket_location('Head')+unreal.Vector(-90,5,-50)
seq=unreal.load_asset('/Game/DirectorCut/Prologue/LS_BossPrologue_Cinematic')
for binding in seq.get_bindings():
 if any(k in binding.get_name() for k in ['Niagara','Flame','Breath']): binding.remove()
for a in actors:
 if a.get_actor_label()=='BossIntro_Dragon_NiagaraBreath': unreal.EditorLevelLibrary.destroy_actor(a)
existing=[]
for a in actors:
 if not unreal.SystemLibrary.is_valid(a): continue
 pc=a.get_component_by_class(unreal.ParticleSystemComponent)
 if pc and (pc.get_editor_property('template')==source or a.get_actor_label()=='BossIntro_Dragon_Flamethrower'): existing.append(a)
emitter=existing[0] if existing else unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.Emitter,mouth,unreal.Rotator())
emitter.set_actor_label('BossIntro_Dragon_Flamethrower')
component=emitter.get_component_by_class(unreal.ParticleSystemComponent)
component.set_template(effect)
component.set_auto_activate(False)
component.deactivate()
emitter.set_actor_location(mouth,False,False)
# The sequence raises the dragon 150 cm during the shot. Aim at the hero's chest.
direction=hero.get_actor_location()+unreal.Vector(0,0,95)-(mouth+unreal.Vector(0,0,150))
emitter.set_actor_rotation(unreal.MathLibrary.make_rot_from_z(direction),False)
emitter.set_actor_scale3d(unreal.Vector(1,1,1))
emitter.attach_to_component(mesh,'Head',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
b=seq.add_possessable(emitter)
t=b.add_track(unreal.MovieSceneParticleTrack)
s=t.add_section(); s.set_range(0,600)
ch=s.get_all_channels()[0]
for frame,value in [(0,unreal.ParticleKey.DEACTIVATE),(200,unreal.ParticleKey.ACTIVATE),(250,unreal.ParticleKey.DEACTIVATE)]: ch.add_key(unreal.FrameNumber(frame),value)
lib.save_loaded_asset(seq)
assert unreal.EditorLevelLibrary.save_current_level()
unreal.log('FLAMETHROWER_INSTALLED mouth='+str(mouth)+' max_lifetime=0.40')





