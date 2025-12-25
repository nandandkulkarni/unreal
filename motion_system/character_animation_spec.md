# Character Animation Specification

## Overview

Animation system for controlling skeletal mesh animations with automatic track management and frame-based timing.

## Commands

### `animation`

Set the active animation for a skeletal mesh actor.

```json
{
    "command": "animation",
    "actor": "CharacterName",
    "name": "AnimationName"
}
```

## Animation Names

Common animation names (depends on skeletal mesh):

**Locomotion:**
- `"Idle"`
- `"Walk_Fwd"`
- `"Jog_Fwd"`
- `"Run_Fwd"`
- `"Sprint_Fwd"`

**Actions:**
- `"Jump_Start"`
- `"Jump_Loop"`
- `"Jump_End"`
- `"Crouch_Idle"`
- `"Crouch_Walk"`

**Note:** Animation names must match the skeletal mesh's animation blueprint or available animation sequences.

## Animation Tracks

**Automatic Management:**
- Previous animation automatically ends when new animation starts
- Animation sections created in sequence
- Frame-based timing synchronized with movement

**Track Structure:**
```
Animation Track:
  [Idle: frames 0-30]
  [Walk_Fwd: frames 30-150]
  [Jog_Fwd: frames 150-300]
```

## Timing

**Frame Calculation:**
- Animation starts at current timeline position
- Calculated based on FPS and accumulated time
- Synchronized with movement/rotation keyframes

**Example:**
```json
[
    {"command": "animation", "actor": "Hero", "name": "Idle"},
    {"command": "wait", "actor": "Hero", "seconds": 1},
    {"command": "animation", "actor": "Hero", "name": "Jog_Fwd"},
    {"command": "move_for_seconds", "direction": "north", "seconds": 5, "speed_mph": 8}
]
```

Timeline:
- Frame 0-30: Idle animation
- Frame 30-180: Jog_Fwd animation (during movement)

## Animation Blending

**Current Implementation:**
- Hard cuts between animations
- No automatic blending

**Future Enhancement:**
- Blend duration parameter
- Smooth transitions

## Multiple Characters

Each character has independent animation tracks:

```json
[
    {"command": "animation", "actor": "Jessica", "name": "Jog_Fwd"},
    {"command": "animation", "actor": "Sarah", "name": "Jog_Fwd"},
    {"command": "move_for_seconds", "actor": "Jessica", "direction": "north", "seconds": 5, "speed_mph": 8},
    {"command": "move_for_seconds", "actor": "Sarah", "direction": "north", "seconds": 5, "speed_mph": 8}
]
```

Both characters jog simultaneously with synchronized movement.

## Animation Finalization

**End of Sequence:**
- Open animations automatically closed at sequence end
- End frame set to final timeline position

**Manual End:**
- Start new animation to end previous one
- No explicit "stop animation" command needed

## Examples

### Basic Animation Sequence
```json
[
    {"command": "add_actor", "actor": "Hero", "location": [0, 0, 0]},
    {"command": "animation", "actor": "Hero", "name": "Idle"},
    {"command": "wait", "actor": "Hero", "seconds": 2},
    {"command": "animation", "actor": "Hero", "name": "Walk_Fwd"},
    {"command": "move_for_seconds", "actor": "Hero", "direction": "north", "seconds": 3, "speed_mph": 4}
]
```

### Synchronized Tandem Animation
```json
[
    {"command": "animation", "actor": "Jessica", "name": "Jog_Fwd"},
    {"command": "animation", "actor": "Sarah", "name": "Jog_Fwd"},
    {"command": "face", "actor": "Jessica", "direction": "north"},
    {"command": "face", "actor": "Sarah", "direction": "north"},
    {"command": "move_for_seconds", "actor": "Jessica", "direction": "north", "seconds": 5, "speed_mph": 8},
    {"command": "move_for_seconds", "actor": "Sarah", "direction": "north", "seconds": 5, "speed_mph": 8}
]
```

## Implementation

**Module:** `motion_planner.py`

**Function:** `process_animation(cmd, state, fps)`

**Process:**
1. Get current frame from timeline position
2. End previous animation (if exists) at current frame
3. Create new animation section
4. Store as "current_animation" in actor state
5. Animation continues until next animation command or sequence end

**Data Structure:**
```python
{
    "name": "Jog_Fwd",
    "start_frame": 30,
    "end_frame": 180  # Set when next animation starts or at sequence end
}
```

## Limitations

- Animation names must exist in skeletal mesh
- No animation speed control (plays at authored speed)
- No animation blending (hard cuts only)
- No sub-animation control (e.g., upper/lower body separation)

## Future Enhancements

- [ ] Animation blending with duration parameter
- [ ] Animation speed/rate control
- [ ] Animation montage support
- [ ] Layered animation (upper/lower body)
- [ ] Animation notify events

## Status

✅ **Production Ready** - Core functionality implemented and tested
⚠️ **Blending** - Not yet implemented
