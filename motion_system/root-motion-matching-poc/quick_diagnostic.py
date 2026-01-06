"""
Quick diagnostic: Check what's available in the current project
"""

import unreal

print("=" * 80)
print("PROJECT DIAGNOSTIC")
print("=" * 80)

# Check Characters folder
try:
    chars_exists = unreal.EditorAssetLibrary.does_directory_exist("/Game/Characters")
    print(f"\n/Game/Characters exists: {chars_exists}")
    
    if chars_exists:
        chars = unreal.EditorAssetLibrary.list_assets("/Game/Characters", recursive=False, include_folder=True)
        print(f"Contents of /Game/Characters:")
        for char in chars[:10]:
            print(f"  - {char}")
except Exception as e:
    print(f"Error checking Characters: {e}")

# Check for Mannequins
try:
    mann_exists = unreal.EditorAssetLibrary.does_directory_exist("/Game/Characters/Mannequins")
    print(f"\n/Game/Characters/Mannequins exists: {mann_exists}")
except Exception as e:
    print(f"Error: {e}")

# Try to load skeleton
try:
    skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Mannequins/Meshes/SK_Mannequin")
    if skel:
        print(f"\n✓ Skeleton found: {skel.get_name()}")
    else:
        print("\n✗ Skeleton not found at expected path")
except Exception as e:
    print(f"\n✗ Error loading skeleton: {e}")

print("\n" + "=" * 80)
print("If skeleton not found, you're in the wrong project!")
print("The POC was designed for a project with Mannequin assets.")
print("=" * 80)
