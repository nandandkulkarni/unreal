# AnimSequence API Reference (Unreal Engine 5.x)

Based on reflection analysis of Belica animations in this project.

## Available Methods

### Animation Length
- ✅ **`get_play_length()`** - Returns animation duration in seconds
  ```python
  duration = anim.get_play_length()  # e.g., 1.333 seconds
  ```

### Properties (Direct Access)
- ✅ **`sequence_length`** - Duration in seconds (same as get_play_length())
  ```python
  duration = anim.sequence_length
  ```

### Editor Properties (via get_editor_property)
- ✅ **`sequence_length`** - Duration in seconds
- ✅ **`rate_scale`** - Playback speed multiplier (default: 1.0)
  ```python
  duration = anim.get_editor_property('sequence_length')
  rate = anim.get_editor_property('rate_scale')
  ```

### Other Useful Methods
- `get_skeleton()` - Get the skeleton this animation uses
- `get_anim_pose_at_time(time)` - Get pose at specific time
- `get_anim_pose_at_frame(frame)` - Get pose at specific frame
- `modify()` - Mark for modification (before set_editor_property)

## NOT Available (Common Misconceptions)

❌ **Frame Count Methods** - None of these exist:
- `get_number_of_frames()`
- `get_frame_count()`
- `get_total_frames()`

❌ **Frame Count Properties** - None of these exist:
- `number_of_frames`
- `frame_count`
- `num_frames`

❌ **Frame Rate Properties** - Not directly accessible:
- `target_frame_rate`
- `import_file_framerate`

## Workarounds

### Calculate Frame Count
Since frame count isn't directly available, calculate it:
```python
# Assume 30 fps for Belica animations
fps = 30.0
duration = anim.get_play_length()
frame_count = int(duration * fps)
```

### Get Animation Speed
Use `sequence_length` and measure root motion distance:
```python
duration = anim.sequence_length
# If you know the distance traveled:
# speed_mps = distance_meters / duration
```

## Full Method List (39 methods)
- `acquire_editor_element_handle()`
- `add_animation_modifier_of_class()`
- `add_asset_user_data_of_class()`
- `add_transform_attribute()`
- `call_method()`
- `cast()`
- `clear_retarget_source_asset()`
- `create_attribute_identifier()`
- `find_meta_data_by_class()`
- `get_anim_pose_at_frame()`
- `get_anim_pose_at_time()`
- `get_asset_user_data_of_class()`
- `get_class()`
- `get_default_object()`
- `get_editor_property()`
- `get_fname()`
- `get_full_name()`
- `get_name()`
- `get_outer()`
- `get_outermost()`
- `get_package()`
- `get_path_name()`
- ✅ **`get_play_length()`**
- `get_retarget_source_asset()`
- `get_skeleton()`
- `get_typed_outer()`
- `get_world()`
- `has_asset_user_data_of_class()`
- `is_editor_property_overridden()`
- `is_package_external()`
- `modify()`
- `rename()`
- `reset_editor_property()`
- `set_editor_properties()`
- `set_editor_property()`
- `set_preview_skeletal_mesh()`
- `set_retarget_source_asset()`
- `static_class()`
- `update_retarget_source_asset_data()`

## Properties (4 direct properties)
- `controller` - AnimationDataController
- `data_model` - NoneType
- `data_model_interface` - AnimationDataModel
- ✅ **`sequence_length`** - float (duration in seconds)

## Example: Safe Animation Info Extraction
```python
def get_anim_info(anim):
    """Safely extract animation information."""
    info = {
        "name": anim.get_name(),
        "duration": 0.0,
        "frames": 0,
    }
    
    try:
        # Method 1: get_play_length()
        info["duration"] = anim.get_play_length()
    except:
        try:
            # Method 2: sequence_length property
            info["duration"] = anim.sequence_length
        except:
            try:
                # Method 3: get_editor_property
                info["duration"] = anim.get_editor_property('sequence_length')
            except:
                pass
    
    # Calculate frames (assume 30 fps)
    if info["duration"] > 0:
        info["frames"] = int(info["duration"] * 30.0)
    
    return info
```

## Notes
- This API is for **Unreal Engine 5.x** with Python scripting
- Different Unreal versions may have different APIs
- Always use try/except when accessing properties
- Frame rate is assumed (30 fps for Belica), not queried from the animation
