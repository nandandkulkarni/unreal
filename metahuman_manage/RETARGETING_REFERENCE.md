# MetaHuman IK Rig Retargeting Reference

Retarget animations from Manny to **MetaHuman Pia** using the modern UE5 IK Rig approach.

## Approach: IK Rig Chains (No Virtual Bones)

The script uses `IKRigController` and `IKRetargeterController` to:
1. Create IK Rig with retarget chains for MetaHuman Pia
2. Set up IK Retargeter with auto chain mapping
3. Batch retarget Manny animations

## Project Assets

| Asset Type | Path |
|------------|------|
| MetaHuman Pia Body | `/Game/MetaHumans/Pia/Body/f_srt_nrw_body` |
| Manny Mesh | `/Game/Characters/Mannequins/Meshes/SKM_Manny` |
| Output IK Rig | `/Game/MetaHumans/Pia/Animations/IK_Pia` |
| Output Retargeter | `/Game/MetaHumans/Pia/Animations/RTG_Manny_To_Pia` |

---

## Script Changes Summary

1. **Log path** - Uses script's current directory
2. **MetaHuman body path** - Updated to use `f_med_nrw_body`
3. **Virtual bone creation** - Fixed API usage
4. **IK Rig configuration** - Uses existing auto-generated rigs
5. **Animation Blueprint duplication** - Implemented
6. **Null checks** - Added for safety

---

## Unreal Python API Reference

### Loading Assets
```python
asset = unreal.load_asset("/Game/Path/To/Asset")
exists = unreal.EditorAssetLibrary.does_asset_exist("/Game/Path")
```

### IK Retargeter
```python
# Create
factory = unreal.IKRetargeterFactory()
retargeter = asset_tools.create_asset(name, path, unreal.IKRetargeter, factory)

# Configure
retargeter.set_editor_property('source_ik_rig_asset', source_rig)
retargeter.set_editor_property('target_ik_rig_asset', target_rig)
```

### Virtual Bones
```python
# Get existing
virtual_bones = skeleton.get_virtual_bones()

# Add new (source_bone, target_bone, virtual_bone_name)
skeleton.add_virtual_bone("foot_l", "foot_l", "ik_foot_l")
```

### Batch Retargeting
```python
unreal.IKRetargetBatchOperation.duplicate_and_retarget(
    assets_to_retarget=anim_sequences,
    source_mesh=source_skeletal_mesh,
    target_mesh=target_skeletal_mesh,
    ik_retarget_asset=retargeter,
    folder_to_save="/Game/Output/Path"
)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Asset not found" | Check Content Browser, verify asset path case-sensitivity |
| "IKRetargetBatchOperation not available" | UE5.4+ required, use manual retargeting in editor |
| "Virtual bone already exists" | Script checks for existing bones, safe to re-run |
| "Failed to save skeleton" | Check if skeleton is locked or read-only |

---

## Related Files

- [metahuman_animation_setup.py](./metahuman_animation_setup.py) - Main script
- [metahuman_setup_log.txt](./metahuman_setup_log.txt) - Execution log (created after run)

## Source Tutorial

Based on: https://www.youtube.com/watch?v=wJKrIHWRTco
