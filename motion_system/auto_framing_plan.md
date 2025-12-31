# Auto-Framing Implementation Plan

## Overview
Implement `frame_subject(actor, coverage)` to automatically calculate and animate focal length based on subject distance, maintaining consistent framing throughout the sequence.

## User API

```python
movie.add_camera("TrackingCam", location=(11000, 244, 200))\
     .frame_subject("Runner1", coverage=0.7)\
     .look_at("Runner1")\
     .focus_on("Runner1")\
     .add()
```

## Implementation Steps

### 1. CameraBuilder Method (motion_builder.py)
Add `frame_subject()` method:
- Stores `auto_frame` command with actor name and coverage
- Independent of `look_at()` and `focus_on()`

### 2. Focal Length Calculator (motion_planner.py)
Create utility function:
```python
def calculate_focal_length(camera_pos, subject_pos, subject_height, coverage, sensor_height=24):
    # Calculate distance
    # Apply formula: focal_length = sensor_height / (2 * tan(FOV/2))
    # Where FOV derived from: frame_height = subject_height / coverage
    return focal_length_mm
```

### 3. Adaptive Sampling Logic (motion_planner.py)
In `process_add_camera()`:
- Sample subject position at regular intervals (every 1-2 seconds)
- Calculate focal length at each sample point
- Add keyframe only if change exceeds threshold (e.g., >10%)
- Typical result: 3-5 keyframes instead of 60+

### 4. Keyframe Application (keyframe_applier.py)
Add focal length track support:
- Create focal length track on camera
- Add keyframes with calculated values
- Use smooth interpolation (cubic)

## Key Assumptions
- Subject height: 1.8m (default human)
- Sensor height: 24mm (full frame)
- Sample interval: 2 seconds
- Change threshold: 10% for keyframe addition

## Example Output
```
Frame 0:   focal_length = 935mm  (Runner at 100m)
Frame 120: focal_length = 701mm  (Runner at 75m)
Frame 240: focal_length = 467mm  (Runner at 50m)
Frame 360: focal_length = 234mm  (Runner at 25m)
Frame 480: focal_length = 47mm   (Runner at 0m)
```

## Verification
Test with `sprint_with_camera.py` - runner approaching camera should maintain consistent frame coverage.
