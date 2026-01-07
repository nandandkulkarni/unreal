"""
Fixed Track Generator (V1 Fixed)
Generates 6-Lane Track with Correct Decal Alignments
"""
import unreal
import sys

# ==============================================================================
# LOGGING
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\create_100m_sprint_track.log"

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
print("FIXING TRACK GENERATION (X-AXIS ALIGNMENT)")
print("=" * 80)

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# Track
NUM_LANES = 6
LANE_WIDTH = 122.0      # Standard 1.22m
TRACK_WIDTH = NUM_LANES * LANE_WIDTH
TRACK_LENGTH = 10000.0  # 100 meters
SEGMENT_LENGTH = 200.0  # 2m mesh segments

# Decals
LINE_WIDTH = 5.0        # 5cm standard width
START_LINE_WIDTH = 5.0
FINISH_LINE_WIDTH = 5.0
DECAL_HEIGHT = 200.0    # Projection depth

# Assets
ASPHALT_MATERIAL = "/Game/Fab/Megascans/Surfaces/Asphalt_Fresh_sfrofg0a/High/sfrofg0a_tier_1/Materials/MI_sfrofg0a.MI_sfrofg0a"

# ==============================================================================
# CLEANUP
# ==============================================================================
def cleanup_scene():
    """Remove all track related actors"""
    print("\nCleaning up old track & decals...")
    world = unreal.EditorLevelLibrary.get_editor_world()
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    
    deleted = 0
    clean_labels = ["SimpleTrack", "LaneLine", "StartFinish", "Track_Segment", "StartLine", "FinishLine"]
    
    for actor in all_actors:
        label = actor.get_actor_label()
        if any(key in label for key in clean_labels):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            deleted += 1
            
    print(f"✓ Removed {deleted} old actors")

# ==============================================================================
# DECAL HELPERS
# ==============================================================================
def create_decal(name, x, y, size_x, size_y, size_z, rotation):
    """Generic decal creator"""
    location = unreal.Vector(x, y, 51) # Just above ground
    
    decal_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DecalActor,
        location
    )
    decal_actor.set_actor_label(name)
    decal_actor.set_folder_path(unreal.Name("SimpleTrack/Decals"))
    
    decal_comp = decal_actor.decal
    
    # DecalSize property expects half-extents
    # X = Projection Axis (Depth)
    # Y = Width
    # Z = Length
    
    size_vector = unreal.Vector(
        size_x, # Projection
        size_y, # Width
        size_z  # Length
    )
    
    decal_comp.set_editor_property("DecalSize", size_vector)
    decal_actor.set_actor_rotation(rotation, teleport_physics=False)
    
    # Material (Basic White)
    dmi = decal_comp.create_dynamic_material_instance()
    if dmi:
        dmi.set_vector_parameter_value("Color", unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
        
    return decal_actor

def add_lane_divider(index, y_pos):
    """
    Add a solid lane divider running along X-Axis
    
    Correction:
    - User reported Rot(-90, 0, 0) was perpendicular.
    - We will try Rot(-90, 90, 0).
    - Align Local Y with World X (Track Length).
    - Align Local Z with World Y (Track Width/Thickness).
    """
    
    rotation = unreal.Rotator(-90, 90, 0) 
    
    # Logic with Yaw 90:
    # Local Y -> World X (Track Direction/Length) -> Make this LARGE
    # Local Z -> World Y (Line Thickness) -> Make this SMALL
    
    proj_depth = DECAL_HEIGHT
    length_extent = TRACK_LENGTH / 2.0 # Make Y Large
    width_extent = LINE_WIDTH / 2.0    # Make Z Small
    
    create_decal(
        f"LaneLine_Solid_{index}",
        0,              # Center X
        y_pos,          # Y Position
        proj_depth,     # Size X
        length_extent,  # Size Y (Length)
        width_extent,   # Size Z (Width)
        rotation
    )

def add_start_finish_line(name, x_pos, width):
    """
    Add horizontal line across Y-Axis (Start/Finish)
    
    Correction:
    - Needs to run along World Y.
    - Use Rot(-90, 0, 0).
    - Align Local Y with World Y (Line Span/Width).
    - Align Local Z with World X (Line Thickness).
    """
    
    rotation = unreal.Rotator(-90, 0, 0)
    
    # Logic with Yaw 0:
    # Local Y -> World Y (Track Width/Span) -> Make this LARGE
    # Local Z -> World X (Line Thickness) -> Make this SMALL
    
    proj_depth = DECAL_HEIGHT
    
    span_extent = width / 2.0             # Make Y Large
    thickness_extent = START_LINE_WIDTH / 2.0 # Make Z Small
    
    create_decal(
        name,
        x_pos,
        0,              # Center Y
        proj_depth,     # Size X
        span_extent,    # Size Y (Span)
        thickness_extent, # Size Z (Thickness)
        rotation
    )

# ==============================================================================
# BUILD TRACK
# ==============================================================================
def build_track():
    print(f"\nBuilding 6-Lane Track ({TRACK_WIDTH/100:.2f}m wide)...")
    
    # 1. Mesh
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
    asphalt_mat = unreal.load_object(None, ASPHALT_MATERIAL)
    
    num_segments = int(TRACK_LENGTH / SEGMENT_LENGTH)
    
    for i in range(num_segments):
        x = (i * SEGMENT_LENGTH) - (TRACK_LENGTH / 2) + (SEGMENT_LENGTH / 2)
        
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor,
            unreal.Vector(x, 0, 0)
        )
        actor.set_actor_label(f"SimpleTrack_Segment_{i}")
        actor.set_folder_path(unreal.Name("SimpleTrack/Mesh"))
        actor.static_mesh_component.set_static_mesh(cube_mesh)
        actor.set_actor_scale3d(unreal.Vector(SEGMENT_LENGTH/100.0, TRACK_WIDTH/100.0, 0.1))
        
        if asphalt_mat:
            actor.static_mesh_component.set_material(0, asphalt_mat)

    print(f"✓ Created track mesh")

    # 2. Lane Dividers (X-Axis)
    print("\nAdding Lane Dividers (X-Axis aligned)...")
    start_y = -(TRACK_WIDTH / 2)
    
    for i in range(NUM_LANES + 1):
        line_y = start_y + (i * LANE_WIDTH)
        add_lane_divider(i, line_y)
        
    print(f"✓ Created {NUM_LANES + 1} dividers")

    # 3. Start/Finish Lines (Y-Axis)
    print("\nAdding Start/Finish Lines (Y-Axis aligned)...")
    
    add_start_finish_line("StartLine", -(TRACK_LENGTH / 2) + 2.5, TRACK_WIDTH)
    add_start_finish_line("FinishLine", (TRACK_LENGTH / 2) - 2.5, TRACK_WIDTH)
    
    print("✓ Created markings")
    
    print("\n✓ COMPLETE")

# ==============================================================================
# EXECUTE
# ==============================================================================
try:
    cleanup_scene()
    build_track()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
