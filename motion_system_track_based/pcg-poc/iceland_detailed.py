"""
Detailed Iceland Environment Asset Inspector
Shows complete information about all assets including their actual types
"""
import unreal
import sys
import datetime

# ==============================================================================
# LOGGING SETUP
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\iceland_detailed.log"

class FileLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
        
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = FileLogger(LOG_FILE_PATH)

def log(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

print("=" * 80)
log("ICELAND ENVIRONMENT - DETAILED ASSET INSPECTOR")
print("=" * 80)

# ==============================================================================
# DETAILED ASSET INSPECTION
# ==============================================================================
def inspect_iceland_assets():
    """Get detailed information about Iceland Environment assets"""
    log("\nInspecting Iceland_Environment folder...")
    
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    # Search in Iceland_Environment folder
    filter = unreal.ARFilter(
        package_paths=["/Game/Iceland_Environment"],
        recursive_paths=True
    )
    
    all_assets = asset_registry.get_assets(filter)
    
    print(f"\nFound {len(all_assets)} total assets")
    print("\n" + "=" * 80)
    print("DETAILED ASSET LIST")
    print("=" * 80)
    
    # Group by folder
    by_folder = {}
    
    for asset_data in all_assets:
        asset_name = str(asset_data.asset_name)
        asset_class = str(asset_data.asset_class_path.asset_name) if hasattr(asset_data, 'asset_class_path') else str(asset_data.asset_class)
        package_path = str(asset_data.package_path)
        package_name = str(asset_data.package_name)
        
        # Extract folder from package path
        folder = package_path if package_path else "/Game/Iceland_Environment"
        
        if folder not in by_folder:
            by_folder[folder] = []
        
        by_folder[folder].append({
            'name': asset_name,
            'class': asset_class,
            'package': package_name
        })
    
    # Print organized by folder
    for folder in sorted(by_folder.keys()):
        assets = by_folder[folder]
        print(f"\n📁 {folder} ({len(assets)} assets)")
        print("-" * 80)
        
        for asset in sorted(assets, key=lambda x: x['name']):
            print(f"  • {asset['name']}")
            print(f"    Type: {asset['class']}")
            print(f"    Path: {asset['package']}")
            print()
    
    # Summary by type
    print("\n" + "=" * 80)
    print("SUMMARY BY TYPE")
    print("=" * 80)
    
    type_counts = {}
    for folder_assets in by_folder.values():
        for asset in folder_assets:
            asset_type = asset['class']
            type_counts[asset_type] = type_counts.get(asset_type, 0) + 1
    
    for asset_type in sorted(type_counts.keys()):
        count = type_counts[asset_type]
        print(f"  {asset_type}: {count}")
    
    # Find landscapes specifically
    print("\n" + "=" * 80)
    print("LANDSCAPE ASSETS")
    print("=" * 80)
    
    landscapes_found = []
    for folder_assets in by_folder.values():
        for asset in folder_assets:
            if 'Landscape' in asset['class'] or 'landscape' in asset['name'].lower():
                landscapes_found.append(asset)
                print(f"  • {asset['name']} ({asset['class']})")
                print(f"    {asset['package']}")
    
    if not landscapes_found:
        print("  No landscape assets found (they may be in the level itself)")
    
    # Find materials
    print("\n" + "=" * 80)
    print("MATERIAL ASSETS")
    print("=" * 80)
    
    materials_found = []
    for folder_assets in by_folder.values():
        for asset in folder_assets:
            if 'Material' in asset['class']:
                materials_found.append(asset)
                print(f"  • {asset['name']} ({asset['class']})")
                print(f"    {asset['package']}")
    
    if not materials_found:
        print("  No material assets detected in this scan")
    
    return by_folder

# ==============================================================================
# CHECK FOR LEVELS
# ==============================================================================
def check_for_levels():
    """Check if there are any level files in Iceland_Environment"""
    log("\nChecking for level files...")
    
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    filter = unreal.ARFilter(
        package_paths=["/Game/Iceland_Environment"],
        recursive_paths=True,
        class_names=["World"]
    )
    
    levels = asset_registry.get_assets(filter)
    
    print("\n" + "=" * 80)
    print("LEVEL FILES")
    print("=" * 80)
    
    if levels:
        for level_data in levels:
            level_name = str(level_data.asset_name)
            level_path = str(level_data.package_name)
            print(f"  • {level_name}")
            print(f"    Path: {level_path}")
            print(f"    → You can open this level to see the terrain!")
    else:
        print("  No level files found")
        print("  The Iceland Environment may be:")
        print("    - A collection of assets to use in your own level")
        print("    - Or the level might be in a different folder")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
try:
    assets = inspect_iceland_assets()
    check_for_levels()
    
    print("\n" + "=" * 80)
    print("✓ INSPECTION COMPLETE!")
    print("=" * 80)
    print("\nWhat Iceland Environment Contains:")
    print("  - Check the detailed list above")
    print("  - Look for level files you can open")
    print("  - Materials and textures for terrain")
    print("\nNext: Tell me what you found and we'll create scripts to work with it!")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
