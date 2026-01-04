"""
Configure Motion Matching Database - V2
Based on systematic API exploration

This version uses the ACTUAL API discovered through reflection:
- PoseSearchFeatureChannel_Position
- PoseSearchFeatureChannel_Trajectory  
- PoseSearchDatabaseSequence
- Proper array manipulation
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
    old_logs = glob.glob(r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\configure_v2_*.log")
    for old_log in old_logs:
        try:
            os.remove(old_log)
        except:
            pass
except:
    pass

# Create timestamped log file
timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file = rf"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\configure_v2_{timestamp}.log"

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
        f.write(f"Motion Matching Database Configuration V2\n")
        f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
    log(f"Log file: {log_file}")
except Exception as e:
    print(f"ERROR creating log file: {e}")


def add_trajectory_channel_to_schema(schema):
    """Add a Trajectory channel to the schema"""
    log_header("Adding Trajectory Channel")
    
    try:
        # Get current channels
        channels = schema.get_editor_property("channels")
        if channels is None:
            channels = []
        
        log(f"Current channels: {len(channels)}")
        
        # Create a Trajectory channel
        trajectory_channel = unreal.PoseSearchFeatureChannel_Trajectory()
        log(f"✓ Created Trajectory channel instance")
        
        # Try to configure it
        try:
            # Explore what properties it has
            trajectory_channel.set_editor_property("weight", 1.0)
            log(f"  Set weight: 1.0")
        except Exception as e:
            log(f"  Note: {e}")
        
        # Append to channels array
        channels.append(trajectory_channel)
        log(f"  Appended to channels array")
        
        # Set back to schema
        schema.set_editor_property("channels", channels)
        log(f"  Set channels array back to schema")
        
        # Verify
        new_channels = schema.get_editor_property("channels")
        log(f"✓ Trajectory channel added! New count: {len(new_channels)}")
        
        # Save schema
        unreal.EditorAssetLibrary.save_loaded_asset(schema)
        log(f"✓ Schema saved")
        
        return True
        
    except Exception as e:
        log(f"✗ Error adding trajectory channel: {e}")
        log(traceback.format_exc())
        return False


def add_pose_channel_to_schema(schema):
    """Add a Pose channel to the schema"""
    log_header("Adding Pose Channel")
    
    try:
        # Get current channels
        channels = schema.get_editor_property("channels")
        if channels is None:
            channels = []
        
        log(f"Current channels: {len(channels)}")
        
        # Create a Pose channel
        pose_channel = unreal.PoseSearchFeatureChannel_Pose()
        log(f"✓ Created Pose channel instance")
        
        # Try to configure it
        try:
            pose_channel.set_editor_property("weight", 1.0)
            log(f"  Set weight: 1.0")
        except Exception as e:
            log(f"  Note: {e}")
        
        # Append to channels array
        channels.append(pose_channel)
        log(f"  Appended to channels array")
        
        # Set back to schema
        schema.set_editor_property("channels", channels)
        log(f"  Set channels array back to schema")
        
        # Verify
        new_channels = schema.get_editor_property("channels")
        log(f"✓ Pose channel added! New count: {len(new_channels)}")
        
        # Save schema
        unreal.EditorAssetLibrary.save_loaded_asset(schema)
        log(f"✓ Schema saved")
        
        return True
        
    except Exception as e:
        log(f"✗ Error adding pose channel: {e}")
        log(traceback.format_exc())
        return False


def add_animations_to_database_v2(database, animation_list):
    """Add animations using discovered API"""
    log_header("Adding Animations to Database V2")
    
    if not animation_list:
        log("⚠ No animations provided")
        return False
    
    try:
        # Check current animation count
        current_count = database.get_num_animation_assets()
        log(f"Current animation count: {current_count}")
        
        # Try to add animations using PoseSearchDatabaseSequence
        log(f"\nAttempting to add {len(animation_list)} animations...")
        
        added = 0
        for i, anim_info in enumerate(animation_list[:10]):  # First 10
            try:
                log(f"\n  Adding {anim_info['name']}...")
                
                # Create a PoseSearchDatabaseSequence
                db_sequence = unreal.PoseSearchDatabaseSequence()
                log(f"    Created PoseSearchDatabaseSequence")
                
                # Try to set the sequence
                db_sequence.set_editor_property("sequence", anim_info["asset"])
                log(f"    Set sequence property")
                
                # Now we need to add this to the database
                # The challenge is the database doesn't expose an add method
                # Let's try to get the animation_assets array and modify it
                
                # This might not work, but let's try
                try:
                    anim_assets = database.get_editor_property("animation_assets")
                    if anim_assets is None:
                        anim_assets = []
                    
                    anim_assets.append(db_sequence)
                    database.set_editor_property("animation_assets", anim_assets)
                    
                    log(f"    ✓ Added via animation_assets property")
                    added += 1
                    
                except Exception as e:
                    log(f"    ✗ Could not add via animation_assets: {e}")
                
            except Exception as e:
                log(f"    ✗ Error: {e}")
                continue
        
        if added > 0:
            # Save database
            unreal.EditorAssetLibrary.save_loaded_asset(database)
            log(f"\n✓ Database saved with {added} animations added")
            
            # Verify
            new_count = database.get_num_animation_assets()
            log(f"New animation count: {new_count}")
            
            return True
        else:
            log(f"\n⚠ Could not add animations programmatically")
            log(f"  Manual addition still required")
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
    
    # Focus on essential animations
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


def configure_database_v2():
    """Main configuration function using discovered API"""
    log_header("MOTION MATCHING DATABASE CONFIGURATION V2")
    log("Using API discovered through systematic exploration")
    
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
        
        # Add Trajectory channel
        trajectory_added = add_trajectory_channel_to_schema(schema)
        
        # Add Pose channel
        pose_added = add_pose_channel_to_schema(schema)
        
        # Find animations
        animations = find_core_animations()
        
        # Add animations
        anims_added = add_animations_to_database_v2(database, animations)
        
        # Summary
        log_header("CONFIGURATION COMPLETE")
        log(f"Trajectory channel added: {trajectory_added}")
        log(f"Pose channel added: {pose_added}")
        log(f"Animations added: {anims_added}")
        log(f"\nLog file: {log_file}")
        
        if trajectory_added and pose_added:
            log("\n✓ Schema configuration successful!")
        
        if not anims_added:
            log("\n⚠ Animation addition may require manual steps")
            log("  Check the database in the editor")
        
        return True
        
    except Exception as e:
        log_header("FATAL ERROR")
        log(f"✗ Unexpected error: {e}")
        log(traceback.format_exc())
        log(f"\nLog file: {log_file}")
        return False


if __name__ == "__main__":
    result = configure_database_v2()
    log(f"\nFinal result: {'SUCCESS' if result else 'FAILED'}")
