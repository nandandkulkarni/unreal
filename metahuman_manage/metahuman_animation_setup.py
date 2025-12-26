"""
MetaHuman IK Rig Retargeting Script
Runs INSIDE Unreal Engine's Python interpreter.

Uses the modern UE5 IK Rig approach (not virtual bones):
1. Creates/configures IK Rig with retarget chains for MetaHuman
2. Sets up IK Retargeter with auto chain mapping
3. Batch retargets Manny animations to MetaHuman

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
MANNY_IK_RIG_PATH = "/Game/Characters/Mannequins/Rigs/IK_Mannequin"

# Output paths
OUTPUT_PATH = f"/Game/MetaHumans/{METAHUMAN_NAME}/Animations"

# Log file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else r"C:\UnrealProjects\Coding\unreal\metahuman_manage"
LOG_FILE = os.path.join(SCRIPT_DIR, "metahuman_setup_log.txt")

# ============================================================================
# RETARGET CHAIN DEFINITIONS
# Standard UE5 mannequin bone chains
# ============================================================================
RETARGET_CHAINS = [
    # Main body chains
    ("Spine", "spine_01", "spine_05"),
    ("Head", "neck_01", "head"),
    
    # Arms
    ("LeftClavicle", "clavicle_l", "clavicle_l"),
    ("LeftArm", "upperarm_l", "hand_l"),
    ("RightClavicle", "clavicle_r", "clavicle_r"),
    ("RightArm", "upperarm_r", "hand_r"),
    
    # Legs  
    ("LeftLeg", "thigh_l", "ball_l"),
    ("RightLeg", "thigh_r", "ball_r"),
    
    # Left hand fingers
    ("LeftThumb", "thumb_01_l", "thumb_03_l"),
    ("LeftIndex", "index_metacarpal_l", "index_03_l"),
    ("LeftMiddle", "middle_metacarpal_l", "middle_03_l"),
    ("LeftRing", "ring_metacarpal_l", "ring_03_l"),
    ("LeftPinky", "pinky_metacarpal_l", "pinky_03_l"),
    
    # Right hand fingers
    ("RightThumb", "thumb_01_r", "thumb_03_r"),
    ("RightIndex", "index_metacarpal_r", "index_03_r"),
    ("RightMiddle", "middle_metacarpal_r", "middle_03_r"),
    ("RightRing", "ring_metacarpal_r", "ring_03_r"),
    ("RightPinky", "pinky_metacarpal_r", "pinky_03_r"),
]

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
    
    # Find existing Manny IK Rig
    ik_rig_paths = [
        MANNY_IK_RIG_PATH,
        "/Game/Characters/Mannequins/Rigs/IK_Mannequin",
        "/Game/IK_AutoGeneratedSource",
    ]
    
    for path in ik_rig_paths:
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            assets['ik_rig'] = unreal.load_asset(path)
            if assets['ik_rig']:
                log(f"✓ Found Manny IK Rig: {path}")
                break
    
    return assets

# ============================================================================
# IK RIG CREATION
# ============================================================================
def create_ik_rig(skeletal_mesh, rig_name, output_path):
    """Create an IK Rig with retarget chains for the given skeletal mesh"""
    log("=" * 60)
    log(f"Creating IK Rig: {rig_name}")
    log("=" * 60)
    
    rig_path = f"{output_path}/{rig_name}"
    
    # Check if already exists
    if unreal.EditorAssetLibrary.does_asset_exist(rig_path):
        existing = unreal.load_asset(rig_path)
        if existing:
            log(f"✓ IK Rig already exists: {rig_path}")
            return existing
    
    # Ensure output directory exists
    if not unreal.EditorAssetLibrary.does_directory_exist(output_path):
        unreal.EditorAssetLibrary.make_directory(output_path)
        log(f"✓ Created directory: {output_path}")
    
    try:
        # Create IK Rig asset
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        factory = unreal.IKRigDefinitionFactory()
        
        ik_rig = asset_tools.create_asset(
            rig_name,
            output_path,
            unreal.IKRigDefinition,
            factory
        )
        
        if not ik_rig:
            log("✗ Failed to create IK Rig asset", "ERROR")
            return None
        
        log(f"✓ Created IK Rig: {rig_name}")
        
        # Get controller to configure the rig
        controller = unreal.IKRigController.get_controller(ik_rig)
        if not controller:
            log("✗ Could not get IKRigController", "ERROR")
            return ik_rig
        
        # Set skeletal mesh
        controller.set_skeletal_mesh(skeletal_mesh)
        log(f"  ✓ Set skeletal mesh: {skeletal_mesh.get_name()}")
        
        # Set retarget root
        controller.set_retarget_root("pelvis")
        log("  ✓ Set retarget root: pelvis")
        
        # Add retarget chains
        chains_added = 0
        for chain_name, start_bone, end_bone in RETARGET_CHAINS:
            try:
                result = controller.add_retarget_chain(chain_name, start_bone, end_bone, "")
                if result:
                    log(f"  ✓ Added chain: {chain_name} ({start_bone} → {end_bone})")
                    chains_added += 1
                else:
                    log(f"  ⊙ Chain exists or failed: {chain_name}", "WARNING")
            except Exception as e:
                log(f"  ⚠ Could not add chain {chain_name}: {e}", "WARNING")
        
        log(f"✓ Added {chains_added} retarget chains")
        
        # Save the asset
        unreal.EditorAssetLibrary.save_loaded_asset(ik_rig)
        return ik_rig
        
    except Exception as e:
        log(f"✗ Error creating IK Rig: {e}", "ERROR")
        return None

# ============================================================================
# IK RETARGETER SETUP
# ============================================================================
def create_ik_retargeter(source_rig, target_rig, source_mesh, target_mesh):
    """Create and configure IK Retargeter"""
    log("=" * 60)
    log("Creating IK Retargeter")
    log("=" * 60)
    
    retargeter_name = f"RTG_Manny_To_{METAHUMAN_NAME}"
    retargeter_path = f"{OUTPUT_PATH}/{retargeter_name}"
    
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
        
        # Set source IK Rig
        controller.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, source_rig)
        log(f"  ✓ Set source IK Rig: {source_rig.get_name()}")
        
        # Set target IK Rig
        controller.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, target_rig)
        log(f"  ✓ Set target IK Rig: {target_rig.get_name()}")
        
        # Auto-map chains using fuzzy matching
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
        
        # Apply A-pose adjustment for target (MetaHuman)
        apply_apose_adjustment(controller)
        
        # Save
        unreal.EditorAssetLibrary.save_loaded_asset(retargeter)
        return retargeter
        
    except Exception as e:
        log(f"✗ Error creating IK Retargeter: {e}", "ERROR")
        return None

# ============================================================================
# A-POSE ADJUSTMENT
# ============================================================================
def apply_apose_adjustment(retargeter_controller):
    """
    Adjust target skeleton pose from T-pose to A-pose.
    Manny is in A-pose, MetaHuman may be in T-pose.
    Rotate arms down ~50 degrees to match.
    """
    log("  Applying A-pose adjustment...")
    
    # Rotation offsets for T-pose to A-pose conversion
    # These values rotate the arms downward to match Manny's A-pose
    # Format: (bone_name, roll, pitch, yaw) in degrees
    APOSE_OFFSETS = [
        # Left arm - rotate down and slightly forward
        ("clavicle_l", 0, 0, -10),     # Slight clavicle adjustment
        ("upperarm_l", 0, -45, 0),     # Main arm rotation down
        
        # Right arm - mirror of left
        ("clavicle_r", 0, 0, 10),      # Slight clavicle adjustment  
        ("upperarm_r", 0, 45, 0),      # Main arm rotation down
    ]
    
    adjusted = 0
    for bone_name, roll, pitch, yaw in APOSE_OFFSETS:
        try:
            # Create rotation from euler angles
            rotation = unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)
            
            # Apply to target skeleton's retarget pose
            retargeter_controller.set_rotation_offset_for_retarget_pose_bone(
                bone_name,
                rotation,
                unreal.RetargetSourceOrTarget.TARGET
            )
            log(f"    ✓ Adjusted {bone_name}: ({roll}, {pitch}, {yaw})")
            adjusted += 1
        except Exception as e:
            log(f"    ⚠ Could not adjust {bone_name}: {e}", "WARNING")
    
    if adjusted > 0:
        log(f"  ✓ Applied A-pose adjustments to {adjusted} bones")
    else:
        log("  ⚠ No A-pose adjustments applied - may need manual adjustment", "WARNING")

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
        # Note: This may require additional steps depending on UE version
        if target_skeleton:
            try:
                # AnimBlueprint has a target_skeleton property
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
    log("MetaHuman IK Rig Retargeting")
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
        
        # Create IK Rig for MetaHuman (or use existing)
        metahuman_rig = create_ik_rig(
            metahuman['mesh'],
            f"IK_{METAHUMAN_NAME}",
            OUTPUT_PATH
        )
        
        # Use Manny's existing IK Rig or create one
        manny_rig = manny.get('ik_rig')
        if not manny_rig:
            manny_rig = create_ik_rig(
                manny['mesh'],
                "IK_Manny_Source",
                OUTPUT_PATH
            )
        
        if not metahuman_rig or not manny_rig:
            log("✗ FATAL: Could not create IK Rigs", "ERROR")
            save_log()
            return
        
        # Create IK Retargeter
        retargeter = create_ik_retargeter(
            manny_rig,
            metahuman_rig,
            manny['mesh'],
            metahuman['mesh']
        )
        
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
        log(f"  ✓ IK Rig: IK_{METAHUMAN_NAME}")
        log(f"  ✓ IK Retargeter: RTG_Manny_To_{METAHUMAN_NAME}")
        if retargeted:
            log(f"  ✓ Retargeted {len(retargeted)} animations")
        if anim_bp:
            log(f"  ✓ Animation Blueprint: ABP_{METAHUMAN_NAME}")
        log("")
        log("A-pose adjustment: Applied (clavicle + upperarm rotations)")
        log("")
        log("Next steps:")
        log("1. Assign ABP_Pia to your MetaHuman character")
        log("2. Open IK Retargeter to verify preview looks correct")
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
