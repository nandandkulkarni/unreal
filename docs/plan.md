# Motion Command System - Development Plan

## 🎯 What We Are Trying to Achieve

Create an intuitive, high-level motion command API for Unreal Engine that allows choreographing character movements using simple commands instead of manual keyframe calculations.

### Core Objectives:
1. **Command-Based Motion API** - Replace manual keyframe math with human-readable commands like:
   - `move_by_distance`, `move_for_seconds`, `move_to_location`
   - `turn_by_direction`, `turn_by_degree`
   - `move_and_turn` (simultaneous actions)
   - `animation`, `wait`

2. **Two-Pass Architecture** - Separate concerns for better debugging:
   - **Pass 1 (motion_planner.py)**: Motion commands → Keyframe data (pure Python, no Unreal API)
   - **Pass 2 (keyframe_applier.py)**: Keyframe data → Unreal Sequencer (Unreal API only)

3. **Multi-Actor Support** - Choreograph multiple characters simultaneously using unified timeline with `actor` field

4. **Waypoint System** - Create named positions and reference them later for complex paths

5. **Intuitive Speed Units** - Use real-world units (`speed_mph`, `speed_mps`) instead of cm/s

---

## ✅ What Has Been Done So Far

### Version 1 - Monolithic Script
- Single large file with all functionality
- Manual keyframe calculations throughout
- **Problem**: Hard to maintain and debug

### Version 2 - Modular System ✓ WORKING
**File**: `unreal_setup_complete_belica_scene_updated_v2.py`

**Achievements**:
- ✓ Successfully refactored into 8 modules in `imports/` folder:
  - `logger.py`, `cleanup.py`, `sequence_setup.py`, `camera_setup.py`
  - `mannequin_setup.py`, `hud_setup.py`, `visual_aids.py`
- ✓ **Camera Look-at Tracking** working perfectly using `CameraLookatTrackingSettings`
  - Key discovery: `lookat_tracking_settings` is property on `CineCameraActor` (not component)
  - Found via `enumerate_all_api_properties.py` → `api_reference.txt`
- ✓ Camera positioned at (-500, 0, 400) behind mannequin
- ✓ Mannequin at ground level (Z: 6.882729)
- ✓ Multi-animation support (Jog_Fwd, Jog_Left_Start)
- ✓ Manual keyframe system functional

**Status**: V2 is production-ready and working

### Version 3 - Motion Command System ✓ COMPLETE & PRODUCTION-READY

**Modules Created**:
1. **motion_system/motion_planner.py** ✓ COMPLETE
   - Converts high-level commands to keyframe data
   - 10+ command processing functions
   - State tracking (position, rotation, time)
   - Waypoint management
   - Speed conversions (mph/mps → cm/s)
   - Sequential command chaining logic

2. **motion_system/keyframe_applier.py** ✓ COMPLETE
   - Applies keyframe data to Unreal Sequencer API
   - Transform keyframe application (Location X/Y/Z, Rotation Yaw)
   - Animation section management

3. **motion_system/sequence_setup.py** ✓ COMPLETE
   - Creates Level Sequences with test names
   - Format: TestSequence_{TestName}_{timestamp}_{number}
   - Configurable FPS and duration

4. **motion_system/cleanup.py** ✓ COMPLETE
   - Deletes old test actors and sequences
   - Preserves axis markers (Axis_ and Origin_ actors)
   - Optional sequence preservation via keep_sequence flag

5. **motion_system/axis_markers.py** ✓ COMPLETE
   - Creates permanent visual reference at world origin
   - 4 colored segments: Red (+X), Yellow (-X), Blue (+Y), Purple (-Y)
   - 200cm length, 2cm width, 1mm thickness

6. **tests/test_motion_system.py** ✓ COMPLETE
   - Core testing framework class
   - Position assertion (1cm tolerance)
   - Rotation assertion (0.5° tolerance)
   - Duration assertion (100ms tolerance)
   - Expected state calculator (uses motion_planner)
   - Actual state reader (from Unreal sequence keyframes)

7. **tests/run_integrated_test.py** ✓ COMPLETE & ALL TESTS PASSING
   - All-in-one test runner
   - 6 automated test cases (all passing)
   - Creates sequences with descriptive names
   - keep_sequence flag to preserve specific tests
   - Comprehensive pass/fail reporting
   - Axis markers created at test suite start

8. **external_control/render_test_sequence.py** ✓ COMPLETE
   - Movie Render Queue integration
   - Remote Control API execution
   - Configures PNG sequence output (1920x1080, 30fps)
   - Automatic sequence detection

**Command Types Implemented**:
- ✓ `move_by_distance` - Move N meters in direction (forward/backward/left/right)
- ✓ `move_for_seconds` - Move for N seconds at speed
- ✓ `move_to_location` - Move to absolute XYZ
- ✓ `move_to_waypoint` - Move to named waypoint
- ✓ `move_and_turn` - Simultaneous movement + rotation
- ✓ `turn_by_direction` - Turn to compass direction (north/south/east/west)
- ✓ `turn_by_degree` - Turn relative degrees
- ✓ `animation` - Set active animation
- ✓ `wait` - Pause for seconds

**Example Motion Plan**:
```python
motion_plan = [
    {"actor": "belica", "command": "animation", "name": "Jog_Fwd"},
    {"actor": "belica", "command": "move_by_distance", "direction": "forward", "meters": 5, "speed_mph": 3, "waypoint_name": "point_A"},
    {"actor": "belica", "command": "wait", "seconds": 1},
    {"actor": "belica", "command": "animation", "name": "Jog_Left_Start"},
    {"actor": "belica", "command": "move_and_turn", "direction": "left", "meters": 3, "turn_degrees": 90, "speed_mph": 2, "turn_speed_deg_per_sec": 45},
    {"actor": "belica", "command": "animation", "name": "Jog_Fwd"},
    {"actor": "belica", "command": "move_for_seconds", "direction": "forward", "seconds": 3, "speed_mph": 2},
]
```

**Test Cases** (All Passing ✓):
```python
# 6 automated test cases in run_integrated_test.py:
1. Simple Forward - 5m forward movement ✓
2. Turn and Move - 90° turn then 3m forward ✓
3. Move to Location - Absolute position (500, 500, 6.88) ✓
4. Waypoint Test - Move 5m, turn 180°, return to waypoint ✓
5. Complex Path - Square pattern (4x3m sides with 90° turns) ✓
6. Square Path Return - 5m×5m square, returns to origin (0,0) ✓ [keep_sequence=True]
```

**Test Results**:
- All tests passing with exact accuracy
- Position tolerance: 1cm (achieved: <0.01cm error)
- Rotation tolerance: 0.5° (achieved: exact matches)
- Timing tolerance: 100ms (achieved: exact frame counts)
- Square Path Return: Final position (0.00, 0.00, 6.88) - perfect return to start

**Sequence Preservation**:
- Sequences named with test names: TestSequence_{TestName}_{timestamp}_{number}
- Optional keep_sequence flag preserves specific tests from cleanup
- Axis markers persist across test runs for visual reference

---

## 🔧 Technical Details

### API Discoveries
- **Camera Look-at Property**: `CineCameraActor.lookat_tracking_settings` (line 31 in api_reference.txt)
- **Actor vs Binding**: `actor_to_track` requires actual `Actor` object, not `MovieSceneBindingProxy`
- **Get Actors**: Use `EditorLevelLibrary.get_all_level_actors()` or direct actor references

### Speed Conversions
```python
speed_mph * 44.704 = cm/s
speed_mps * 100 = cm/s
```

### Frame Calculations
```python
frame = int(seconds * fps)
frame_number = unreal.FrameNumber(frame)
```

### Direction Vectors (Relative to Yaw Rotation)
- Forward: cos(yaw), sin(yaw)
- Backward: -cos(yaw), -sin(yaw)
- Left: -sin(yaw), cos(yaw)
- Right: sin(yaw), -cos(yaw)

### Sequential Chaining Logic
Each command starts when previous ends:
```python
current_time = 0
for command in motion_plan:
    start_time = current_time
    duration = calculate_duration(command)
    e✓ Testing framework created (test_motion_system.py)
   - ✓ Automated test suite created (run_motion_tests.py)
   - Run `run_motion_tests.py` in Unreal to execute all tests
   - Or run `belica_scene_v3_motion_commands.py` for full demo
    current_time = end_time
```

---

## 📋 Next Steps

### Immediate (Phase 1)
1. **TEST V3 SYSTEM** 🔥 PRIORITY
   - Run `belica_scene_v3_motion_commands.py` in Unreal
   - Verify Pass 1 output (motion commands → keyframe data)
   - Verify Pass 2 application (keyframe data → Unreal tracks)
   - Check logs for errors

2. **Debug Issues**
   - Fix any import errors
   - Verify direction vector calculations
   - Test waypoint creation/reuse
   - Validate turn commands update rotation correctly
   - Check animation sections don't overlap

3. **Validate Core Features**
   - Sequential chaining works correctly
   - Speed conversions accurate
   - Camera look-at tracking persists
   - Multi-command sequences execute smoothly

### Short-term (Phase 2)
4. **Test Each Command Type**
   - Create test motion plan for each command
   - Validate edge cases (zero distance, zero duration, etc.)
   - Test Z-axis support in move commands
   - Test all compass directions

5. **Multi-Actor Choreography**
   - Add second actor to motion plan
   - Test simultaneous movements
   - Verify actor isolation (no cross-contamination)

6. **Waypoint System Testing**
   - Create waypoint in first command
   - Reference in later command
   - Test waypoint reuse multiple times
   - Test undefined waypoint error handling

### Medium-term (Phase 3)
7. **Advanced Features** (if needed)
   - Easing/interpolation options for smoother motion
   - Camera movement commands (dolly, pan, orbit)
   - Path following (spline-based movement)
   - Simultaneous multi-action support beyond move_and_turn

8. **Error Handling & Validation**
   - Command validation before processing
   - Better error messages for invalid commands
   - Speed limit warnings
   - Collision detection warnings

9. **Performance Optimization**
   - Keyframe reduction (remove redundant keyframes)
   - Batch track operations
   - Optimize channel access

### Long-term (Phase 4)
10. **Advanced Choreography**
    - Formation movement (group actors)
    - Relative positioning (move_relative_to_actor)
    - Event triggers (on_reach_waypoint callbacks)
    - Timeline branching (conditional movements)

11. **Tools & Utilities**
    - Motion plan validator
    - Motion plan visualizer (preview without Unreal)
    - Motion plan converter (import from motion capture data)
    - Command library (common movement patterns)

---

## 🐛 Known Issues & Workarounds

### Issue 1: Binding vs Actor Object Types
**Problem**: Some APIs require `MovieSceneBindingProxy`, others require `Actor`
**Solution**: Keep both references in actors_info dict
```python
actors_info = {
    "belica": {
        "actor": mannequin,        # Actor object
        "binding": mannequin_binding  # Binding proxy
    }
}
```

### Issue 2: Look-at Property Not Found
**Problem**: Property name variations across Unreal versions
**Solution**: Use API enumeration tool to find exact property name
- Run: `enumerate_all_api_properties.py`
- Check: `api_reference.txt` for property locations

### Issue 3: Transform Section Not Updating
**Problem**: Keyframes added but viewport not showing changes
**Solution**: 
1. Call `LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()`
2. Use `set_current_time(0)` before playing
3. Enable camera cut lock: `set_lock_camera_cut_to_viewport(True)`

---

## 📁 File Structure
 (full demo)
├── run_motion_tests.py                   # Automated test suite (5 tests)
├── test_motion_system.py                 # Testing framework core
```
unreal/direct/
├── belica_scene_v3_motion_commands.py    # V3 main script
├── unreal_setup_complete_belica_scene_updated_v2.py  # V2 working version
├── api_reference.txt                     # API documentation
├── enumerate_all_api_properties.py       # API discovery tool
└── plan.md                              # This file

unreal/motion_system/                     # Shared modules
├── motion_planner.py                     # Pass 1: Commands → Keyframes
├── keyframe_applier.py                   # Pass 2: Keyframes → Unreal
├── logger.py
├── cleanup.py
├── sequence_setup.py
├── camera_setup.py
├── mannequin_setup.py
├── hud_setup.py
└── visual_aids.py
```

---

## 🎬 Usage Example

```python
# Define motion plan
motion_plan = [
    {"actor": "hero", "command": "animation", "name": "Walk_Fwd"},
    {"actor": "hero", "command": "move_by_distance", "direction": "forward", 
     "meters": 10, "speed_mph": 5, "waypoint_name": "start_point"},
    {"actor": "hero", "command": "turn_by_degree", "degrees": 90},
    {"actor": "hero", "command": "wait", "seconds": 2},
    {"actor": "hero", "command": "animation", "name": "Run_Fwd"},
    {"actor": "hero", "command": "move_to_waypoint", "waypoint": "start_point", 
     "speed_mph": 10},
]

# Execute (two-pass system handles the rest)
keyframe_data = motion_planner.plan_motion(motion_plan, actors_info, fps)
keyframe_applier.apply_keyframes_to_actor(...)
```

---

## 🔍 Debug Checklist

When things don't work:

1. **Check Logs**
   - Look for error messages in Unreal output log
   - Check custom logger output

2. **Verify API Changes**
   - Re-run `enumerate_all_api_properties.py`
   - Compare with cached `api_reference.txt`

3. **Inspect Sequencer**
   - Open sequence in Unreal editor
   - Check tracks exist (Transform, Animation)
   - Verify keyframes present on timeline
   - Check channel values (Location X/Y/Z, Rotation Yaw)

4. **Test Incrementally**
   - Start with single command
   - Add commands one at a time
   - Identify which command breaks

5. **Validate State**
   - Print keyframe_data after Pass 1
   - Verify position/rotation calculations
   - Check frame number conversions

---

## 💡 Key Insights

1. **Two-Pass Separation is Critical**
   - Allows inspection of intermediate keyframe data
   - Makes debugging much easier
   - Enables alternative output formats (JSON export, visualization)

2. **Sequential Chaining Simplifies UX**
   - No need to calculate absolute times
   - More intuitive than explicit start_time
   - Easier to insert/reorder commands

3. **Real-World Units Matter**
   - mph/mps more intuitive than cm/s
   - Meters easier than centimeters
   - Degrees clearer than radians

4. **Waypoints Enable Complex Patterns**
   - Return to start
   - Figure-8 patterns
   - Multi-actor rendezvous points

5. **Actor Field Enables Choreography**
   - Single unified timeline
   🧪 Testing Framework

### Test Architecture
```
Motion Plan → [Expected Calculator] → Expected Final State → [SQLite DB]
                                             ↓
Motion Plan → [Unreal Execution] → Actual Keyframes → [SQLite DB]
                                             ↓
                                      [Comparison]
                                             ↓
                                   Pass/Fail Report (✓/✗)
                                             ↓
                                      [Database Analysis]
```

### Database Schema
- **test_runs** - Test suite executions with timestamps
- **tests** - Individual test cases with start position/rotation
- **commands** - Motion commands with parameters (JSON)
- **keyframes_expected** - Pass 1 output (motion_planner)
- **keyframes_actual** - Pass 2 read from Unreal sequence
- **assertions** - Test results (position, rotation, duration)
- **waypoints** - Named positions created during tests

### Assertions
- **Position Tolerance**: 1 cm (catches position errors)
- **Rotation Tolerance**: 0.5° (catches rotation drift)
- **Duration Tolerance**: 100ms (catches timing errors)

### Analysis Queries
```python with SQLite logging
exec(open(r'C:\UnrealProjects\Coding\unreal\direct\run_motion_tests.py').read())

# After tests, analyze results interactively
exec(open(r'C:\UnrealProjects\Coding\unreal\direct\query_debug_db.py').read())

# Or query programmatically
from motion_system.debug_db import get_debug_db
db = get_debug_db()
db.get_test_summary()
db.find_error_source(tolerance_cm=1.0

# Compare Pass 1 vs Pass 2 (conversion issues)
db.compare_pass1_pass2(tolerance=0.1)

# Detect regressions vs baseline
db.get_regression_analysis(baseline_run_id=1)

# Validate speed calculations
db.calculate_actual_speed(command_id=5)
```

### Test Cases
1. **Simple Forward Movement** - Validates basic linear motion
2. **Turn and Move** - Validates rotation then movement
3.Run full demo with camera tracking
exec(open(r'C:\UnrealProjects\Coding\unreal\direct\belica_scene_v3_motion_commands.py').read())

# Run automated test suite (recommended first)
exec(open(r'C:\UnrealProjects\Coding\unreal\direct\run_motion_test
5. **Complex Path** - Validates square pattern (accumulation errors)

### Running Tests
```python
# Run full test suite (all 5 tests)
exec(open(r'C:\UnrealProjects\Coding\unreal\direct\run_motion_tests.py').read())

# Run single test manually
from test_motion_system import run_test
run_test(motion_plan, sequence, actor_binding, start_position, start_rotation)
```

---

## 🚀 Success Criteria

V3 system is ready for production when:+ SQLite Database Complete  
**Next Action**: Run `run_motion_tests.py` to validate all 5 test cases  
**Files Ready**: 
- ✓ belica_scene_v3_motion_commands.py (full demo)
- ✓ run_motion_tests.py (automated tests with DB)
- ✓ test_motion_system.py (test framework)
- ✓ debug_db.py (SQLite integration)
- ✓ query_debug_db.py (interactive analysis)
- ✓ motion_planner.py (Pass 1)
- ✓ keyframe_applier.py (Pass 2)

**Database Benefits**:
- 🎯 Pinpoint exact command that introduced error
- 📊 Pattern detection across multiple test runs
- 🔍 Pass 1 vs Pass 2 validation (data flow integrity)
- 📈 Historical regression tracking
- 🏃 Speed calculation verification
- 👥 Multi-actor coordination analysis (future
- ✓ belica_scene_v3_motion_commands.py (full demo)
- ✓ run_motion_tests.py (automated tests)
- ✓ test_motion_system.py (test framework)
- ✓ motion_planner.py (Pass 1)
- ✓ keyframe_applier.py (Pass 2)
- ✅ Speed conversions yield expected movement distances
- ✅ Waypoints can be created and referenced
- ✅ Multi-actor support works (2+ actors simultaneously)
- ✅ Camera look-at tracking follows moving actors
- ✅ Animations change at correct times
- ✅ Turn commands update rotation correctly
- ✅ Direction vectors (forward/left/etc) relative to current yaw
- ✅ Logs provide clear visibility into execution
- ✅ Final positions match expected within toleranceneously)
- ✅ Camera look-at tracking follows moving actors
- ✅ Animations change at correct times
- ✅ Turn commands update rotation correctly
- ✅ Direction vectors (forward/left/etc) relative to current yaw
- ✅ Logs provide clear visibility into execution

---

## 📞 Quick Reference

### Run V3 System
```python
# In Unreal Python console or external_control
exec(open(r'C:\UnrealProjects\Coding\unreal\direct\belica_scene_v3_motion_commands.py').read())
```

### Check API Properties
```python
# Find property on object
for prop in dir(my_object):
    if 'lookat' in prop.lower():
        print(prop)
```

### Force Refresh Sequence
```python
unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
```

---

**Last Updated**: December 23, 2025  
**Status**: V3 Implementation Complete - Ready for Testing  
**Next Action**: Execute belica_scene_v3_motion_commands.py in Unreal Engine
