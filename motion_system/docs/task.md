# Fluent Motion API & Corridor Development

## Phase 4: API Refactoring
- [x] Refactor `motion_builder.py` for Chained Syntax
- [x] Add `MovementChain` helper class to handle `.move().move()`
- [x] Implement `.velocity()` and `.accelerate()` mutual exclusivity

## Phase 5: Corridor Engine Logic
- [x] Implement Perpendicular Vector math in `motion_planner.py`
- [x] Add boundary clamping logic (Radius-aware)
- [x] Add Velocity Ramping (Linear interpolation of speed)

## Phase 6: Fluent Movies
- [x] Create `sprint_fluent.py` 100m demonstration
- [x] Verify multi-segment momentum handoff
- [x] Verify 100m Sprint in Unreal (SCENE GENERATION COMPLETE)

## Phase 7: Advanced Camera Integration
- [x] Create `sprint_with_camera.py` with tracking shots
- [x] Implement `look_at_actor` supported in new fluent API
- [x] Implement explicit `focus_on` support for auto-focus with manual rotation
- [x] Verify that the camera's look-at target correctly switches between Runner1 and Runner2 over time.
- [x] Verify that the camera's focus target correctly switches between Runner1 and Runner2 over time, and that depth-of-field effects are applied correctly.
- [x] Verify that the keyframe density for rotation, focus distance, and focal length in Sequencer is manageable and not excessive (0 rotations, 3 targets).
- [x] Switch to Native Auto-Tracking (LookAt & Focus Constraints) as per user request.
- [x] Implement `interp_speed` support for smooth Look-At target switching to fix sudden snapping._applier
- [x] Test with sprint_with_camera.py

## Phase 7b: Audio Support
- [x] Implement `add_audio` in MovieBuilder
- [x] Process audio commands in motion_planner
- [x] Apply audio tracks in sequence_setup (Unreal)
- [x] Verify audio with `audio_test.py`

## Phase 8: Auto-Framing Implementation
- [x] Add `frame_subject()` method to CameraBuilder
- [x] Implement focal length calculation utility
- [x] Add adaptive sampling logic in motion_planner
- [x] Create focal length keyframe track in keyframe_applier
- [x] Test with sprint_with_camera.py

## Phase 9: Frame Capture & QA Workflow
- [x] Create frame_capture.py utility
- [x] Implement hybrid QA metadata pattern
- [x] Create qa_tool.py for QA workflow
- [x] Verify frame capture works (2/3 frames captured)
- [x] Fix focal length calculation for height + width
- [x] Fix LookAt targeting (implement height_pct for Z-offset)
- [x] Fix Focus targeting (implement height_pct for Z-offset)
- [x] Implement Camera Sequence Chaining (CameraCommandBuilder)
- [ ] Debug frame capture timing for all frames
- [ ] Create image analysis script for verification

## Phase 10: Blueprint Event Track Integration (Future)
- [ ] Research MovieSceneEventTrack Python API
- [ ] Create Blueprint custom event for screenshot
- [ ] Add Event Track to sequence at verification frames
- [ ] Test embedded screenshot during playback

## Phase 12: Animation Transitions
- [x] Fluent API Design (`anim()` method)
- [x] Motion Planner Updates (State Persistence)
- [x] Implementation Steps (Update `ActorBuilder`, `sprint_with_camera.py`)
- [x] Add `add_audio_track` logic in `sequence_setup.py` (using `MovieSceneAudioTrack`)
- [x] Verify using a placeholder audio asset from StarterContent

## Phase 11: Audio Implementation
- [x] Design and Implement `add_audio` command in `motion_builder.py`
- [x] Implement `process_add_audio` in `motion_planner.py`
- [x] Add `add_audio_track` logic in `sequence_setup.py` (using `MovieSceneAudioTrack`)
- [x] Verify using a placeholder audio asset from StarterContent

## Phase 13: move_straight API Rename
- [x] Rename `.move()` to `.move_straight()` in `motion_builder.py`
- [x] Update `single_person.py` with new method name
- [x] Update `sprint_with_camera.py` with new method name
- [x] Verify execution of renamed scripts
- [x] Case-insensitive direction handling in `motion_math.py`

## Phase 14: Rotation Debugging & Fix
- [x] Identify missing imports in `motion_planner.py`
- [x] Fix `process_face` to use `motion_math` functions
- [x] Fix `process_move_by_distance` to use `motion_math` functions
- [x] Verify `test_turns.py` generates rotation keyframes
- [x] Verify `single_person.py` rotates correctly in Unreal

## Phase 15: Enhanced Camera Test
- [/] Update `test_turns.py` with 4 turns + 4 moves
- [ ] Implement `OverheadCam` for turn sequence
- [ ] Implement `TrackingCam` for move sequence
- [ ] Verify camera cuts in Unreal

## Phase 16: Restricting Move Direction
- [x] Remove `.direction()` from `MotionCommandBuilder` in `motion_builder.py`
- [x] Update `test_turns.py` to use explicit `face()` before moves
- [x] Verify `single_person.py` and other scripts
- [x] Verify JSON output defaults to "forward"

## Phase 17: AI-Friendly Independent Verbs & Gap Detection
- [x] Implement `TimeSpan` utility in `motion_builder.py`
- [x] Create `StayCommandBuilder` with `.for_time()`, `.till_end()`, and `.anim()`
- [x] Update `MotionCommandBuilder` to use `.for_time()` and keep velocity/acceleration
- [x] Update `ActorBuilder` with independent `move_straight()` and `stay()`
- [x] Implement "Strict Director" gap detection and `till_end` resolution in `MovieBuilder.__exit__`
- [x] Update `movies/test_turns.py` to verify the new API
- [x] Verify `wait` and `animation` commands in JSON result
