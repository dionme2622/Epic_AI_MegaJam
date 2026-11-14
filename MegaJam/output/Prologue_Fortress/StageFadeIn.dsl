(event EventBeginPlay
  (CameraFades|StartCameraFade :self (Game|GetPlayerCameraManager :PlayerIndex 0)
    :FromAlpha 1.0 :ToAlpha 0.0 :Duration 1.5
    :Color "(R=0.000000,G=0.000000,B=0.000000,A=1.000000)" :bShouldFadeAudio false :bHoldWhenFinished false))
