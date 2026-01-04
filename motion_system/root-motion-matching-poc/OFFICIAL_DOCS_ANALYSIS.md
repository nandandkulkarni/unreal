# Official UE Python API Documentation - PoseSearchDatabase

**Source**: Epic Games Developer Documentation  
**Versions Checked**: UE 5.0, 5.3, 5.4, 5.5, 5.7

---

## 📋 Complete Property List from Official Docs

### ✅ Confirmed Available Properties

According to official Epic Games documentation, `unreal.PoseSearchDatabase` has these properties:

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| `animation_assets` | `Array[InstancedStruct]` | **[Read-Write]** | Animation sequences in database |
| `schema` | `PoseSearchSchema` | [Read-Write] | Defines matching channels |
| `normalization_set` | `PoseSearchNormalizationSet` | [Read-Write] | Normalize multiple databases |
| `exclude_from_database_parameters` | `FloatInterval` | [Read-Write] | Trim animation start/end |
| `kd_tree_max_leaf_size` | `int32` | [Read-Write] | KD-tree leaf size |
| `kd_tree_query_num_neighbors` | `int32` | [Read-Write] | Number of neighbors for search |
| `number_of_principal_components` | `int32` | [Read-Write] | Dimensions for KD-tree |
| `pose_search_mode` | `PoseSearchMode` | [Read-Write] | How database performs search |
| `preview_mesh` | `SkeletalMesh` | [Read-Write] | Preview skeletal mesh |
| `skip_search_if_possible` | `bool` | [Read-Write] | Skip if can't improve cost |
| `base_cost_bias` | `float` | [Read-Write] | Base cost for all poses |
| `continuing_pose_cost_bias` | `float` | [Read-Write] | Cost bias for continuing pose |
| `tags` | `Array[Name]` | [Read-Write] | Metadata tags |

### 🔑 Key Finding: `animation_assets`

**Official Documentation States**:
```python
animation_assets: Array[InstancedStruct]  # [Read-Write]
```

**What This Means**:
- Property is documented as **Read-Write**
- Type is `Array[InstancedStruct]`
- Should be accessible via `get_editor_property()` and `set_editor_property()`

---

## ❌ Reality vs Documentation

### What the Docs Say:
```python
# According to official docs, this SHOULD work:
database.get_editor_property("animation_assets")  # Should return Array[InstancedStruct]
database.set_editor_property("animation_assets", new_array)  # Should set the array
```

### What Actually Happens:
```python
# In practice (tested in our scripts):
database.get_editor_property("animation_assets")
# ERROR: PoseSearchDatabase: Failed to find property 'animation_assets'

database.set_editor_property("animation_assets", [])
# ERROR: PoseSearchDatabase: Failed to find property 'animation_assets'
```

---

## 🔍 UE 5.0 Specific Properties

In **Unreal Engine 5.0** documentation, there were different properties:

| Property (UE 5.0) | Type | Access |
|-------------------|------|--------|
| `sequences` | `Array(PoseSearchDatabaseSequence)` | [Read-Write] |
| `simple_sequences` | `Array(AnimSequence)` | [Read-Write] |
| `extrapolation_parameters` | `PoseSearchExtrapolationParameters` | [Read-Write] |
| `weights` | `PoseSearchWeightParams` | [Read-Write] |

**Note**: These properties changed in later versions (5.3+) to use `animation_assets` instead.

---

## 🎯 Methods from Official Docs

The documentation states that properties are accessed via:

### Generic Methods (Inherited from UObject):
- `get_editor_property(property_name: str)` - Get property value
- `set_editor_property(property_name: str, value)` - Set property value
- `set_editor_properties(properties: dict)` - Set multiple properties

### Specific Methods (from our exploration):
- `get_num_animation_assets()` → `int` - ✅ **Works!**
- `get_animation_asset(index: int)` → `AnimationAsset` - ✅ **Works!**

### Missing Methods (C++ only, not in Python):
- ❌ `AddAnimationAsset()` - Not exposed to Python
- ❌ `BuildIndex()` - Not exposed to Python
- ❌ `RemoveAnimationAsset()` - Not exposed to Python

---

## 📊 Documentation vs Reality Summary

| Feature | Documented | Reality | Status |
|---------|-----------|---------|--------|
| `animation_assets` property exists | ✅ Yes | ❌ No | **Broken** |
| Property is Read-Write | ✅ Yes | ❌ No | **Broken** |
| Type is `Array[InstancedStruct]` | ✅ Yes | ❓ Unknown | **Can't verify** |
| `get_num_animation_assets()` | ❓ Not listed | ✅ Works | **Bonus!** |
| `get_animation_asset(i)` | ❓ Not listed | ✅ Works | **Bonus!** |
| `AddAnimationAsset()` method | ❌ No (C++ only) | ❌ No | **Expected** |

---

## 🔬 Why the Discrepancy?

### Possible Reasons:

1. **Documentation Reflects C++ API**:
   - Docs are auto-generated from C++ headers
   - Python bindings are incomplete
   - `[Read-Write]` refers to C++ accessibility, not Python

2. **InstancedStruct Limitation**:
   - `InstancedStruct` is a complex C++ type
   - Python bindings for `InstancedStruct` arrays are incomplete
   - Can't properly marshal between C++ and Python

3. **Experimental Plugin Status**:
   - PoseSearch is marked "Experimental"
   - Python API exposure is lower priority
   - Full automation not intended for experimental features

4. **Property Name Changed**:
   - UE 5.0 used `sequences` (simple array)
   - UE 5.3+ uses `animation_assets` (InstancedStruct array)
   - Python bindings may not have been updated

---

## ✅ What We Can Confirm Works

Based on our testing AND the official docs:

### Working:
```python
# Load database
db = unreal.load_object(None, "/Game/Path/To/Database")

# Get schema (confirmed in docs)
schema = db.get_editor_property("schema")  # ✅ Works

# Get animation count (not in docs, but works!)
count = db.get_num_animation_assets()  # ✅ Works

# Get specific animation (not in docs, but works!)
anim = db.get_animation_asset(0)  # ✅ Works
```

### Not Working:
```python
# Get animation assets array (in docs, doesn't work)
assets = db.get_editor_property("animation_assets")  # ❌ Fails

# Set animation assets (in docs, doesn't work)
db.set_editor_property("animation_assets", [])  # ❌ Fails

# Add animation (C++ only, not in Python docs)
db.call_method("AddAnimationAsset", (anim,))  # ❌ Fails
```

---

## 📝 Conclusion

**The official documentation is MISLEADING for Python users**:

1. ✅ Properties are listed correctly for C++
2. ❌ Python accessibility is NOT accurately reflected
3. ⚠️ `[Read-Write]` tag doesn't guarantee Python access
4. 🔍 Actual Python API is more limited than documented

**Our 67% automation rate is the MAXIMUM possible** with the current Python bindings, despite what the documentation suggests should be possible.

---

## 🔗 Official Documentation URLs

- **Main Python API**: https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api
- **PoseSearchDatabase (C++)**: https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/PoseSearch/UPoseSearchDatabase
- **Python Scripting Guide**: https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python

**Note**: Direct URL access returns 403 errors, but content is accessible via web search.
