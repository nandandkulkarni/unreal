# Directional Light Implementation Plan

## Overview
Add `add_directional_light` command support to the motion system with intuitive cardinal directions, angle presets, and named intensity/color options.

## Proposed Changes

### New Module: `motion_includes/light_setup.py`

Create new module for directional light creation and management.

**Functions:**
- `get_cardinal_yaw(direction)` - Map cardinal direction to yaw angle
- `get_angle_pitch(angle_preset)` - Map angle preset to pitch value
- `get_intensity_value(intensity)` - Map intensity preset to numeric value
- `get_color_value(color)` - Map color preset to RGB Color
- `create_directional_light(name, from_dir, angle, intensity, color, **kwargs)` - Main creation function

---

### Modified: `motion_planner.py`

Add handler for `add_directional_light` command.

**Changes:**
1. Import: `from .motion_includes import light_setup`
2. Add `process_add_directional_light()` function
3. Add command routing in `plan_motion()`

**Command Structure:**
```python
{
    "command": "add_directional_light",
    "actor": "SunLight",
    "from": "west",
    "direction_offset": 0,
    "angle": "low",
    "angle_offset": 0,
    "intensity": "moderate",
    "color": "golden",
    "cast_shadows": true,
    "atmosphere_sun": true
}
```

---

### Modified: `run_scene.py`

Add `light_setup` to module reload list.

---

### Modified: `tandem_run_square.json`

Add directional light command at the beginning of the plan.

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

## Verification Plan

1. Run `python trigger_movie.py movies\tandem_run_square.json`
2. Verify directional light appears in scene
3. Verify characters are lit with warm golden sunset lighting
4. Verify shadows are cast
5. Verify atmosphere/sky responds to light

## Implementation Order

1. Create `light_setup.py` with all helper functions
2. Update `motion_planner.py` with command handler
3. Update `run_scene.py` reload list
4. Add light command to `tandem_run_square.json`
5. Test execution
