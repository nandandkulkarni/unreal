# MetaHuman Animation Setup - Script Comparison

## Two Versions Available

### 1. `metahuman_animation_setup_auto.py` ⭐ **RECOMMENDED**

**Approach:** Let Unreal auto-generate IK Rigs

**Pros:**
- ✅ Simpler code (~350 lines vs ~610 lines)
- ✅ Matches YouTube tutorial workflow exactly
- ✅ Unreal automatically detects correct A-pose
- ✅ No hardcoded bone names or rotation values
- ✅ Handles different MetaHuman body types automatically
- ✅ **95% confidence** - fewer things can go wrong

**Cons:**
- ⚠️ Less control over IK Rig configuration
- ⚠️ Relies on Unreal's auto-generation (black box)

**Best for:**
- First-time setup
- Quick prototyping
- Following the tutorial
- When you trust Unreal's defaults

---

### 2. `metahuman_animation_setup_manual.py`

**Approach:** Manually create IK Rigs with full control

**Pros:**
- ✅ Full control over every detail
- ✅ Explicitly creates 20 retarget chains
- ✅ Automated A-pose adjustment
- ✅ More transparent - you see exactly what's created

**Cons:**
- ⚠️ More complex code
- ⚠️ A-pose rotation values are estimated (70% confidence)
- ⚠️ Hardcoded bone names may not match all MetaHuman types
- ⚠️ More potential failure points

**Best for:**
- Advanced users who want full control
- Custom skeleton setups
- Debugging retargeting issues
- Learning how IK Rigs work internally

---

## Quick Comparison Table

| Feature | Auto Version | Manual Version |
|---------|--------------|----------------|
| **Lines of Code** | ~350 | ~610 |
| **IK Rig Creation** | Unreal auto-generates | Manually creates with 20 chains |
| **A-Pose Adjustment** | Auto-detected | Hardcoded rotations (±45°) |
| **Bone Names** | Auto-detected | Hardcoded list |
| **Confidence Level** | 95% | 80% |
| **Matches Tutorial** | ✅ Yes | ❌ No (more advanced) |
| **Complexity** | Low | High |

---

## Recommendation

**Start with `metahuman_animation_setup_auto.py`**

If you encounter issues or need more control, switch to the manual version.

---

## Usage

Both scripts are run the same way:

1. Open Unreal Engine
2. **Tools → Execute Python Script**
3. Select either:
   - `metahuman_animation_setup_auto.py` (recommended)
   - `metahuman_animation_setup_manual.py` (advanced)
4. Check Output Log for results
5. Review log file: `metahuman_setup_auto_log.txt` or `metahuman_setup_log.txt`

---

## What Both Scripts Create

| Asset | Path |
|-------|------|
| IK Retargeter | `/Game/MetaHumans/Pia/Animations/RTG_Manny_To_Pia` |
| IK Rigs | Auto: Auto-generated<br>Manual: `IK_Pia`, `IK_Manny_Source` |
| Retargeted Animations | `/Game/MetaHumans/Pia/Animations/` |
| Animation Blueprint | `/Game/MetaHumans/Pia/Animations/ABP_Pia` |
