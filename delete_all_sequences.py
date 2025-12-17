"""
Delete All Sequences (In-Unreal Script)
Run this script INSIDE Unreal Editor to delete all sequence assets

Usage:
  1. Unreal Editor → Tools → Execute Python Script
  2. Select this file: delete_all_sequences.py
  3. Press OK
"""

import unreal

def delete_all_sequences():
    """Delete all Level Sequence assets from the Content Browser"""
    print("=" * 60)
    print("DELETING ALL SEQUENCES")
    print("=" * 60)
    
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    editor_asset_lib = unreal.EditorAssetLibrary
    
    # Find all Level Sequence assets
    print("\nSearching for Level Sequence assets...")
    filter = unreal.ARFilter(
        class_paths=[unreal.TopLevelAssetPath("/Script/LevelSequence", "LevelSequence")],
        package_paths=["/Game"],
        recursive_paths=True
    )
    
    assets = asset_registry.get_assets(filter)
    
    if not assets:
        print("  No sequence assets found")
        return
    
    print(f"  Found {len(assets)} sequence(s)\n")
    
    deleted_count = 0
    failed_count = 0
    
    for asset_data in assets:
        asset_path = asset_data.get_full_name()
        package_path = asset_data.package_name
        
        print(f"  Deleting: {package_path}")
        
        try:
            # Close sequence if it's open
            current_seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
            if current_seq:
                current_path = current_seq.get_path_name()
                if str(package_path) in current_path:
                    print("    Closing open sequence...")
                    unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
            
            # Delete the asset
            success = editor_asset_lib.delete_asset(str(package_path))
            if success:
                print("    [OK] Deleted")
                deleted_count += 1
            else:
                print("    [X] Failed to delete")
                failed_count += 1
        except Exception as e:
            print(f"    [X] Exception: {e}")
            failed_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"DELETION COMPLETE")
    print(f"{'=' * 60}")
    print(f"  Deleted: {deleted_count} sequence(s)")
    if failed_count > 0:
        print(f"  Failed:  {failed_count} sequence(s)")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    delete_all_sequences()
