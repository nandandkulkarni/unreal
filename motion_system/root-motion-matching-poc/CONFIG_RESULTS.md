# Motion Matching POC - Configuration Results

**Date**: 2026-01-04 16:10  
**Status**: ⚠️ **MANUAL CONFIGURATION REQUIRED**

---

## Programmatic Configuration Attempt

We attempted to configure the database programmatically and discovered:

### ✅ What Worked
- Schema and Database assets loaded successfully
- Found 11 core locomotion animations
- Identified required configuration steps
- Documented manual process

### ❌ API Limitations Discovered

1. **Schema Channels**:
   - `BoneReference` API different than expected
   - Cannot programmatically add channels
   - **Solution**: Manual addition in editor

2. **Database Animations**:
   - `PoseSearchDatabaseAnimSequence` class not exposed to Python
   - `animation_assets` property not writable via Python
   - **Solution**: Manual addition in editor

3. **Database Building**:
   - No `build()` or `build_index()` method in Python API
   - **Solution**: Manual build in editor

---

## Why This Happened

The PoseSearch plugin is marked as "Experimental" in UE5. The Python API exposure is incomplete:
- C++ classes exist but not all are exposed to Python
- Complex editor-only operations (like InstancedStruct manipulation) are not scriptable
- This is common for experimental features

---

## What You Need to Do

**Follow the manual configuration guide**: `MANUAL_CONFIG_GUIDE.md`

**Time Required**: 5-10 minutes

**Steps**:
1. Open `MannyMotionSchema` → Add channels (Trajectory + Pose)
2. Open `MannyMotionDatabase` → Add 11 animations → Build

---

## Animations Ready to Add

The script identified these 11 core locomotion animations:

1. `MM_Idle` - Standing idle
2. `MF_Unarmed_Walk_Fwd` - Walk forward
3. `MF_Unarmed_Walk_Fwd_Left` - Walk forward-left
4. `MF_Unarmed_Walk_Fwd_Right` - Walk forward-right
5. `MF_Unarmed_Jog_Fwd` - Jog forward
6. `MF_Unarmed_Jog_Fwd_Left` - Jog forward-left
7. `MF_Unarmed_Jog_Fwd_Right` - Jog forward-right
8. `MM_Jump` - Jump start
9. `MM_Fall_Loop` - Falling loop
10. `MM_Land` - Landing
11. `MM_WallJump` - Wall jump

All located in: `/Game/Characters/Mannequins/Anims/Unarmed/`

---

## After Manual Configuration

Once you've configured the database manually, you can:

1. **Verify** it worked:
   ```bash
   python run_remote.py test_verify_database.py
   ```

2. **Create movie sequence** to demonstrate motion matching

3. **Test motion matching** in-game

---

## Future Improvements

Potential approaches for better automation:
1. **Editor Utility Widgets**: Create a Blueprint-based UI tool
2. **C++ Plugin**: Extend Python API with custom bindings
3. **Unreal Python Plugin**: Use community plugins with extended API
4. **Wait for Epic**: Future UE versions may expose more API

For now, manual configuration is the most reliable approach.

---

**See `MANUAL_CONFIG_GUIDE.md` for detailed step-by-step instructions!**
