# Multi-Pass Camera Property Generation - Implementation Plan

## Overview
Refactor camera property generation from monolithic post-processing into 5 independent, debuggable passes. Each pass generates specific camera keyframes and saves intermediate debug JSON.

## Pass Architecture

### Pass 1: Base Command Processing
- **Input**: Raw commands from `motion_plan`
- **Output**: Actor location/rotation/animation keyframes, timeline metadata
- **File**: `{scene}_1_base_command_processing.json`
- **What it does**: Parse all commands, generate actor movement, store timelines for camera properties
- **No changes needed**: Already implemented

### Pass 2: Camera Movement
- **Input**: `camera_move` commands, actor positions (from Pass 1)
- **Output**: Camera location keyframes
- **File**: `{scene}_2_camera_movement.json`
- **What it does**: Process camera movement commands (static, move, follow)
- **Function**: `generate_camera_movement(actors_info, actor_states, fps)`
- **Status**: Already handled in Pass 1, needs extraction

### Pass 3: Look-At Rotation
- **Input**: Camera location (Pass 2), subject positions (Pass 1), `look_at_timeline`
- **Output**: Camera rotation keyframes (pitch, yaw, roll)
- **File**: `{scene}_3_look_at_rotation.json`
- **What it does**: Calculate rotation angles to point camera at active subject
- **Function**: `generate_look_at_rotation(actors_info, actor_states, fps)`
- **Status**: **NEW** - needs implementation

### Pass 4: Focus Distance
- **Input**: Camera location (Pass 2), subject positions (Pass 1), `focus_timeline`
- **Output**: Focus distance keyframes (for depth-of-field)
- **File**: `{scene}_4_focus_distance.json`
- **What it does**: Calculate 3D distance to active subject for DoF
- **Function**: `generate_focus_distance(actors_info, actor_states, fps)`
- **Status**: **NEW** - needs implementation

### Pass 5: Focal Length
- **Input**: Camera location (Pass 2), subject positions (Pass 1), `frame_subject_timeline`
- **Output**: Focal length keyframes (zoom)
- **File**: `{scene}_5_focal_length.json`
- **What it does**: Calculate focal length to maintain subject coverage
- **Function**: `generate_focal_length(actors_info, actor_states, fps)` (rename existing)
- **Status**: Already implemented as `generate_timeline_based_focal_length`, needs rename

## Implementation Steps

### 1. Update `save_planning_debug` Call Sites
**File**: [motion_planner.py](file:///c:/UnrealProjects/coding/unreal/motion_system/motion_planner.py)

Replace current calls:
```python
save_planning_debug("pass_1", ...)  # After command processing
save_planning_debug("pass_2", ...)  # After post-processing
```

With new 5-pass structure:
```python
save_planning_debug("1_base_command_processing", actor_states, camera_cuts, scene_name)
# Pass 2: Camera movement (already in Pass 1, just save again)
save_planning_debug("2_camera_movement", actor_states, camera_cuts, scene_name)
# Pass 3: Look-at rotation
generate_look_at_rotation(actors_info, actor_states, fps)
save_planning_debug("3_look_at_rotation", actor_states, camera_cuts, scene_name)
# Pass 4: Focus distance
generate_focus_distance(actors_info, actor_states, fps)
save_planning_debug("4_focus_distance", actor_states, camera_cuts, scene_name)
# Pass 5: Focal length
generate_focal_length(actors_info, actor_states, fps)
save_planning_debug("5_focal_length", actor_states, camera_cuts, scene_name)
```

### 2. Implement Pass 3: Look-At Rotation
**Function**: `generate_look_at_rotation(actors_info, actor_states, fps)`

**Algorithm**:
```python
for camera_name, camera_state in actor_states.items():
    if "look_at_timeline" not in camera_state:
        continue
    
    camera_loc = actors_info[camera_name]["location"]
    rotation_keyframes = []
    
    for frame in range(max_frame):
        time = frame / fps
        # Find active subject from timeline
        active_subject = get_subject_at_time(camera_state["look_at_timeline"], time)
        
        # Get subject position at this frame
        subject_pos = get_actor_location_at_frame(actor_states[active_subject], frame)
        
        # Calculate rotation to look at subject
        pitch, yaw, roll = calculate_look_at_rotation(camera_loc, subject_pos)
        
        # Add keyframe (adaptive sampling)
        if rotation_changed_significantly(last_rotation, (pitch, yaw, roll)):
            rotation_keyframes.append({
                "frame": frame,
                "pitch": pitch,
                "yaw": yaw,
                "roll": roll
            })
    
    camera_state["keyframes"]["rotation"] = rotation_keyframes
```

### 3. Implement Pass 4: Focus Distance
**Function**: `generate_focus_distance(actors_info, actor_states, fps)`

**Algorithm**:
```python
for camera_name, camera_state in actor_states.items():
    if "focus_timeline" not in camera_state:
        continue
    
    camera_loc = actors_info[camera_name]["location"]
    focus_keyframes = []
    
    for frame in range(max_frame):
        time = frame / fps
        active_subject = get_subject_at_time(camera_state["focus_timeline"], time)
        subject_pos = get_actor_location_at_frame(actor_states[active_subject], frame)
        
        # Calculate 3D distance
        distance = sqrt((camera_loc.x - subject_pos["x"])**2 + 
                       (camera_loc.y - subject_pos["y"])**2 + 
                       (camera_loc.z - subject_pos["z"])**2)
        
        # Adaptive sampling
        if distance_changed_significantly(last_distance, distance):
            focus_keyframes.append({
                "frame": frame,
                "value": distance  # in cm
            })
    
    camera_state["keyframes"]["current_focus_distance"] = focus_keyframes
```

### 4. Rename Pass 5: Focal Length
Rename `generate_timeline_based_focal_length` → `generate_focal_length`

### 5. Build Timeline Data in Pass 1
**File**: [motion_builder.py](file:///c:/UnrealProjects/coding/unreal/motion_system/motion_builder.py)

Update `CameraCommandBuilder` to emit timeline commands:
- `look_at()` → emit `look_at_timeline` entry
- `focus_on()` → emit `focus_timeline` entry  
- `frame_subject()` → emit `frame_subject_timeline` entry (already done)

Similar to how `camera_wait` currently works.

## Timeline Data Structure

Each camera in `actor_states` will have:
```python
{
    "FrontCam": {
        "keyframes": {...},
        "look_at_timeline": [
            {"start_time": 0.0, "end_time": 4.0, "subject": "Runner1", "height_pct": 0.7},
            {"start_time": 4.0, "end_time": 8.0, "subject": "Runner2", "height_pct": 0.7}
        ],
        "focus_timeline": [
            {"start_time": 0.0, "end_time": 4.0, "subject": "Runner1", "height_pct": 0.7},
            {"start_time": 4.0, "end_time": 8.0, "subject": "Runner2", "height_pct": 0.7}
        ],
        "frame_subject_timeline": [
            {"start_time": 0.0, "end_time": 4.0, "subject": "Runner1", "coverage": 0.7},
            {"start_time": 4.0, "end_time": 8.0, "subject": "Runner2", "coverage": 0.7}
        ]
    }
}
```

## Verification Plan

1. Run `sprint_with_camera.py`
2. Verify 5 debug JSON files are created with correct naming
3. Check Pass 3 output has rotation keyframes switching at 4s, 8s
4. Check Pass 4 output has focus distance keyframes
5. Check Pass 5 output has focal length keyframes (already working)
6. Verify in Unreal that camera actually rotates and refocuses between runners

## Benefits

- ✅ **Debuggable**: Each pass has its own JSON output
- ✅ **Testable**: Can test each pass independently
- ✅ **Extensible**: Easy to add Pass 6 (aperture), Pass 7 (color), etc.
- ✅ **Clear naming**: File names show order, technical name, and purpose
- ✅ **Separation of concerns**: Each pass does one thing well

## Phase 6: Basic Audio Support

### 1. Motion Builder: `add_audio`
**Function**: `add_audio(path: str, start_time: float = 0.0, volume: float = 1.0)`
- Adds an audio command to `scene_commands`
- Path will be relative to project content or absolute

### 2. Motion Planner: `process_add_audio`
- Parses the audio command
- Passes it through to `actor_states` as a global "audio_tracks" list or similar
- No complex physics required, just timing

### 3. Sequence Setup: `add_audio_track`
- **Class**: `unreal.MovieSceneAudioTrack`
- **Logic**:
  - Add Master Audio Track to Sequence
  - Create Section (`unreal.MovieSceneAudioSection`)
  - Load Sound Wave (`unreal.load_asset(path)`)
  - Set StartFrame/EndFrame
  - Set Row Index (to layer multiple tracks)

## Phase 12: Animation Transitions
To support changing animations (e.g., Jog -> Run) mid-sequence:

### 1. Fluent API Design
Enforce "Move-First" syntax. All changes must be attached to a specific move segment.

```python
# Correct: Attach animation to the move
r.move().anim("Jog_Fwd").by_distance(10)

# Chaining (State Persists):
r.move().anim("Run_Fwd", speed=1.5).by_distance(20).speed(20)
```

### 2. Motion Builder Refactor
- Remove `.anim()` from `ActorBuilder`.
- Add `.anim()` to `MotionCommandBuilder`.
- `MotionCommandBuilder` logic:
    - On init: Copy current state (speed, anim) from Actor.
    - On `.anim()`: Update local command parameters AND update Actor's persistent state (so next move inherits it).
