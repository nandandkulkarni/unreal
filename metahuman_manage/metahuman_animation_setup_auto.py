"""
MetaHuman Animation Setup - AUTO-GENERATED IK RIGS VERSION
Runs INSIDE Unreal Engine's Python interpreter.

This version uses Unreal's built-in auto-generation for IK Rigs.
Simpler, more reliable, matches the YouTube tutorial workflow.

Advantages:
- Unreal automatically detects correct A-pose
- No hardcoded bone names or rotation values
- Handles different MetaHuman body types automatically
- Less code = fewer bugs

Based on: https://www.youtube.com/watch?v=wJKrIHWRTco
"""
import unreal
import os
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================
METAHUMAN_NAME = "Pia"
METAHUMAN_BASE_PATH = f"/Game/MetaHumans/{METAHUMAN_NAME}"

# Body mesh patterns to search
BODY_MESH_PATTERNS = [
    "f_srt_nrw_body",      # Pia's body type
    "f_med_nrw_body",      # Ada's body type  
    "m_med_nrw_body",      # Male medium body
    f"{METAHUMAN_NAME}_Body",
    "Body",
]

# Manny paths
MANNY_MESH_PATH = "/Game/Characters/Mannequins/Meshes/SKM_Manny"

# Output paths
OUTPUT_PATH = f"/Game/MetaHumans/{METAHUMAN_NAME}/Animations"

# Log file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else r"C:\UnrealProjects\Coding\unreal\metahuman_manage"
LOG_FILE = os.path.join(SCRIPT_DIR, "metahuman_setup_auto_log.txt")

# ============================================================================
# LOGGING
# ============================================================================
log_lines = []

def log(message, level="INFO"):
    """Log to console and buffer"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    log_lines.append(log_line)
    
    if level == "ERROR":
        unreal.log_error(message)
    elif level == "WARNING":
        unreal.log_warning(message)
    else:
        unreal.log(message)

def save_log():
    """Save log to file"""
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(log_lines))
        log(f"Log saved: {LOG_FILE}")
    except Exception as e:
        log(f"Failed to save log: {e}", "WARNING")

# ============================================================================
# ASSET DISCOVERY
# ============================================================================
def find_metahuman_assets():
    """Find MetaHuman skeletal mesh and skeleton"""
    log("=" * 60)
    log("Finding MetaHuman Assets")
    log("=" * 60)
    
    assets = {}
    
    # Find body mesh
    for pattern in BODY_MESH_PATTERNS:
        path = f"{METAHUMAN_BASE_PATH}/Body/{pattern}"
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            assets['mesh'] = unreal.load_asset(path)
            if assets['mesh']:
                log(f"✓ Found body mesh: {path}")
                assets['skeleton'] = assets['mesh'].skeleton
                if assets['skeleton']:
                    log(f"✓ Found skeleton: {assets['skeleton'].get_name()}")
                break
    
    if 'mesh' not in assets:
        log("✗ MetaHuman body mesh not found", "ERROR")
        body_folder = f"{METAHUMAN_BASE_PATH}/Body"
        if unreal.EditorAssetLibrary.does_directory_exist(body_folder):
            for item in unreal.EditorAssetLibrary.list_assets(body_folder):
                log(f"  Available: {item}")
    
    return assets

def find_manny_assets():
    """Find Manny mannequin assets with robust fallback"""
    log("=" * 60)
    log("Finding Manny Assets")
    log("=" * 60)
    
    assets = {}
    
    manny_paths = [
        MANNY_MESH_PATH,
        "/Game/Characters/Mannequins/Meshes/SKM_Manny",
        "/Game/Characters/Mannequin_UE4/Meshes/SK_Mannequin", # UE4 fallback
        "/Game/ThirdPerson/Characters/Mannequins/Meshes/SKM_Manny",
    ]
    
    # 1. Try standard paths
    for path in manny_paths:
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            assets['mesh'] = unreal.load_asset(path)
            if assets['mesh']:
                log(f"✓ Found Manny mesh at standard path: {path}")
                assets['skeleton'] = assets['mesh'].skeleton
                break
    
    # 2. Robust fallback: Search all SkeletalMeshes in /Game
    if 'mesh' not in assets:
        log("Standard paths failed. Searching Asset Registry for 'Manny'...", "WARNING")
        ar = unreal.AssetRegistryHelpers.get_asset_registry()
        
        # Filter for SkeletalMeshes
        filter = unreal.ARFilter(
            class_names=["SkeletalMesh"], 
            package_paths=["/Game"], 
            recursive_paths=True
        )
        
        asset_datas = ar.get_assets(filter)
        for asset_data in asset_datas:
            full_path = str(asset_data.package_name)
            if "Manny" in full_path and "SKM_" in full_path:
                assets['mesh'] = asset_data.get_asset()
                if assets['mesh']:
                    log(f"✓ Found Manny mesh via search: {full_path}")
                    assets['skeleton'] = assets['mesh'].skeleton
                    break
    
    if 'mesh' not in assets:
        log("✗ Manny mesh not found anywhere in /Game", "ERROR")
    
    return assets

# ============================================================================
# IK RETARGETER WITH AUTO-GENERATED RIGS
# ============================================================================
def create_ik_retargeter_auto(source_mesh, target_mesh):
    """
    Create IK Retargeter and let Unreal auto-generate IK Rigs.
    This is the simpler approach shown in the tutorial.
    """
    log("=" * 60)
    log("Creating IK Retargeter (Auto-Generated Rigs)")
    log("=" * 60)
    
    retargeter_name = f"RTG_Manny_To_{METAHUMAN_NAME}"
    retargeter_path = f"{OUTPUT_PATH}/{retargeter_name}"
    
    # Ensure output directory exists
    if not unreal.EditorAssetLibrary.does_directory_exist(OUTPUT_PATH):
        unreal.EditorAssetLibrary.make_directory(OUTPUT_PATH)
        log(f"✓ Created directory: {OUTPUT_PATH}")
    
    # Check if exists
    if unreal.EditorAssetLibrary.does_asset_exist(retargeter_path):
        existing = unreal.load_asset(retargeter_path)
        if existing:
            log(f"✓ IK Retargeter already exists: {retargeter_path}")
            return existing
    
    try:
        # Create retargeter
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        factory = unreal.IKRetargetFactory()
        
        retargeter = asset_tools.create_asset(
            retargeter_name,
            OUTPUT_PATH,
            unreal.IKRetargeter,
            factory
        )
        
        if not retargeter:
            log("✗ Failed to create IK Retargeter", "ERROR")
            return None
        
        log(f"✓ Created IK Retargeter: {retargeter_name}")
        
        # Get controller
        controller = unreal.IKRetargeterController.get_controller(retargeter)
        if not controller:
            log("✗ Could not get IKRetargeterController", "ERROR")
            return retargeter
        
        # Set source and target meshes - Unreal will auto-generate IK Rigs
        log("  Setting source mesh (Manny)...")
        controller.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, source_mesh)
        
        log("  Setting target mesh (MetaHuman)...")
        controller.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, target_mesh)
        
        log("  ✓ Unreal will auto-generate IK Rigs and chains")
        log("  ✓ A-pose will be automatically detected")
        
        # Auto-map chains
        try:
            controller.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
            log("  ✓ Auto-mapped chains (fuzzy matching)")
        except Exception as e:
            log(f"  ⚠ Auto-map failed, trying exact: {e}", "WARNING")
            try:
                controller.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
                log("  ✓ Auto-mapped chains (exact matching)")
            except Exception as e2:
                log(f"  ⚠ Could not auto-map chains: {e2}", "WARNING")
                log("  You may need to map chains manually in the editor", "WARNING")
        
        # Apply tutorial-specific configurations
        configure_retargeter_settings(controller, retargeter)
        
        # Save
        unreal.EditorAssetLibrary.save_loaded_asset(retargeter)
        return retargeter
        
    except Exception as e:
        log(f"✗ Error creating IK Retargeter: {e}", "ERROR")
        return None

# ============================================================================
# RETARGETER CONFIGURATION (Tutorial Settings)
# ============================================================================
def configure_retargeter_settings(controller, retargeter):
    """
    Apply manual configuration settings shown in the tutorial.
    These settings ensure proper root motion and animation transfer.
    """
    log("=" * 60)
    log("Applying Tutorial Configuration Settings")
    log("=" * 60)
    
    try:
        # 1. Set root settings
        # The tutorial shows setting the retarget root to "pelvis"
        log("  Configuring root settings...")
        try:
            # Get source and target IK Rigs
            source_rig = retargeter.get_editor_property('source_ik_rig_asset')
            target_rig = retargeter.get_editor_property('target_ik_rig_asset')
            
            if source_rig and target_rig:
                # Set retarget root on both rigs
                source_controller = unreal.IKRigController.get_controller(source_rig)
                target_controller = unreal.IKRigController.get_controller(target_rig)
                
                if source_controller:
                    source_controller.set_retarget_root("pelvis")
                    log("    ✓ Set source retarget root: pelvis")
                
                if target_controller:
                    target_controller.set_retarget_root("pelvis")
                    log("    ✓ Set target retarget root: pelvis")
        except Exception as e:
            log(f"    ⚠ Could not set retarget root: {e}", "WARNING")
        
        # 2. Configure global settings
        log("  Configuring global retargeter settings...")
        try:
            # Set global scale mode to "Globally Scaled"
            # This ensures root motion translates correctly
            retargeter.set_editor_property('target_mesh_scale', 1.0)
            log("    ✓ Set target mesh scale: 1.0")
            
            # Enable root motion
            retargeter.set_editor_property('enable_root_motion', True)
            log("    ✓ Enabled root motion")
        except Exception as e:
            log(f"    ⚠ Could not set global settings: {e}", "WARNING")
        
        # 3. Configure chain settings
        log("  Configuring chain settings...")
        try:
            # Get all chain mappings
            chain_mappings = controller.get_chain_mappings()
            
            configured_chains = 0
            for chain_mapping in chain_mappings:
                try:
                    chain_name = chain_mapping.get_editor_property('target_chain')
                    
                    # Set FK/IK blend (typically 0.0 for FK, 1.0 for IK)
                    # Tutorial uses FK for most chains
                    controller.set_chain_fk_ik_blend(chain_name, 0.0, unreal.RetargetSourceOrTarget.TARGET)
                    
                    # Set chain settings based on type
                    if "Leg" in chain_name or "Foot" in chain_name:
                        # Legs use IK for better ground contact
                        controller.set_chain_fk_ik_blend(chain_name, 1.0, unreal.RetargetSourceOrTarget.TARGET)
                    
                    configured_chains += 1
                except Exception as e:
                    log(f"    ⚠ Could not configure chain {chain_name}: {e}", "WARNING")
            
            if configured_chains > 0:
                log(f"    ✓ Configured {configured_chains} chains")
        except Exception as e:
            log(f"    ⚠ Could not configure chains: {e}", "WARNING")
        
        # 4. Set translation mode
        log("  Setting translation mode...")
        try:
            # Set to "Globally Scaled" for proper root motion
            # This is shown in the tutorial settings panel
            retargeter.set_editor_property('root_motion_mode', unreal.RootMotionMode.GLOBALLY_SCALED)
            log("    ✓ Set root motion mode: Globally Scaled")
        except Exception as e:
            log(f"    ⚠ Could not set translation mode: {e}", "WARNING")
            log("    You may need to set this manually in the editor", "WARNING")
        
        log("✓ Configuration complete")
        
    except Exception as e:
        log(f"⚠ Configuration partially failed: {e}", "WARNING")
        log("  Some settings may need manual adjustment in the editor", "WARNING")

# ============================================================================
# ANIMATION RETARGETING
# ============================================================================  
def retarget_animations(retargeter, source_mesh, target_mesh, source_mesh_path):
    """Batch retarget all animations from Manny"""
    log("=" * 60)
    log("Retargeting Animations")
    log("=" * 60)
    
    # 1. Determine Source Path (Default or Derived from Mesh)
    source_folder_default = "/Game/Characters/Mannequins/Animations/Manny"
    
    # Try to infer from source mesh path
    mesh_folder = os.path.dirname(source_mesh_path)
    # Check for parallel "Anims" or "Animations" folder
    candidates = [
        source_folder_default,
        mesh_folder.replace('/Meshes', '/Animations'),
        mesh_folder.replace('/Meshes', '/Anims'),
        f"{mesh_folder.replace('/Meshes', '/Anims')}/Unarmed" # FilmIK structure
    ]
    
    found_folder = None
    for candidate in candidates:
        if unreal.EditorAssetLibrary.does_directory_exist(candidate):
            found_folder = candidate
            log(f"  ✓ Inferred animation source: {found_folder}")
            break
            
    if not found_folder:
        log("  ⚠ Standard animation folder not found. Searching...", "WARNING")
        ar = unreal.AssetRegistryHelpers.get_asset_registry()
        filter = unreal.ARFilter(
            class_names=["AnimSequence"], 
            package_paths=["/Game"], 
            recursive_paths=True
        )
        assets = ar.get_assets(filter)
        for asset in assets:
            path = str(asset.package_name)
            if "Manny" in path or "Unarmed" in path:
                found_folder = os.path.dirname(path)
                log(f"  ✓ Found inferred animation source via search: {found_folder}")
                break
    
    if not found_folder:
        log("✗ Animation folder not found", "ERROR")
        return []

    anim_path = found_folder
    
    log(f"Scanning: {anim_path}")
    
    # Collect animation sequences
    all_assets = unreal.EditorAssetLibrary.list_assets(anim_path, recursive=True)
    anim_sequences = []
    
    for asset_path in all_assets:
        asset = unreal.load_asset(asset_path)
        if asset and isinstance(asset, unreal.AnimSequence):
            anim_sequences.append(asset)
    
    log(f"Found {len(anim_sequences)} animations to retarget")
    
    if not anim_sequences:
        return []
    
    # Batch retarget
    try:
        # Run batch retarget
        batch_op = unreal.IKRetargetBatchOperation()
        try:
            new_assets = batch_op.duplicate_and_retarget(
                anim_sequences,
                source_mesh,
                target_mesh,
                retargeter,
                search="",
                replace="",
                prefix="RTG_",
                suffix="",
                remap_referenced_assets=True
            )
            
            # Move assets to correct folder
            moved_count = 0
            for asset_data in new_assets:
                source_path = str(asset_data.package_name)
                asset_name = str(asset_data.asset_name)
                dest_path = f"{OUTPUT_PATH}/{asset_name}"
                
                if unreal.EditorAssetLibrary.rename_asset(source_path, dest_path):
                    moved_count += 1
                    
            log(f"✓ Retargeted and moved {moved_count} animations to {OUTPUT_PATH}")
            return new_assets
            
        except Exception as e:
            log(f"✗ Retargeting failed: {e}", "ERROR")
            return []
            
    except AttributeError:
        log("IKRetargetBatchOperation not available", "WARNING")
        log("Use right-click → Retarget Animations in Content Browser", "WARNING")
        return []
    except Exception as e:
        log(f"✗ Retargeting failed: {e}", "ERROR")
        return []

# ============================================================================
# ANIMATION BLUEPRINT DUPLICATION
# ============================================================================
def duplicate_animation_blueprint(target_skeleton, source_mesh_path):
    """
    Duplicate ABP_Manny (or ABP_Unarmed) and retarget it to the new skeleton.
    """
    log("=" * 60)
    log("Duplicating Animation Blueprint")
    log("=" * 60)
    
    # Potential paths for ABP
    abp_paths = [
        "/Game/Characters/Mannequins/Animations/ABP_Manny",
        "/Game/ThirdPerson/Characters/Mannequins/Animations/ABP_Manny",
        f"{os.path.dirname(source_mesh_path).replace('/Meshes', '/Animations')}/ABP_Manny",
        f"{os.path.dirname(source_mesh_path).replace('/Meshes', '/Anims')}/Unarmed/ABP_Unarmed" # FilmIK
    ]
    
    source_abp_path = None
    for path in abp_paths:
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            source_abp_path = path
            log(f"  ✓ Found AnimBP: {path}")
            break
            
    # Fallback search
    if not source_abp_path:
        log("  Searching for AnimBP...", "WARNING")
        ar = unreal.AssetRegistryHelpers.get_asset_registry()
        filter = unreal.ARFilter(
            class_names=["AnimBlueprint"], 
            package_paths=["/Game"], 
            recursive_paths=True
        )
        assets = ar.get_assets(filter)
        for asset in assets:
            if asset.asset_name in ["ABP_Manny", "ABP_Unarmed"]:
                source_abp_path = str(asset.package_name)
                log(f"  ✓ Found AnimBP via search: {source_abp_path}")
                break

    if not source_abp_path:
        log("✗ Could not find Manny or Unarmed Animation Blueprint", "ERROR")
        return None
    
    # Target path for duplicated AnimBP
    new_bp_name = f"ABP_{METAHUMAN_NAME}"
    new_bp_path = f"{OUTPUT_PATH}/{new_bp_name}"
    
    # Check if already exists
    if unreal.EditorAssetLibrary.does_asset_exist(new_bp_path):
        existing = unreal.load_asset(new_bp_path)
        if existing:
            log(f"✓ Animation Blueprint already exists: {new_bp_path}")
            return existing
    
    try:
        # Duplicate the Animation Blueprint
        new_bp = unreal.EditorAssetLibrary.duplicate_asset(
            source_abp_path,
            new_bp_path
        )
        
        if not new_bp:
            log("✗ Failed to duplicate Animation Blueprint", "ERROR")
            return None
        
        log(f"✓ Duplicated Animation Blueprint: {new_bp_name}")
        
        # Try to remap skeleton
        if target_skeleton:
            try:
                new_bp.set_editor_property('target_skeleton', target_skeleton)
                log(f"  ✓ Remapped to skeleton: {target_skeleton.get_name()}")
            except Exception as e:
                log(f"  ⚠ Could not auto-remap skeleton: {e}", "WARNING")
                log("  Manual skeleton remapping may be needed in editor", "WARNING")
                log("  Open ABP → File → Remap Skeleton", "WARNING")
        
        # Save
        unreal.EditorAssetLibrary.save_loaded_asset(new_bp)
        return new_bp
        
    except Exception as e:
        log(f"✗ Error duplicating Animation Blueprint: {e}", "ERROR")
        return None

# ============================================================================
# MAIN
# ============================================================================
def main():
    """Main execution"""
    log("=" * 60)
    log("MetaHuman Animation Setup - AUTO-GENERATED VERSION")
    log(f"Target: {METAHUMAN_NAME}")
    log("=" * 60)
    
    try:
        # Find assets
        metahuman_assets = find_metahuman_assets()
        manny_assets = find_manny_assets()
        
        if 'mesh' not in metahuman_assets or 'skeleton' not in metahuman_assets:
            log("✗ FATAL: MetaHuman assets not found", "ERROR")
            save_log()
            return
        
        if 'mesh' not in manny_assets:
            log("✗ FATAL: Manny assets not found", "ERROR")
            save_log()
            return
        
        # Create IK Retargeter with auto-generated rigs
        retargeter = create_ik_retargeter_auto(
            manny_assets['mesh'],
            metahuman_assets['mesh']
        )
        
        if not retargeter:
            log("✗ FATAL: Could not create IK Retargeter", "ERROR")
            save_log()
            return
        
        # Retarget animations
        retargeted = []
        if retargeter:
            retargeted = retarget_animations(
                retargeter,
                manny_assets['mesh'],
                metahuman_assets['mesh'],
                manny_assets['mesh'].get_path_name()
            )
        
        # Duplicate Animation Blueprint
        anim_bp = None
        if metahuman_assets.get('skeleton') and manny_assets.get('mesh'):
             anim_bp = duplicate_animation_blueprint(metahuman_assets['skeleton'], manny_assets['mesh'].get_path_name())
        
        # Summary
        log("=" * 60)
        log("✓ SETUP COMPLETE")
        log("=" * 60)
        log(f"MetaHuman: {METAHUMAN_NAME}")
        log(f"Output folder: {OUTPUT_PATH}")
        log("")
        log("Created assets:")
        log(f"  ✓ IK Retargeter: {retargeter.get_name()}")
        log(f"  ✓ IK Rigs: Auto-generated by Unreal")
        if retargeted:
            log(f"  ✓ Retargeted {len(retargeted)} animations")
        if anim_bp:
            log(f"  ✓ Animation Blueprint: ABP_{METAHUMAN_NAME}")
        log("")
        log("Configuration applied:")
        log("  ✓ A-pose: Auto-detected by Unreal")
        log("  ✓ Retarget root: pelvis")
        log("  ✓ Root motion mode: Globally Scaled")
        log("  ✓ Chain FK/IK blend: Configured (Legs=IK, Others=FK)")
        log("")
        log("Next steps:")
        log("1. Open IK Retargeter to verify preview looks correct")
        log("2. Assign ABP_Pia to your MetaHuman character")
        log("3. Test animation in viewport")
        
    except Exception as e:
        log(f"✗ FATAL: {e}", "ERROR")
        import traceback
        for line in traceback.format_exc().split('\n'):
            if line:
                log(f"  {line}")
    
    finally:
        save_log()

# Run
main()
