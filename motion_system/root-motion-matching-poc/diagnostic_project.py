"""
Project diagnostic with logging
"""

import unreal
import os

LOG_FILE = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs\diagnostic.log"

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

# Clear log
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

log("=" * 80)
log("PROJECT DIAGNOSTIC")
log("=" * 80)

# Check project directory
try:
    proj_dir = unreal.SystemLibrary.get_project_directory()
    log(f"\nProject Directory: {proj_dir}")
except:
    log("\nCould not get project directory")

# Check Characters folder
try:
    chars_exists = unreal.EditorAssetLibrary.does_directory_exist("/Game/Characters")
    log(f"/Game/Characters exists: {chars_exists}")
    
    if chars_exists:
        chars = unreal.EditorAssetLibrary.list_assets("/Game/Characters", recursive=False, include_folder=True)
        log(f"\nContents of /Game/Characters ({len(chars)} items):")
        for char in chars[:10]:
            log(f"  - {char}")
except Exception as e:
    log(f"Error checking Characters: {e}")

# Check for Mannequins
try:
    mann_exists = unreal.EditorAssetLibrary.does_directory_exist("/Game/Characters/Mannequins")
    log(f"\n/Game/Characters/Mannequins exists: {mann_exists}")
except Exception as e:
    log(f"Error: {e}")

# Try to load skeleton
try:
    skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Mannequins/Meshes/SK_Mannequin")
    if skel:
        log(f"\n✓ Skeleton found: {skel.get_name()}")
    else:
        log("\n✗ Skeleton NOT found at /Game/Characters/Mannequins/Meshes/SK_Mannequin")
except Exception as e:
    log(f"\n✗ Error loading skeleton: {e}")

log("\n" + "=" * 80)
log(f"Log saved to: {LOG_FILE}")
