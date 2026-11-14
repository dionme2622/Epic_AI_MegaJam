import json
a=json.load(open("tmp/Stage2Workshop/audit.json",encoding="utf8"))
for r in a:
 if r["label"] in ["Stage1_Backdrop","Stage1_Ground","Stage1_BackgroundFill","Stage1_Lift","Stage1_WheelHigh","Stage1_WheelLow","Stage1_GearHigh","Stage1_GearLow","Stage1_GateBarrier","Stage1_Player","Stage1_PuzzleDirector","Stage1_LiftCollider"]:
  print(json.dumps(r,indent=2,ensure_ascii=False))
