# Character Movement Specification

## Overview

Movement system supporting cardinal directions, relative movement, and waypoint navigation with automatic speed conversion and keyframe generation.

## Movement Commands

### `move_by_distance`

Move a specified distance in a direction.

```json
{
    "command": "move_by_distance",
    "actor": "CharacterName",
    "direction": "north",
    "meters": 10,
    "speed_mph": 8,
    "offset": 15,
    "waypoint_name": "checkpoint1"
}
```

### `move_for_seconds`

Move for a specified duration.

```json
{
    "command": "move_for_seconds",
    "actor": "CharacterName",
    "direction": "east",
    "seconds": 5,
    "speed_mph": 8
}
```

### `move_to_location`

Move to absolute XYZ coordinates.

```json
{
    "command": "move_to_location",
    "actor": "CharacterName",
    "target": [1000, 500, 0],
    "speed_mph": 6
}
```

### `move_to_waypoint`

Move to a named waypoint.

```json
{
    "command": "move_to_waypoint",
    "actor": "CharacterName",
    "waypoint": "checkpoint1",
    "speed_mph": 8
}
```

### `move_and_turn`

Simultaneous movement and rotation.

```json
{
    "command": "move_and_turn",
    "actor": "CharacterName",
    "direction": "north",
    "meters": 5,
    "turn_degrees": 45,
    "speed_mph": 6
}
```

## Direction Options

### Cardinal Directions (Absolute)
- `"north"` - 0° (X+)
- `"north_east"` - 45°
- `"east"` - 90° (Y+)
- `"south_east"` - 135°
- `"south"` - 180° (X-)
- `"south_west"` - -135°
- `"west"` - -90° (Y-)
- `"north_west"` - -45°

### Relative Directions
- `"forward"` - Current facing direction
- `"backward"` - Opposite of facing
- `"left"` - 90° left of facing
- `"right"` - 90° right of facing

### Direction Offsets

Add `"offset"` parameter to adjust cardinal directions:
```json
{
    "direction": "north_east",
    "offset": 15
}
```
Result: 60° instead of 45°

## Speed Specification

### MPH (Miles Per Hour)
```json
"speed_mph": 8
```

### Meters Per Second
```json
"speed_mps": 3.5
```

**Conversion:**
- 1 mph = 44.704 cm/s
- 1 m/s = 100 cm/s

**Default:** 100 cm/s if not specified

## Waypoint System

**Create Waypoint:**
Add `waypoint_name` to any movement command:
```json
{
    "command": "move_by_distance",
    "direction": "north",
    "meters": 10,
    "speed_mph": 8,
    "waypoint_name": "start_position"
}
```

**Use Waypoint:**
```json
{
    "command": "move_to_waypoint",
    "waypoint": "start_position",
    "speed_mph": 8
}
```

## Keyframe Generation

Movement commands automatically generate:
- **Start keyframe** at current position
- **End keyframe** at destination
- **Rotation keyframe** to maintain facing direction
- **Frame timing** based on FPS and duration

## Examples

### Square Pattern
```json
[
    {"command": "move_for_seconds", "actor": "Hero", "direction": "north", "seconds": 5, "speed_mph": 8},
    {"command": "move_for_seconds", "actor": "Hero", "direction": "east", "seconds": 5, "speed_mph": 8},
    {"command": "move_for_seconds", "actor": "Hero", "direction": "south", "seconds": 5, "speed_mph": 8},
    {"command": "move_for_seconds", "actor": "Hero", "direction": "west", "seconds": 5, "speed_mph": 8}
]
```

### Waypoint Loop
```json
[
    {"command": "move_by_distance", "direction": "north", "meters": 10, "speed_mph": 6, "waypoint_name": "point_a"},
    {"command": "move_by_distance", "direction": "east", "meters": 10, "speed_mph": 6, "waypoint_name": "point_b"},
    {"command": "move_to_waypoint", "waypoint": "point_a", "speed_mph": 6}
]
```

## Implementation

**Module:** `motion_planner.py`

**Functions:**
- `process_move_by_distance()`
- `process_move_for_seconds()`
- `process_move_to_location()`
- `process_move_to_waypoint()`
- `process_move_and_turn()`

**Helper Functions:**
- `calculate_direction_vector()` - Convert direction to XY vector
- `get_speed_cm_per_sec()` - Convert speed to cm/s
- `get_cardinal_angle()` - Map direction to angle

## Status

✅ **Production Ready** - Fully implemented and tested
