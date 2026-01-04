# Motion Matching Database - Manual Configuration Guide

**Status**: Programmatic configuration has API limitations  
**Solution**: Manual configuration required (5-10 minutes)

---

## What We Discovered

The Python API for PoseSearch has limitations:
- ❌ Cannot programmatically add channels to schema
- ❌ Cannot programmatically add animations to database  
- ❌ Cannot programmatically build database index

**These operations must be done manually in the Unreal Editor.**

---

## Manual Configuration Steps

### Step 1: Configure the Schema (2 minutes)

1. **Open the Schema**:
   - Navigate to `/Game/MotionMatching/` in Content Browser
   - Double-click `MannyMotionSchema`

2. **Add Trajectory Channel**:
   - Click **"+ Add Channel"**
   - Select **"Trajectory"**
   - Leave default settings (or adjust sample times if desired)

3. **Add Pose Channel**:
   - Click **"+ Add Channel"** again
   - Select **"Pose"**
   - In the Pose channel settings:
     - Add bones: `pelvis`, `foot_l`, `foot_r`
     - Enable **Position** and **Velocity**

4. **Save**: Click **Save** button

---

### Step 2: Add Animations to Database (3 minutes)

1. **Open the Database**:
   - In `/Game/MotionMatching/`
   - Double-click `MannyMotionDatabase`

2. **Add Animation Sequences**:
   - Find the **"Animation Sequences"** section
   - Click **"+ Add"** button
   - Select these 11 core animations:
     1. `MM_Idle`
     2. `MF_Unarmed_Walk_Fwd`
     3. `MF_Unarmed_Walk_Fwd_Left`
     4. `MF_Unarmed_Walk_Fwd_Right`
     5. `MF_Unarmed_Jog_Fwd`
     6. `MF_Unarmed_Jog_Fwd_Left`
     7. `MF_Unarmed_Jog_Fwd_Right`
     8. `MM_Jump`
     9. `MM_Fall_Loop`
     10. `MM_Land`
     11. `MM_WallJump`

   **Tip**: Use the search box to find animations quickly

3. **Build the Database**:
   - Click the **"Build Database"** button at the top
   - Wait for indexing to complete (should take 10-30 seconds)
   - You should see the pose count increase

4. **Save**: Click **Save** button

---

## Verification

After configuration, you should see:

**In MannyMotionSchema**:
- ✅ 2 channels (Trajectory + Pose)
- ✅ Pose channel has 3 bones

**In MannyMotionDatabase**:
- ✅ 11 animation sequences listed
- ✅ Pose count > 0 (indicates successful build)
- ✅ Green checkmark or "Built" status

---

## Next Steps

Once manually configured, run the verification test:

```bash
python run_remote.py test_verify_database.py
```

Then proceed to **movie sequence creation** to see motion matching in action!

---

## Alternative: Use Default Schema

If you want to skip manual configuration for now:

1. Create a new PoseSearchSchema from template:
   - Right-click in Content Browser
   - Animation → Pose Search → Pose Search Schema
   - This creates a schema with default channels

2. Assign it to your database
3. Add animations
4. Build

---

## Troubleshooting

### "Build Database" button is grayed out
- Make sure you've added at least one animation sequence
- Ensure the schema is properly assigned

### Pose count stays at 0 after building
- Check that animations are compatible with the skeleton
- Verify schema channels are configured
- Try removing and re-adding one animation

### Can't find animations
- They're in `/Game/Characters/Mannequins/Anims/Unarmed/`
- Use the asset picker's search function
- Filter by "AnimSequence" type

---

**Estimated Time**: 5-10 minutes total

Once complete, the database will be fully functional for motion matching!
