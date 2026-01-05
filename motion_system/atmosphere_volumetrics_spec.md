# Atmosphere & Volumetrics Specification

## Overview

Control atmospheric effects and volumetric fog to add depth and realism to procedurally generated scenes.

## Commands

### 1. Add Atmosphere

Create and configure exponential height fog with volumetric settings.

```json
{
    "command": "add_atmosphere",
    "fog_density": 0.02,
    "fog_height_falloff": 0.2,
    "fog_color": "atmospheric",
    "volumetric": true,
    "volumetric_scattering": 1.0,
    "start_distance": 0
}
```

**Or with preset:**
```json
{
    "command": "add_atmosphere",
    "fog_density": "medium",
    "fog_color": "warm_haze"
}
```

### 2. Animate Fog

Animate fog properties over time.

```json
{
    "command": "animate_fog",
    "target_density": "light",
    "target_color": [0.9, 0.95, 1.0],
    "duration": 5.0
}
```

### 3. Configure Light Shafts

Enable god rays / light shafts on a directional light.

```json
{
    "command": "configure_light_shafts",
    "actor": "SunLight",
    "enable_light_shafts": true,
    "bloom_scale": 0.3,
    "bloom_threshold": 8.0,
    "occlusion_mask_darkness": 0.5
}
```

## Fog Density Presets

Brightness levels for different atmospheric conditions:

- `"clear"` → 0.005 (minimal haze, high visibility)
- `"light"` → 0.02 (subtle atmospheric depth)
- `"medium"` → 0.05 (noticeable fog, moderate visibility)
- `"heavy"` → 0.1 (thick fog, reduced visibility)
- `"dense"` → 0.2 (very thick fog, low visibility)

**Can also use explicit numeric values:** `"fog_density": 0.03`

## Fog Color Presets

Color temperature for atmospheric fog:

- `"atmospheric"` → [0.85, 0.9, 1.0] (cool blue, natural sky)
- `"warm_haze"` → [1.0, 0.95, 0.9] (warm white, sunset haze)
- `"cool_white"` → [0.95, 0.95, 1.0] (slightly cool white)
- `"pollution"` → [0.9, 0.85, 0.7] (gray-brown smog)
- `"mystical"` → [0.7, 0.8, 1.0] (deep blue, magical)
- `"forest"` → [0.8, 0.9, 0.85] (greenish tint)

**Can also use explicit RGB arrays:** `"fog_color": [0.9, 0.85, 0.8]` (values 0-1)

## Light Shaft Presets

God ray intensity presets:

- `"subtle"` → bloom_scale: 0.1 (gentle rays)
- `"cinematic"` → bloom_scale: 0.3 (visible atmospheric scattering)
- `"dramatic"` → bloom_scale: 0.6 (strong god rays)

## Parameters

### `add_atmosphere`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fog_density` | float or preset | 0.02 | Controls fog thickness |
| `fog_height_falloff` | float | 0.2 | How quickly fog density decreases with altitude |
| `fog_color` | preset or RGB | "atmospheric" | Base fog color |
| `volumetric` | bool | true | Enable volumetric fog rendering |
| `volumetric_scattering` | float | 1.0 | Scattering intensity (0-2) |
| `start_distance` | float | 0 | Distance where fog starts (cm) |
| `fog_max_opacity` | float | 1.0 | Maximum fog opacity (0-1) |

### `animate_fog`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_density` | float or preset | required | Target fog density |
| `target_color` | preset or RGB | optional | Target fog color |
| `duration` | float | required | Animation duration in seconds |

### `configure_light_shafts`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `actor` | string | required | Name of directional light actor |
| `enable_light_shafts` | bool | true | Enable/disable light shafts |
| `bloom_scale` | float or preset | 0.3 | Intensity of light shafts |
| `bloom_threshold` | float | 8.0 | Brightness threshold for bloom |
| `occlusion_mask_darkness` | float | 0.5 | Shadow darkness (0-1) |

## Extended Directional Light

The `add_directional_light` command now supports volumetric options:

```json
{
    "command": "add_directional_light",
    "actor": "SunLight",
    "from": "west",
    "angle": "low",
    "intensity": "moderate",
    "cast_volumetric_shadow": true,
    "light_shaft_occlusion": true,
    "light_shaft_bloom_scale": 0.3
}
```

**New Parameters:**
- `cast_volumetric_shadow` (bool, default: true) - Shadow in volumetric fog
- `light_shaft_occlusion` (bool, default: true) - Enable light shaft occlusion
- `light_shaft_bloom_scale` (float, default: 0.2) - God ray intensity

## Implementation Notes

### Height Falloff

Controls altitude-based density gradient:
- **0.0** = Uniform fog density at all heights
- **0.2** = Gradual falloff (realistic)
- **0.5** = Strong falloff (ground fog effect)
- **1.0** = Very steep falloff (low-lying fog)

### Volumetric Fog Performance

Volumetric fog is GPU-intensive. Best practices:
- Use sparingly in complex scenes
- Reduce `volumetric_scattering` if performance drops
- Test on target hardware

### Color Format

Colors use normalized RGB (0.0-1.0):
```json
"fog_color": [0.85, 0.9, 1.0]  // R, G, B
```

Converted internally to Unreal's `LinearColor`.

## Example Usage

### Morning Fog Dissipation
```json
{
    "name": "Morning Fog",
    "plan": [
        {
            "command": "add_atmosphere",
            "fog_density": "heavy",
            "fog_color": "atmospheric",
            "volumetric": true
        },
        {
            "command": "add_directional_light",
            "actor": "SunLight",
            "from": "east",
            "angle": "low",
            "intensity": "soft",
            "cast_volumetric_shadow": true,
            "light_shaft_bloom_scale": 0.4
        },
        {
            "command": "wait",
            "actor": "Camera",
            "seconds": 2.0
        },
        {
            "command": "animate_fog",
            "target_density": "light",
            "duration": 8.0
        }
    ]
}
```

### Mystical Forest
```json
{
    "command": "add_atmosphere",
    "fog_density": "medium",
    "fog_color": "mystical",
    "fog_height_falloff": 0.4,
    "volumetric": true,
    "volumetric_scattering": 1.5
}
```

### Cathedral God Rays
```json
[
    {
        "command": "add_atmosphere",
        "fog_density": "light",
        "fog_color": "warm_haze",
        "volumetric": true
    },
    {
        "command": "add_directional_light",
        "actor": "WindowLight",
        "from": "west",
        "angle": "medium",
        "intensity": "bright",
        "light_shaft_bloom_scale": 0.6
    }
]
```

## Keyframe Generation

**Fog animation generates:**
- Start density keyframe at current time
- End density keyframe at target time
- Start color keyframe at current time (if color specified)
- End color keyframe at target time (if color specified)

**Frame timing:** Based on FPS and duration

## Status

✅ **Specification Complete** - Ready for implementation
🚧 **Implementation In Progress**

## Related Documentation

- [directional_light_spec.md](directional_light_spec.md) - Lighting system
- [high_level_feature_spec.md](high_level_feature_spec.md) - Feature overview
- [timing_sequencing_spec.md](timing_sequencing_spec.md) - Timing system
