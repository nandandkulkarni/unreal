# AI-Friendly Independent Verbs & Strict Director Validation

This plan introduces specialized builders for movement and stationary states, a unified `TimeSpan` timing utility, and strict timeline validation for active characters.

## User Review Required

> [!IMPORTANT]
> **API Atomicity**: `move_straight()`, `stay()`, and `face()` are independent verbs. They cannot be chained together.
> - **Move**: `a.move_straight().by_distance(10).for_time(TimeSpan.seconds(2)).anim("Run")`
> - **Stay**: `a.stay().for_time(TimeSpan.seconds(5)).anim("Idle")` or `a.stay().till_end()`
> 
> **Strict Director Mode**: Actors with even one command MUST account for their entire timeline. If they finish early without calling `.till_end()`, the builder will throw a `MotionTimelineError`.

## Proposed Changes

### Motion System Core

#### [MODIFY] [motion_builder.py](file:///c:/UnrealProjects/coding/unreal/motion_system/motion_builder.py)
- **TimeSpan** [NEW]: Utility class for handling durations (`.seconds(s)`, `.frames(f)`).
- **ActorBuilder**:
  - `move_straight()`: Returns a `MotionCommandBuilder`.
  - `stay()`: Returns a `StayCommandBuilder`.
  - `face()`: Stays as a one-shot method but verifies command order.
- **MotionCommandBuilder**:
  - Add `.for_time(duration: TimeSpan | float)`.
  - Retain all existing movement features (velocity, acceleration, corridors).
- **StayCommandBuilder** [NEW]:
  - Methods: `.for_time(duration)`, `.till_end()`, `.anim(name)`.
- **MovieBuilder**:
  - In `__exit__`, resolve `.till_end()` and enforce the "Strict Director" rule for managed actors.

### Movie Scripts

#### [MODIFY] [movies/test_turns.py](file:///c:/UnrealProjects/coding/unreal/motion_system/movies/test_turns.py)
- Update to use the new `TimeSpan` and independent verb pattern.

## Verification Plan

### Automated Tests
- Test Gap Detection: Create a script where a managed actor ends 2s before the movie ends -> expect `MotionTimelineError`.
- Test `TimeSpan`: Verify it correctly converts frames to seconds based on movie FPS.

### Manual Verification
- Watch the "Rotation Test" in Unreal. 
- Confirm actors transition correctly between movement and stationary states with appropriate animations.
