import unreal as u
from pathlib import Path
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
out=[]
for x in [-1000,0,440,1215,2200,4400,7000,8200,8400,8600,8700,8850,8950,9200,9800]:
 hit=u.SystemLibrary.line_trace_single(w,u.Vector(x,0,1100),u.Vector(x,0,-250),u.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],u.DrawDebugTrace.NONE,True)
 if hit:
  point=hit.to_dict()
  try: actor=hit.get_editor_property("Actor")
  except Exception: actor=None
  out.append((x,str(point),str(actor)))
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage2Workshop/ground_z.txt").write_text(str(out))


