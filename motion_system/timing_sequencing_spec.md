# Timing & Sequencing Specification

## Overview

Timing system for controlling sequence duration, frame rates, and pauses with automatic keyframe timing and frame calculation.

## Commands

### `wait`

Pause timeline for specified duration while maintaining position and rotation.

```json
{
    "command": "wait",
    "actor": "CharacterName",
    "seconds": 2.0
}
```

**Note:** Actor name is required but actor doesn't move - this advances the timeline.

## FPS Configuration

**Scene-Level Setting:**
```json
{
    "name": "Scene Name",
    "fps": 30,
    "plan": [...]
}
```

**Supported FPS:**
- 24 fps (film standard)
- 30 fps (default, video standard)
- 60 fps (high frame rate)

**Frame Calculation:**
```
frame = time_in_seconds * fps
```

## Sequence Duration

**Automatic Calculation:**
- System calculates total frames based on all commands
- Adds 30-frame buffer at end
- Sets sequence playback range automatically

**Manual Override:**
Not currently supported - duration is always auto-calculated.

## Timeline Management

**Sequential Execution:**
- Commands execute in order
- Each command advances timeline
- Time accumulates across all commands

**Example Timeline:**
```json
[
    {"command": "animation", "actor": "Hero", "name": "Idle"},           // Frame 0
    {"command": "wait", "actor": "Hero", "seconds": 1},                  // Frames 0-30
    {"command": "move_for_seconds", "direction": "north", "seconds": 5}, // Frames 30-180
    {"command": "wait", "actor": "Hero", "seconds": 2}                   // Frames 180-240
]
```

Total duration: 8 seconds = 240 frames @ 30fps

## Keyframe Timing

**Automatic Keyframe Generation:**
- Start keyframe at command start time
- End keyframe at command end time
- Interpolation handled by Unreal sequencer

**Example:**
```json
{
    "command": "move_for_seconds",
    "direction": "north",
    "seconds": 5,
    "speed_mph": 8
}
```

Generates:
- Location keyframe at frame 0 (start position)
- Location keyframe at frame 150 (end position, 5s * 30fps)
- Rotation keyframe at frame 0 (maintain facing)

## Multi-Actor Timing

**Independent Timelines:**
Each actor has its own timeline position:

```json
[
    {"command": "move_for_seconds", "actor": "Jessica", "direction": "north", "seconds": 5},
    {"command": "move_for_seconds", "actor": "Sarah", "direction": "north", "seconds": 5}
]
```

Both actors move simultaneously from frame 0-150.

**Sequential Per-Actor:**
```json
[
    {"command": "move_for_seconds", "actor": "Jessica", "direction": "north", "seconds": 3},
    {"command": "wait", "actor": "Jessica", "seconds": 2},
    {"command": "move_for_seconds", "actor": "Jessica", "direction": "east", "seconds": 3}
]
```

Jessica's timeline: 0-90 (move), 90-150 (wait), 150-240 (move)

## Wait Command Details

**Purpose:**
- Create pauses in action
- Synchronize multi-actor sequences
- Hold position/rotation

**Keyframes Generated:**
- Location keyframe at start (current position)
- Location keyframe at end (same position)
- Rotation keyframe at start (current rotation)
- Rotation keyframe at end (same rotation)

**Example - Synchronized Start:**
```json
[
    {"command": "add_actor", "actor": "Jessica", "location": [0, 0, 0]},
    {"command": "add_actor", "actor": "Sarah", "location": [0, -300, 0]},
    {"command": "animation", "actor": "Jessica", "name": "Idle"},
    {"command": "animation", "actor": "Sarah", "name": "Idle"},
    {"command": "wait", "actor": "Jessica", "seconds": 1},
    {"command": "wait", "actor": "Sarah", "seconds": 1},
    {"command": "animation", "actor": "Jessica", "name": "Jog_Fwd"},
    {"command": "animation", "actor": "Sarah", "name": "Jog_Fwd"},
    {"command": "move_for_seconds", "actor": "Jessica", "direction": "north", "seconds": 5},
    {"command": "move_for_seconds", "actor": "Sarah", "direction": "north", "seconds": 5}
]
```

Both characters idle for 1 second, then jog north simultaneously.

## Sequence Playback

**Automatic Setup:**
- Sequence created with calculated duration
- Playback range set to total frames + buffer
- Viewport locked to camera cuts (if camera present)
- Sequence starts playing from frame 0

**Playback Control:**
- Play/pause via Unreal sequencer UI
- Scrub timeline to preview specific frames
- Loop playback for testing

## Frame Precision

**Floating Point to Integer:**
```python
frame = int(time_in_seconds * fps)
```

**Rounding:**
- Always rounds down (floor)
- Ensures consistent frame alignment

**Example @ 30fps:**
- 0.5s → frame 15
- 1.0s → frame 30
- 1.5s → frame 45
- 5.0s → frame 150

## Implementation

**Module:** `motion_planner.py`

**Function:** `process_wait(cmd, state, fps)`

**State Tracking:**
Each actor maintains:
```python
{
    "current_time": 5.0,  # Accumulated seconds
    "current_pos": {"x": 100, "y": 200, "z": 0},
    "current_rotation": {"pitch": 0, "yaw": 45, "roll": 0}
}
```

**Sequence Setup:**
- Module: `sequence_setup.py`
- Function: `create_sequence(fps, duration_seconds, test_name)`

## Examples

### Simple Pause
```json
{
    "command": "wait",
    "actor": "Hero",
    "seconds": 3
}
```

### Staggered Start
```json
[
    {"command": "move_for_seconds", "actor": "Leader", "direction": "north", "seconds": 5},
    {"command": "wait", "actor": "Follower", "seconds": 1},
    {"command": "move_for_seconds", "actor": "Follower", "direction": "north", "seconds": 5}
]
```

Leader starts immediately, Follower starts 1 second later.

## Limitations

- No reverse time travel (can't go back in timeline)
- No parallel timelines per actor (sequential only)
- No time dilation/speed control
- Wait command requires actor name (even though it doesn't affect specific actor)

## Status

✅ **Production Ready** - Fully implemented and tested
