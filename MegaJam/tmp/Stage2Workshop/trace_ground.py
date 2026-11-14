import unreal as u
from pathlib import Path
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
rows=[]
for x in [-1000,0,440,1215,2200,4400,7000,8200,8400,8600,8700,8850,8950,9200,9800]:
 hit=u.SystemLibrary.line_trace_single(w,u.Vector(x,0,1100),u.Vector(x,0,-250),u.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],u.DrawDebugTrace.NONE,True)
 rows.append((x,str(hit)))
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,u.SkyLight):
  c=a.get_component_by_class(u.SkyLightComponent)
  rows.append(("SkyLight",str(c.get_editor_property("intensity"))))
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage2Workshop/ground_trace.txt").write_text("\n".join(map(str,rows)),encoding="utf8")
