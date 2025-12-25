# Directional Light Implementation Walkthrough

## Summary

Successfully implemented directional light support for the motion system with intuitive cardinal directions, angle presets, and named intensity/color options. The tandem scene now runs with beautiful golden sunset lighting.

## Implementation

### 1. Created `light_setup.py` Module

New module at [motion_includes/light_setup.py](file:///C:/UnrealProjects/Coding/unreal/motion_system/motion_includes/light_setup.py) with:

**Cardinal Direction Mapping (8 directions):**
- `north`, `north_east`, `east`, `south_east`, `south`, `south_west`, `west`, `north_west`
- Maps to yaw angles: 0°, 45°, 90°, 135°, 180°, -135°, -90°, -45°

**Angle Presets (8 elevations):**
- `horizon` (-5°), `low` (-15°), `low_high` (-25°), `medium` (-45°)
- `medium_high` (-60°), `high` (-75°), `very_high` (-85°), `overhead` (-90°)

**Intensity Presets (9 levels):**
- `very_dim` (2.0) → `extreme` (18.0)
- Default: `normal` (10.0)

**Color Presets (8 options):**
- `deep_sunset`, `sunset`, `golden`, `warm_white`, `white`, `cool_white`, `overcast`, `moonlight`
- RGB values from warm orange to cool blue

**Main Function:**
```python
create_directional_light(name, from_direction, angle, 
                        direction_offset=0, angle_offset=0,
                        intensity="normal", color="white", ...)
```

### 2. Updated `motion_planner.py`

Added to [motion_planner.py](file:///C:/UnrealProjects/Coding/unreal/motion_system/motion_planner.py):

- Import: `from .motion_includes import light_setup`
- Command routing for `add_directional_light`
- New function: `process_add_directional_light(cmd, actors_info)`

**Key Design Decision:** Lights are stored in `actors_info` but NOT added to sequence (no binding) since they don't need animation tracks.

### 3. Fixed `run_scene.py`

Updated [run_scene.py](file:///C:/UnrealProjects/Coding/unreal/motion_system/run_scene.py):

- Added `light_setup` to module reload list
- Fixed binding_map to filter out actors without bindings:
  ```python
  binding_map = {name: info["binding"] for name, info in actors_info.items() if "binding" in info}
  ```

### 4. Updated Tandem Scene

Added directional light to [tandem_run_square.json](file:///C:/UnrealProjects/Coding/unreal/motion_system/movies/tandem_run_square.json):

```json
{
    "command": "add_directional_light",
    "actor": "SunLight",
    "from": "west",
    "angle": "low",
    "intensity": "moderate",
    "color": "golden",
    "atmosphere_sun": true
}
```

## Testing

### Diagnostic Script

Created [diag_directional_light.py](file:///C:/UnrealProjects/Coding/unreal/motion_system/diagnostics/diag_directional_light.py) to test light spawning:
- Deletes existing test light before creating new one
- Creates reddish sunset light (pitch=-10°, warm orange color)
- Successfully tested with `python run_diagnostic.py diagnostics\diag_directional_light.py`

### Tandem Scene Execution

Ran `python trigger_movie.py movies\tandem_run_square.json`:
- ✅ Result: `{'ReturnValue': True}`
- ✅ Two characters running synchronized square pattern
- ✅ Camera tracking Jessica
- ✅ **Golden sunset directional light** from west at low angle
- ✅ Warm golden lighting visible on characters
- ✅ Atmosphere system responding to light

## Key Features

**Intuitive Command Structure:**
```json
{
    "command": "add_directional_light",
    "actor": "SunLight",
    "from": "west",              // Cardinal direction
    "direction_offset": 0,       // Fine-tune yaw
    "angle": "low",              // Elevation preset
    "angle_offset": 0,           // Fine-tune pitch
    "intensity": "moderate",     // Named or numeric
    "color": "golden",           // Named or RGB array
    "atmosphere_sun": true
}
```

**Automatic Cleanup:**
- Lights tagged with "MotionSystemActor"
- Deleted automatically by cleanup system on each run
- No manual cleanup needed

## Files Modified

- ✅ [motion_includes/light_setup.py](file:///C:/UnrealProjects/Coding/unreal/motion_system/motion_includes/light_setup.py) - NEW
- ✅ [motion_planner.py](file:///C:/UnrealProjects/Coding/unreal/motion_system/motion_planner.py) - Added light command handler
- ✅ [run_scene.py](file:///C:/UnrealProjects/Coding/unreal/motion_system/run_scene.py) - Fixed binding_map, added reload
- ✅ [movies/tandem_run_square.json](file:///C:/UnrealProjects/Coding/unreal/motion_system/movies/tandem_run_square.json) - Added golden sunset light
- ✅ [diagnostics/diag_directional_light.py](file:///C:/UnrealProjects/Coding/unreal/motion_system/diagnostics/diag_directional_light.py) - NEW
- ✅ [run_diagnostic.py](file:///C:/UnrealProjects/Coding/unreal/motion_system/run_diagnostic.py) - NEW

## Result

The motion system now supports cinematic directional lighting with:
- 8 cardinal directions
- 8 elevation angles
- 9 intensity levels
- 8 color presets
- Optional fine-tuning with offsets

The tandem scene showcases beautiful golden sunset lighting with two characters running in synchronized patterns under warm, atmospheric lighting.

## Smart Zoom (Auto-FOV)

We implemented a cinematic feature that automatically adjusts the camera's zoom (Focal Length) to maintain a constant subject size on screen.

### How it works
- **Math**: The system calculates the distance between the camera and the target frame-by-frame.
- **Trigonometry**: It solves for the exact Field of View (FOV) needed to make a 180cm character occupy exactly 30% of the viewport height.
- **Result**: Even as runners move from 50m away to 5m away, they stay perfectly framed.

```json
/* Corner3Cam configuration */
"auto_zoom": {
    "target_occupancy": 0.3,
    "min_fov": 15,
    "max_fov": 80
}
```

### Verification Results
- **Logs**: Confirmed `706 FOV keyframes` generated and applied to `Corner3Cam`.
- **Result**: Visual consistency confirmed in Unreal Sequencer.

render_diffs(file:///C:/UnrealProjects/Coding/unreal/motion_system/motion_planner.py)

