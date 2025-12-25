# Directional Light Command Specification

## Design Decision: Option 2 - Animated Directional Lights

Support for creating and animating directional lights with intuitive cardinal direction and angle-based positioning.

## Command Structure

### 1. Add Directional Light

```json
{
    "command": "add_directional_light",
    "actor": "SunLight",
    "from": "west",              // Cardinal direction (required)
    "direction_offset": 0,       // Optional: adjust yaw in degrees
    "angle": "low",              // Vertical angle preset (required)
    "angle_offset": 0,           // Optional: adjust pitch in degrees
    "intensity": "soft",         // Named preset or numeric value (optional, default "normal")
    "color": "golden",           // Named preset or RGB array (optional, default "white")
    "cast_shadows": true,        // Optional: default true
    "atmosphere_sun": true       // Optional: default true
}
```

### 2. Rotate Light (Animate Direction)

```json
{
    "command": "rotate_light",
    "actor": "SunLight",
    "from": "east",
    "direction_offset": 0,
    "angle": "high",
    "angle_offset": 0,
    "duration": 5.0
}
```

### 3. Light Intensity (Animate Brightness)

```json
{
    "command": "light_intensity",
    "actor": "SunLight",
    "target_intensity": "dim",  // Named preset or numeric value
    "duration": 2.0
}
```

### 4. Light Color (Animate Color)

```json
{
    "command": "light_color",
    "actor": "SunLight",
    "target_color": "sunset",  // Named preset or RGB array
    "duration": 3.0
}
```

## Cardinal Directions (`from`)

Horizontal direction where light is coming FROM:

- `"north"` → yaw = 0°
- `"north_east"` → yaw = 45°
- `"east"` → yaw = 90°
- `"south_east"` → yaw = 135°
- `"south"` → yaw = 180°
- `"south_west"` → yaw = -135°
- `"west"` → yaw = -90°
- `"north_west"` → yaw = -45°

**Optional `direction_offset`:** Adjusts yaw by specified degrees
- Example: `"from": "west", "direction_offset": 15` → yaw = -75° (slightly north of west)

## Vertical Angles (`angle`)

Elevation angle of the light (8 presets):

- `"horizon"` → pitch = -5° (grazing angle, dramatic)
- `"low"` → pitch = -15° (golden hour, warm)
- `"low_high"` → pitch = -25° (between low and medium)
- `"medium"` → pitch = -45° (balanced)
- `"medium_high"` → pitch = -60° (getting harsh)
- `"high"` → pitch = -75° (strong shadows)
- `"very_high"` → pitch = -85° (nearly overhead)
- `"overhead"` → pitch = -90° (straight down, noon)

**Optional `angle_offset`:** Adjusts pitch by specified degrees
- Example: `"angle": "low", "angle_offset": -5` → pitch = -20° (lower than "low")

## Intensity Presets (`intensity`)

Brightness levels (9 presets):

- `"very_dim"` → 2.0 (deep twilight, barely lit)
- `"dim"` → 4.0 (early twilight, soft glow)
- `"soft"` → 6.0 (overcast, gentle)
- `"moderate"` → 8.0 (light overcast, pleasant)
- `"normal"` → 10.0 (standard daylight) **[DEFAULT]**
- `"bright"` → 12.0 (clear day)
- `"very_bright"` → 14.0 (harsh midday)
- `"intense"` → 16.0 (desert sun, dramatic)
- `"extreme"` → 18.0 (maximum brightness, stylized)

**Can also use explicit numeric values:** `"intensity": 11.5`

## Color Presets (`color`)

Color temperature spectrum (8 presets):

- `"deep_sunset"` → [1.0, 0.6, 0.3] (deep orange)
- `"sunset"` → [1.0, 0.7, 0.5] (warm orange)
- `"golden"` → [1.0, 0.85, 0.7] (golden hour)
- `"warm_white"` → [1.0, 0.95, 0.9] (slightly warm)
- `"white"` → [1.0, 1.0, 1.0] (neutral) **[DEFAULT]**
- `"cool_white"` → [0.95, 0.95, 1.0] (slightly cool)
- `"overcast"` → [0.8, 0.85, 1.0] (cool blue-gray)
- `"moonlight"` → [0.6, 0.7, 1.0] (blue moonlight)

**Can also use explicit RGB arrays:** `"color": [1.0, 0.8, 0.6]`

## Implementation Notes

### Rotation Calculation

```python
# Yaw (horizontal direction)
base_yaw = get_cardinal_yaw(from_direction)
final_yaw = base_yaw + direction_offset

# Pitch (vertical angle)
base_pitch = get_angle_pitch(angle_preset)
final_pitch = base_pitch + angle_offset

# Final rotation
rotation = unreal.Rotator(pitch=final_pitch, yaw=final_yaw, roll=0)
```

### Actor Location

Location is cosmetic (directional lights are infinite). Default to `[0, 0, 1000]` for editor visibility.

Optional: Can calculate location from direction for visual consistency:
```python
location = unreal.Vector(
    x = -5000 * cos(yaw_rad),
    y = -5000 * sin(yaw_rad),
    z = 2000
)
```

## Example Usage

### Sunset Scene
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

### Noon Overhead
```json
{
    "command": "add_directional_light",
    "actor": "SunLight",
    "from": "north",
    "angle": "overhead",
    "intensity": "bright",
    "color": "white"
}
```

### Time-of-Day Animation
```json
[
    {
        "command": "add_directional_light",
        "actor": "SunLight",
        "from": "east",
        "angle": "low",
        "intensity": "soft"
    },
    {
        "command": "rotate_light",
        "actor": "SunLight",
        "from": "west",
        "angle": "low",
        "duration": 10.0
    },
    {
        "command": "light_intensity",
        "actor": "SunLight",
        "target_intensity": "very_dim",
        "duration": 10.0
    }
]
```

## Status

**Design Complete** - Ready for implementation
**Date:** 2025-12-25
