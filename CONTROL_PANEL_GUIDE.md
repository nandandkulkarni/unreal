# Control Panel Guide

## Overview

The **Cinematic Pipeline Control Panel** is a 3-button UI that automates the complete video creation workflow using Unreal Engine's Remote Control API.

**Launch:** `python control_panel.py`

---

## ✅ What's Working Now

### Stage 1: Create Scene (REMOTE - NEW!)
**Status:** ✅ **Fully automated via Remote Control API**

**What it does:**
- Spawns 2 characters in level using `EditorActorSubsystem.SpawnActorFromClass`
- Creates cinematic camera using `LevelSequenceEditorSubsystem.CreateCamera`
- Adds characters as spawnables to sequence
- All done remotely - no need to run Python inside Unreal!

**Technical details:**
- Uses `remote_create_scene.py` script
- Calls validated Remote Control API functions
- Characters spawn at Y=-100 and Y=100 (200cm apart)
- Camera created as spawnable in sequence

**Limitations:**
- Animation keyframes still need manual setup in Sequencer
- Camera positioning needs adjustment in Unreal
- Basic scene structure only - full animation via create_two_characters.py

---

### Stage 2: Play in Editor (REMOTE)
**Status:** ✅ **Fully working**

**What it does:**
- Opens sequence in Sequencer
- Locks camera cut to viewport
- Plays sequence remotely
- Verifies playback

**Script:** `remote_camera_fix_and_test.py`

---

### Stage 3: Render Video
**Status:** ⚠️ **Must run inside Unreal**

**What it does:**
- Shows instructions to render in Unreal
- Outputs Apple ProRes .mov file
- 1920x1080 @ 30fps

**Why not remote?**
- Movie Pipeline rendering crashes Remote Control server
- Complex job configuration required
- Best to run `render_two_characters.py` inside Unreal

---

## 🎯 Complete Workflow

### Quick Start (3 Buttons)

1. **Green Button (Stage 1):** Create scene remotely
   - Spawns characters and camera
   - Takes ~5 seconds
   - Check Unreal Editor to see actors

2. **Blue Button (Stage 2):** Play in editor
   - Tests sequence playback
   - Verifies camera setup
   - Instant remote playback

3. **Orange Button (Stage 3):** Render video
   - Follow instructions shown
   - Run script in Unreal
   - Get .mov file output

---

## 🔧 Technical Architecture

### Remote Control API Functions Used

**Stage 1 (Scene Creation):**
```python
# Spawn actors
EditorActorSubsystem.SpawnActorFromClass(
    ActorClass="/Script/Engine.Character",
    Location={"X": 0, "Y": -100, "Z": 100}
)

# Create camera
LevelSequenceEditorSubsystem.CreateCamera(bSpawnable=True)

# Add spawnables
LevelSequenceEditorSubsystem.AddSpawnableFromClass(
    ClassToSpawn="/Script/Engine.Character"
)
```

**Stage 2 (Playback):**
```python
# Open and play
LevelSequenceEditorBlueprintLibrary.OpenLevelSequence(...)
LevelSequenceEditorBlueprintLibrary.SetLockCameraCutToViewport(True)
LevelSequenceEditorBlueprintLibrary.Play()
```

---

## 📊 What Changed (Breakthrough)

### Before Discovery
- ❌ Thought remote scene creation impossible
- ❌ Stage 1 showed manual instructions only
- ❌ Had to run Python scripts inside Unreal

### After Discovery
- ✅ Found EditorActorSubsystem accessible via Remote Control
- ✅ Validated 3 spawn functions: SpawnActorFromClass, CreateCamera, AddSpawnableFromClass
- ✅ Stage 1 now creates scenes remotely
- ✅ Full automation possible (except rendering)

---

## 🚀 Future Enhancements

### High Priority
1. **Add animation keyframes remotely** - Use MovieScene3DTransformTrack API
2. **Camera positioning** - Set transform remotely via SetActorTransform
3. **Complete scene setup** - Full waypoint animation remote creation

### Medium Priority
1. **Sequence management** - Create/delete sequences remotely
2. **Asset browser** - List and manage sequences
3. **Render queue** - Blueprint wrapper for remote render trigger

### Low Priority
1. **Multiple scenes** - Template system for different scene types
2. **Batch processing** - Create multiple videos
3. **Remote debugging** - Live status monitoring

---

## 📝 Files Reference

### Main Files
- `control_panel.py` - 3-button UI application
- `remote_create_scene.py` - Remote scene creator (Stage 1)
- `remote_camera_fix_and_test.py` - Remote playback (Stage 2)
- `render_two_characters.py` - Video renderer (Stage 3, in Unreal)

### Supporting Files
- `quick_spawn_test.py` - Validation tests for spawn functions
- `enumerate_all_remote_api.py` - API discovery tool
- `remote_api_complete_list.md` - Complete API reference (317 lines)
- `create_two_characters.py` - Full scene creator (in Unreal, for complete animation)

---

## 🐛 Troubleshooting

### Stage 1 Button Does Nothing
**Check:**
- Remote Control server running in Unreal?
- Window → Developer Tools → Remote Control Web App
- Test: http://localhost:30010

### Characters Not Visible
**Solution:**
- Open World Outliner in Unreal
- Look for Character_0, Character_1
- May need to adjust camera to see them

### Sequence Not Playing
**Solution:**
- Use Stage 2 button to test playback
- Sequence may need animation setup
- Run create_two_characters.py for full animation

### Render Button Shows Instructions
**Reason:**
- Remote rendering crashes server
- Best practice: Run render script inside Unreal
- Blueprint wrapper possible but complex

---

## 🎓 Key Learnings

1. **Remote Control API is powerful** - Can spawn actors and create sequences!
2. **EditorActorSubsystem is accessible** - Key discovery for remote spawning
3. **Testing assumptions matters** - "Not possible" turned out to be wrong
4. **Control panel simplifies workflow** - 3 buttons vs many manual steps
5. **Partial automation is valuable** - Even without remote rendering, saves time

---

## 📖 Related Documentation

- **STATUS.md** - Complete project status and technical details
- **remote_api_complete_list.md** - Full Remote Control API reference
- **QUICK_FIX_INSTRUCTIONS.txt** - Quick reference guide

---

*Last Updated: 2025-12-16*  
*Breakthrough: Remote scene creation now fully working!*
