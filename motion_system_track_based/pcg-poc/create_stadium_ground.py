"""
Full Stadium Ground Generator
Creates a single large oval grass surface that covers the ENTIRE stadium area.
(Infield + Track + Outfield)
This serves as the "Landscape" for PCG grass.
"""
import unreal
import sys
import math

# ==============================================================================
# LOGGING
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\create_stadium_ground.log"

class FileLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
        
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = FileLogger(LOG_FILE_PATH)

print("=" * 80)
print("GENERATING FULL STADIUM GROUND")
print("=" * 80)

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# Track Params
NUM_LANES = 6
LANE_WIDTH = 122.0
TRACK_WIDTH = NUM_LANES * LANE_WIDTH # ~732 cm
STRAIGHT_LEN = 10000.0
CURVE_LEN = 10000.0
RADIUS = CURVE_LEN / math.pi # ~3183.1 cm

# Stadium Margin (Outfield size)
MARGIN = 3000.0 # 30m outfield

# Outer Dimensions
# The ground must extend to RADIUS + TRACK/2 + MARGIN
STADIUM_RADIUS = (RADIUS + (TRACK_WIDTH / 2.0)) + MARGIN
STADIUM_WIDTH = STADIUM_RADIUS * 2.0

# Assets
GRASS_MATERIAL = "/Game/Fab/Megascans/Surfaces/Lawn_Grass_tkynejer/High/tkynejer_tier_1/Materials/MI_tkynejer.MI_tkynejer"

# ==============================================================================
# CLEANUP
# ==============================================================================
def cleanup_stadium():
    print("\nCleaning up old stadium ground...")
    world = unreal.EditorLevelLibrary.get_editor_world()
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    
    deleted = 0
    clean_labels = ["Stadium_Ground", "Infield_Rect", "Infield_End"] # Remove infield too, as this replaces it
    
    for actor in all_actors:
        label = actor.get_actor_label()
        if any(key in label for key in clean_labels):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            deleted += 1
            
    print(f"✓ Removed {deleted} old actors")

# ==============================================================================
# BUILDER
# ==============================================================================
def build_stadium():
    print(f"\nBuilding Full Stadium Ground...")
    
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
    cyl_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cylinder.Cylinder")
    grass_mat = unreal.load_object(None, GRASS_MATERIAL)
    
    # 1. Central Rectangle
    rect_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(0, 0, -5) # Z = -5 (Below track)
    )
    rect_actor.set_actor_label("Stadium_Ground_Rect")
    rect_actor.set_folder_path(unreal.Name("OvalTrack/Stadium"))
    rect_actor.static_mesh_component.set_static_mesh(cube_mesh)
    
    # Scale
    rect_actor.set_actor_scale3d(unreal.Vector(
        STRAIGHT_LEN / 100.0,
        STADIUM_WIDTH / 100.0, 
        0.1
    ))
    
    # Material & Tiling
    if grass_mat:
        dmi = rect_actor.static_mesh_component.create_dynamic_material_instance(0, grass_mat)
        scale_factor = 30.0
        dmi.set_scalar_parameter_value("Tiling", scale_factor)
        dmi.set_scalar_parameter_value("Main Tiling", scale_factor)
        
    # 2. End Caps
    scale_xy = STADIUM_RADIUS / 50.0 # Cylinder Radius is 50
    
    positions = [
        ("Stadium_Ground_Right", unreal.Vector(STRAIGHT_LEN / 2.0, 0, -5)),
        ("Stadium_Ground_Left", unreal.Vector(-(STRAIGHT_LEN / 2.0), 0, -5))
    ]
    
    for name, loc in positions:
        cap_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor,
            loc
        )
        cap_actor.set_actor_label(name)
        cap_actor.set_folder_path(unreal.Name("OvalTrack/Stadium"))
        cap_actor.static_mesh_component.set_static_mesh(cyl_mesh)
        
        cap_actor.set_actor_scale3d(unreal.Vector(scale_xy, scale_xy, 0.1))
        
        if grass_mat:
            cap_dmi = cap_actor.static_mesh_component.create_dynamic_material_instance(0, grass_mat)
            cap_dmi.set_scalar_parameter_value("Tiling", scale_factor)
            cap_dmi.set_scalar_parameter_value("Main Tiling", scale_factor)
            
    # 3. Add PCG Volume (Preparation)
    # We spawn a PCGVolume actor that encloses this area.
    # The user can then assign a graph to it.
    
    pcg_vol_cls = unreal.load_class(None, "/Script/PCG.PCGVolume")
    if pcg_vol_cls:
        pcg_vol = unreal.EditorLevelLibrary.spawn_actor_from_class(
            pcg_vol_cls,
            unreal.Vector(0, 0, 100)
        )
        pcg_vol.set_actor_label("Stadium_Grass_PCG_Volume")
        pcg_vol.set_folder_path(unreal.Name("OvalTrack/PCG"))
        
        # Scale to cover stadium
        # Box Extent logic? No, set_actor_scale on a Volume usually works differently or uses BrushComponent.
        # But PCGVolume is usually a Bounds.
        # Let's set scale: X=TotalLen, Y=Width, Z=Height
        
        total_len = STRAIGHT_LEN + (STADIUM_RADIUS * 2) 
        pcg_vol.set_actor_scale3d(unreal.Vector(total_len/100.0, STADIUM_WIDTH/100.0, 10.0))
        print("✓ Created PCG Volume (Empty)")
    else:
        print("⚠ PCGVolume class not found (Plugin might be disabled or path differs)")

    print("✓ Created Full Stadium Ground")
    print(f"\n✓ Log saved to: {LOG_FILE_PATH}")

# ==============================================================================
# EXECUTE
# ==============================================================================
try:
    cleanup_stadium()
    build_stadium()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
