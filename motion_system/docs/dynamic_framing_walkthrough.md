# Dynamic Frame Subject Switching - Walkthrough

## Feature Overview
Implemented timeline-based auto-zoom that dynamically switches between subjects, maintaining proper framing as the camera shifts focus between actors.

## Implementation

### User API
```python
with movie.for_camera("FrontCam") as cam:
    # 0-4s: Track Runner1 with auto-zoom
    cam.frame_subject("Runner1", coverage=0.7)
    cam.look_at("Runner1", height_pct=0.7)
    cam.focus_on("Runner1", height_pct=0.7)
    cam.wait(4.0)
    
    # 4-8s: Switch to Runner2
    cam.frame_subject("Runner2", coverage=0.7)
    cam.look_at("Runner2", height_pct=0.7)
    cam.focus_on("Runner2", height_pct=0.7)
    cam.wait(4.0)
```

### Architecture

**Multi-Pass Keyframe Generation:**
1. **Pass 1 (Command Processing)**: Build timeline metadata
   - `camera_wait` commands store `frame_subject_timeline` segments
   - Actor positions stored as keyframes
   
2. **Pass 2 (Focal Length Calculation)**: Generate zoom keyframes
   - For each timeline segment, calculate focal length based on active subject
   - Adaptive sampling: keyframes at switches + every 2s if >10% change
   
3. **Pass 3 (Baking)**: Apply all keyframes to Unreal sequencer

### Key Components

**[motion_builder.py](file:///c:/UnrealProjects/coding/unreal/motion_system/motion_builder.py)**
- `CameraCommandBuilder.frame_subject()`: Sets current frame subject state
- `CameraCommandBuilder.wait()`: Emits `camera_wait` with timeline metadata

**[motion_planner.py](file:///c:/UnrealProjects/coding/unreal/motion_system/motion_planner.py)**
- `process_camera_wait()`: Builds `frame_subject_timeline` from commands
- `generate_timeline_based_focal_length()`: Calculates focal length per segment

## Result
- Camera rotation switches between runners (jarring snap)
- Camera focus (DoF) switches between runners
- **Auto-zoom dynamically adjusts** to maintain 70% coverage of active subject
- Clean sequencer timeline (~15-20 keyframes instead of 600)

## Testing
Verified in [sprint_with_camera.py](file:///c:/UnrealProjects/coding/unreal/motion_system/movies/sprint_with_camera.py) with two runners switching every 4 seconds.
