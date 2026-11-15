# WeLoveIndies opening attribution

- Official source: https://www.weloveindies.com/Trailer/WLI_Intro.mp4
- Official requirement reference: https://www.weloveindies.com/en/contact (FREE USAGE)
- Original file: Content/Movies/WLI_Intro.mp4 (downloaded without editing)
- Duration: 7.52 seconds; H.264 3840×2160, AAC stereo 48 kHz.

DefaultGame.ini registers WLI_Intro as a StartupMovie, waits for completion and disables skipping. Packaging includes the MP4 as a non-UFS movie file. WindowsMoviePlayer is enabled by default in UE 5.8.

Flow: launch game → official intro with its original audio → lobby → Start Game → existing prologue. Returning to the lobby from an ending does not replay the launch movie. The normal editor PIE Play button does not exercise startup movies; verify from a standalone game process or packaged Windows game.

Verification: the complete source video decoded without errors in FFmpeg; standalone launch reached L_DirectorCutLobby without a WindowsMoviePlayer load error. Packaged-build playback has not been separately tested.
