# Unreal Cinematic Pipeline - Project Status

**Last Updated:** 2025-12-16 (Evening - Remote Spawning Discovery)  
**Commit:** e7136c3  
**Goal:** Create automated YouTube-ready cinematic videos using Unreal Engine 5.7

## 🎉 MAJOR BREAKTHROUGH: Remote Scene Creation Now Possible!

**Discovery Date:** 2025-12-16 Evening  
**Status:** ✅ **Fully validated and working**

We can now create actors and sequences **entirely remotely** via the Remote Control API!

**What works remotely:**
- ✅ **SpawnActorFromClass** - Create actors in level
- ✅ **CreateCamera** - Add camera to sequences
- ✅ **AddSpawnableFromClass** - Add spawnables to sequences
- ✅ **Full scene creation** - No need to run scripts inside Unreal!

**Test file:** `external_control/quick_spawn_test.py`  
**Documentation:** `external_control/remote_api_complete_list.md` (317 lines, 7 accessible subsystems)

**Key accessible subsystems:**
- `EditorActorSubsystem` - 23 functions (spawn, destroy, transform actors)
- `LevelSequenceEditorSubsystem` - 33 functions (add spawnables, create cameras)
- `LevelSequenceEditorBlueprintLibrary` - 63 functions (playback control)
- `MovieSceneSequenceExtensions` - 71 functions (sequence manipulation)

This changes everything - we can now automate the entire workflow remotely!

---

## 🎯 Project Objective

Create realistic cinematic sequences with character animation and camera work in Unreal Engine, controllable via external Python scripts for automation and YouTube video production.

---

## ✅ WHAT'S WORKING

### 1. Cinematic Sequence Creation (Inside Unreal)
**Script:** `create_complete_cinematic.py`  
**Status:** ✓ Fully functional  
**How to run:** Unreal Editor → Tools → Execute Python Script

**What it creates:**
- 10-second character walking animation with 5 waypoints
- Cinematic camera with orbital movement around character
- Camera depth of field effects
- Character starts at (0,0,100), walks in square path
- Camera orbits from 500 units away with smooth movement

**Technical details:**
- Uses Unreal Python API directly
- Creates Level Sequence asset: `/Game/Sequences/CharacterWalkSequence`
- Adds character to sequence as possessable
- Creates transform tracks with location/rotation keyframes
- Spawns CineCameraActor with orbital camera movement
- Camera Cut track for cinematics viewport

---

### 2. Remote Sequence Playback (From PowerShell)
**Scripts:**
- `test_sequence_playback.py` - Simple playback test
- `remote_camera_fix_and_test.py` - Automated fix, test, and verify
- `remote_cinematic_control.py` - Full remote control demo

**Status:** ✓ Fully functional via Remote Control API  
**How to run:** `python remote_camera_fix_and_test.py`

**What works:**
- Open sequences remotely via HTTP
- Start/stop/pause playback
- Lock camera cut to viewport (critical for seeing animation)
- Force sequencer updates
- Move and rotate actors remotely
- Check playback status

**Technical breakthrough:**
- Uses Remote Control Web Server (port 30010)
- HTTP PUT requests to `/remote/object/call` endpoint
- Key function: `SetLockCameraCutToViewport(true)` enables viewport animation
- No need to run Python inside Unreal - works from external scripts

---

### 3. Remote Control API Setup
**Status:** ✓ Working  
**Files:** `setup_remote_control.py` (auto-config), `DefaultEngine.ini` (manual config)

**Settings that work:**
```ini
[RemoteControl]
bDeveloperMode=True
bRemoteExecution=True
RemoteControlWebInterfacePort=30010
bEnableRemotePythonExecution=True
```

**How to start Remote Control:**
- In Unreal: Window → Developer Tools → Remote Control Web App
- Or run command: `WebControl.StartServer`
- Server runs on: http://localhost:30010

---

### 4. Video Rendering
**Status:** ✓ Working (must run inside Unreal)  
**File:** `render_sequence_to_video.py`

**How to render:**
- Run inside Unreal: Tools → Execute Python Script → `render_sequence_to_video.py`
- Opens render preview window
- Renders to: `C:\U\CinematicPipeline\Saved\VideoCaptures`
- Output format: Apple ProRes .mov (1920x1080 @ 30fps)
- File size: ~305MB for 10-second sequence

**Technical details:**
- Uses Movie Pipeline Queue API (modern UE5 method)
- Renders with cinematic quality settings
- Creates job in Movie Render Queue
- Executes via PIE (Play In Editor) executor

**Remote rendering attempts:**
- ❌ Cannot trigger render via Remote Control API
- **Files tested:**
  - `external_control/remote_render_video.py` - Tried Python execution (blocked by UE 5.7)
  - `external_control/remote_render_video_v2.py` - Step-by-step API calls (crashes server)
  - `external_control/find_movie_pipeline.py` - Found correct object paths
- **Results:**
  - ✓ Can find MoviePipelineQueueSubsystem at runtime
  - ✓ Can get queue and allocate job
  - ❌ RenderQueueWithExecutor crashes Remote Control server
  - Job requires configuration (sequence, map, settings) before render
- **Conclusion:** Remote rendering is technically possible but complex/unstable
- **Best approach:** Run `render_sequence_to_video.py` inside Unreal (current method)
- **Future option:** Create Blueprint wrapper function (see `create_render_blueprint.py`)

---

## 🔧 HOW WE MADE IT WORK

### Challenge 1: Camera Cut Track "No Object Binding specified"
**Problem:** Camera Cut track showed error, camera wouldn't work  
**Root cause:** Unreal Engine 5.7 bug with camera binding GUID assignment  

**Solution that works:**
```python
camera_binding_id = camera_cut_section.get_editor_property('camera_binding_id')
camera_binding_id.guid = camera_binding.get_id()  # THIS IS THE KEY
camera_cut_section.set_editor_property('camera_binding_id', camera_binding_id)
```

**Status:** Warning still visible in UI but playback works perfectly

---

### Challenge 2: Remote Python Script Execution Blocked
**Problem:** Tried to execute Python scripts via Remote Control API  
**Attempted:** `PythonScriptLibrary.ExecutePythonCommand()`  
**Result:** Blocked by UE 5.7 security - "Object cannot be accessed remotely"

**Attempts made:**
- Added to `ForceAllowedClasses` configuration
- Tried multiple CDO paths
- Tried `RemoteControlAllowlistedClasses`
- All configurations failed

**Workaround that works:**
- Don't execute Python scripts remotely
- Instead, call Unreal functions directly via Remote Control API
- Use `LevelSequenceEditorBlueprintLibrary` functions
- Use `K2_SetActorLocation`, `K2_SetActorRotation` for actor control

---

### Challenge 3: Sequence Plays But Character Doesn't Animate
**Problem:** Remote `Play()` returned success but viewport didn't animate  
**Root cause:** Camera Cut not locked to viewport

**Solution:**
```python
# Step 1: Open sequence
call_function(EDITOR_LIBRARY, 'OpenLevelSequence', {'LevelSequence': sequence_path})

# Step 2: Lock camera to viewport (CRITICAL!)
call_function(EDITOR_LIBRARY, 'SetLockCameraCutToViewport', {'bLock': True})

# Step 3: Force update
call_function(EDITOR_LIBRARY, 'ForceUpdate')

# Step 4: Play
call_function(EDITOR_LIBRARY, 'Play')
```

**Discovery:** Used `/remote/object/describe` to enumerate all available functions on `LevelSequenceEditorBlueprintLibrary`

---

## 📋 AVAILABLE FUNCTIONS REFERENCE

**File:** `external_control/available_sequence_functions.md`  
**Contains:** Complete list of all Remote Control callable functions discovered via enumeration

**Key functions used:**
- `OpenLevelSequence(LevelSequence)` - Open sequence in Sequencer
- `SetLockCameraCutToViewport(bLock)` - Lock viewport to camera cuts
- `ForceUpdate()` - Force evaluation and UI update
- `Play()` - Start playback
- `Pause()` - Pause playback
- `IsPlaying()` - Check playback status
- `IsCameraCutLockedToViewport()` - Check lock status

---

## 🚫 WHAT DOESN'T WORK

### 1. Remote Python Script Execution
**Status:** ❌ Blocked by UE 5.7 security  
**Impact:** Cannot execute arbitrary Python code remotely  
**Workaround:** Use Remote Control API function calls instead

### 2. ~~Creating Assets Remotely~~ ✅ NOW WORKING!
**Status:** ✅ **BREAKTHROUGH - Fully working as of 2025-12-16**  
**Discovery:** EditorActorSubsystem and LevelSequenceEditorSubsystem ARE accessible via Remote Control API  
**What works:**
- Spawn actors: `EditorActorSubsystem.SpawnActorFromClass()`
- Create cameras: `LevelSequenceEditorSubsystem.CreateCamera()`
- Add spawnables: `LevelSequenceEditorSubsystem.AddSpawnableFromClass()`
**Test file:** `external_control/quick_spawn_test.py` - All 3 tests passed!  
**Impact:** Can now create entire scenes remotely without running scripts inside Unreal

### 3. Camera Binding Warning in UI
**Status:** ⚠️ Cosmetic issue only  
**Impact:** Warning visible but doesn't affect functionality  
**Fix available:** `fix_camera_binding.py` (must run inside Unreal)

---

## 📁 FILE STRUCTURE

```
CinematicPipeline_Scripts/
├── create_complete_cinematic.py      # Main sequence creator (run in Unreal)
├── create_two_characters.py          # NEW: Two-character scene (run in Unreal)
├── render_sequence_to_video.py       # ✓ Video renderer (run in Unreal) - WORKING!
├── render_two_characters.py          # NEW: Render two-character scene
├── control_panel.py                  # NEW: 3-button UI for workflow automation
├── create_render_blueprint.py        # Instructions for remote render setup (future)
├── fix_camera_binding.py             # Fix camera binding warning (run in Unreal)
├── view_logs.py                      # View fix logs
├── setup_remote_control.py           # Auto-configure Remote Control
├── STATUS.md                         # This file
├── QUICK_FIX_INSTRUCTIONS.txt        # Quick reference
├── logs/
│   └── camera_binding_fix.log        # Fix execution logs
└── external_control/
    ├── remote_camera_fix_and_test.py # Automated fix + test (run from PowerShell)
    ├── test_sequence_playback.py     # Simple playback test
    ├── remote_cinematic_control.py   # Full demo script
    ├── quick_spawn_test.py           # NEW: Test remote actor spawning - WORKING!
    ├── enumerate_all_remote_api.py   # NEW: Complete API enumeration tool
    ├── remote_api_complete_list.md   # NEW: 317-line complete API reference
    ├── remote_render_sequence.py     # Attempt remote rendering (partial)
    ├── remote_render_video.py        # Remote render attempts (all blocked)
    ├── remote_render_video_v2.py     # Blueprint-based remote render (needs setup)
    ├── enumerate_sequence_functions.py # Function discovery tool
    └── available_sequence_functions.md # Function reference

CinematicPipeline/Saved/VideoCaptures/
└── .mov                              # ✓ 305MB rendered video (Apple ProRes)
```

---

## 🎮 HOW TO USE THE CURRENT SYSTEM

### First Time Setup

1. **Start Unreal Engine 5.7** with Film/Video template project
   - Project: `CinematicPipeline`
   - Location: `C:\U\CinematicPipeline`

2. **Enable Remote Control**
   - Window → Developer Tools → Remote Control Web App
   - Or run: `WebControl.StartServer`
   - Verify: http://localhost:30010 accessible

3. **Create Cinematic Sequence** (one-time)
   - Tools → Execute Python Script
   - Select: `C:\U\CinematicPipeline_Scripts\create_complete_cinematic.py`
   - Click Execute
   - Check: `/Game/Sequences/CharacterWalkSequence` created

### Daily Usage - Control From PowerShell

```powershell
# Navigate to scripts
cd C:\U\CinematicPipeline_Scripts\external_control

# Run automated test (opens, fixes, plays, verifies)
python remote_camera_fix_and_test.py

# Or run simple playback test
python test_sequence_playback.py
Render to Video

**In Unreal Editor:**
1. Tools → Execute Python Script
2. Select: `C:\U\CinematicPipeline_Scripts\render_sequence_to_video.py`
3. Click Execute
4. Wait for render preview window to complete
5. Video saved to: `C:\U\CinematicPipeline\Saved\VideoCaptures\.mov`
6. File size: ~305MB (Apple ProRes, 1920x1080, 30fps)

**Note:** Remote rendering trigger (via `remote_render_sequence.py`) can start playback but not actual file rendering. Use the Unreal script for video output.

---
# Or run full demo with character movement
python remote_cinematic_control.py
```

### If You Need to Restart

1. Open this file: `STATUS.md`
2. Check commit: `e7136c3`
3. Pull latest: `git pull origin master`
4. Verify Unreal Engine is running
5. Verify Remote Control server is started
6. Run: `python remote_camera_fix_and_test.py`

---

## 🔬 TECHNICAL DISCOVERIES

### BREAKTHROUGH: Remote Scene Creation (2025-12-16)

**Game-changing discovery:** EditorActorSubsystem and LevelSequenceEditorSubsystem are accessible via Remote Control API!

**What this enables:**
- Create actors remotely without running Python inside Unreal
- Add spawnables to sequences via HTTP API
- Create cameras and complete scenes externally
- Full automation from PowerShell/external scripts

**Accessible subsystems (via enumerate_all_remote_api.py):**

1. **EditorActorSubsystem** (23 functions)
   - SpawnActorFromClass - Create new actors
   - SpawnActorFromObject - Spawn from object reference
   - DestroyActor - Remove actors
   - GetAllLevelActors - List actors in level
   - SetActorTransform - Move/rotate actors
   
2. **LevelSequenceEditorSubsystem** (33 functions)
   - AddSpawnableFromClass - Add spawnable to sequence
   - AddSpawnableFromInstance - Add from existing actor
   - CreateCamera - Create cinematic camera
   - RemoveActorsFromBinding - Clean up bindings
   
3. **LevelSequenceEditorBlueprintLibrary** (63 functions)
   - Play, Pause, Stop - Playback control
   - SetLockCameraCutToViewport - Critical for viewport animation
   - GetCurrentTime, SetCurrentTime - Scrubbing
   
4. **MovieSceneSequenceExtensions** (71 functions)
   - AddTrack, RemoveTrack - Track management
   - SetPlaybackRange - Sequence duration
   - GetBindings - Get possessables/spawnables

**Example working code:**
```python
import requests

def call_function(object_path, function_name, parameters=None):
    payload = {"objectPath": object_path, "functionName": function_name}
    if parameters:
        payload["parameters"] = parameters
    return requests.put("http://localhost:30010/remote/object/call", json=payload)

# Spawn a character
result = call_function(
    "/Script/UnrealEd.Default__EditorActorSubsystem",
    "SpawnActorFromClass",
    {"ActorClass": "/Script/Engine.Character", "Location": {"X": 0, "Y": 0, "Z": 100}}
)
# Returns: {'ReturnValue': '/Game/Main.Main:PersistentLevel.Character_0'}

# Create camera in sequence
result = call_function(
    "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem",
    "CreateCamera",
    {"bSpawnable": True}
)
# Returns: Success

# Add spawnable character to sequence
result = call_function(
    "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem",
    "AddSpawnableFromClass",
    {"ClassToSpawn": "/Script/Engine.Character"}
)
# Returns: Success
```

**Validation:** All tests in `quick_spawn_test.py` passed successfully

---

### Remote Control API Patterns

**Function Call Pattern:**
```python
import requests
import json

url = "http://localhost:30010/remote/object/call"
payload = {
    "objectPath": "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
    "functionName": "Play",
    "parameters": {}  # Optional
}

response = requests.put(url, json=payload, headers={'Content-Type': 'application/json'})
```

**Property Get Pattern:**
```python
url = "http://localhost:30010/remote/object/property"
payload = {
    "objectPath": "/path/to/object",
    "propertyName": "PropertyName",
    "access": "READ_ACCESS"
}

response = requests.put(url, json=payload)
```

### Object Path Patterns

**Class Default Objects (CDO):**
- Format: `/Script/ModuleName.Default__ClassName`
- Example: `/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary`

**Asset References:**
- Format: `/Game/Path/AssetName.AssetName`
- Example: `/Game/Sequences/CharacterWalkSequence.CharacterWalkSequence`

**Level Actors:**
- Format: `/Game/MapName.MapName:PersistentLevel.ActorClass_Instance`
- Example: `/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1`

### Python API vs Remote Control API

| Capability | Python API (Unreal) | Remote Control (HTTP) |
|------------|--------------------|-----------------------|
| Create assets | ✓ | ❌ (Package/material creation still blocked) |
| Spawn actors | ✓ | ✅ **NEW! EditorActorSubsystem** |
| Create cameras | ✓ | ✅ **NEW! LevelSequenceEditorSubsystem** |
| Add spawnables | ✓ | ✅ **NEW! AddSpawnableFromClass** |
| Modify sequences | ✓ | ✅ MovieSceneSequenceExtensions |
| Control playback | ✓ | ✓ |
| Move actors | ✓ | ✓ |
| Execute Python | ✓ | ❌ |
| Run from outside | ❌ | ✓ |
| Test in PowerShell | ❌ | ✓ |

**Updated Best Practice:** Remote Control API now suitable for complete scene creation! Only use Python API for asset packaging.

---

## 📝 KNOWN ISSUES

### 1. Camera Cut Track Warning
**Issue:** "No Object Binding specified" shown in Camera Cut track  
**Impact:** Visual warning only, doesn't affect playback  
**Status:** Working despite warning  
**Fix:** Run `fix_camera_binding.py` inside Unreal (optional)

### 2. EditorLevelLibrary Deprecation
**Issue:** Warning about deprecated `get_all_level_actors()`  
**Impact:** None, still works  
**Recommended:** Update to `EditorActorUtilitiesSubsystem` in future

### 3. Unicode Escape in File Paths
**Issue:** Python interprets `\U` as Unicode escape  
**Solution:** Use forward slashes: `C:/U/path` or raw strings: `r"C:\U\path"`

---

## 🚧 WHAT'S PENDING

### High Priority
1. ~~**Remove camera binding warning**~~ - Working despite warning (cosmetic only)
2. ~~**Render to video file**~~ - ✓ DONE - 305MB .mov file working
3. ~~**Remote scene creation**~~ - ✅ DONE - EditorActorSubsystem working!
4. **Update remote_create_scene.py** - Use new spawning functions
5. **Control panel Stage 1 automation** - Enable remote scene creation button
6. **Add lighting setup** - For better YouTube video quality
7. **Add post-processing** - Color grading, bloom, etc.

### Medium Priority
1. **Remote render trigger** - Blueprint wrapper for Remote Control (setup in `create_render_blueprint.py`)
2. **Multiple camera angles** - Switch between cameras
3. **Audio integration** - Background music, sound effects
4. **Title cards / text overlays** - Opening/closing credits
5. **Two-character scene refinement** - Test with remote spawning

### Low Priority / Future
1. **Blueprint integration** - Control from Blueprint graphs
2. **Real-time parameter control** - Adjust while playing
3. **Multiple character animations** - More complex scenes
4. **Environment setup** - Lighting, props, backgrounds

---

## 🎓 KEY LEARNINGS

1. **Remote Control API is MORE powerful than we thought!** - Can spawn actors and create sequences!
2. **EditorActorSubsystem is the key** - Previously thought to be inaccessible, but it works!
3. **Comprehensive enumeration is essential** - Testing 14 subsystems revealed hidden capabilities
4. **SetLockCameraCutToViewport is critical** - Without this, viewport doesn't animate
5. **Python script execution is blocked** - Security in UE 5.7 prevents remote Python execution
6. **ForceUpdate is necessary** - Ensures UI and evaluation sync
7. **Function enumeration is valuable** - `/remote/object/describe` reveals all available functions
8. **Test from PowerShell is faster** - No need to run inside Unreal for testing
9. **Camera binding GUID must be set correctly** - Common UE 5.7 bug, specific fix required
10. **Always test assumptions** - "Not possible remotely" turned out to be "using wrong subsystem"

---

## 🔗 USEFUL REFERENCES

### Unreal Engine Documentation
- Level Sequence API: https://docs.unrealengine.com/5.7/PythonAPI/class/LevelSequence.html
- Remote Control: https://docs.unrealengine.com/5.7/remote-control-api/

### Remote Control Endpoints
- Function call: `http://localhost:30010/remote/object/call`
- Property access: `http://localhost:30010/remote/object/property`
- Object describe: `http://localhost:30010/remote/object/describe`

### Git Repository
- Remote: https://github.com/nandandkulkarni/unreal
- Latest commit: e7136c3

---

## 🆘 TROUBLESHOOTING

### Playback doesn't show animation
**Solution:** Run `python remote_camera_fix_and_test.py` - ensures camera lock is set

### Remote Control not responding
**Check:**
1. Unreal Editor is running
2. Remote Control Web Server started (Window → Developer Tools → Remote Control Web App)
3. Port 30010 not blocked by firewall
4. Test: `curl http://localhost:30010`

### Script fails with "module unreal not found"
**Issue:** Running Python script that requires Unreal API outside of Unreal  
**Solution:** Run script inside Unreal (Tools → Execute Python Script)

### Camera Cut track shows error but works
**Status:** Known cosmetic issue  
**Action:** No action needed if playback works, or run `fix_camera_binding.py` inside Unreal

---

## 📧 PROJECT INFO

**Started:** December 2025  
**Platform:** Unreal Engine 5.7 + Python 3.11.8  
**Goal:** YouTube cinematic video production  
**Status:** Core playback working, pending production features  
**Next milestone:** Add lighting and render first video

---

*This document should be updated after major changes or discoveries.*
