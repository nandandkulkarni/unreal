# Unreal Cinematic Pipeline - Project Status

**Last Updated:** 2025-12-16  
**Commit:** e7136c3  
**Goal:** Create automated YouTube-ready cinematic videos using Unreal Engine 5.7

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
**Configuration:** `DefaultEngine.ini`  
**Status:** ✓ Working

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

### 2. Creating Assets Remotely
**Status:** ❌ Not possible via Remote Control API  
**Impact:** Must create sequences inside Unreal first  
**Workaround:** Run `create_complete_cinematic.py` inside Unreal once

### 3. Camera Binding Warning in UI
**Status:** ⚠️ Cosmetic issue only  
**Impact:** Warning visible but doesn't affect functionality  
**Fix available:** `fix_camera_binding.py` (must run inside Unreal)

---

## 📁 FILE STRUCTURE

```
CinematicPipeline_Scripts/
├── create_complete_cinematic.py      # Main sequence creator (run in Unreal)
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
    ├── enumerate_sequence_functions.py # Function discovery tool
    └── available_sequence_functions.md # Function reference
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
| Create assets | ✓ | ❌ |
| Modify sequences | ✓ | ⚠️ Limited |
| Control playback | ✓ | ✓ |
| Move actors | ✓ | ✓ |
| Execute Python | ✓ | ❌ |
| Run from outside | ❌ | ✓ |
| Test in PowerShell | ❌ | ✓ |

**Best Practice:** Use Python API for creation, Remote Control API for playback/control

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
1. **Remove camera binding warning** - Fix GUID assignment properly
2. **Add lighting setup** - For YouTube video quality
3. **Add post-processing** - Color grading, bloom, etc.
4. **Render to video file** - Export as MP4/MOV

### Medium Priority
1. **Multiple camera angles** - Switch between cameras
2. **Audio integration** - Background music, sound effects
3. **Title cards / text overlays** - Opening/closing credits
4. **Automated rendering** - Script full video export

### Low Priority / Future
1. **Blueprint integration** - Control from Blueprint graphs
2. **Real-time parameter control** - Adjust while playing
3. **Multiple character animations** - More complex scenes
4. **Environment setup** - Lighting, props, backgrounds

---

## 🎓 KEY LEARNINGS

1. **Remote Control API is powerful** - Can control almost everything remotely via HTTP
2. **SetLockCameraCutToViewport is critical** - Without this, viewport doesn't animate
3. **Python script execution is blocked** - Security in UE 5.7 prevents remote Python execution
4. **ForceUpdate is necessary** - Ensures UI and evaluation sync
5. **Function enumeration is valuable** - `/remote/object/describe` reveals all available functions
6. **Test from PowerShell is faster** - No need to run inside Unreal for testing
7. **Camera binding GUID must be set correctly** - Common UE 5.7 bug, specific fix required

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
