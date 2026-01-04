# Motion Matching POC Pipeline - Implementation Plan (Updated with API Research)

## Overview

Create an end-to-end Python pipeline that runs inside Unreal Engine to:
1. **Create a Motion Matching database** for the Manny character
2. **Generate a movie sequence** with Manny performing various movements
3. **Demonstrate Motion Matching API** by having Manny dynamically match motions from the database

This pipeline will follow the existing motion system architecture (runner/script pattern) and integrate with the Motion Matching (Pose Search) system in Unreal Engine 5.

---

## User Review Required

> [!IMPORTANT]
> **Motion Matching API Availability**
> 
> Based on research, the following Unreal Python classes are available:
> - `unreal.PoseSearchSchema` - Defines matching criteria with channels
> - `unreal.PoseSearchDatabase` - Stores animation sequences
> - `unreal.AnimNode_MotionMatching` - Animation node for runtime matching
> 
> **Note**: The PoseSearch plugin is marked as "Experimental" in UE5. Ensure the following plugins are enabled:
> - Motion Trajectory
> - Pose Search

> [!WARNING]
> **Animation Requirements**
> 
> Motion Matching works best with:
> - Root motion enabled animations
> - A variety of locomotion animations (idle, walk, jog, run, turns, stops)
> - Animations from the same skeleton (Manny/UE5 Mannequin)
> 
> **Default UE5 Manny Animation Paths** (based on research):
> - Skeleton: `/Game/Characters/Mannequins/Rigs/SK_Mannequin` or similar
> - Animations: `/Game/Characters/Mannequins/Animations/Manny/` or `/Content/Characters/Mannequins/Animations/M_UE5Mannequin/`
> - Common animations: `MM_Walk_Fwd`, `MM_Run_Fwd`, `MM_Idle`, `MM_Jump_Start`, etc.

> [!CAUTION]
> **Simplified Approach**
> 
> Due to the complexity of programmatically configuring PoseSearchSchema channels and the experimental nature of the API, this implementation will use a **hybrid approach**:
> 
> 1. **Option A (Fully Automated)**: Attempt to create schema and database programmatically
> 2. **Option B (Semi-Automated)**: Reference pre-created schema/database assets if they exist
> 3. **Fallback**: Use standard animation blueprint without motion matching if PoseSearch is unavailable
> 
> The implementation will detect which approach is viable at runtime.

---

## Proposed Changes

### Motion Matching Database Setup

#### [NEW] [create_motion_database.py](file:///C:/UnrealProjects/coding/unreal/motion_system/root-motion-matching-poc/create_motion_database.py)

**Purpose**: Create and configure a Pose Search Database for Manny

**Key API Calls**:
```python
# Asset creation
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
data_asset_factory = unreal.DataAssetFactory()

# Create PoseSearchSchema
schema = asset_tools.create_asset(
    asset_name="MannyMotionSchema",
    package_path="/Game/MotionMatching",
    asset_class=unreal.PoseSearchSchema,
    factory=data_asset_factory
)

# Create PoseSearchDatabase
database = asset_tools.create_asset(
    asset_name="MannyMotionDatabase",
    package_path="/Game/MotionMatching",
    asset_class=unreal.PoseSearchDatabase,
    factory=data_asset_factory
)

# Configure database
database.set_editor_property("schema", schema)
database.set_editor_property("animation_assets", animation_list)

# Save assets
unreal.EditorAssetLibrary.save_loaded_asset(schema)
unreal.EditorAssetLibrary.save_loaded_asset(database)
```

**Key Functions**:
- `find_manny_skeleton()` - Locates Manny skeleton asset
  - Try: `/Game/Characters/Mannequins/Rigs/SK_Mannequin`
  - Fallback: Search using `unreal.EditorAssetLibrary.list_assets()`
- `find_manny_animations()` - Finds locomotion animations
  - Search paths: `/Game/Characters/Mannequins/Animations/`
  - Filter for: Walk, Run, Idle, Jump animations
- `create_pose_search_schema()` - Creates schema with default settings
- `create_pose_search_database()` - Creates database and links to schema
- `add_animations_to_database()` - Populates database with animations
  - Uses `database.animation_assets` property (Array of InstancedStruct)

**Workflow**:
1. Check if PoseSearch plugin is available
2. Find Manny skeleton and animations
3. Create PoseSearchSchema at `/Game/MotionMatching/MannyMotionSchema`
4. Create PoseSearchDatabase at `/Game/MotionMatching/MannyMotionDatabase`
5. Link database to schema
6. Add animation sequences to database
7. Save and validate assets

---

### Movie Sequence with Motion Matching

#### [NEW] [motion_matching_sequence.py](file:///C:/UnrealProjects/coding/unreal/motion_system/root-motion-matching-poc/motion_matching_sequence.py)

**Purpose**: Create a movie sequence demonstrating motion matching

**Key API Calls**:
```python
# Spawn Manny
manny = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.SkeletalMeshActor,
    location=unreal.Vector(0, 0, 0),
    rotation=unreal.Rotator(0, 0, 0)
)

# Set skeletal mesh
skeletal_mesh = unreal.load_object(None, "/Game/Characters/Mannequins/Meshes/SKM_Manny")
manny.skeletal_mesh_component.set_skinned_asset_and_update(skeletal_mesh)

# Set animation mode to use AnimBP (if motion matching AnimBP exists)
anim_bp = unreal.load_object(None, "/Game/MotionMatching/ABP_MannyMotionMatching")
if anim_bp:
    manny.skeletal_mesh_component.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
    manny.skeletal_mesh_component.set_anim_instance_class(anim_bp.generated_class())
```

**Key Functions**:
- `spawn_manny_with_motion_matching()` - Spawns Manny with MM setup
  - Uses `unreal.EditorLevelLibrary.spawn_actor_from_class()`
  - Sets skeletal mesh via `set_skinned_asset_and_update()`
  - Configures AnimBP if available
- `create_movement_keyframes()` - Generates position/velocity keyframes
  - Creates waypoint path with varying speeds
  - Calculates velocity vectors for motion matching input
- `apply_motion_matching_inputs()` - Sets AnimBP parameters per frame
  - If using AnimBP: Set velocity/direction parameters
  - If using direct animation: Fall back to animation sequences
- `setup_camera_tracking()` - Adds camera following Manny
  - Reuses existing `camera_setup.py` functions
  - Uses `look_at` and `focus_on` patterns from motion system

**Sequence Design**:
1. Spawn Manny at origin
2. Create a path with various movements:
   - Start idle (0 velocity)
   - Accelerate to walk (2 m/s)
   - Accelerate to jog (4 m/s)
   - Sharp turn left (change direction)
   - Sprint forward (8 m/s)
   - Decelerate to walk (2 m/s)
   - Turn right
   - Return to idle
3. Camera follows Manny with cinematic framing
4. Sequence duration: ~20 seconds at 60fps (1200 frames)

**Motion Matching Integration**:
- **Primary**: Use AnimBP with `unreal.AnimNode_MotionMatching`
  - Set `database` property to created PoseSearchDatabase
  - Control via velocity/direction inputs
- **Fallback**: Use direct animation sequences if MM unavailable
  - Play animations based on speed thresholds
  - Blend between animations manually

---

### Main Pipeline Script

#### [NEW] [run_motion_matching_poc.py](file:///C:/UnrealProjects/coding/unreal/motion_system/root-motion-matching-poc/run_motion_matching_poc.py)

**Purpose**: Main script executed inside Unreal Engine (the "Script")

**Key API Calls**:
```python
# Module reloading (following existing pattern)
import importlib
import sys
modules_to_reload = ["create_motion_database", "motion_matching_sequence"]
for mod in modules_to_reload:
    if mod in sys.modules:
        importlib.reload(sys.modules[mod])

# Cleanup (using existing system)
from motion_system.motion_includes import cleanup
cleanup.close_open_sequences()
cleanup.delete_old_actors()

# Sequence creation (using existing system)
from motion_system.motion_includes import sequence_setup
sequence, name, num, fps, frames = sequence_setup.create_sequence(
    fps=60, 
    duration_seconds=20, 
    test_name="MotionMatchingPOC"
)

# Open sequence
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
```

**Workflow**:
1. Import and reload all necessary modules
2. Check PoseSearch plugin availability
3. Execute database creation (if not exists)
   - Check if `/Game/MotionMatching/MannyMotionDatabase` exists
   - Create if missing
4. Cleanup old sequences/actors
5. Create new level sequence (60fps, 20 seconds)
6. Spawn Manny with motion matching setup
7. Generate movement keyframes with velocity data
8. Apply keyframes to sequence
9. Setup camera tracking
10. Play sequence and verify
11. Log results and capture verification frames

**Integration with Existing System**:
- Uses `motion_system.logger` for logging
- Uses `motion_system.motion_includes.cleanup` for cleanup
- Uses `motion_system.motion_includes.sequence_setup` for sequence creation
- Uses `motion_system.motion_includes.camera_setup` for camera
- Follows same pattern as `run_scene.py`

---

### Remote Trigger Script

#### [NEW] [trigger_motion_matching_poc.py](file:///C:/UnrealProjects/coding/unreal/motion_system/root-motion-matching-poc/trigger_motion_matching_poc.py)

**Purpose**: Trigger script to run from local machine (the "Runner")

**Key API Calls**:
```python
import requests
import os

# Read script content
script_path = os.path.join(os.path.dirname(__file__), "run_motion_matching_poc.py")
with open(script_path, 'r') as f:
    script_content = f.read()

# Send to Unreal
url = "http://localhost:30010/remote/object/call"
payload = {
    "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
    "functionName": "ExecutePythonCommand",
    "parameters": {"PythonCommand": script_content}
}

response = requests.put(url, json=payload)
```

**Functionality**:
- Reads `run_motion_matching_poc.py` content
- Sends to Unreal Engine via HTTP PUT to port 30010
- Follows same pattern as existing trigger scripts in `tests/`

---

### Documentation

#### [NEW] [README.md](file:///C:/UnrealProjects/coding/unreal/motion_system/root-motion-matching-poc/README.md)

**Contents**:
- Overview of motion matching POC
- Prerequisites:
  - Enable Motion Trajectory plugin
  - Enable Pose Search plugin
  - Verify Manny assets are available
- Usage instructions:
  - Run `python trigger_motion_matching_poc.py` from local machine
  - Or execute `run_motion_matching_poc.py` inside Unreal
- Expected results:
  - Database created at `/Game/MotionMatching/`
  - Sequence plays with Manny using motion matching
  - Camera tracks Manny smoothly
- Troubleshooting guide:
  - Plugin not found errors
  - Animation asset path issues
  - Motion matching not activating
- API reference for motion matching components

---

## Concrete API Objects and Methods

### Asset Creation
- `unreal.AssetToolsHelpers.get_asset_tools()` - Get asset tools instance
- `unreal.DataAssetFactory()` - Factory for creating DataAssets
- `asset_tools.create_asset(name, path, class, factory)` - Create new asset
- `unreal.EditorAssetLibrary.save_loaded_asset(asset)` - Save asset
- `unreal.EditorAssetLibrary.does_asset_exist(path)` - Check if asset exists
- `unreal.load_object(None, path)` - Load existing asset

### Motion Matching Classes
- `unreal.PoseSearchSchema` - Schema defining matching criteria
  - Property: `channels` (Array of PoseSearchFeatureChannel)
- `unreal.PoseSearchDatabase` - Database of animation sequences
  - Property: `schema` (PoseSearchSchema reference)
  - Property: `animation_assets` (Array of InstancedStruct)
  - Property: `pose_search_mode` (PoseSearchMode enum)
- `unreal.AnimNode_MotionMatching` - Animation node
  - Property: `database` (PoseSearchDatabase reference)
  - Property: `blend_time` (float)

### Actor Spawning
- `unreal.EditorLevelLibrary.spawn_actor_from_class(class, location, rotation)` - Spawn actor
- `unreal.SkeletalMeshActor` - Skeletal mesh actor class
- `actor.skeletal_mesh_component` - Get skeletal mesh component
- `component.set_skinned_asset_and_update(mesh)` - Set skeletal mesh
- `component.set_animation_mode(mode)` - Set animation mode
- `component.set_anim_instance_class(class)` - Set AnimBP class

### Sequence and Keyframes
- `sequence_setup.create_sequence(fps, duration_seconds, test_name)` - Create sequence
- `unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)` - Open sequence
- `sequence.add_possessable(actor)` - Add actor to sequence
- `keyframe_applier.apply_keyframes_to_actor(...)` - Apply keyframes (existing system)

### Asset Discovery
- `unreal.EditorAssetLibrary.list_assets(path, recursive=True)` - List assets in path
- `unreal.EditorAssetLibrary.find_asset_data(path)` - Find asset data
- `asset_data.get_asset()` - Get actual asset from asset data

---

## Verification Plan

### Automated Tests

1. **Plugin Availability Test**
   ```python
   # Check if PoseSearch plugin is loaded
   plugin_manager = unreal.PluginBrowserModule()
   # Verify Motion Trajectory and Pose Search plugins
   ```

2. **Database Creation Test**
   ```python
   # Verify assets exist
   schema_exists = unreal.EditorAssetLibrary.does_asset_exist(
       "/Game/MotionMatching/MannyMotionSchema"
   )
   db_exists = unreal.EditorAssetLibrary.does_asset_exist(
       "/Game/MotionMatching/MannyMotionDatabase"
   )
   # Verify database has animations loaded
   database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
   assert len(database.animation_assets) > 0
   ```

3. **Sequence Playback Test**
   ```python
   # Verify sequence plays correctly
   # - Manny spawns at correct location
   # - Sequence has expected duration
   # - Camera tracks Manny
   ```

### Manual Verification

1. **Visual Inspection**
   - Run `python trigger_motion_matching_poc.py`
   - Watch the sequence play in Unreal Editor
   - Verify Manny moves naturally
   - Check camera framing and tracking

2. **Database Inspection**
   - Open `/Game/MotionMatching/MannyMotionDatabase` in editor
   - Verify animations are listed
   - Check schema configuration

3. **Performance Check**
   - Monitor frame rate during playback
   - Check for animation glitches or pops
   - Verify motion matching search is performant

### Success Criteria

- ✅ PoseSearch plugin is available
- ✅ Database assets created successfully
- ✅ Manny spawns with correct mesh
- ✅ Sequence plays from start to finish
- ✅ Camera tracks Manny smoothly
- ✅ No errors in Unreal log
- ✅ Pipeline can be re-run multiple times
- ✅ (Bonus) Motion matching selects appropriate animations based on velocity
