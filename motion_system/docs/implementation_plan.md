# 400m Dash Choreography System - Implementation Plan

## Overview
Build a complete choreography system for a 6-runner 400m track race with waypoint chains, speed profiles, lane assignments, and staggered starts.

---

## Design Decisions

### **1. Waypoint Chain API**

**Problem:** Need to move through multiple waypoints with varying speeds

**Solution:** Add `move_through_waypoints()` method with speed profiles

```python
with movie.for_actor(RUNNER1) as r1:
    r1.move_through_waypoints(
        waypoints=[WP_START, WP_CURVE1, WP_STRAIGHT2, WP_FINISH],
        speed_profile={
            "start_speed": 0.0,      # m/s
            "acceleration": 3.0,      # m/s²
            "max_speed": 10.0,        # m/s (elite sprinter)
            "deceleration": 2.0       # m/s² (after finish)
        }
    )
```

### **2. Speed & Acceleration Handling**

**Options:**
- **A)** Calculate speed per segment
- **B)** Global speed profile with physics
- **C)** Keyframe-based speed curves

**Recommendation: Option B (Global Speed Profile)**

```python
# Physics-based calculation
def calculate_speed_at_time(t, profile):
    if t < acceleration_phase:
        return profile.start_speed + profile.acceleration * t
    elif t < cruise_phase:
        return profile.max_speed
    else:
        return max(0, profile.max_speed - profile.deceleration * (t - cruise_start))
```

### **3. Track Geometry**

**400m Standard Track:**
- 2 straights: 84.39m each
- 2 curves: 115.61m each (radius ~36.5m)
- 8 lanes: 1.22m width each

**Staggered Starts (Lane Offsets):**
```python
# Lane 1 (inside) = 0m offset
# Lane 2 = 7.04m ahead
# Lane 3 = 14.68m ahead
# Lane 4 = 22.85m ahead
# Lane 5 = 31.52m ahead
# Lane 6 = 40.70m ahead
```

---

## Proposed Changes

### 1. ActorBuilder Speed Methods

#### [MODIFY] [motion_builder.py](file:///c:/UnrealProjects/coding/unreal/motion_system/motion_builder.py)

Add speed/acceleration parameters to existing methods:

```python
def move_for_seconds(self, seconds, direction, speed_mtps=None, acceleration=None):
    """Move with optional acceleration"""
    # Calculate distance with acceleration
    if acceleration:
        distance = 0.5 * acceleration * seconds**2 + speed_mtps * seconds
    else:
        distance = speed_mtps * seconds
```

Add new waypoint chain method:

```python
def move_through_waypoints(self, waypoints: List[str], speed_profile: Dict):
    """Move through a chain of waypoints with speed profile
    
    Args:
        waypoints: List of waypoint names
        speed_profile: {
            "start_speed": float,
            "acceleration": float,
            "max_speed": float,
            "deceleration": float
        }
    """
    # Calculate total distance
    # Apply physics-based speed calculation
    # Generate move commands
```

---

### 2. 400m Race Movie Definition

#### [NEW] [movies/race_400m.py](file:///c:/UnrealProjects/coding/unreal/motion_system/movies/race_400m.py)

```python
from motion_builder import MovieBuilder

# Runner names
RUNNER1 = "Runner1"
RUNNER2 = "Runner2"
RUNNER3 = "Runner3"
RUNNER4 = "Runner4"
RUNNER5 = "Runner5"
RUNNER6 = "Runner6"

# Track waypoints (shared)
WP_START = "wp_start"
WP_CURVE1_ENTRY = "wp_curve1_entry"
WP_CURVE1_APEX = "wp_curve1_apex"
WP_CURVE1_EXIT = "wp_curve1_exit"
WP_STRAIGHT2 = "wp_straight2"
WP_CURVE2_ENTRY = "wp_curve2_entry"
WP_CURVE2_APEX = "wp_curve2_apex"
WP_CURVE2_EXIT = "wp_curve2_exit"
WP_FINISH = "wp_finish"

def define_movie():
    with MovieBuilder("400m Dash", fps=60) as movie:
        # Environment
        movie.delete_all_skylights()
        movie.add_floor("Track", location=(0,0,-0.5), scale=3000)
        movie.add_directional_light("Sun", direction_from="east", angle="high")
        
        # Track geometry (in cm)
        LANE_WIDTH = 122  # 1.22m
        STRAIGHT_LENGTH = 8439  # 84.39m
        
        # Staggered starts (in cm)
        stagger_offsets = [0, 704, 1468, 2285, 3152, 4070]
        
        # Add runners
        for i, runner in enumerate([RUNNER1, RUNNER2, RUNNER3, RUNNER4, RUNNER5, RUNNER6]):
            lane_y = i * LANE_WIDTH
            start_x = -stagger_offsets[i]
            movie.add_actor(runner, location=(start_x, lane_y, 0), yaw_offset=0)
        
        # Define track waypoints (for lane 1, others offset)
        # ... waypoint definitions ...
        
        # Race choreography
        with movie.simultaneous() as group:
            for i, runner in enumerate([RUNNER1, RUNNER2, RUNNER3, RUNNER4, RUNNER5, RUNNER6]):
                with group.for_actor(runner) as r:
                    r.animation("Sprint_Fwd")
                    r.move_through_waypoints(
                        waypoints=[WP_START, WP_CURVE1_ENTRY, WP_CURVE1_APEX, 
                                  WP_CURVE1_EXIT, WP_STRAIGHT2, WP_CURVE2_ENTRY,
                                  WP_CURVE2_APEX, WP_CURVE2_EXIT, WP_FINISH],
                        speed_profile={
                            "start_speed": 0.0,
                            "acceleration": 3.0,
                            "max_speed": 9.5 + (i * 0.1),  # Variation
                            "deceleration": 2.0
                        }
                    )
        
        # Camera cuts
        movie.add_camera("StartCam", location=(-1000, 300, 200))
        movie.add_camera("FinishCam", location=(STRAIGHT_LENGTH, 0, 200))
        
        movie.at_time(0).camera_cut("StartCam")
        movie.at_time(30).camera_cut("FinishCam")
    
    return movie.build()
```

---

## Verification Plan

### Manual Testing
1. Run `race_400m.py` in Unreal
2. Verify staggered starts
3. Check speed profiles (acceleration visible)
4. Confirm lane merging on curves
5. Verify finish line timing

### Expected Results
- 6 runners start simultaneously in staggered positions
- Acceleration phase: 0-3 seconds
- Cruise phase: 3-45 seconds
- Finish times: ~45-50 seconds (realistic for elite sprinters)
