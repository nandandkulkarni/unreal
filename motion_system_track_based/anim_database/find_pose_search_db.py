"""
Find Pose Search Databases

Searches for assets of type PoseSearchDatabase in the project.
"""
import unreal
import os

OUTPUT_FILE = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\found_psz.txt"

def log(msg):
    print(msg)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Clear file
with open(OUTPUT_FILE, 'w') as f: f.write("")

assets = unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_class("PoseSearchDatabase", True)

log(f"Found {len(assets)} PoseSearchDatabase assets:")
for asset in assets:
    log(f"  {asset.package_name}")
    
    # Load and inspect
    obj = unreal.EditorAssetLibrary.load_asset(asset.package_name)
    if obj:
        log(f"    Loaded: {obj}")
        # Try to print properties
        log(f"    Type: {type(obj)}")
        
        # Check if we can access animations
        # Usually databases have a list of 'databases' or 'animations'
        # Inspect properties via dir()
        # properties = dir(obj)
        # log(f"    Properties: {properties[:10]}...") # Too spammy
