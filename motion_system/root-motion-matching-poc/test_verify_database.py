"""
Test Script: Verify Motion Matching Database and Spawn Manny

This script:
1. Verifies the database assets exist
2. Spawns Manny character
3. Checks if motion matching is configured
4. Logs all results
"""
import unreal
import sys
import os
import time
import traceback
import glob

# Add parent directory to path
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = r"C:\UnrealProjects\Coding\unreal\motion_system\root-motion-matching-poc"

parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Delete old log files
try:
    old_logs = glob.glob(r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\test_verify_*.log")
    for old_log in old_logs:
        try:
            os.remove(old_log)
        except:
            pass
except:
    pass

# Create timestamped log file
timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file = rf"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\test_verify_{timestamp}.log"

def log_to_file(msg):
    """Write to log file"""
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

# Initialize log file
try:
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Motion Matching Verification Test\n")
        f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
    log(f"Log file: {log_file}")
except Exception as e:
    print(f"ERROR creating log file: {e}")


def verify_database_assets():
    """Verify that database assets exist"""
    log_header("Verifying Database Assets")
    
    assets_to_check = {
        "Schema": "/Game/MotionMatching/MannyMotionSchema",
        "Database": "/Game/MotionMatching/MannyMotionDatabase",
        "Skeleton": "/Game/Characters/Mannequins/Meshes/SK_Mannequin",
        "Manny Mesh": "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple",
    }
    
    results = {}
    
    for name, path in assets_to_check.items():
        try:
            asset = unreal.load_object(None, path)
            if asset:
                log(f"✓ {name}: Found")
                log(f"  Path: {path}")
                log(f"  Type: {type(asset).__name__}")
                results[name] = True
            else:
                log(f"✗ {name}: Not found")
                log(f"  Path: {path}")
                results[name] = False
        except Exception as e:
            log(f"✗ {name}: Error loading")
            log(f"  Path: {path}")
            log(f"  Error: {e}")
            results[name] = False
    
    return results


def check_database_configuration():
    """Check if database has animations configured"""
    log_header("Checking Database Configuration")
    
    try:
        database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
        if not database:
            log("✗ Database not found")
            return False
        
        log("✓ Database loaded")
        
        # Try to get properties (may not work via Python)
        try:
            # Check if we can access any properties
            log("Attempting to read database properties...")
            log(f"  Database class: {type(database).__name__}")
            
            # List available properties
            props = dir(database)
            log(f"  Available attributes: {len([p for p in props if not p.startswith('_')])}")
            
            log("\n⚠ Note: Animation configuration must be done manually in the editor")
            log("  1. Open the database asset")
            log("  2. Add animation sequences")
            log("  3. Build the database")
            
        except Exception as e:
            log(f"  Property access limited (expected): {e}")
        
        return True
        
    except Exception as e:
        log(f"✗ Error checking database: {e}")
        log(traceback.format_exc())
        return False


def spawn_manny_test():
    """Spawn Manny character for testing"""
    log_header("Spawning Manny Character")
    
    try:
        # Load Manny mesh
        manny_mesh = unreal.load_object(None, "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple")
        if not manny_mesh:
            log("✗ Could not load Manny mesh")
            return None
        
        log(f"✓ Loaded Manny mesh: {manny_mesh.get_name()}")
        
        # Spawn location
        location = unreal.Vector(0, 0, 100)
        rotation = unreal.Rotator(0, 0, 0)
        
        # Spawn skeletal mesh actor
        manny = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SkeletalMeshActor,
            location,
            rotation
        )
        
        if manny:
            manny.set_actor_label("Test_Manny_MotionMatching")
            
            # Set the mesh
            skel_comp = manny.skeletal_mesh_component
            skel_comp.set_skinned_asset_and_update(manny_mesh)
            
            log(f"✓ Spawned Manny at {location}")
            log(f"  Actor: {manny.get_actor_label()}")
            log(f"  Mesh: {manny_mesh.get_name()}")
            
            return manny
        else:
            log("✗ Failed to spawn Manny")
            return None
            
    except Exception as e:
        log(f"✗ Error spawning Manny: {e}")
        log(traceback.format_exc())
        return None


def cleanup_test_actors():
    """Clean up any previous test actors"""
    log_header("Cleaning Up Previous Test Actors")
    
    try:
        all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
        deleted = 0
        
        for actor in all_actors:
            try:
                label = actor.get_actor_label()
                if "Test_Manny" in label or "MotionMatching" in label:
                    unreal.EditorLevelLibrary.destroy_actor(actor)
                    log(f"  Deleted: {label}")
                    deleted += 1
            except:
                pass
        
        if deleted > 0:
            log(f"✓ Cleaned up {deleted} test actor(s)")
        else:
            log("  No test actors to clean up")
        
        return True
        
    except Exception as e:
        log(f"⚠ Warning: Cleanup error: {e}")
        return False


def run_verification_test():
    """Main test function"""
    log_header("MOTION MATCHING VERIFICATION TEST")
    
    try:
        # Step 1: Cleanup
        cleanup_test_actors()
        
        # Step 2: Verify assets
        asset_results = verify_database_assets()
        
        all_assets_found = all(asset_results.values())
        if not all_assets_found:
            log("\n⚠ WARNING: Some assets not found")
            log("Run create_motion_database.py first")
            return False
        
        # Step 3: Check database configuration
        db_configured = check_database_configuration()
        
        # Step 4: Spawn Manny
        manny = spawn_manny_test()
        
        if not manny:
            log("\n✗ FAILED: Could not spawn Manny")
            return False
        
        # Summary
        log_header("TEST COMPLETE")
        log("✓ All database assets verified")
        log("✓ Manny spawned successfully")
        log(f"\nCheck the scene for actor: Test_Manny_MotionMatching")
        log(f"Log file: {log_file}")
        
        if not db_configured:
            log("\n⚠ Next step: Configure database manually in editor")
        
        return True
        
    except Exception as e:
        log_header("FATAL ERROR")
        log(f"✗ Unexpected error: {e}")
        log(traceback.format_exc())
        log(f"\nLog file: {log_file}")
        return False


if __name__ == "__main__":
    result = run_verification_test()
    log(f"\nFinal result: {'SUCCESS' if result else 'FAILED'}")
