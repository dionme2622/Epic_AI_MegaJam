# Stage 2 puzzle controller

`Stage2PuzzleController` is a reusable native Actor; it creates no level or UI.
Open the project after compiling and create a Blueprint subclass, then place an instance in a test level.

1. Assign a Post Process Volume (enabled and covering the camera) and movable puzzle lights. Shadows affect only those lights. Bloom and manual exposure override the assigned volume; tune their editable intensities for the scene.
2. Assign two movable shadow-piece actors, world-space target positions, and a tolerance in centimetres. Use `MoveShadowPiece` for dragging and `CheckShadowPuzzle` after any other movement. Both positions and shadows ON are required.
3. Bind UI buttons to `SetShadowsEnabled`, `SetBloomEnabled`, and `SetDarkExposure`; bind `OnSettingsChanged` to refresh UI and authored clue visuals. This class does not bind keys, pause the game, or save settings.
4. Call `EnterSymbol` from the three console buttons. The answer is Star, Moon, Sun; a wrong entry clears progress. `OnSequenceUpdated` exposes progress.
5. Call `SelectFilm` for A/B/C. Bind `OnFilmChanged` to swap the authored screen image and use `IsCurrentFilmClueVisible` when settings or film change. Visibility conditions: A bloom OFF, B shadows OFF, C dark exposure. Call `SubmitFilmSolution` with scene 3, Right, Gear.
6. Bind `OnPuzzleCompleted` to doors and presentation (1 shadow, 2 symbols, 3 film). Completion is latched and emitted once. Gates, proximity checks, interaction controls, hint UI, film images, and audio must be implemented by the level/Blueprint integration.

The controller does not automatically reveal or conceal clues or add light occluders. Post-process and shadow appearance depends on the assigned scene, movable light configuration, renderer and material settings. Validate in PIE and in a packaged build. This actor changes its assigned volume settings and lights and does not restore their previous values on destruction; use level-specific instances.
