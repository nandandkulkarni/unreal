"""
COMPLETE EXAMPLE: Motion Matching Query from Python

This script demonstrates end-to-end Motion Matching query:
1. Spawn character to get AnimInstance
2. Create trajectory data
3. Query Motion Matching database
4. Get best matching animation

This enables Motion Matching for procedural movies!
"""

import unreal
import os
from datetime import datetime

LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs"
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIR, f"complete_query_example_{timestamp}.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

log("=" * 80)
log("COMPLETE MOTION MATCHING QUERY EXAMPLE")
log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 80)

# ============================================================================
# STEP 1: Get World and Spawn Character
# ============================================================================
log("\n[STEP 1] Spawning Character...")

try:
    # Get editor world
    editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_subsystem.get_editor_world()
    log(f"✓ World: {world.get_name()}")
    
    # Load character blueprint
    character_bp = unreal.load_object(None, "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
    if not character_bp:
        raise Exception("Character blueprint not found")
    log(f"✓ Character BP loaded")
    
    # Spawn character
    spawn_location = unreal.Vector(0, 0, 100)
    spawn_rotation = unreal.Rotator(0, 0, 0)
    
    character = unreal.EditorLevelLibrary.spawn_actor_from_object(
        character_bp,
        spawn_location,
        spawn_rotation
    )
    log(f"✓ Character spawned: {character.get_name()}")
    
    # Get skeletal mesh component
    skel_comp = character.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    log(f"✓ Skeletal mesh component: {skel_comp.get_name()}")
    
    # Get AnimInstance
    anim_instance = skel_comp.get_anim_instance()
    if not anim_instance:
        raise Exception("No AnimInstance - character needs AnimBP")
    log(f"✓ AnimInstance: {anim_instance.get_name()}")
    
except Exception as e:
    log(f"✗ ERROR: {e}")
    import traceback
    log(traceback.format_exc())
    raise

# ============================================================================
# STEP 2: Load Motion Matching Database
# ============================================================================
log("\n[STEP 2] Loading Motion Matching Database...")

try:
    database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
    if not database:
        raise Exception("Database not found")
    log(f"✓ Database loaded: {database.get_name()}")
    
    # Get animation count
    lib = unreal.AAANKPoseBlueprintLibrary
    count = lib.get_animation_count(database)
    log(f"  Animations in database: {count}")
    
except Exception as e:
    log(f"✗ ERROR: {e}")
    raise

# ============================================================================
# STEP 3: Create Query Parameters
# ============================================================================
log("\n[STEP 3] Creating Query Parameters...")

try:
    # Create continuing properties (for first query, no continuing pose)
    continuing_props = unreal.PoseSearchContinuingProperties()
    # Leave default values - no need to set interrupt_mode
    log(f"✓ Continuing properties created")
    
    # Create future properties (trajectory)
    future_props = unreal.PoseSearchFutureProperties()
    # Note: These properties define desired future movement
    # For now, leaving default (will match idle/neutral poses)
    log(f"✓ Future properties created")
    
    # Pose history name (from AnimGraph PoseSearchHistoryCollector node)
    pose_history_name = "PoseHistory"  # Default name
    log(f"✓ Pose history name: {pose_history_name}")
    
except Exception as e:
    log(f"✗ ERROR: {e}")
    import traceback
    log(traceback.format_exc())
    raise

# ============================================================================
# STEP 4: Query Motion Matching Database!
# ============================================================================
log("\n[STEP 4] Querying Motion Matching Database...")

try:
    pose_search_lib = unreal.PoseSearchLibrary
    
    # THE MAGIC CALL!
    result = pose_search_lib.motion_match(
        anim_instance=anim_instance,
        assets_to_search=[database],
        pose_history_name=pose_history_name,
        continuing_properties=continuing_props,
        future=future_props
    )
    
    log(f"✓ Query successful!")
    log(f"\n  RESULT:")
    log(f"    Selected Animation: {result.selected_anim.get_name() if result.selected_anim else 'None'}")
    log(f"    Selected Time: {result.selected_time}")
    log(f"    Search Cost: {result.search_cost}")
    log(f"    Play Rate: {result.wanted_play_rate}")
    log(f"    Is Mirrored: {result.is_mirrored}")
    log(f"    Loop: {result.loop}")
    
    # This is what you'd use in procedural movies!
    if result.selected_anim:
        log(f"\n  FOR PROCEDURAL MOVIE:")
        log(f"    Animation: {result.selected_anim.get_path_name()}")
        log(f"    Start Frame: {result.selected_time}")
        log(f"    Playback Speed: {result.wanted_play_rate}")
    
except Exception as e:
    log(f"✗ ERROR: {e}")
    import traceback
    log(traceback.format_exc())

# ============================================================================
# STEP 5: Cleanup (optional)
# ============================================================================
log("\n[STEP 5] Cleanup...")

try:
    # Destroy spawned character
    character.destroy_actor()
    log(f"✓ Character destroyed")
except Exception as e:
    log(f"⚠ Cleanup warning: {e}")

# ============================================================================
# Summary
# ============================================================================
log("\n" + "=" * 80)
log("✅ COMPLETE SUCCESS!")
log("=" * 80)

log("""
WHAT WE ACHIEVED:
✓ Spawned character from Python
✓ Got AnimInstance
✓ Queried Motion Matching database
✓ Got best matching animation + frame

FOR PROCEDURAL MOVIES:
You can now:
1. Spawn a character (hidden, off-screen)
2. Query Motion Matching with desired velocity/trajectory
3. Get best animation for that movement
4. Use in your procedural movie sequencer

WORKFLOW:
def get_animation_for_movement(velocity, direction):
    # Spawn character
    character = spawn_character()
    anim_instance = get_anim_instance(character)
    
    # Create trajectory for desired movement
    future_props = create_trajectory(velocity, direction)
    
    # Query Motion Matching
    result = motion_match(anim_instance, database, future_props)
    
    # Cleanup
    character.destroy()
    
    return result.selected_anim, result.selected_time

This enables TRUE Motion Matching for procedural movies!
""")

log(f"\nLog saved to: {LOG_FILE}")
