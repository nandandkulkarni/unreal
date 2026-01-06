"""
Diagnostic Script - Find Belica Animations

This script searches for Belica-related assets in the project to identify
the correct folder path.
"""

import unreal

# Output file
OUTPUT_FILE = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\anim_database\diagnostic_output.txt"

def log(msg):
    print(msg)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Clear previous output
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write("")

log("=" * 80)
log("DIAGNOSTIC: SEARCHING FOR BELICA ASSETS")
log("=" * 80)

# Search patterns
search_patterns = [
    "/Game/ParagonLtBelica",
    "/Game/Paragon",
    "/Game/Characters/Belica",
    "/Game/Heroes/Belica",
]

log("\n--- Searching for Belica folders ---")
for pattern in search_patterns:
    log(f"\nChecking: {pattern}")
    try:
        # Check if path exists
        if unreal.EditorAssetLibrary.does_directory_exist(pattern):
            log(f"  ✓ Directory exists!")
            
            # List subdirectories
            subdirs = unreal.EditorAssetLibrary.list_assets(pattern, recursive=False, include_folder=True)
            log(f"  Found {len(subdirs)} items:")
            for subdir in subdirs[:10]:  # Show first 10
                log(f"    - {subdir}")
        else:
            log(f"  ✗ Directory not found")
    except Exception as e:
        log(f"  ✗ Error: {e}")

# Search for any Belica-related assets
log("\n--- Searching for 'Belica' in asset names ---")
try:
    # Get asset registry
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    # Search for assets with "Belica" in the name
    all_assets = asset_registry.get_all_assets()
    
    belica_assets = []
    for asset_data in all_assets:
        asset_name = str(asset_data.asset_name)
        package_path = str(asset_data.package_path)
        
        if "belica" in asset_name.lower() or "belica" in package_path.lower():
            belica_assets.append((package_path, asset_name, str(asset_data.asset_class)))
    
    log(f"\nFound {len(belica_assets)} Belica-related assets")
    
    if belica_assets:
        log("\nFirst 20 Belica assets:")
        for path, name, cls in belica_assets[:20]:
            log(f"  [{cls:20s}] {path}/{name}")
        
        # Find animation-specific paths
        anim_paths = set()
        for path, name, cls in belica_assets:
            if "AnimSequence" in cls or "Anim" in path:
                # Extract base path
                parts = path.split('/')
                if len(parts) > 3:
                    base_path = '/'.join(parts[:5])  # Get first few levels
                    anim_paths.add(base_path)
        
        if anim_paths:
            log("\n--- Potential Animation Folders ---")
            for anim_path in sorted(anim_paths):
                log(f"  {anim_path}")
    else:
        log("\n⚠ No Belica assets found in project!")
        log("  Make sure Belica content is imported to your Unreal project")
        
except Exception as e:
    log(f"\n✗ Error during search: {e}")
    import traceback
    log(traceback.format_exc())

log("\n" + "=" * 80)
log("DIAGNOSTIC COMPLETE")
log("=" * 80)
