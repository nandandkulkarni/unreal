"""
Configure Database V3 - Final Implementation

Based on:
1. Deep API exploration results
2. Official Unreal Engine Python API documentation
3. Confirmed that animation_assets is Array[InstancedStruct] and Read-Write

This version uses InstancedStruct to properly wrap PoseSearchDatabaseSequence
"""
import unreal
import sys
import os
import time
import traceback
import glob

# Add parent directory
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = r"C:\UnrealProjects\Coding\unreal\motion_system\root-motion-matching-poc"

parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Delete old logs
try:
    old_logs = glob.glob(r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\configure_v3_*.log")
    for old_log in old_logs:
        try:
            os.remove(old_log)
        except:
            pass
except:
    pass

timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file = rf"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\configure_v3_{timestamp}.log"

def log_to_file(msg):
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception as e:
        print(f"ERROR writing to log: {e}")

try:
    from motion_system import logger
    def log(msg):
        logger.log(msg)
        log_to_file(msg)
    def log_header(msg):
        logger.log_header(msg)
        log_to_file("="*80)
        log_to_file(msg)
        log_to_file("="*80)
except ImportError:
    def log(msg):
        print(f"  {msg}")
        log_to_file(f"  {msg}")
    def log_header(msg):
        print(f"\n{'='*80}\n{msg}\n{'='*80}")
        log_to_file(f"\n{'='*80}\n{msg}\n{'='*80}")

# Initialize log
try:
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Motion Matching Database Configuration V3\n")
        f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
    log(f"Log file: {log_file}")
except Exception as e:
    print(f"ERROR creating log file: {e}")


def add_animations_v3(database, animation_list):
    """Add animations using InstancedStruct approach"""
    log_header("Adding Animations V3 - InstancedStruct Approach")
    
    if not animation_list:
        log("⚠ No animations provided")
        return False
    
    try:
        current_count = database.get_num_animation_assets()
        log(f"Current animation count: {current_count}")
        
        log(f"\nAttempting to add {len(animation_list)} animations...")
        
        # Approach: Use call_method with proper tuple args
        log("\n--- Approach 1: call_method with tuple ---")
        added = 0
        for i, anim_info in enumerate(animation_list[:5]):  # Test with first 5
            try:
                log(f"\n  Adding {anim_info['name']}...")
                
                # Create PoseSearchDatabaseSequence
                db_seq = unreal.PoseSearchDatabaseSequence()
                db_seq.set_editor_property("sequence", anim_info["asset"])
                log(f"    Created and configured PoseSearchDatabaseSequence")
                
                # Try call_method with tuple
                try:
                    result = database.call_method("AddAnimationAsset", (db_seq,))
                    log(f"    ✓ call_method succeeded! Result: {result}")
                    added += 1
                except Exception as e:
                    log(f"    ✗ call_method failed: {e}")
                
            except Exception as e:
                log(f"    ✗ Error: {e}")
                continue
        
        if added > 0:
            unreal.EditorAssetLibrary.save_loaded_asset(database)
            log(f"\n✓ Added {added} animations!")
            new_count = database.get_num_animation_assets()
            log(f"New animation count: {new_count}")
            return True
        
        # Approach 2: Try using InstancedStruct directly
        log("\n--- Approach 2: InstancedStruct wrapper ---")
        try:
            # Create InstancedStruct
            instanced_struct = unreal.InstancedStruct()
            log("  Created InstancedStruct")
            
            # Create and configure sequence
            db_seq = unreal.PoseSearchDatabaseSequence()
            db_seq.set_editor_property("sequence", animation_list[0]["asset"])
            log("  Created PoseSearchDatabaseSequence")
            
            # Try to set the struct value
            try:
                instanced_struct.set_editor_property("value", db_seq)
                log("  ✓ Set value on InstancedStruct")
                
                # Now try to add via call_method
                result = database.call_method("AddAnimationAsset", (instanced_struct,))
                log(f"  ✓ Added via InstancedStruct! Result: {result}")
                
                unreal.EditorAssetLibrary.save_loaded_asset(database)
                new_count = database.get_num_animation_assets()
                log(f"  New count: {new_count}")
                return True
                
            except Exception as e:
                log(f"  ✗ InstancedStruct approach failed: {e}")
        
        except Exception as e:
            log(f"  ✗ Could not create InstancedStruct: {e}")
        
        # If nothing worked
        log("\n⚠ Could not add animations programmatically")
        log("  Manual addition required (5 minutes)")
        return False
        
    except Exception as e:
        log(f"✗ Error: {e}")
        log(traceback.format_exc())
        return False


def find_core_animations():
    """Find core locomotion animations"""
    log_header("Finding Core Animations")
    
    animations = []
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    filter = unreal.ARFilter(
        class_names=["AnimSequence"],
        recursive_paths=True,
        package_paths=["/Game/Characters/Mannequins/Anims/Unarmed"]
    )
    
    assets = asset_registry.get_assets(filter)
    
    essential = ["Idle", "Walk_Fwd", "Jog_Fwd", "Jump", "Fall", "Land"]
    
    for asset_data in assets:
        try:
            asset_name = str(asset_data.asset_name)
            
            if any(keyword in asset_name for keyword in essential):
                anim = asset_data.get_asset()
                if anim:
                    animations.append({
                        "asset": anim,
                        "name": asset_name,
                        "path": str(asset_data.package_name)
                    })
                    log(f"  Found: {asset_name}")
        except:
            continue
    
    log(f"\n✓ Found {len(animations)} core animations")
    return animations


def configure_database_v3():
    """Main configuration V3"""
    log_header("MOTION MATCHING DATABASE CONFIGURATION V3")
    log("Final attempt using all discovered API methods")
    
    try:
        # Load database
        log_header("Loading Database")
        database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
        if not database:
            log("✗ Database not found")
            return False
        log("✓ Database loaded")
        
        # Find animations
        animations = find_core_animations()
        
        # Add animations using V3 approach
        anims_added = add_animations_v3(database, animations)
        
        # Summary
        log_header("CONFIGURATION COMPLETE")
        log(f"Animations added: {anims_added}")
        log(f"\nLog file: {log_file}")
        
        if anims_added:
            log("\n✓ Animation addition successful!")
            log("  Next: Build database in editor")
        else:
            log("\n⚠ Animation addition requires manual steps")
            log("  See MANUAL_CONFIG_GUIDE.md")
        
        return True
        
    except Exception as e:
        log_header("FATAL ERROR")
        log(f"✗ Unexpected error: {e}")
        log(traceback.format_exc())
        log(f"\nLog file: {log_file}")
        return False


if __name__ == "__main__":
    result = configure_database_v3()
    log(f"\nFinal result: {'SUCCESS' if result else 'FAILED'}")
