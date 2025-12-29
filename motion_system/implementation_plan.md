# Motion System Builder Implementation Plan

## Goal Description
Migrate from error-prone dictionary/JSON configs to a type-safe, fluent Python Builder pattern for defining motion sequences. This will enable IDE autocompletion, compile-time checking, and smarter state tracking during sequence definition.

## Proposed Changes

### Motion System Core
#### [EXISTING] [motion_builder.py](file:///c:/UnrealProjects/coding/unreal/motion_system/motion_builder.py)
- `MovieBuilder` class already exists.
- Implements `add_actor`, `add_camera`, `for_actor`, `simultaneous` contexts.
- `build()` returns the `movie_data` dictionary.

#### [MODIFY] [motion_planner.py](file:///c:/UnrealProjects/coding/unreal/direct/motion_system/motion_planner.py)
- Update `plan_motion` to accept the `plan` list from `MovieBuilder`.


## Detailed API Design

```python
class MovieBuilder:
    def __init__(self, name: str, create_new_level: bool = True, fps: int = 30):
        pass

    def add_actor(self, name: str, location: Tuple[float, float, float]) -> 'MovieBuilder':
        pass
        
    def for_actor(self, actor_name: str) -> 'ActorBuilder':
        pass
        
    def simultaneous(self) -> 'SimultaneousContext':
        pass
        
    def build(self) -> Dict:
        """Generates the movie_data dict containing the plan"""
        pass
```

## Verification Plan

### Automated Tests
- Create `tests/test_movie_builder.py` to verify the JSON output of `MovieBuilder`.

### Manual Verification
- Create `motion_system/unreal_builder_test.py`: The script to run **inside** Unreal. It will:
    1. Import `MovieBuilder`.
    2. Build a sequence plan.
    3. Pass the plan to `motion_planner.plan_motion`.
    4. Apply keyframes using `keyframe_applier`.
- Create `motion_system/run_builder_test_remote.py`: The local runner script. It will:
    1. Use `unreal_connection` to connect to Unreal.
    2. Execute `unreal_builder_test.py` remotely.

