# Frame Capture Verification Plan

## Overview
Implement automated frame capture to visually verify camera features (auto-framing, focus, rotation) by rendering specific frames from sequences and saving them as images.

## Goals
1. Capture frames at key moments (start, middle, end)
2. Verify auto-framing (subject size in frame)
3. Verify focus and rotation tracking
4. Save images for visual inspection

## Implementation Approach

### Option 1: High-Res Screenshot (Recommended)
**Pros:** Simple, fast, works in editor
**Cons:** Requires viewport to be visible

```python
# Capture frame at specific time
unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(frame_number)
unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, "output.png")
```

### Option 2: Movie Render Queue
**Pros:** Production quality, works in background
**Cons:** Slower, more complex setup

## Proposed API

### User-Facing
```python
# In movie script
movie.verify_at_frames([0, 300, 600])  # Capture at these frames
movie.save_to_json("dist/sprint_with_camera.json")
movie.run(to_unreal=True, capture_frames=True)
```

### Implementation Components

#### 1. Frame Capture Utility (new file: `motion_includes/frame_capture.py`)
```python
def capture_frame(sequence, frame_number, output_path):
    """Capture single frame from sequence"""
    # Set time
    # Wait for render
    # Take screenshot
    # Return path
```

#### 2. Verification Points Storage
Add to JSON:
```json
{
  "verification_frames": [0, 300, 600],
  "output_dir": "dist/frames/sprint_with_camera"
}
```

#### 3. Post-Generation Capture (in `run_scene.py`)
After sequence generation:
```python
if scene_data.get("verification_frames"):
    for frame in verification_frames:
        capture_frame(sequence, frame, output_path)
```

## Verification Workflow

1. **Generate Scene** - Run motion script normally
2. **Auto-Capture** - System captures frames at specified times
3. **Save Images** - Store in `dist/frames/{movie_name}/frame_{number}.png`
4. **Visual Review** - User reviews images to verify:
   - Subject framing (70% coverage?)
   - Focus (subject sharp?)
   - Rotation (camera pointing at subject?)

## Output Structure
```
dist/
  frames/
    sprint_with_camera/
      frame_0000.png    # Start (runner far, telephoto)
      frame_0300.png    # Middle (runner closer, medium)
      frame_0600.png    # End (runner close, wide)
```

## Implementation Steps

1. Create `motion_includes/frame_capture.py` with capture utility
2. Add `verify_at_frames()` method to `MovieBuilder`
3. Update `run_scene.py` to trigger captures after generation
4. Test with `sprint_with_camera.py`

## Verification Criteria

For auto-framing test:
- **Frame 0:** Runner small (far away, ~935mm focal length)
- **Frame 300:** Runner medium (mid-distance, ~467mm)
- **Frame 600:** Runner large (close, ~47mm)
- **All frames:** Runner occupies ~70% of frame height

## Alternative: Manual Verification
If automated capture is complex, provide instructions:
```
1. Open sequence in Unreal
2. Scrub to frame 0, 300, 600
3. Take screenshots manually
4. Verify subject size
```
