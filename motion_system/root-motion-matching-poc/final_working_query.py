"""
FINAL WORKING EXAMPLE: Motion Matching Query with Results

This demonstrates a complete Motion Matching query that returns
actual animation results for use in procedural movies.
"""

import unreal
import os
from datetime import datetime

LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs"
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIR, f"final_working_query_{timestamp}.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

log("=" * 80)
log("FINAL WORKING MOTION MATCHING QUERY")
log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 80)

# Spawn character and get AnimInstance
log("\n[1] Setting up runtime context...")
editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = editor_subsystem.get_editor_world()
character_bp = unreal.load_object(None, "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
character = unreal.EditorLevelLibrary.spawn_actor_from_object(
    character_bp, unreal.Vector(0, 0, 100), unreal.Rotator(0, 0, 0)
)
skel_comp = character.get_components_by_class(unreal.SkeletalMeshComponent)[0]
anim_instance = skel_comp.get_anim_instance()
log(f"✓ AnimInstance ready: {anim_instance.get_name()}")

# Load database
database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
log(f"✓ Database loaded with {unreal.AAANKPoseBlueprintLibrary.get_animation_count(database)} animations")

# Test different movement scenarios
log("\n" + "=" * 80)
log("TESTING DIFFERENT MOVEMENT SCENARIOS")
log("=" * 80)

scenarios = [
    ("Idle/Standing", None),
    ("Walking Forward", "/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd"),
    ("Jogging Forward", "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd"),
]

for scenario_name, anim_path in scenarios:
    log(f"\n--- Scenario: {scenario_name} ---")
    
    # Create query parameters
    continuing_props = unreal.PoseSearchContinuingProperties()
    future_props = unreal.PoseSearchFutureProperties()
    
    # Set desired animation type (if any)
    if anim_path:
        desired_anim = unreal.load_object(None, anim_path)
        if desired_anim:
            future_props.animation = desired_anim
            future_props.animation_time = 0.0
            future_props.interval_time = 0.5
            log(f"  Desired animation: {desired_anim.get_name()}")
    
    # Query Motion Matching
    try:
        result = unreal.PoseSearchLibrary.motion_match(
            anim_instance=anim_instance,
            assets_to_search=[database],
            pose_history_name="PoseHistory",
            continuing_properties=continuing_props,
            future=future_props
        )
        
        if result.selected_anim:
            log(f"  ✓ MATCH FOUND:")
            log(f"    Animation: {result.selected_anim.get_name()}")
            log(f"    Path: {result.selected_anim.get_path_name()}")
            log(f"    Start Time: {result.selected_time:.2f}s")
            log(f"    Search Cost: {result.search_cost:.2f}")
            log(f"    Play Rate: {result.wanted_play_rate:.2f}x")
            log(f"    Mirrored: {result.is_mirrored}")
            
            log(f"\n  FOR PROCEDURAL MOVIE:")
            log(f"    track.add_section(")
            log(f"        animation='{result.selected_anim.get_path_name()}',")
            log(f"        start_time={result.selected_time:.2f},")
            log(f"        play_rate={result.wanted_play_rate:.2f}")
            log(f"    )")
        else:
            log(f"  ⚠ No match found (cost: {result.search_cost})")
            
    except Exception as e:
        log(f"  ✗ ERROR: {e}")

# Cleanup
character.destroy_actor()
log(f"\n✓ Cleanup complete")

log("\n" + "=" * 80)
log("✅ DEMONSTRATION COMPLETE")
log("=" * 80)
log(f"\nLog: {LOG_FILE}")
