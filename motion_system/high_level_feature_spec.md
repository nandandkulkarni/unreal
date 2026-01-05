# Motion System - High-Level Feature Specification

## Overview

The Motion System is a JSON-based procedural animation framework for Unreal Engine that enables creation of cinematic sequences through simple, readable commands.

## Supported Features

### 1. Character Management

**Add Characters to Scene**
- Spawn skeletal mesh actors at specified locations
- Support for custom meshes and rotations
- Automatic tagging for cleanup

**Commands:** `add_actor`

**Detailed Spec:** [character_management_spec.md](file:///C:/UnrealProjects/Coding/unreal/motion_system/character_management_spec.md)

---

### 2. Character Movement

**Cardinal Direction Movement**
- Move in 8 cardinal directions (north, south, east, west, NE, NW, SE, SW)
- Support for forward/backward/left/right relative movement
- Optional degree offsets for precise control

**Movement Types:**
- `move_by_distance` - Move specified distance
- `move_for_seconds` - Move for specified duration
- `move_to_location` - Move to absolute coordinates
- `move_to_waypoint` - Move to named waypoint
- `move_and_turn` - Simultaneous movement and rotation

**Speed Control:**
- Specify in MPH or meters/second
- Automatic conversion to Unreal units

**Detailed Spec:** [character_movement_spec.md](file:///C:/UnrealProjects/Coding/unreal/motion_system/character_movement_spec.md)

---

### 3. Character Rotation

**Rotation Commands:**
- `face` - Face absolute cardinal direction
- `turn_by_degree` - Relative rotation
- `turn_left` / `turn_right` - Convenience shortcuts
- `turn_by_direction` - Turn to face direction

**Features:**
- Shortest path rotation
- Configurable duration
- Support for pitch, yaw, roll

**Detailed Spec:** [character_rotation_spec.md](file:///C:/UnrealProjects/Coding/unreal/motion_system/character_rotation_spec.md)

---

### 4. Character Animation

**Animation Control:**
- `animation` - Set skeletal mesh animation
- Automatic animation track management
- Support for animation blending

**Detailed Spec:** [character_animation_spec.md](file:///C:/UnrealProjects/Coding/unreal/motion_system/character_animation_spec.md)

---

### 5. Camera System

**Camera Types:**
- CineCameraActor support
- Configurable FOV, aperture, focus

**Camera Commands:**
- `add_camera` - Create camera with initial placement
- `camera_move` - Animate camera position/rotation
- `camera_look_at` - Enable LookAt tracking

**Advanced Features:**
- LookAt tracking with offset
- Interpolation speed control
- Automatic camera cuts track

**Detailed Spec:** [camera_features_review.md](file:///C:/UnrealProjects/Coding/unreal/motion_system/camera_features_review.md)

---

### 6. Directional Lighting

**Lighting Control:**
- Cardinal direction positioning (8 directions)
- Elevation angle presets (8 levels: horizon → overhead)
- Named intensity presets (9 levels: very_dim → extreme)
- Named color presets (8 options: deep_sunset → moonlight)

**Commands:**
- `add_directional_light` - Create directional light
- `rotate_light` - Animate light direction
- `light_intensity` - Animate brightness
- `light_color` - Animate color

**Features:**
- Atmosphere integration
- Shadow control
- Fine-tuning with direction/angle offsets

**Detailed Spec:** [directional_light_spec.md](file:///C:/UnrealProjects/Coding/unreal/motion_system/directional_light_spec.md)

---

### 7. Atmosphere & Volumetrics

**Atmospheric Effects:**
- Exponential height fog with volumetric rendering
- God rays / light shafts
- Atmospheric scattering
- Animated fog properties

**Commands:**
- `add_atmosphere` - Create volumetric fog
- `animate_fog` - Animate fog density/color
- `configure_light_shafts` - Enable god rays on lights

**Features:**
- Density presets (clear → dense)
- Color presets (atmospheric, mystical, warm haze, etc.)
- Height falloff for ground fog effects
- Volumetric shadow support
- Light shaft bloom presets

**Detailed Spec:** [atmosphere_volumetrics_spec.md](file:///C:/UnrealProjects/Coding/unreal/motion_system/atmosphere_volumetrics_spec.md)

---

### 8. Timing & Sequencing

**Timing Commands:**
- `wait` - Pause for specified duration
- Automatic keyframe timing
- FPS-based frame calculation

**Sequence Management:**
- Automatic sequence creation
- Configurable FPS (default: 30)
- Dynamic duration calculation

**Detailed Spec:** [timing_sequencing_spec.md](file:///C:/UnrealProjects/Coding/unreal/motion_system/timing_sequencing_spec.md)

---

### 9. Scene Management

**Level Setup:**
- Optional new level creation
- Automatic cleanup of previous test actors
- Preservation of axis markers

**Waypoint System:**
- Named waypoints for reusable positions
- Waypoint-based navigation

---

## Command Structure

All commands follow a consistent JSON structure:

```json
{
    "command": "command_name",
    "actor": "ActorName",
    ...parameters...
}
```

Commands are executed sequentially in the order specified in the `plan` array.

## File Format

**Scene Definition:**
```json
{
    "name": "Scene Name",
    "create_new_level": true,
    "fps": 30,
    "plan": [
        { "command": "add_actor", ... },
        { "command": "animation", ... },
        { "command": "move_for_seconds", ... }
    ]
}
```

## Execution

**Run a scene:**
```bash
python trigger_movie.py movies/scene_name.json
```

**Run diagnostics:**
```bash
python run_diagnostic.py diagnostics/diag_script.py
```

## Project Structure

See [project_structure.md](file:///C:/UnrealProjects/Coding/unreal/motion_system/project_structure.md) for detailed module organization.

## Recent Additions

- ✅ Atmosphere & volumetrics system (2026-01-05)
- ✅ Directional lighting system (2025-12-25)
- ✅ Camera LookAt tracking
- ✅ Tandem character support
- ✅ Compact JSON formatting utility

## Status

**Production Ready:**
- Character movement and rotation
- Directional lighting
- Atmosphere and volumetrics
- Animation control
- Camera system
- Directional lighting
- Sequence generation

**In Development:**
- Additional light types (point, spot)
- Post-processing effects
- Advanced camera features
