# Implementation Plan: Dynamic Level Creation

We will modify the movie generation workflow to ensure every recording starts in a clean, professional "Basic" level environment.

## Proposed Changes

### [Component] Motion System Workflow

#### [MODIFY] [run_scene.py](file:///c:/UnrealProjects/Coding/unreal/motion_system/run_scene.py)
- Call `level_setup.create_basic_level()` if `"create_new_level": true` is found in the JSON root.
- Ensure level is created *before* the sequence and camera setup.

#### [NEW] [level_setup.py](file:///c:/UnrealProjects/Coding/unreal/motion_system/level_setup.py)
- Implement `create_basic_level()` using `unreal.LevelEditorSubsystem.new_level_from_template()`.
- Use the verified path `/Engine/Maps/Templates/Template_Default`.

## Verification Plan

### Automated Tests
- Run `trigger_movie.py` and verify in the logs that a new level was created.

### Manual Verification
- Confirm that the Unreal Editor viewport switches to a clean "Basic" level (Floor + Sky + Light) after running a scene.
