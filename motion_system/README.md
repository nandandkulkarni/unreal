# Motion System Builder - Quick Reference

## Core Concepts

### Terminal Constraint Methods
Movement commands use **terminal methods** that commit the move and prevent overconstrained physics:

```python
# Pick ONE constraint pattern per move:
a.move_straight().direction("North").anim("Jog_Fwd").distance_in_time(21.0, 7.0)   # → calculates speed
a.move_straight().direction("East").anim("Run").distance_at_speed(100.0, 10.0)     # → calculates time
a.move_straight().direction("South").anim("Sprint").time_at_speed(5.0, 8.0)        # → calculates distance
```

### Mandatory Direction
All `move_straight()` commands **must** specify a cardinal direction:

```python
# ✅ Correct
a.move_straight().direction("North").distance_in_time(10.0, 5.0)

# ❌ Error - missing direction
a.move_straight().distance_in_time(10.0, 5.0)
```

### Stationary Actions
Use `stay()` for actors at rest, with optional animations and `till_end()` for timeline completion:

```python
a.stay().anim("Idle").till_end()
a.stay().for_time(TimeSpan.from_seconds(5.0)).anim("Crouch")
```

### Rotations with Animations
The `face()` method supports optional turn animations:

```python
a.face("East", duration=2.0, anim="Turn_Right")
a.face("North", duration=1.0)  # No animation
```

## Complete Example

```python
from motion_builder import MovieBuilder, TimeSpan

with MovieBuilder("My Scene", fps=60) as movie:
    movie.add_actor("Hero", location=(0, 0, 0), yaw_offset=-90)
    
    with movie.for_actor("Hero") as a:
        # Turn and move
        a.face("North", duration=1.0, anim="Turn_Right")
        a.move_straight().direction("North").anim("Jog_Fwd").distance_in_time(20.0, 5.0)
        
        # Turn again and sprint
        a.face("East", duration=1.0)
        a.move_straight().direction("East").anim("Sprint").distance_at_speed(50.0, 12.0)
        
        # Stay until end
        a.stay().anim("Idle").till_end()
    
    # Camera setup
    movie.add_camera("MainCam", location=(0, -1000, 500)).add()
    with movie.for_camera("MainCam") as cam:
        cam.look_at("Hero", height_pct=0.7)
        cam.focus_on("Hero", height_pct=0.7)
        cam.stay().till_end()
    
    movie.at_time(0.0).camera_cut("MainCam")
    movie.save_to_json("dist/my_scene.json")

movie.run(to_unreal=True)
```

## Key Rules

1. **Direction is mandatory** - Every `move_straight()` must have `.direction()`
2. **One constraint per move** - Terminal methods are mutually exclusive
3. **Timeline accountability** - All managed actors must reach the end via `till_end()` or explicit timing
4. **Cardinal directions only** - Use North, South, East, West (not "forward" or "backward")

## Terminal Methods Reference

| Method | Parameters | Calculates | Use When |
|--------|-----------|------------|----------|
| `distance_in_time(m, s)` | meters, seconds | speed | You know how far and how long |
| `distance_at_speed(m, mps)` | meters, speed | time | You know distance and speed |
| `time_at_speed(s, mps)` | seconds, speed | distance | You know duration and speed |
