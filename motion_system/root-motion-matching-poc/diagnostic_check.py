"""
Diagnostic script to check Motion Matching / PoseSearch availability
"""
import unreal
import os

# Setup logging to file
log_file = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\diagnostic_log.txt"

def log(msg):
    """Write to both console and file"""
    print(msg)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Clear previous log
with open(log_file, 'w', encoding='utf-8') as f:
    f.write("")

log("="*80)
log("MOTION MATCHING DIAGNOSTIC")
log("="*80)
log("")

# Check for PoseSearch classes
log("Checking for PoseSearch classes...")
classes_to_check = [
    "PoseSearchDatabase",
    "PoseSearchSchema",
    "AnimNode_MotionMatching",
    "PoseSearchFeatureChannel",
]

available_classes = []
missing_classes = []

for class_name in classes_to_check:
    if hasattr(unreal, class_name):
        available_classes.append(class_name)
        log(f"  ✓ unreal.{class_name} - AVAILABLE")
    else:
        missing_classes.append(class_name)
        log(f"  ✗ unreal.{class_name} - NOT FOUND")

log("")
log(f"Available: {len(available_classes)}/{len(classes_to_check)}")

if missing_classes:
    log("")
    log("Missing classes:")
    for cls in missing_classes:
        log(f"  - {cls}")
    log("")
    log("This likely means the PoseSearch plugin is not enabled.")
    log("To enable:")
    log("  1. Edit → Plugins")
    log("  2. Search for 'Pose Search'")
    log("  3. Enable 'Pose Search' and 'Motion Trajectory'")
    log("  4. Restart Unreal Engine")

log("")
log("="*80)
log("Checking for Manny assets...")
log("="*80)
log("")

# Check for Manny skeleton
skeleton_paths = [
    "/Game/Characters/Mannequins/Rigs/SK_Mannequin",
    "/Game/Characters/Mannequins/Meshes/SKM_Manny",
    "/Game/ThirdPerson/Characters/Mannequins/Rigs/SK_Mannequin",
]

found_skeleton = False
for path in skeleton_paths:
    asset = unreal.load_object(None, path)
    if asset:
        log(f"  ✓ Found: {path}")
        log(f"    Type: {type(asset).__name__}")
        found_skeleton = True
        break
    else:
        log(f"  ✗ Not found: {path}")

if not found_skeleton:
    log("")
    log("  Searching for Mannequin assets...")
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    filter = unreal.ARFilter(
        class_names=["Skeleton"],
        recursive_paths=True,
        package_paths=["/Game"]
    )
    
    assets = asset_registry.get_assets(filter)
    log(f"  Found {len(assets)} Skeleton assets total")
    
    for asset_data in assets:
        asset_name = str(asset_data.asset_name)
        if "Manny" in asset_name or "Mannequin" in asset_name:
            log(f"    - {asset_data.object_path}")

log("")
log("="*80)
log("Checking animation assets...")
log("="*80)
log("")

anim_folders = [
    "/Game/Characters/Mannequins/Animations",
    "/Game/ThirdPerson/Characters/Mannequins/Animations",
]

total_anims = 0
for folder in anim_folders:
    filter = unreal.ARFilter(
        class_names=["AnimSequence"],
        recursive_paths=True,
        package_paths=[folder]
    )
    
    assets = asset_registry.get_assets(filter)
    if assets:
        log(f"  {folder}: {len(assets)} animations")
        total_anims += len(assets)
        
        # Show first 5
        for i, asset_data in enumerate(assets[:5]):
            log(f"    - {asset_data.asset_name}")
        if len(assets) > 5:
            log(f"    ... and {len(assets) - 5} more")

log("")
log(f"Total animations found: {total_anims}")

log("")
log("="*80)
log("DIAGNOSTIC COMPLETE")
log(f"Log written to: {log_file}")
log("="*80)
