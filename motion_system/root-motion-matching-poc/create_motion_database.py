"""
Motion Matching Database Setup

This module creates and configures Pose Search assets for motion matching with Manny.
Includes schema creation, database creation, and animation population.
"""
import unreal
import sys
import os

# Add parent directory to path for imports
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = r"C:\UnrealProjects\Coding\unreal\motion_system\root-motion-matching-poc"

parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import motion system logger
import time
import traceback
import glob

# Delete old log files
try:
    old_logs = glob.glob(r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\database_creation_*.log")
    for old_log in old_logs:
        try:
            os.remove(old_log)
        except:
            pass
except:
    pass

# Create timestamped log file
timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file = rf"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\database_creation_{timestamp}.log"

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
    # Fallback if motion_system not available
    def log(msg):
        print(f"  {msg}")
        log_to_file(f"  {msg}")
    def log_header(msg):
        print(f"\n{'='*80}\n{msg}\n{'='*80}")
        log_to_file(f"\n{'='*80}\n{msg}\n{'='*80}")

# Initialize log file
try:
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Motion Matching Database Creation Log\n")
        f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
    log(f"Log file: {log_file}")
except Exception as e:
    print(f"ERROR creating log file: {e}")


def check_plugin_availability():
    """Check if PoseSearch plugin is available"""
    log_header("Checking Plugin Availability")
    
    try:
        # Try to access PoseSearch classes
        _ = unreal.PoseSearchDatabase
        _ = unreal.PoseSearchSchema
        log("✓ PoseSearch plugin classes are available")
        return True
    except AttributeError as e:
        log(f"✗ PoseSearch plugin not available: {e}")
        log("  Please enable the 'Pose Search' plugin in Unreal Engine")
        return False


def find_manny_skeleton():
    """Find the Manny skeleton asset"""
    log_header("Finding Manny Skeleton")
    
    # Common paths for Manny skeleton (updated for ThirdPerson project)
    skeleton_paths = [
        "/Game/Characters/Mannequins/Meshes/SK_Mannequin",
        "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple",
        "/Game/ThirdPerson/Characters/Mannequins/Meshes/SK_Mannequin",
    ]
    
    for path in skeleton_paths:
        log(f"Trying: {path}")
        skeleton = unreal.load_object(None, path)
        if skeleton:
            log(f"✓ Found skeleton: {path}")
            return skeleton, path
    
    # If not found, try searching
    log("Skeleton not found in common paths, searching...")
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    # Search for Skeleton assets
    filter = unreal.ARFilter(
        class_names=["Skeleton"],
        recursive_paths=True,
        package_paths=["/Game/Characters"]
    )
    
    assets = asset_registry.get_assets(filter)
    for asset_data in assets:
        asset_name = asset_data.asset_name
        if "Manny" in asset_name or "Mannequin" in asset_name:
            skeleton = asset_data.get_asset()
            path = asset_data.object_path
            log(f"✓ Found skeleton via search: {path}")
            return skeleton, str(path)
    
    log("✗ Could not find Manny skeleton")
    return None, None


def find_manny_animations(skeleton_path):
    """Find Manny locomotion animations"""
    log_header("Finding Manny Animations")
    
    # Animation folder paths for ThirdPerson project
    anim_folders = [
        "/Game/Characters/Mannequins/Anims",
        "/Game/Characters/Mannequins/Anims/Unarmed",
        "/Game/ThirdPerson/Characters/Mannequins/Anims",
    ]
    
    animations = []
    
    try:
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        log("Asset registry obtained")
    except Exception as e:
        log(f"✗ ERROR: Could not get asset registry: {e}")
        log(traceback.format_exc())
        return animations
    
    for folder in anim_folders:
        log(f"Searching folder: {folder}")
        
        try:
            # Search for AnimSequence assets
            filter = unreal.ARFilter(
                class_names=["AnimSequence"],
                recursive_paths=True,
                package_paths=[folder]
            )
            
            assets = asset_registry.get_assets(filter)
            log(f"  Found {len(assets)} total assets in {folder}")
            
            for asset_data in assets:
                try:
                    asset_name = str(asset_data.asset_name)
                    
                    # Filter for locomotion animations
                    # Look for common patterns: Walk, Run, Idle, Jog, Sprint, Jump, MM_ prefix
                    locomotion_keywords = ["Walk", "Run", "Idle", "Jog", "Sprint", "Jump", "MM_", "Fall", "Land", "Dash"]
                    
                    if any(keyword.lower() in asset_name.lower() for keyword in locomotion_keywords):
                        anim = asset_data.get_asset()
                        if anim:
                            # Use package_name instead of object_path
                            asset_path = str(asset_data.package_name)
                            animations.append({
                                "asset": anim,
                                "name": asset_name,
                                "path": asset_path
                            })
                            log(f"  Found: {asset_name}")
                except Exception as e:
                    log(f"  Warning: Error processing asset: {e}")
                    continue
                    
        except Exception as e:
            log(f"  ✗ ERROR searching folder {folder}: {e}")
            log(f"  {traceback.format_exc()}")
            continue
    
    log(f"✓ Found {len(animations)} locomotion animations total")
    return animations


def create_pose_search_schema(skeleton, output_path="/Game/MotionMatching/MannyMotionSchema"):
    """Create a PoseSearchSchema asset"""
    log_header("Creating Pose Search Schema")
    
    # Check if schema already exists
    if unreal.EditorAssetLibrary.does_asset_exist(output_path):
        log(f"Schema already exists at {output_path}, loading...")
        schema = unreal.load_object(None, output_path)
        if schema:
            log("✓ Loaded existing schema")
            return schema
    
    try:
        # Create the schema asset
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        # Extract package path and asset name
        package_path = output_path.rsplit('/', 1)[0]
        asset_name = output_path.rsplit('/', 1)[1]
        
        log(f"Creating schema at: {package_path}/{asset_name}")
        
        # Create using AssetTools directly without setting factory class
        # The factory will infer the type from the asset_class parameter
        factory = unreal.DataAssetFactory()
        
        schema = asset_tools.create_asset(
            asset_name=asset_name,
            package_path=package_path,
            asset_class=unreal.PoseSearchSchema,
            factory=factory
        )
        
        if schema:
            # Set skeleton reference if available
            if skeleton:
                try:
                    schema.set_editor_property("skeleton", skeleton)
                    log("  Set skeleton reference")
                except Exception as e:
                    log(f"  Warning: Could not set skeleton: {e}")
            
            # Save the asset
            unreal.EditorAssetLibrary.save_loaded_asset(schema)
            log(f"✓ Created schema: {output_path}")
            return schema
        else:
            log("✗ Failed to create schema asset")
            return None
            
    except Exception as e:
        log(f"✗ Error creating schema: {e}")
        import traceback
        log(traceback.format_exc())
        return None


def create_pose_search_database(schema, output_path="/Game/MotionMatching/MannyMotionDatabase"):
    """Create a PoseSearchDatabase asset"""
    log_header("Creating Pose Search Database")
    
    # Check if database already exists
    if unreal.EditorAssetLibrary.does_asset_exist(output_path):
        log(f"Database already exists at {output_path}, loading...")
        database = unreal.load_object(None, output_path)
        if database:
            log("✓ Loaded existing database")
            return database
    
    try:
        # Create the database asset
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        # Extract package path and asset name
        package_path = output_path.rsplit('/', 1)[0]
        asset_name = output_path.rsplit('/', 1)[1]
        
        log(f"Creating database at: {package_path}/{asset_name}")
        
        # Create using DataAssetFactory
        factory = unreal.DataAssetFactory()
        
        database = asset_tools.create_asset(
            asset_name=asset_name,
            package_path=package_path,
            asset_class=unreal.PoseSearchDatabase,
            factory=factory
        )
        
        if database:
            # Link to schema
            if schema:
                try:
                    database.set_editor_property("schema", schema)
                    log("  Linked to schema")
                except Exception as e:
                    log(f"  Warning: Could not link schema: {e}")
            
            # Save the asset
            unreal.EditorAssetLibrary.save_loaded_asset(database)
            log(f"✓ Created database: {output_path}")
            return database
        else:
            log("✗ Failed to create database asset")
            return None
            
    except Exception as e:
        log(f"✗ Error creating database: {e}")
        import traceback
        log(traceback.format_exc())
        return None


def add_animations_to_database(database, animations):
    """Add animation sequences to the PoseSearchDatabase"""
    log_header("Adding Animations to Database")
    
    if not database:
        log("✗ No database provided")
        return False
    
    if not animations:
        log("✗ No animations provided")
        return False
    
    try:
        # Get current animation assets
        current_anims = database.get_editor_property("animation_assets")
        if current_anims is None:
            current_anims = []
        
        log(f"Current animations in database: {len(current_anims)}")
        log(f"Animations to add: {len(animations)}")
        
        # Note: The animation_assets property is an Array of InstancedStruct
        # This is complex to manipulate via Python, so we'll document this
        # and suggest manual addition or use of editor utilities
        
        log("⚠ Note: Adding animations programmatically to PoseSearchDatabase")
        log("  is complex due to InstancedStruct array type.")
        log("  Recommended approach:")
        log("  1. Open the database asset in the editor")
        log("  2. Manually add animations via the UI")
        log("  OR")
        log("  3. Use editor utility widgets or C++ for batch addition")
        
        # List the animations that should be added
        log("\nAnimations found for manual addition:")
        for i, anim_info in enumerate(animations[:10], 1):  # Show first 10
            log(f"  {i}. {anim_info['name']}")
        
        if len(animations) > 10:
            log(f"  ... and {len(animations) - 10} more")
        
        return True
        
    except Exception as e:
        log(f"✗ Error accessing database animations: {e}")
        import traceback
        log(traceback.format_exc())
        return False


def create_motion_matching_database():
    """Main function to create motion matching database"""
    log_header("MOTION MATCHING DATABASE SETUP")
    
    try:
        # Step 1: Check plugin availability
        if not check_plugin_availability():
            log("\n✗ FAILED: PoseSearch plugin not available")
            log("Please enable 'Pose Search' and 'Motion Trajectory' plugins")
            return False
        
        # Step 2: Find Manny skeleton
        skeleton, skeleton_path = find_manny_skeleton()
        if not skeleton:
            log("\n✗ FAILED: Could not find Manny skeleton")
            return False
        
        # Step 3: Find animations
        animations = find_manny_animations(skeleton_path)
        if not animations:
            log("\n⚠ WARNING: No animations found")
            log("Database will be created but empty")
        
        # Step 4: Create schema
        schema = create_pose_search_schema(skeleton)
        if not schema:
            log("\n✗ FAILED: Could not create schema")
            return False
        
        # Step 5: Create database
        database = create_pose_search_database(schema)
        if not database:
            log("\n✗ FAILED: Could not create database")
            return False
        
        # Step 6: Add animations (documentation only for now)
        add_animations_to_database(database, animations)
        
        # Summary
        log_header("SETUP COMPLETE")
        log(f"✓ Schema created: /Game/MotionMatching/MannyMotionSchema")
        log(f"✓ Database created: /Game/MotionMatching/MannyMotionDatabase")
        log(f"✓ Found {len(animations)} animations for manual addition")
        log("\nNext steps:")
        log("1. Open /Game/MotionMatching/MannyMotionDatabase in editor")
        log("2. Configure schema channels (trajectory, bones)")
        log("3. Add animation sequences to database")
        log("4. Build the database index")
        log(f"\nLog file: {log_file}")
        
        return True
        
    except Exception as e:
        log_header("FATAL ERROR")
        log(f"✗ Unexpected error: {e}")
        log(traceback.format_exc())
        log(f"\nLog file: {log_file}")
        return False


if __name__ == "__main__":
    result = create_motion_matching_database()
    log(f"\nFinal result: {'SUCCESS' if result else 'FAILED'}")
