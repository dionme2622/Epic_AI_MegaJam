import unreal as u, json
from pathlib import Path
api=u.get_editor_subsystem(u.EditorActorSubsystem); le=u.get_editor_subsystem(u.LevelEditorSubsystem)
res={}
for path in ['/Game/DirectorCut/Stage/Stage3_','/Game/Stage3Integrated/Sections/L_Bloom','/Game/Stage3Integrated/Sections/L_Resolution']:
 assert le.load_level(path)
 rows=[]
 for a in api.get_all_level_actors():
  name=a.get_actor_label()
  if any(s in name.lower() for s in ('floor','tile','sign','dot','mosaic','directionallight','sky','light','wall','archive empty')):
   p=a.get_actor_location(); b,e=a.get_actor_bounds(False)
   comps=[]
   for c in a.get_components_by_class(u.StaticMeshComponent):
    m=c.get_editor_property('static_mesh')
    comps.append(dict(name=c.get_name(),mesh=m.get_path_name() if m else None,mat=[str(c.get_material(i)) for i in range(c.get_num_materials())],collision=str(c.get_collision_profile_name()),relative=c.get_editor_property('relative_location').to_tuple(),scale=c.get_editor_property('relative_scale3d').to_tuple()))
   rows.append(dict(name=name,cls=a.get_class().get_name(),location=p.to_tuple(),center=b.to_tuple(),extent=e.to_tuple(),components=comps))
 res[path]=rows
Path(r'C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/stage3_redesign_audit.json').write_text(json.dumps(res,indent=2),encoding='utf8')
assert le.load_level('/Game/DirectorCut/Stage/Stage3_')
u.log('STAGE3 REDESIGN AUDIT DONE')
