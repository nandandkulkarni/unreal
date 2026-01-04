# Motion Matching POC - Database Creation

This folder contains scripts to create and configure a Motion Matching (Pose Search) database for the Manny character in Unreal Engine 5.

## Prerequisites

1. **Unreal Engine 5** with the following plugins enabled:
   - Motion Trajectory
   - Pose Search

2. **Python Environment**:
   - `requests` library for remote execution
   - Install: `pip install requests`

3. **Manny Character Assets**:
   - Skeleton: `/Game/Characters/Mannequins/Rigs/SK_Mannequin`
   - Animations: `/Game/Characters/Mannequins/Animations/`

## Quick Start

### Step 1: Verify Installation (Recommended First)

Test that everything is set up correctly:

```bash
python run_remote.py test_verify_database.py
```

This will:
- Verify all database assets exist
- Check database configuration
- Spawn Manny in the scene
- Clean up previous test actors

### Step 2: Create Database (If Not Already Done)

Run any script in this folder using the generic runner:

```bash
# Run database creation
python run_remote.py create_motion_database.py

# List available scripts
python run_remote.py
```

The generic runner (`run_remote.py`) can execute any Python script in this folder inside Unreal Engine.

### Step 3: Manual Configuration

Run directly inside Unreal Engine's Python console:

```python
exec(open(r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\create_motion_database.py").read())
```

## What It Does

The script performs the following steps:

1. **Plugin Check**: Verifies PoseSearch plugin is available
2. **Asset Discovery**: 
   - Finds Manny skeleton
   - Searches for locomotion animations (Walk, Run, Idle, Jump, etc.)
3. **Schema Creation**: Creates `/Game/MotionMatching/MannyMotionSchema`
4. **Database Creation**: Creates `/Game/MotionMatching/MannyMotionDatabase`
5. **Documentation**: Lists found animations for manual addition

## Expected Output

```
================================================================================
MOTION MATCHING DATABASE SETUP
================================================================================

================================================================================
Checking Plugin Availability
================================================================================
  ✓ PoseSearch plugin classes are available

================================================================================
Finding Manny Skeleton
================================================================================
  Trying: /Game/Characters/Mannequins/Rigs/SK_Mannequin
  ✓ Found skeleton: /Game/Characters/Mannequins/Rigs/SK_Mannequin

================================================================================
Finding Manny Animations
================================================================================
  Searching folder: /Game/Characters/Mannequins/Animations
    Found: MM_Walk_Fwd
    Found: MM_Run_Fwd
    Found: MM_Idle
  ✓ Found 15 locomotion animations

================================================================================
Creating Pose Search Schema
================================================================================
  Creating schema at: /Game/MotionMatching/MannyMotionSchema
  Set skeleton reference
  ✓ Created schema: /Game/MotionMatching/MannyMotionSchema

================================================================================
Creating Pose Search Database
================================================================================
  Creating database at: /Game/MotionMatching/MannyMotionDatabase
  Linked to schema
  ✓ Created database: /Game/MotionMatching/MannyMotionDatabase

================================================================================
SETUP COMPLETE
================================================================================
  ✓ Schema created: /Game/MotionMatching/MannyMotionSchema
  ✓ Database created: /Game/MotionMatching/MannyMotionDatabase
  ✓ Found 15 animations for manual addition
```

## Next Steps (Manual)

After running the script, you need to manually configure the database:

### 1. Open the Schema

1. Navigate to `/Game/MotionMatching/` in Content Browser
2. Open `MannyMotionSchema`
3. Add channels:
   - **Trajectory Channel**: For motion prediction
   - **Bone Channels**: For pelvis, feet positions

### 2. Open the Database

1. Open `MannyMotionDatabase`
2. In the **Animation Sequences** section:
   - Click **Add** for each animation
   - Select animations from the list provided by the script
3. Click **Build Database** to index the animations

### 3. Verify

1. Check that the database shows indexed poses
2. Verify schema channels are configured
3. Test by creating a simple AnimBP with Motion Matching node

## Troubleshooting

### Plugin Not Available

```
✗ PoseSearch plugin not available
```

**Solution**: 
1. Open Unreal Engine
2. Edit → Plugins
3. Search for "Pose Search"
4. Enable "Pose Search" and "Motion Trajectory"
5. Restart Unreal Engine

### Skeleton Not Found

```
✗ Could not find Manny skeleton
```

**Solution**:
1. Verify you have the Mannequin assets in your project
2. Check if using Third Person template
3. Manually locate skeleton path in Content Browser
4. Update `skeleton_paths` list in `create_motion_database.py`

### No Animations Found

```
⚠ WARNING: No animations found
```

**Solution**:
1. Check animation folder paths in Content Browser
2. Update `anim_folders` list in `create_motion_database.py`
3. Ensure animations have root motion enabled

### Connection Error

```
✗ Could not connect to Unreal Engine
```

**Solution**:
1. Ensure Unreal Engine is running
2. Enable Remote Control plugin
3. Verify HTTP server is on port 30010
4. Check Windows Firewall settings

## Files

### Scripts
- `run_remote.py` - **Generic runner script** (runs any script in this folder remotely)
- `create_motion_database.py` - Main database creation script (runs in Unreal)
- `test_verify_database.py` - **Verification test script** (checks assets and spawns Manny)
- `diagnostic_check.py` - Diagnostic tool for checking plugin and assets
- `trigger_database_creation.py` - Specific trigger for database creation (runs locally)

### Documentation
- `README.md` - This file
- `implementation_plan.md` - Detailed implementation plan
- `STATUS.md` - **Current project status and progress**
- `SUCCESS_SUMMARY.md` - Database creation results

### Logs (Auto-cleaned)
- `database_creation_YYYYMMDD_HHMMSS.log` - Database creation logs
- `test_verify_YYYYMMDD_HHMMSS.log` - Verification test logs
- `diagnostic_log.txt` - Diagnostic check logs

**Note**: Log files are automatically cleaned up on each run to prevent clutter.

## API Reference

### Key Classes Used

- `unreal.PoseSearchSchema` - Defines matching criteria
- `unreal.PoseSearchDatabase` - Stores animation sequences
- `unreal.AssetToolsHelpers` - Asset creation utilities
- `unreal.DataAssetFactory` - Factory for DataAssets
- `unreal.EditorAssetLibrary` - Asset management

### Key Functions

- `check_plugin_availability()` - Verify PoseSearch is available
- `find_manny_skeleton()` - Locate Manny skeleton asset
- `find_manny_animations()` - Search for locomotion animations
- `create_pose_search_schema()` - Create schema asset
- `create_pose_search_database()` - Create database asset
- `create_motion_matching_database()` - Main entry point

## Known Limitations

1. **Animation Addition**: Adding animations to the database programmatically is complex due to `InstancedStruct` array type. Manual addition via editor is recommended.

2. **Schema Configuration**: Channel configuration (trajectory, bones) must be done manually in the editor.

3. **Plugin Dependency**: Requires experimental PoseSearch plugin which may have limited stability.

## Future Enhancements

- Automatic schema channel configuration
- Batch animation addition via editor utilities
- Integration with FBX import pipelines
- AnimBP creation with Motion Matching node
- Automated testing and validation
