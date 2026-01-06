"""
Find animation folders in the project
"""

import unreal
import os

LOG_FILE = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs\find_anim_folders.log"

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

log("Finding animation folders...")

# Check Characters folder structure
try:
    chars_folders = unreal.EditorAssetLibrary.list_assets("/Game/Characters", recursive=False, include_folder=True)
    log("\n/Game/Characters structure:")
    for folder in chars_folders[:20]:
        log(f"  {folder}")
except Exception as e:
    log(f"Error: {e}")

# Check Mannequins folder
try:
    mann_folders = unreal.EditorAssetLibrary.list_assets("/Game/Characters/Mannequins", recursive=False, include_folder=True)
    log("\n/Game/Characters/Mannequins structure:")
    for folder in mann_folders[:20]:
        log(f"  {folder}")
except Exception as e:
    log(f"Error: {e}")

# Try to find any AnimSequence assets
try:
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    filter = unreal.ARFilter(
        class_names=["AnimSequence"],
        recursive_paths=True,
        package_paths=["/Game/Characters"]
    )
    
    assets = asset_registry.get_assets(filter)
    log(f"\n✓ Found {len(assets)} total AnimSequence assets")
    
    # Show first 20
    log("\nFirst 20 animation assets:")
    for i, asset_data in enumerate(assets[:20], 1):
        path = str(asset_data.package_name)
        name = str(asset_data.asset_name)
        log(f"  {i}. {name}")
        log(f"      Path: {path}")
        
except Exception as e:
    log(f"Error searching: {e}")

log(f"\nLog: {LOG_FILE}")
