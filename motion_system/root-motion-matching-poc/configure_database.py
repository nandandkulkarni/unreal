"""
Configure Motion Matching Database Programmatically

This script:
1. Adds channels to the PoseSearchSchema (trajectory, bones)
2. Adds animation sequences to the PoseSearchDatabase
3. Builds the database index
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
    old_logs = glob.glob(r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\configure_database_*.log")
    for old_log in old_logs:
        try:
            os.remove(old_log)
        except:
            pass
except:
    pass

# Create timestamped log file
timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file = rf"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\configure_database_{timestamp}.log"

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
        f.write(f"Motion Matching Database Configuration\n")
        f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
    log(f"Log file: {log_file}")
except Exception as e:
    print(f"ERROR creating log file: {e}")


def configure_schema_channels(schema):
    """Add channels to the PoseSearchSchema"""
    log_header("Configuring Schema Channels")
    
    try:
        # Get current channels
        current_channels = schema.get_editor_property("channels")
        if current_channels is None:
            current_channels = []
        
        log(f"Current channels: {len(current_channels)}")
        
        # Try to add a Position channel for the pelvis/root
        try:
            log("\nAttempting to create Position channel...")
            
            # Create a bone reference for pelvis
            bone_ref = unreal.BoneReference()
            bone_ref.bone_name = "pelvis"  # Common pelvis bone name
            
            # Create position channel
            position_channel = unreal.PoseSearchFeatureChannel_Position()
            position_channel.set_editor_property("bone", bone_ref)
            position_channel.set_editor_property("weight", 1.0)
            position_channel.set_editor_property("sample_time_offset", 0.0)
            
            log(f"  Created Position channel for bone: {bone_ref.bone_name}")
            
            # Try to append to channels
            current_channels.append(position_channel)
            schema.set_editor_property("channels", current_channels)
            
            log(f"✓ Added Position channel")
            
        except Exception as e:
            log(f"⚠ Could not add Position channel: {e}")
            log(f"  This may require manual configuration in the editor")
        
        # Save schema
        unreal.EditorAssetLibrary.save_loaded_asset(schema)
        log("\n✓ Schema saved")
        
        return True
        
    except Exception as e:
        log(f"✗ Error configuring schema: {e}")
        log(traceback.format_exc())
        return False


def add_animations_to_database(database, animation_list):
    """Add animation sequences to the database"""
    log_header("Adding Animations to Database")
    
    if not animation_list:
        log("⚠ No animations provided")
        return False
    
    try:
        log(f"Attempting to add {len(animation_list)} animations...")
        
        # Get current animation assets
        try:
            current_anims = database.get_editor_property("animation_assets")
            if current_anims is None:
                current_anims = []
            log(f"Current animations in database: {len(current_anims)}")
        except Exception as e:
            log(f"⚠ Could not read animation_assets: {e}")
            current_anims = []
        
        # Try different approaches to add animations
        added_count = 0
        
        # Approach 1: Try using PoseSearchDatabaseAnimSequence
        try:
            log("\nApproach 1: Using PoseSearchDatabaseAnimSequence...")
            
            for i, anim_info in enumerate(animation_list[:10]):  # Start with first 10
                try:
                    # Create database anim sequence wrapper
                    db_anim = unreal.PoseSearchDatabaseAnimSequence()
                    db_anim.set_editor_property("sequence", anim_info["asset"])
                    
                    # Wrap in InstancedStruct
                    instanced_struct = unreal.InstancedStruct()
                    instanced_struct.set_editor_property("value", db_anim)
                    
                    current_anims.append(instanced_struct)
                    added_count += 1
                    log(f"  Added: {anim_info['name']}")
                    
                except Exception as e:
                    log(f"  ⚠ Could not add {anim_info['name']}: {e}")
                    continue
            
            if added_count > 0:
                database.set_editor_property("animation_assets", current_anims)
                log(f"\n✓ Added {added_count} animations via Approach 1")
            
        except Exception as e:
            log(f"✗ Approach 1 failed: {e}")
            log(traceback.format_exc())
        
        # If Approach 1 didn't work, document manual steps
        if added_count == 0:
            log("\n⚠ Programmatic animation addition not successful")
            log("  This is expected - the API for adding animations is complex")
            log("\nManual steps required:")
            log("  1. Open /Game/MotionMatching/MannyMotionDatabase in editor")
            log("  2. Click 'Add' in Animation Sequences section")
            log("  3. Select animations from the list below:")
            
            for i, anim_info in enumerate(animation_list[:20], 1):
                log(f"     {i}. {anim_info['name']}")
            
            if len(animation_list) > 20:
                log(f"     ... and {len(animation_list) - 20} more")
        
        # Save database
        unreal.EditorAssetLibrary.save_loaded_asset(database)
        log("\n✓ Database saved")
        
        return added_count > 0
        
    except Exception as e:
        log(f"✗ Error adding animations: {e}")
        log(traceback.format_exc())
        return False


def build_database(database):
    """Build the database index"""
    log_header("Building Database Index")
    
    try:
        # Try to find and call build method
        log("Attempting to build database...")
        
        # Check if database has a build method
        if hasattr(database, 'build_index'):
            database.build_index()
            log("✓ Called build_index()")
            return True
        elif hasattr(database, 'build'):
            database.build()
            log("✓ Called build()")
            return True
        else:
            log("⚠ No build method found on database")
            log("  You may need to build manually in the editor:")
            log("  1. Open the database asset")
            log("  2. Click 'Build Database' button")
            return False
            
    except Exception as e:
        log(f"⚠ Could not build database: {e}")
        log("  Manual build required in editor")
        return False


def find_animations():
    """Find animations for the database"""
    log_header("Finding Animations")
    
    anim_folders = [
        "/Game/Characters/Mannequins/Anims/Unarmed",
    ]
    
    animations = []
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    for folder in anim_folders:
        filter = unreal.ARFilter(
            class_names=["AnimSequence"],
            recursive_paths=True,
            package_paths=[folder]
        )
        
        assets = asset_registry.get_assets(filter)
        
        for asset_data in assets:
            try:
                asset_name = str(asset_data.asset_name)
                
                # Focus on basic locomotion
                if any(keyword in asset_name for keyword in ["Walk_Fwd", "Jog_Fwd", "Idle", "Jump", "Land", "Fall"]):
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
    
    log(f"\n✓ Found {len(animations)} core locomotion animations")
    return animations


def configure_database():
    """Main configuration function"""
    log_header("MOTION MATCHING DATABASE CONFIGURATION")
    
    try:
        # Load schema
        log_header("Loading Schema")
        schema = unreal.load_object(None, "/Game/MotionMatching/MannyMotionSchema")
        if not schema:
            log("✗ Schema not found")
            return False
        log("✓ Schema loaded")
        
        # Load database
        log_header("Loading Database")
        database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
        if not database:
            log("✗ Database not found")
            return False
        log("✓ Database loaded")
        
        # Configure schema channels
        schema_configured = configure_schema_channels(schema)
        
        # Find animations
        animations = find_animations()
        
        # Add animations to database
        anims_added = add_animations_to_database(database, animations)
        
        # Build database
        db_built = build_database(database)
        
        # Summary
        log_header("CONFIGURATION COMPLETE")
        log(f"Schema channels configured: {schema_configured}")
        log(f"Animations added: {anims_added}")
        log(f"Database built: {db_built}")
        log(f"\nLog file: {log_file}")
        
        if not anims_added or not db_built:
            log("\n⚠ Some steps require manual completion in the editor")
            log("See log for details")
        
        return True
        
    except Exception as e:
        log_header("FATAL ERROR")
        log(f"✗ Unexpected error: {e}")
        log(traceback.format_exc())
        log(f"\nLog file: {log_file}")
        return False


if __name__ == "__main__":
    result = configure_database()
    log(f"\nFinal result: {'SUCCESS' if result else 'FAILED'}")
