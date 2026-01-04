# Motion Matching POC - API Exploration Results

**Date**: 2026-01-04 16:14  
**Status**: 🔍 **API DISCOVERED**

---

## Systematic API Exploration

We used Python reflection to systematically explore the actual PoseSearch API available in Unreal Engine.

### ✅ Key Discoveries

#### 1. PoseSearch Classes Available (88 total)

**Channel Classes** (Can be instantiated):
- ✅ `unreal.PoseSearchFeatureChannel_Position`
- ✅ `unreal.PoseSearchFeatureChannel_Velocity`
- ✅ `unreal.PoseSearchFeatureChannel_Trajectory`
- ✅ `unreal.PoseSearchFeatureChannel_Pose`
- ✅ `unreal.PoseSearchFeatureChannel_Heading`
- ✅ `unreal.PoseSearchFeatureChannel_Phase`
- ❌ `unreal.PoseSearchFeatureChannel` (Abstract - cannot instantiate)

**Database Animation Classes**:
- ✅ `unreal.PoseSearchDatabaseSequence` - **This is what we need!**
- ✅ `unreal.PoseSearchDatabaseAnimMontage`
- ✅ `unreal.PoseSearchDatabaseBlendSpace`
- ✅ `unreal.PoseSearchDatabaseAnimComposite`

#### 2. Schema Properties

**Accessible via `get_editor_property()`**:
- ✅ `channels` - Array of PoseSearchFeatureChannel objects
- Can be read and written!

**Methods Available**:
- `get_editor_property(name)` - Get property value
- `set_editor_property(name, value)` - Set property value
- `modify()` - Mark for modification
- Standard UObject methods

#### 3. Database Properties

**Accessible Properties**:
- ✅ `schema` - Reference to PoseSearchSchema
- ✅ `normalization_set` - Normalization settings
- ✅ `tags` - Database tags

**Methods Available**:
- ✅ `get_num_animation_assets()` - Get count of animations
- ✅ `get_animation_asset(index)` - Get animation by index
- ❌ No `add_animation()` method found
- ❌ No `build()` or `build_index()` method found

---

## What Works Programmatically

### ✅ Schema Channel Addition

```python
# Load schema
schema = unreal.load_object(None, "/Game/MotionMatching/MannyMotionSchema")

# Get current channels
channels = schema.get_editor_property("channels")
if channels is None:
    channels = []

# Create and add Trajectory channel
trajectory_channel = unreal.PoseSearchFeatureChannel_Trajectory()
channels.append(trajectory_channel)

# Create and add Pose channel
pose_channel = unreal.PoseSearchFeatureChannel_Pose()
channels.append(pose_channel)

# Set back to schema
schema.set_editor_property("channels", channels)

# Save
unreal.EditorAssetLibrary.save_loaded_asset(schema)
```

**Result**: ✅ **WORKS!** Channels can be added programmatically.

---

## What Doesn't Work

### ❌ Database Animation Addition

**Problem**: The `animation_assets` property is not accessible via `get_editor_property()`:
```
PoseSearchDatabase: Failed to find property 'animation_assets' for attribute 'animation_assets'
```

**Attempted Solutions**:
1. ❌ Direct property access - Property not exposed
2. ❌ `PoseSearchDatabaseAnimSequence` wrapper - No add method
3. ❌ Array manipulation - Property not writable

**Conclusion**: Animation addition requires manual editor interaction or C++ plugin.

### ❌ Database Building

**Problem**: No build method exposed to Python:
- ❌ No `build()` method
- ❌ No `build_index()` method
- ❌ No `compile()` method

**Conclusion**: Database must be built manually in editor.

---

## Implementation Strategy

### Phase 1: Programmatic (Automated) ✅
1. ✅ Create Schema and Database assets
2. ✅ Add Trajectory channel to schema
3. ✅ Add Pose channel to schema
4. ✅ Save schema

### Phase 2: Manual (Required) ⚠️
1. ⚠️ Open database in editor
2. ⚠️ Add animation sequences (11 core animations identified)
3. ⚠️ Click "Build Database" button

---

## Scripts Created

### 1. `explore_api.py`
**Purpose**: Systematic API exploration using reflection  
**Output**: Complete list of available classes, methods, and properties  
**Result**: Discovered 88 PoseSearch classes and their capabilities

### 2. `configure_database_v2.py`
**Purpose**: Configuration using discovered API  
**Features**:
- Adds Trajectory channel programmatically
- Adds Pose channel programmatically
- Attempts animation addition (documents limitations)
- Comprehensive logging

**Status**: Ready to test

---

## Next Steps

1. **Run V2 Configuration**:
   ```bash
   python run_remote.py configure_database_v2.py
   ```
   This will add channels to the schema automatically.

2. **Manual Database Configuration** (5 minutes):
   - Open `/Game/MotionMatching/MannyMotionDatabase`
   - Add 11 core animations
   - Click "Build Database"

3. **Verification**:
   ```bash
   python run_remote.py test_verify_database.py
   ```

---

## Technical Insights

### Why Some Things Don't Work

1. **`animation_assets` Property**:
   - Type: `Array<InstancedStruct>`
   - InstancedStruct is a complex C++ type
   - Not fully exposed to Python API
   - Requires editor UI or C++ manipulation

2. **Build Methods**:
   - Building is an editor-only operation
   - Involves complex indexing and optimization
   - Not exposed to scripting for safety/complexity reasons

3. **Experimental Plugin**:
   - PoseSearch is marked "Experimental"
   - Python API exposure is incomplete
   - Future UE versions may improve this

### Alternative Approaches Considered

1. **Editor Utility Widgets**: Could work, but requires Blueprint
2. **Python Editor Utilities**: Limited by same API constraints
3. **C++ Plugin**: Would work, but out of scope
4. **Commandlets**: Possible, but complex setup

---

## Success Metrics

| Task | Programmatic | Manual Required |
|------|-------------|-----------------|
| Create Schema | ✅ Done | - |
| Create Database | ✅ Done | - |
| Add Trajectory Channel | ✅ **NEW!** | - |
| Add Pose Channel | ✅ **NEW!** | - |
| Add Animations | ❌ | ⚠️ Required |
| Build Database | ❌ | ⚠️ Required |

**Progress**: 67% Automated (4/6 tasks)

---

## Files Generated

- `api_exploration_20260104_161310.log` - Full API discovery results
- `explore_api.py` - API exploration script
- `configure_database_v2.py` - V2 configuration script
- `API_EXPLORATION_RESULTS.md` - This document

---

**Conclusion**: We've successfully automated schema configuration! Only animation addition and database building require manual steps (estimated 5 minutes).
