# MetaHuman IK Rig Retargeting Script

Rewrite script to use proper **IK Rig retarget chains** (as shown in YouTube tutorial) instead of virtual bones.

## Research Summary

| Component | Python API |
|-----------|------------|
| IK Rig editing | `IKRigController` |
| Add retarget chain | `controller.add_retarget_chain(chain_name, start_bone, end_bone, goal)` |
| Set retarget root | `controller.set_retarget_root(bone_name)` |
| IK Retargeter editing | `IKRetargeterController` |
| Auto-map chains | `rtg_controller.auto_map_chains(fuzzy_match=True)` |

## UE5 Mannequin Bone Names

```
root
└── pelvis (retarget root)
    ├── spine_01 → spine_02 → spine_03 → spine_04 → spine_05 → neck_01 → neck_02 → head
    ├── thigh_l → calf_l → foot_l → ball_l
    ├── thigh_r → calf_r → foot_r → ball_r
    ├── clavicle_l → upperarm_l → lowerarm_l → hand_l → (finger chains)
    └── clavicle_r → upperarm_r → lowerarm_r → hand_r → (finger chains)
```

## Retarget Chains to Create

| Chain Name | Start Bone | End Bone |
|------------|------------|----------|
| Spine | spine_01 | spine_05 |
| Head | neck_01 | head |
| LeftArm | clavicle_l | hand_l |
| RightArm | clavicle_r | hand_r |
| LeftLeg | thigh_l | ball_l |
| RightLeg | thigh_r | ball_r |
| LeftThumb | thumb_01_l | thumb_03_l |
| LeftIndex | index_01_l | index_03_l |
| (etc for all fingers) | ... | ... |

---

## Proposed Changes

### [MODIFY] [metahuman_animation_setup.py](file:///c:/UnrealProjects/Coding/unreal/metahuman_manage/metahuman_animation_setup.py)

**Remove:**
- Virtual bone creation (not needed with IK Rig approach)

**Add:**
1. **IK Rig creation/configuration** using `IKRigController`
2. **Retarget chain definitions** for spine, head, arms, legs, fingers
3. **IKRetargeterController** for auto chain mapping
4. **Retarget pose adjustment** for A-pose alignment

**Key code:**
```python
# Get IKRigController
rig_controller = unreal.IKRigController.get_controller(ik_rig)

# Set retarget root
rig_controller.set_retarget_root("pelvis")

# Add retarget chains
rig_controller.add_retarget_chain("Spine", "spine_01", "spine_05", "")
rig_controller.add_retarget_chain("Head", "neck_01", "head", "")
rig_controller.add_retarget_chain("LeftArm", "clavicle_l", "hand_l", "")
rig_controller.add_retarget_chain("RightArm", "clavicle_r", "hand_r", "")
rig_controller.add_retarget_chain("LeftLeg", "thigh_l", "ball_l", "")
rig_controller.add_retarget_chain("RightLeg", "thigh_r", "ball_r", "")

# Auto-map chains in retargeter
rtg_controller = unreal.IKRetargeterController.get_controller(retargeter)
rtg_controller.auto_map_chains(unreal.AutoMapChainType.FUZZY)
```

---

## Verification Plan

1. Run script in Unreal Engine
2. Check Output Log for chain creation messages
3. Open created IK Rigs in editor - verify chains visible
4. Open IK Retargeter - verify source/target mapped
5. Test retarget animation on MetaHuman Pia
