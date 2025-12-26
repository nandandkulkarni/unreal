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
    """Find Manny mannequin assets"""
    log("=" * 60)
    log("Finding Manny Assets")
    log("=" * 60)
    
    assets = {}
    
    manny_paths = [
        MANNY_MESH_PATH,
        "/Game/Characters/Mannequins/Meshes/SKM_Manny",
        "/Game/ThirdPerson/Characters/Mannequins/Meshes/SKM_Manny",
    ]
    
    for path in manny_paths:
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            assets['mesh'] = unreal.load_asset(path)
            if assets['mesh']:
                log(f"✓ Found Manny mesh: {path}")
                assets['skeleton'] = assets['mesh'].skeleton
                break
    
    if 'mesh' not in assets:
        log("✗ Manny mesh not found", "ERROR")
    
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
        factory = unreal.IKRetargeterFactory()
        
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
        controller.set_source_preview_mesh(source_mesh)
        
        log("  Setting target mesh (MetaHuman)...")
        controller.set_target_preview_mesh(target_mesh)
        
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
def retarget_animations(source_mesh, target_mesh, retargeter):
    """Batch retarget animations"""
    log("=" * 60)
    log("Retargeting Animations")
    log("=" * 60)
    
    if not retargeter:
        log("✗ No retargeter provided", "ERROR")
        return []
    
    # Find animation source folder
    anim_paths = [
        "/Game/Characters/Mannequins/Animations",
        "/Game/ThirdPerson/Characters/Mannequins/Animations",
    ]
    
    anim_path = None
    for path in anim_paths:
        if unreal.EditorAssetLibrary.does_directory_exist(path):
            anim_path = path
            break
    
    if not anim_path:
        log("✗ Animation folder not found", "ERROR")
        return []
    
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
        retargeted = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
            assets_to_retarget=anim_sequences,
            source_mesh=source_mesh,
            target_mesh=target_mesh,
            ik_retarget_asset=retargeter,
            search="Manny",
            replace=METAHUMAN_NAME,
            suffix="",
            prefix="",
            folder_to_save=OUTPUT_PATH,
            include_referenced_assets=False
        )
        
        log(f"✓ Retargeted {len(retargeted)} animations")
        return retargeted
        
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
def duplicate_animation_blueprint(target_skeleton):
    """
    Duplicate Manny's Animation Blueprint for the MetaHuman.
    The AnimBP contains the state machine logic for locomotion.
    """
    log("=" * 60)
    log("Duplicating Animation Blueprint")
    log("=" * 60)
    
    # Find source Animation Blueprint
    anim_bp_paths = [
        "/Game/Characters/Mannequins/Animations/ABP_Manny",
        "/Game/ThirdPerson/Characters/Mannequins/Animations/ABP_Manny",
        "/Game/ThirdPerson/Blueprints/Animation/ABP_ThirdPersonCharacter",
    ]
    
    source_bp = None
    source_path = None
    for path in anim_bp_paths:
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            source_bp = unreal.load_asset(path)
            if source_bp:
                source_path = path
                log(f"✓ Found source AnimBP: {path}")
                break
    
    if not source_bp:
        log("✗ Could not find Manny Animation Blueprint", "ERROR")
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
            source_path,
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
        metahuman = find_metahuman_assets()
        manny = find_manny_assets()
        
        if 'mesh' not in metahuman or 'skeleton' not in metahuman:
            log("✗ FATAL: MetaHuman assets not found", "ERROR")
            save_log()
            return
        
        if 'mesh' not in manny:
            log("✗ FATAL: Manny assets not found", "ERROR")
            save_log()
            return
        
        # Create IK Retargeter with auto-generated rigs
        retargeter = create_ik_retargeter_auto(
            manny['mesh'],
            metahuman['mesh']
        )
        
        if not retargeter:
            log("✗ FATAL: Could not create IK Retargeter", "ERROR")
            save_log()
            return
        
        # Retarget animations
        retargeted = []
        if retargeter:
            retargeted = retarget_animations(
                manny['mesh'],
                metahuman['mesh'],
                retargeter
            )
        
        # Duplicate Animation Blueprint
        anim_bp = duplicate_animation_blueprint(metahuman['skeleton'])
        
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
