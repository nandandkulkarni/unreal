"""
List All Level Sequences in Project
Run this script INSIDE Unreal Editor to see all existing sequences

Usage:
  1. Unreal Editor → Tools → Execute Python Script
  2. Select this file: list_all_sequences.py
  3. Press OK
"""

import unreal

def list_all_sequences():
    """List all Level Sequence assets in the Content Browser"""
    print("=" * 60)
    print("LISTING ALL LEVEL SEQUENCES")
    print("=" * 60)
    
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    # Find all Level Sequence assets
    print("\nSearching for Level Sequence assets...")
    filter = unreal.ARFilter(
        class_paths=[unreal.TopLevelAssetPath("/Script/LevelSequence", "LevelSequence")],
        package_paths=["/Game"],
        recursive_paths=True
    )
    
    assets = asset_registry.get_assets(filter)
    
    if not assets:
        print("\n  [!] NO SEQUENCES FOUND")
        print("  Unreal does not come with default sequences.")
        print("  You must create sequences manually or via script.")
        print("\n" + "=" * 60)
        return
    
    print(f"\n  Found {len(assets)} sequence(s):\n")
    
    for i, asset_data in enumerate(assets, 1):
        package_path = asset_data.package_name
        asset_name = asset_data.asset_name
        print(f"  {i}. {asset_name}")
        print(f"     Path: {package_path}")
    
    print(f"\n{'=' * 60}")
    print(f"Total: {len(assets)} sequence(s)")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    list_all_sequences()
