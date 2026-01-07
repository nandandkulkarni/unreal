"""
400m Track Infield Generator (Fixed Tiling)
- Increases Texture Tiling to make grass blades look smaller/realistic
- Prepares surface for PCG
"""
import unreal
import sys
import math

# ==============================================================================
# LOGGING
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\create_infield.log"

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
print("GENERATING INFIELD GRASS SURFACE (FIXED TILING)")
print("=" * 80)

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# Track Dimensions
NUM_LANES = 6
LANE_WIDTH = 122.0
TRACK_WIDTH = NUM_LANES * LANE_WIDTH
STRAIGHT_LEN = 10000.0
CURVE_LEN = 10000.0
RADIUS = CURVE_LEN / math.pi
INFIELD_RADIUS = RADIUS - (TRACK_WIDTH / 2.0)
INFIELD_WIDTH = INFIELD_RADIUS * 2.0

# Assets
GRASS_MATERIAL = "/Game/Fab/Megascans/Surfaces/Lawn_Grass_tkynejer/High/tkynejer_tier_1/Materials/MI_tkynejer.MI_tkynejer"

# Tiling Factor
# If blades are too big, we need to repeat the texture MORE times per meter.
# Default UV mapping on Basic Shapes: 1 UV unit = 1 Mesh Unit (usually).
# Actually default Cube maps 0-1 across the face.
# If face is 50m wide, texture stretches 50m! That's huge blades.
# We need to scale UVs.
# StaticMeshComponent has 'set_material' but not straightforward UV scale without a custom material instance or adjusting the mesh.
# BUT! We can use "TextureCoordinate" in Material or simpler:
# Create a Dynamic Material Instance and look for "Tiling" parameter typical in Megascans.
# Megascans usually has "Tiling" or "Main Tiling" or "UTiling"/"VTiling".
# Let's try Tiling = 50.0 (so 1 texture repeat = 1m approx).

# ==============================================================================
# CLEANUP
# ==============================================================================
def cleanup_infield():
    """Remove old infield actors"""
    print("\nCleaning up old infield...")
    world = unreal.EditorLevelLibrary.get_editor_world()
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    
    deleted = 0
    for actor in all_actors:
        label = actor.get_actor_label()
        if "Infield_" in label:
            unreal.EditorLevelLibrary.destroy_actor(actor)
            deleted += 1
            
    print(f"✓ Removed {deleted} old actors")

# ==============================================================================
# BUILDER
# ==============================================================================
def build_infield():
    print(f"\nBuilding Infield Surface...")
    
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
    cyl_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cylinder.Cylinder")
    grass_mat = unreal.load_object(None, GRASS_MATERIAL)
    
    if not grass_mat:
        print("⚠ Grass material not found")
        return

    # 1. Start with Rectangle
    rect_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(0, 0, 0)
    )
    rect_actor.set_actor_label("Infield_Rect")
    rect_actor.set_folder_path(unreal.Name("OvalTrack/Infield"))
    rect_actor.static_mesh_component.set_static_mesh(cube_mesh)
    
    # Scale
    rect_actor.set_actor_scale3d(unreal.Vector(
        STRAIGHT_LEN / 100.0,
        INFIELD_WIDTH / 100.0, 
        0.1
    ))
    
    # 2. Material Tiling Logic
    # We can try to create a DMI and set Tiling.
    # Standard Megascans param is often "Tiling".
    
    dmi = rect_actor.static_mesh_component.create_dynamic_material_instance(0, grass_mat)
    
    # Try setting Tiling to a high value (e.g. 50 or 100)
    # Beacuse the mesh is scaled up by ~100x.
    scale_factor = 20.0 # Try 20x tiling
    
    # Try common parameter names
    dmi.set_scalar_parameter_value("Tiling", scale_factor)
    dmi.set_scalar_parameter_value("Main Tiling", scale_factor)
    dmi.set_scalar_parameter_value("U Tiling", scale_factor)
    dmi.set_scalar_parameter_value("V Tiling", scale_factor)
    
    # 3. Cylinders
    scale_xy = INFIELD_RADIUS / 50.0
    
    positions = [
        ("Infield_End_Right", unreal.Vector(STRAIGHT_LEN / 2.0, 0, 0)),
        ("Infield_End_Left", unreal.Vector(-(STRAIGHT_LEN / 2.0), 0, 0))
    ]
    
    for name, loc in positions:
        cap_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor,
            loc
        )
        cap_actor.set_actor_label(name)
        cap_actor.set_folder_path(unreal.Name("OvalTrack/Infield"))
        cap_actor.static_mesh_component.set_static_mesh(cyl_mesh)
        
        cap_actor.set_actor_scale3d(unreal.Vector(scale_xy, scale_xy, 0.1))
        
        # Apply same DMI or new one with same settings?
        # Better new one to be safe
        cap_dmi = cap_actor.static_mesh_component.create_dynamic_material_instance(0, grass_mat)
        cap_dmi.set_scalar_parameter_value("Tiling", scale_factor)
        cap_dmi.set_scalar_parameter_value("Main Tiling", scale_factor)
    
    print("✓ Created Infield (Tiling Adjusted ~20x)")

# ==============================================================================
# EXECUTE
# ==============================================================================
try:
    cleanup_infield()
    build_infield()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
