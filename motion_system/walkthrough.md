# Motion System Builder Walkthrough

We have successfully implemented and verified the `MovieBuilder` class, providing a fluent Python interface for defining motion sequences in Unreal Engine.

## Changes Verified
- **JSON Parity**: Validated that `MovieBuilder` generates the same command structure as the legacy manual dictionary method.
- **Remote Execution**: Verified the workflow of defining a script locally and executing it remotely inside Unreal Engine using a runner.

## How to Use

### 1. Define your sequence
Create a python script (e.g., `my_scene.py`) that creates a plan using `MovieBuilder`:

```python
from motion_builder import MovieBuilder

def generate_my_plan():
    builder = MovieBuilder("MySequence")
    builder.add_actor("Belica", (0, 0, 0))
    
    with builder.for_actor("Belica") as belica:
        belica.animation("Jog_Fwd")
        belica.move_by_distance(meters=5, direction="forward", speed_mph=3)
        belica.wait(2.0)
        
    return builder.build()
```

### 2. Run in Unreal
Use the runner pattern to execute this logic inside Unreal:
1. Create a "runner" script (like `run_builder_test_remote.py`).
2. Use `unreal_connection.UnrealRemote` to send your script.

```python
# runner.py
from unreal_connection import UnrealRemote
unreal = UnrealRemote()
unreal.execute_python_file("path/to/my_scene.py")
```

## Verification Artifacts
- **[motion_builder.py](file:///c:/UnrealProjects/coding/unreal/motion_system/motion_builder.py)**: The core class.
- **[test_builder_json.py](file:///c:/UnrealProjects/coding/unreal/tests/test_builder_json.py)**: Verification script for JSON output.
- **[unreal_builder_test.py](file:///c:/UnrealProjects/coding/unreal/motion_system/unreal_builder_test.py)**: The in-engine test script.
- **[run_builder_test_remote.py](file:///c:/UnrealProjects/coding/unreal/motion_system/run_builder_test_remote.py)**: The remote runner utility.


### API Clarity: `move_straight` Refactor & Rotation Fix

Renamed the core movement method and fixed a critical rotation bug:

- **Refactor**: Renamed `.move()` to `.move_straight()` across all builders and removed `.direction()` from the movement chain to enforce forward-only movement.
- **Bug Fix**: Resolved a command ordering issue where immediate actions (like `face()`) were recorded before preceding fluent movements were committed.
- **Robustness**: The planner now strictly uses the centralized `motion_math.py` library, and the builder ensures strict sequential command generation.
- **Verification**: Validated with `movies/test_turns.py`, confirming a perfectly ordered sequence of turns followed by forward moves.

```python
# Before
r.move().by_distance(50)

# After
r.move_straight().by_distance(50)
```
