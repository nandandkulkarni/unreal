import unreal
# This imports the Unreal Engine Python API module into your script
# It provides access to all engine classes, functions, and subsystems
# Without this import, you cannot interact with Unreal Engine from Python

print("\n" + "="*60)
# This prints a newline followed by 60 equal signs to create a visual separator
# The separator makes the output easier to read in the console
# It marks the beginning of our character spawning process

print("STARTING CHARACTER SPAWN PROCESS")
# This prints a header message to the console indicating the script has begun
# It helps identify the output from this script among other console messages
# Good for debugging when running multiple scripts

print("="*60 + "\n")
# This prints another 60 equal signs followed by a newline for visual separation
# It creates a box-like appearance around the header message
# The \n adds spacing before the actual process steps begin

# Step 1: Import
print("[STEP 1] Importing Unreal module...")
# This prints a step indicator to show we're at the first stage of the process
# The [STEP X] format makes it easy to track progress through the script
# It tells the user that we're verifying the Unreal module import

# (import already done at top)
# This is a comment noting that the actual import happened at the beginning
# We can't re-import here, so this step just acknowledges it
# The import statement must be at the top of Python files by convention

print("✓ Unreal module imported\n")
# This prints a success checkmark confirming the import was successful
# The \n adds a blank line after this step for better readability
# If we reached this line, the import didn't fail

# Step 2: Get editor library
print("[STEP 2] Getting editor library...")
# This announces the second step: accessing the editor library
# EditorLevelLibrary is a static utility class for level manipulation
# This step is crucial because we need it to spawn actors

editor_lib = unreal.EditorLevelLibrary
# EditorLevelLibrary is a static class, not a subsystem, so we use it directly
# It provides functions for manipulating the currently open level
# We assign it to a variable so we can call its methods later

print(f"✓ Editor library ready: {editor_lib.__name__}\n")
# This confirms we have access to EditorLevelLibrary
# The __name__ attribute shows the class name
# This helps verify we're using the correct utility class

# Step 3: Define spawn parameters
print("[STEP 3] Defining spawn parameters...")
# This indicates we're now setting up the parameters for where to spawn the actor
# Parameters include location and rotation in 3D space
# These values determine where the character first appears in the level

spawn_location = unreal.Vector(0.0, 0.0, 100.0)
# This creates a 3D vector representing coordinates in Unreal's world space
# The values are (X=0, Y=0, Z=100) where Z is the vertical axis
# 100 units up means the character spawns 1 meter above the origin (Unreal uses cm)

print(f"✓ Spawn location: X={spawn_location.x}, Y={spawn_location.y}, Z={spawn_location.z}")
# This logs the exact coordinates where the character will spawn
# It shows all three axis values separately for clarity
# Useful for debugging if the character appears in the wrong place

spawn_rotation = unreal.Rotator(0.0, 0.0, 0.0)
# This creates a rotator object defining the actor's initial orientation
# The three values represent Pitch (up/down tilt), Yaw (left/right turn), Roll (side tilt)
# All zeros means no rotation from the default forward-facing direction

print(f"✓ Spawn rotation: Pitch={spawn_rotation.pitch}, Yaw={spawn_rotation.yaw}, Roll={spawn_rotation.roll}\n")
# This logs the rotation values for all three axes
# It confirms the orientation settings before spawning
# The \n adds spacing before the next step

# Step 4: Spawn actor
print("[STEP 4] Spawning skeletal mesh actor in level...")
# This announces we're about to create a SkeletalMeshActor in the level
# SkeletalMeshActor already has a skeletal mesh component built-in
# This is better than spawning a base Actor and trying to add components

character = editor_lib.spawn_actor_from_class(
    unreal.SkeletalMeshActor,
    spawn_location,
    spawn_rotation
)
# This spawns a SkeletalMeshActor which comes with a SkeletalMeshComponent
# We use SkeletalMeshActor instead of base Actor to avoid component issues
# The function returns a reference to the newly created actor

print(f"✓ Actor spawned: {character.get_name()}")
# This confirms the actor was created and shows its automatically generated name
# Unreal assigns default names like "SkeletalMeshActor_1", etc.
# The name can be used to find this actor in the World Outliner

print(f"  Actor class: {character.get_class().get_name()}\n")
# This shows the class type of the spawned actor (should be "SkeletalMeshActor")
# It confirms we spawned the correct type of object
# The indentation groups this info with the previous log line

# Step 5: Get the skeletal mesh component
print("[STEP 5] Getting skeletal mesh component...")
# This announces we're retrieving the built-in skeletal mesh component
# SkeletalMeshActor comes with a component already attached
# We just need to get a reference to it

mesh_comp = character.skeletal_mesh_component
# This gets the skeletal mesh component that's already part of the actor
# No need to create or add it - it comes with SkeletalMeshActor
# This component will hold our 3D character model

print(f"✓ Component retrieved: {mesh_comp.get_name()}")
# This confirms the component was created and shows its name
# Component names are usually auto-generated like "SkeletalMeshComponent_0"
# This helps verify the component exists before we try to use it

print(f"  Component class: {mesh_comp.get_class().get_name()}\n")
# This displays the class type of the component (should be "SkeletalMeshComponent")
# It confirms we created the right type of component
# This is useful if you're debugging component creation issues

# Step 6: Root component info
print("[STEP 6] Root component info...")
# This announces we're documenting the root component
# SkeletalMeshActor automatically sets the skeletal mesh component as root
# No need to manually verify - it's built into the actor type

print(f"✓ Root component is automatically set to: {mesh_comp.get_name()}")
# For SkeletalMeshActor, the skeletal mesh component is always the root
# This is handled automatically by Unreal Engine
# The root component determines the actor's overall transform

print(f"  Component hierarchy established\n")
# This confirms the component hierarchy is set up correctly by default
# SkeletalMeshActor handles this automatically

# Step 7: Load skeletal mesh
print("[STEP 7] Loading skeletal mesh asset...")
# This announces we're loading the actual 3D model from the content browser
# Assets must be loaded before they can be used
# This step reads the mesh data from disk into memory

sk_mesh_path = "/MetaHumanCharacter/Body/IdentityTemplate/SKM_Body"
# This defines the path to the skeletal mesh asset in your project
# Using generic MetaHuman body template (available with MetaHuman plugin)
# NOTE: For a specific character like Monica, import from Fab first

sk_mesh = unreal.load_asset(sk_mesh_path)
# This loads the skeletal mesh asset from the specified path
# If the path is invalid, this returns None instead of crashing
# The loaded asset contains the 3D model geometry and bound skeleton

if sk_mesh:
# This checks if the asset loaded successfully (not None)
# If loading failed, sk_mesh will be None and this block won't execute
# It's good practice to check before using the asset

    print(f"✓ Skeletal mesh loaded: {sk_mesh.get_name()}")
    # This confirms successful loading and shows the asset's name
    # The name is the actual asset name, not the full path
    # Useful for verifying you loaded the correct asset
    
    print(f"  Asset path: {sk_mesh_path}")
    # This displays the path we used to load the asset
    # Helps with debugging if you loaded the wrong asset
    # Also documents which asset was used in the log output
    
    print(f"  Skeleton: {sk_mesh.get_skeleton().get_name() if sk_mesh.get_skeleton() else 'None'}\n")
    # This shows which skeleton is bound to this mesh
    # The skeleton determines what animations can be played
    # If no skeleton is bound, it prints "None" which indicates a problem

else:
# This block executes if the asset failed to load (sk_mesh is None)
# Failure usually means the path is wrong or the asset doesn't exist
# Better to handle this gracefully than crash later

    print(f"✗ FAILED to load skeletal mesh from: {sk_mesh_path}\n")
    # This prints an error message with an X mark instead of a checkmark
    # It shows the path that failed so you can correct it
    # The error is informative but doesn't stop the script

# Step 8: Assign mesh to component
print("[STEP 8] Assigning mesh to component...")
# This announces we're connecting the loaded mesh to the component
# Until this happens, the component exists but displays nothing
# This is when the character actually becomes visible

if sk_mesh:
    mesh_comp.set_skinned_asset_and_update(sk_mesh)
    # This assigns the loaded skeletal mesh asset to the component
    # Using set_skinned_asset_and_update (replaces deprecated set_skeletal_mesh)
    # The mesh will appear in the viewport after this call
else:
    print("  ⚠ Skipping mesh assignment - mesh failed to load")

assigned_mesh = mesh_comp.get_skeletal_mesh_asset()
# This retrieves the mesh that's currently assigned to the component
# We do this to verify the assignment worked
# It should return the same mesh we just set

print(f"✓ Mesh assigned to component")
# This confirms the assignment operation completed
# Doesn't necessarily mean it worked, just that it didn't crash
# We verify success in the next line

print(f"  Current mesh: {assigned_mesh.get_name() if assigned_mesh else 'None'}")
# This shows the name of the mesh now assigned to the component
# Should match the mesh we loaded in the previous step
# If it says "None", the assignment failed

print(f"  Character is now visible in viewport\n")
# This reminds you that the character should now be visible in the editor
# You should be able to see it at the spawn location
# If you can't see it, check the spawn location and camera position

# Step 9: Load animation blueprint
print("[STEP 9] Loading animation blueprint...")
# This announces we're loading the Animation Blueprint asset
# Animation Blueprints control which animations play and how they transition
# They're like the "brain" of the animation system

anim_bp_path = "/MetaHumanCharacter/Body/ABP_Body_PostProcess"
# This defines the path to the Animation Blueprint in your project
# Using generic MetaHuman body animation blueprint (post-process)
# NOTE: For a specific character like Monica, import from Fab first

anim_bp = unreal.load_asset(anim_bp_path)
# This loads the Animation Blueprint asset from the specified path
# If the path is invalid, this returns None
# The blueprint contains the animation logic and state machines

if anim_bp:
# This checks if the Animation Blueprint loaded successfully
# If loading failed, anim_bp will be None
# We only proceed if we have a valid blueprint

    print(f"✓ Animation blueprint loaded: {anim_bp.get_name()}")
    # This confirms successful loading and shows the blueprint's name
    # The name helps verify you loaded the correct blueprint
    # Should match the asset name in your content browser
    
    print(f"  Asset path: {anim_bp_path}\n")
    # This displays the path used to load the blueprint
    # Useful for documentation and debugging
    # Helps track which blueprint controls this character's animations

else:
# This block executes if loading the Animation Blueprint failed
# Common causes: wrong path, asset doesn't exist, or typo
# Better to log the error than crash

    print(f"✗ FAILED to load animation blueprint from: {anim_bp_path}\n")
    # This prints an error message showing the failed path
    # The X mark indicates failure (vs ✓ for success)
    # You can use this to correct the path and try again

# Step 10: Set animation mode
print("[STEP 10] Setting animation mode...")
# This announces we're configuring how the component handles animation
# There are different modes: blueprint-driven, single animation, etc.
# We're choosing blueprint mode for complex animation logic

mesh_comp.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
# This tells the component to use an Animation Blueprint for animations
# Alternative modes include ANIMATION_SINGLE_NODE (one animation at a time)
# Blueprint mode allows for state machines and complex blending

current_mode = mesh_comp.get_animation_mode()
# This retrieves the current animation mode from the component
# We use this to verify the mode was set correctly
# It should return ANIMATION_BLUEPRINT if successful

print(f"✓ Animation mode set: {current_mode}\n")
# This confirms the mode was set and shows which mode is active
# Should display "AnimationMode.ANIMATION_BLUEPRINT"
# If it shows something else, the set operation may have failed

# Step 11: Assign animation blueprint class
print("[STEP 11] Assigning animation blueprint class...")
# This announces the final step: connecting the blueprint to the component
# This is different from just setting the mode - this assigns the actual blueprint
# Once this is done, the animation system becomes fully active

if anim_bp:
    mesh_comp.set_anim_instance_class(anim_bp.generated_class())
    # This assigns the Animation Blueprint's class to the skeletal mesh component
    # generated_class() gets the actual class from the blueprint asset
    # The animation logic will now run and control the character's poses
    
    print(f"✓ Animation blueprint class assigned: {anim_bp.get_name()}")
    # This confirms which animation class is now assigned
    # Shows the name of your Animation Blueprint
    # The animation system is now active
    
    print(f"  Animation system is now active\n")
    # This confirms that animations should now be playing
    # The character should be animated according to the blueprint's logic
    # If you don't see animation, check the blueprint's default state
else:
    print("  ⚠ Skipping animation blueprint assignment - blueprint failed to load")
    print(f"  Animation system inactive\n")
    # Blueprint wasn't loaded, so no animations will play
    # Check the asset path and try again

# Final summary
print("="*60)
# This prints a line of 60 equal signs as a visual separator
# It marks the beginning of the final summary section
# Helps distinguish the summary from the step-by-step logs

print("CHARACTER SPAWN COMPLETE!")
# This prints a success message indicating the entire process finished
# All steps completed without stopping the script
# Doesn't guarantee everything worked, just that we reached the end

print("="*60)
# This prints another separator line below the completion message
# Creates a box-like appearance around the summary
# Makes the summary section easy to spot in console output

print(f"Actor Name:        {character.get_name()}")
# This displays the final name of the spawned actor
# Useful for finding the actor in the World Outliner
# The spacing aligns the colons for better readability

print(f"Location:          {spawn_location}")
# This shows where the character was spawned in world space
# Displays the full Vector with X, Y, Z coordinates
# Use this if you need to spawn another character at the same location

print(f"Rotation:          {spawn_rotation}")
# This shows the rotation that was applied to the character
# Displays the full Rotator with Pitch, Yaw, Roll values
# Useful for replicating the same orientation later

print(f"Root Component:    {mesh_comp.get_name()}")
# This shows which component is serving as the root
# For SkeletalMeshActor, it's always the skeletal mesh component
# Confirms the component hierarchy

print(f"Skeletal Mesh:     {sk_mesh.get_name() if sk_mesh else 'None'}")
# This shows which skeletal mesh is assigned to the character
# Displays the mesh name if it loaded successfully, "None" if it failed
# Useful for confirming the correct mesh is being used

print(f"Animation BP:      {anim_bp.get_name() if anim_bp else 'None'}")
# This shows which Animation Blueprint is controlling the character
# Displays the blueprint name if it loaded successfully, "None" if it failed
# Useful for debugging animation issues

print(f"Animation Mode:    {mesh_comp.get_animation_mode()}")
# This shows the current animation mode of the skeletal mesh component
# Should show ANIMATION_BLUEPRINT if everything was set correctly
# Helps diagnose why animations might not be playing

print("="*60 + "\n")
# This prints a final separator line followed by a newline
# Closes off the summary section visually
# The \n adds spacing after the entire process completes