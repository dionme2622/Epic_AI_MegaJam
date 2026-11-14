(event EventBeginPlay
  (CameraFades|StartCameraFade :self (Game|GetPlayerCameraManager :PlayerIndex 0)
    :FromAlpha 1.0 :ToAlpha 0.0 :Duration 1.5
    :Color "(R=0.000000,G=0.000000,B=0.000000,A=1.000000)" :bShouldFadeAudio false :bHoldWhenFinished false))
(event EventTick
  (if (not (Variables|Default|GetTransitionStarted))
    (bind pawn (Game|GetPlayerPawn :PlayerIndex 0))
    (if (> (.x (Transformation|GetActorLocation :self pawn)) (Variables|Default|GetExitX))
      (Variables|Default|SetTransitionStarted true)
      (Input|SetIgnoreMoveInput :self (Game|GetPlayerController :PlayerIndex 0) :bNewMoveInput true)
      (CameraFades|StartCameraFade :self (Game|GetPlayerCameraManager :PlayerIndex 0)
        :FromAlpha 0.0 :ToAlpha 1.0 :Duration 1.5
        :Color "(R=0.000000,G=0.000000,B=0.000000,A=1.000000)" :bShouldFadeAudio false :bHoldWhenFinished true)
      (Utilities|FlowControl|Delay :Duration 1.6)
      (Game|OpenLevel(byObjectReference) :Level "/Game/Level/Stage1.Stage1"))))
