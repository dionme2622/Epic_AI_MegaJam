import unreal as u
from pathlib import Path
h=u.HitResult()
Path(r"C:/LHH/Epic_AI_MegaJam/MegaJam/tmp/Stage2Workshop/api.txt").write_text(str(dir(h))+"\n"+str([n for n in dir(u.GameplayStatics) if "hit_result" in n])+ "\n"+str([n for n in dir(u.SystemLibrary) if "hit_result" in n]))
