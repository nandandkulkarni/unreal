# Character Rotation Specification

## Overview

Rotation system for character facing and turning with support for cardinal directions, relative angles, and shortest-path rotation.

## Rotation Commands

### `face`

Face an absolute world direction or degree.

```json
{
    "command": "face",
    "actor": "CharacterName",
    "direction": "north",
    "offset": 15,
    "duration": 1.0
}
```

**Or with explicit degrees:**
```json
{
    "command": "face",
    "actor": "CharacterName",
    "degrees": 45,
    "duration": 1.0
}
```

### `turn_by_degree`

Turn relative to current facing.

```json
{
    "command": "turn_by_degree",
    "actor": "CharacterName",
    "degrees": 90,
    "duration": 2.0
}
```

### `turn_left`

Convenience command for left turns.

```json
{
    "command": "turn_left",
    "actor": "CharacterName",
    "degrees": 90,
    "duration": 1.5
}
```

### `turn_right`

Convenience command for right turns.

```json
{
    "command": "turn_right",
    "actor": "CharacterName",
    "degrees": 90,
    "duration": 1.5
}
```

## Direction Options

### Cardinal Directions
Same as movement system:
- `"north"`, `"south"`, `"east"`, `"west"`
- `"north_east"`, `"north_west"`, `"south_east"`, `"south_west"`

### Direction Offsets
```json
{
    "direction": "north_east",
    "offset": 15
}
```
Result: Face 60° instead of 45°

### Explicit Degrees
```json
{
    "degrees": 135
}
```

## Shortest Path Rotation

The system automatically calculates the shortest rotation path:

**Example:**
- Current yaw: 10°
- Target: 350°
- Instead of rotating 340° clockwise, rotates 20° counter-clockwise

**Implementation:**
```python
delta = (target_yaw - current_yaw) % 360
if delta > 180:
    delta -= 360
final_yaw = current_yaw + delta
```

## Duration

**Default:** 1.0 second for `face`, 2.0 seconds for `turn_by_degree`

**Custom:**
```json
{
    "duration": 0.5
}
```

Faster rotations (< 0.5s) may look unnatural.

## Rotation vs Movement

**Rotation commands:**
- Change facing direction only
- No position change
- Generate rotation keyframes

**Movement commands:**
- Can change position AND rotation
- Use `move_and_turn` for simultaneous rotation during movement

## Examples

### Face Cardinal Directions
```json
[
    {"command": "face", "actor": "Hero", "direction": "north", "duration": 0.5},
    {"command": "face", "actor": "Hero", "direction": "east", "duration": 0.5},
    {"command": "face", "actor": "Hero", "direction": "south", "duration": 0.5},
    {"command": "face", "actor": "Hero", "direction": "west", "duration": 0.5}
]
```

### Relative Turns
```json
[
    {"command": "turn_right", "actor": "Hero", "degrees": 45},
    {"command": "turn_left", "actor": "Hero", "degrees": 90},
    {"command": "turn_by_degree", "actor": "Hero", "degrees": 180}
]
```

### Precise Facing
```json
{
    "command": "face",
    "actor": "Hero",
    "direction": "north_east",
    "offset": 10,
    "duration": 1.0
}
```
Result: Face 55° (45° + 10°)

## Yaw Offset Handling

Characters may have mesh yaw offsets (e.g., -90° if mesh faces right). The system automatically applies these offsets when setting rotation keyframes.

**Example:**
- Command: `face "north"` (0°)
- Character yaw_offset: -90°
- Applied rotation: -90° (mesh now faces north)

## Keyframe Generation

Rotation commands generate:
- **Start rotation keyframe** at current yaw
- **End rotation keyframe** at target yaw
- **Frame timing** based on FPS and duration

## Implementation

**Module:** `motion_planner.py`

**Functions:**
- `process_face()` - Absolute facing
- `process_turn_by_degree()` - Relative rotation
- `process_turn_left()` - Left turn shortcut
- `process_turn_right()` - Right turn shortcut

**Helper Functions:**
- `get_cardinal_angle()` - Map direction to angle
- `get_shortest_path_yaw()` - Calculate optimal rotation
- `add_rotation_keyframe()` - Apply yaw offset

## Status

✅ **Production Ready** - Fully implemented and tested
