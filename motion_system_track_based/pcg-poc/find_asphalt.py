"""
Find Asphalt Material
Searches for the correct asphalt material path
"""
import unreal

print("=" * 80)
print("SEARCHING FOR ASPHALT MATERIAL")
print("=" * 80)

# Search for asphalt materials
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()

filter = unreal.ARFilter(
    package_paths=["/Game/Fab/Megascans/Surfaces"],
    recursive_paths=True
)

all_assets = asset_registry.get_assets(filter)

print(f"\nFound {len(all_assets)} assets in Megascans/Surfaces")
print("\nAsphalt-related materials:")
print("-" * 80)

for asset_data in all_assets:
    asset_name = str(asset_data.asset_name)
    asset_class = str(asset_data.asset_class_path.asset_name) if hasattr(asset_data, 'asset_class_path') else str(asset_data.asset_class)
    package_name = str(asset_data.package_name)
    
    if 'asphalt' in asset_name.lower() or 'sfrofg0a' in asset_name.lower():
        print(f"\n• {asset_name}")
        print(f"  Type: {asset_class}")
        print(f"  Path: {package_name}")
