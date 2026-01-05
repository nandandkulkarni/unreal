"""
Simple test: Check current project and try to create database

This will help us understand which project is active.
"""

import unreal

print("=" * 80)
print("PROJECT CHECK")
print("=" * 80)

# Check current project
try:
    project_dir = unreal.SystemLibrary.get_project_directory()
    print(f"Project Directory: {project_dir}")
except:
    print("Could not get project directory")

# Try to list assets
try:
    assets = unreal.EditorAssetLibrary.list_assets("/Game", recursive=False, include_folder=True)
    print(f"\nTop-level folders in /Game:")
    for asset in assets[:10]:
        print(f"  - {asset}")
except Exception as e:
    print(f"Error listing assets: {e}")

# Check if MotionMatching folder exists
try:
    mm_exists = unreal.EditorAssetLibrary.does_directory_exist("/Game/MotionMatching")
    print(f"\n/Game/MotionMatching exists: {mm_exists}")
except Exception as e:
    print(f"Error checking directory: {e}")

# Try to create MotionMatching folder if it doesn't exist
if not mm_exists:
    try:
        success = unreal.EditorAssetLibrary.make_directory("/Game/MotionMatching")
        print(f"Created /Game/MotionMatching: {success}")
    except Exception as e:
        print(f"Error creating directory: {e}")

print("\n" + "=" * 80)
print("Test complete - check which project this is running in")
