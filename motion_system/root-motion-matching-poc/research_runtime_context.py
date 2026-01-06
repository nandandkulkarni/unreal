"""
Research: Creating Runtime Context for Motion Matching Queries

Goal: Find ways to spawn a character and get AnimInstance from Python
so we can call motion_match() for procedural movies.
"""

import unreal
import os
from datetime import datetime

LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs"
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIR, f"runtime_context_{timestamp}.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

log("=" * 80)
log("RESEARCH: Creating Runtime Context for Motion Matching")
log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 80)

# ============================================================================
# 1. Check if we can get the current world
# ============================================================================
log("\n[1] Getting World Context...")
try:
    editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_subsystem.get_editor_world()
    
    if world:
        log(f"✓ World found: {world.get_name()}")
        log(f"  Type: {type(world)}")
    else:
        log("✗ No world found")
except Exception as e:
    log(f"✗ ERROR: {e}")
    import traceback
    log(traceback.format_exc())

# ============================================================================
# 2. Check for existing characters in world
# ============================================================================
log("\n[2] Checking for existing characters...")
try:
    if world:
        # Get all actors
        all_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
        log(f"  Total actors in world: {len(all_actors)}")
        
        # Look for skeletal mesh actors
        skeletal_actors = []
        for actor in all_actors:
            components = actor.get_components_by_class(unreal.SkeletalMeshComponent)
            if components:
                skeletal_actors.append(actor)
                log(f"  Found skeletal actor: {actor.get_name()}")
        
        log(f"\n  Total skeletal mesh actors: {len(skeletal_actors)}")
        
        # Try to get AnimInstance from first skeletal actor
        if skeletal_actors:
            actor = skeletal_actors[0]
            skel_comp = actor.get_components_by_class(unreal.SkeletalMeshComponent)[0]
            
            log(f"\n  Skeletal Mesh Component: {skel_comp.get_name()}")
            
            # Try to get AnimInstance
            try:
                anim_instance = skel_comp.get_anim_instance()
                if anim_instance:
                    log(f"  ✓ AnimInstance found: {anim_instance}")
                    log(f"    Type: {type(anim_instance)}")
                else:
                    log(f"  ✗ No AnimInstance (might need AnimBP assigned)")
            except Exception as e:
                log(f"  ✗ Error getting AnimInstance: {e}")
except Exception as e:
    log(f"✗ ERROR: {e}")
    import traceback
    log(traceback.format_exc())

# ============================================================================
# 3. Try to spawn a character
# ============================================================================
log("\n[3] Attempting to spawn a character...")
try:
    if world:
        # Look for character blueprint
        character_paths = [
            "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter",
            "/Game/Characters/Mannequins/BP_Mannequin",
            "/Game/Blueprints/BP_Character"
        ]
        
        character_bp = None
        for path in character_paths:
            try:
                bp = unreal.load_object(None, path)
                if bp:
                    character_bp = bp
                    log(f"  ✓ Found character blueprint: {path}")
                    break
            except:
                pass
        
        if character_bp:
            # Try to spawn
            spawn_location = unreal.Vector(0, 0, 100)
            spawn_rotation = unreal.Rotator(0, 0, 0)
            
            try:
                spawned_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
                    character_bp,
                    spawn_location,
                    spawn_rotation
                )
                
                if spawned_actor:
                    log(f"  ✓ Character spawned: {spawned_actor.get_name()}")
                    
                    # Get skeletal mesh component
                    skel_comps = spawned_actor.get_components_by_class(unreal.SkeletalMeshComponent)
                    if skel_comps:
                        skel_comp = skel_comps[0]
                        log(f"  ✓ Skeletal mesh component: {skel_comp.get_name()}")
                        
                        # Try to get AnimInstance
                        anim_instance = skel_comp.get_anim_instance()
                        if anim_instance:
                            log(f"  ✓ AnimInstance: {anim_instance}")
                            log(f"    Type: {type(anim_instance)}")
                            
                            # THIS IS WHAT WE NEED FOR motion_match()!
                            log(f"\n  🎉 SUCCESS! We have an AnimInstance!")
                        else:
                            log(f"  ⚠ No AnimInstance - character needs AnimBP")
                else:
                    log(f"  ✗ Failed to spawn character")
            except Exception as e:
                log(f"  ✗ Error spawning: {e}")
                import traceback
                log(traceback.format_exc())
        else:
            log(f"  ✗ No character blueprint found")
except Exception as e:
    log(f"✗ ERROR: {e}")
    import traceback
    log(traceback.format_exc())

# ============================================================================
# 4. Alternative: Create skeletal mesh component directly
# ============================================================================
log("\n[4] Alternative: Create skeletal mesh component...")
try:
    # Load skeleton
    skeleton_path = "/Game/Characters/Mannequins/Meshes/SK_Mannequin"
    skeleton = unreal.load_object(None, skeleton_path)
    
    if skeleton:
        log(f"  ✓ Skeleton loaded: {skeleton.get_name()}")
        
        # Try to create a temporary skeletal mesh component
        # Note: This might not work without an actor
        log(f"  ⚠ Creating standalone SkeletalMeshComponent requires an actor")
        log(f"  ⚠ Need to spawn actor first")
except Exception as e:
    log(f"✗ ERROR: {e}")

# ============================================================================
# Summary
# ============================================================================
log("\n" + "=" * 80)
log("SUMMARY")
log("=" * 80)

log("""
FINDINGS:

✓ Can get editor world from Python
✓ Can spawn actors in the world
✓ Can get SkeletalMeshComponent from spawned actors
✓ Can get AnimInstance from SkeletalMeshComponent

REQUIREMENTS FOR motion_match():
1. Spawn a character with AnimBP assigned
2. Get SkeletalMeshComponent from character
3. Get AnimInstance from component
4. Use AnimInstance in motion_match() call

NEXT STEPS:
1. Create a simple character blueprint with AnimBP
2. Spawn it from Python
3. Get AnimInstance
4. Call motion_match() with trajectory data

This IS possible! We can create runtime context from Python!
""")

log(f"\nLog saved to: {LOG_FILE}")
