"""
400m Oval Track Generator (Hybrid Approach)
- Straights: Uses single continuous decals (perfect smooth lines, like the 100m sprint)
- Curves: Uses segmented decals (approximating the curve)
"""
import unreal
import sys
import math

# ==============================================================================
# LOGGING
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\create_400m_track.log"

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
print("GENERATING 400M OVAL TRACK (HYBRID)")
print("=" * 80)

# ==============================================================================
# CONFIGURATION
# ==============================================================================
NUM_LANES = 6
LANE_WIDTH = 122.0      # 1.22m
TRACK_WIDTH = NUM_LANES * LANE_WIDTH

# Dimensions
STRAIGHT_LEN = 10000.0  # 100m
CURVE_LEN = 10000.0     # 100m
RADIUS = CURVE_LEN / math.pi # ~3183.1 cm

# Decals
LINE_WIDTH = 5.0
DECAL_HEIGHT = 200.0

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
    clean_labels = ["SimpleTrack", "LaneLine", "StartFinish", "Track_Segment", "OvalTrack"]
    
    for actor in all_actors:
        label = actor.get_actor_label()
        if any(key in label for key in clean_labels):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            deleted += 1
            
    print(f"✓ Removed {deleted} old actors")

# ==============================================================================
# HELPERS
# ==============================================================================
def create_decal(name, location, rotation, size_x, size_y, size_z):
    """
    Create a decal actor at location/rotation
    size_x: Projection Depth
    size_y: Width (Local Y)
    size_z: Length (Local Z)
    """
    decal_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DecalActor,
        location
    )
    decal_actor.set_actor_label(name)
    decal_actor.set_folder_path(unreal.Name("OvalTrack/Decals"))
    
    decal_comp = decal_actor.decal
    
    size_vector = unreal.Vector(size_x, size_y, size_z)
    decal_comp.set_editor_property("DecalSize", size_vector)
    decal_actor.set_actor_rotation(rotation, teleport_physics=False)
    
    # Material
    dmi = decal_comp.create_dynamic_material_instance()
    if dmi:
        dmi.set_vector_parameter_value("Color", unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
        
    return decal_actor

# ==============================================================================
# BUILDER FUNCTIONS
# ==============================================================================

def build_straight_section(section_index, start_pos, length, rotation_yaw):
    """
    Builds a straight section using ONE large mesh and ONE large decal set.
    """
    print(f"\nBuilding Straight Section {section_index}...")
    
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
    asphalt_mat = unreal.load_object(None, ASPHALT_MATERIAL)
    
    # 1. Asphalt Mesh
    # Center of straight
    # If rotation is 0 (East): x goes from start_x to start_x + length.
    # We spawn at center.
    
    forward_vec = unreal.Vector(math.cos(math.radians(rotation_yaw)), math.sin(math.radians(rotation_yaw)), 0)
    center_pos = start_pos + (forward_vec * (length / 2.0))
    
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        center_pos
    )
    actor.set_actor_label(f"OvalTrack_Straight_{section_index}")
    actor.set_folder_path(unreal.Name("OvalTrack/Mesh"))
    actor.static_mesh_component.set_static_mesh(cube_mesh)
    
    # Scale: X=Length, Y=Width
    actor.static_mesh_component.set_world_scale3d(unreal.Vector(
        length / 100.0,
        TRACK_WIDTH / 100.0,
        0.1
    ))
    actor.set_actor_rotation(unreal.Rotator(0, rotation_yaw, 0), teleport_physics=False)
    
    if asphalt_mat:
        actor.static_mesh_component.set_material(0, asphalt_mat)
        
    # 2. Lane Dividers (Continuous Lines)
    # Using specific rotation logic from 100m sprint script that worked:
    # Rot(-90, 90, 0) relative to Track Forward.
    # Actually, we need to combine with Track Yaw.
    
    # Base Rotation for Line running along X: Rot(-90, 90, 0) -> Local Y is Length (World X), Local Z is Width (World Y).
    # If Track Yaw is 0: Use Rot(-90, 90, 0).
    # If Track Yaw is 180: Use Rot(-90, 90+180, 0) -> Rot(-90, 270, 0).
    
    # Decal:
    # Size X: Depth
    # Size Y: Length (Along Track) -> length/2
    # Size Z: Width (Across Track) -> LINE_WIDTH/2
    
    decal_rot = unreal.Rotator(-90, 90 + rotation_yaw, 0)
    
    # Start Y offset (World Local Y)
    start_y_local = -(TRACK_WIDTH / 2)
    
    for i in range(NUM_LANES + 1):
        line_y_local = start_y_local + (i * LANE_WIDTH)
        
        # Calculate World Position for Decal Center
        # It's at 'center_pos' + 'offset'
        # Offset is 'line_y_local' in the Right Vector direction
        
        right_vec = unreal.Vector(
            math.cos(math.radians(rotation_yaw + 90)),
            math.sin(math.radians(rotation_yaw + 90)), 
            0
        )
        
        decal_pos = center_pos + (right_vec * line_y_local)
        decal_pos.z = 51 # Height
        
        create_decal(
            f"Straight_{section_index}_Line_{i}",
            decal_pos,
            decal_rot,
            DECAL_HEIGHT,
            length / 2.0,      # Size Y (Length)
            LINE_WIDTH / 2.0   # Size Z (Width)
        )

def build_curve_section(section_index, start_angle_deg, end_angle_deg, center_x, center_y):
    """
    Builds a curve using segments.
    """
    print(f"\nBuilding Curve Section {section_index}...")
    
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
    asphalt_mat = unreal.load_object(None, ASPHALT_MATERIAL)
    
    # Arc Length calculation
    angle_diff = end_angle_deg - start_angle_deg
    arc_len = abs(math.radians(angle_diff) * RADIUS)
    
    # Segment count
    # Use 1m segments for smoothness
    seg_len = 100.0 
    num_segments = int(arc_len / seg_len)
    
    angle_step = angle_diff / num_segments
    
    for i in range(num_segments):
        # Current angle
        # We want center of segment, so i + 0.5
        current_angle = start_angle_deg + (angle_step * (i + 0.5))
        rad = math.radians(current_angle)
        
        # Pos
        x = center_x + (RADIUS * math.cos(rad))
        y = center_y + (RADIUS * math.sin(rad))
        
        # Tangent Yaw
        # For a circle, tangent is angle + 90
        # If moving CCW.
        # Check: Angle -90 (Bottom). Pos (0, -R). Tangent 0 (East). -90+90=0. OK.
        yaw = current_angle + 90
        
        loc = unreal.Vector(x, y, 0)
        rot = unreal.Rotator(0, yaw, 0)
        
        # Mesh
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor,
            loc
        )
        actor.set_actor_label(f"Curve_{section_index}_Seg_{i}")
        actor.set_folder_path(unreal.Name("OvalTrack/Mesh"))
        actor.static_mesh_component.set_static_mesh(cube_mesh)
        actor.static_mesh_component.set_world_scale3d(unreal.Vector(seg_len/100.0, TRACK_WIDTH/100.0, 0.1))
        actor.set_actor_rotation(rot, teleport_physics=False)
        
        if asphalt_mat:
            actor.static_mesh_component.set_material(0, asphalt_mat)
            
        # Decals (Segmented)
        start_y_local = -(TRACK_WIDTH / 2)
        
        for k in range(NUM_LANES + 1):
            line_y_local = start_y_local + (k * LANE_WIDTH)
            
            # Offset logic (same as Straight really, just varying Yaw)
            yaw_rad = math.radians(yaw)
            offset_x = -line_y_local * math.sin(yaw_rad)
            offset_y = line_y_local * math.cos(yaw_rad)
            
            decal_loc = unreal.Vector(loc.x + offset_x, loc.y + offset_y, 51)
            decal_rot = unreal.Rotator(-90, 90 + yaw, 0)
            
            create_decal(
                f"Curve_{section_index}_{i}_Line_{k}",
                decal_loc,
                decal_rot,
                DECAL_HEIGHT,
                seg_len / 2.0,
                LINE_WIDTH / 2.0
            )

# ==============================================================================
# MAIN BUILD LOOP
# ==============================================================================
def build_track():
    print(f"\nBuilding 400m Oval Track (Hybrid Mode)...")
    
    # Track Layout Calculation
    # Straight Len: 100m
    # Curve Len: 100m -> R = 31.83m
    
    # 1. Bottom Straight (0 to 100m)
    # Starts at x = -50m, y = -R. Goes East (Yaw 0).
    # Center is (0, -R).
    
    start_x = -(STRAIGHT_LEN / 2.0)
    pos_straight_1 = unreal.Vector(start_x, -RADIUS, 0)
    # Actually, our helper spawns at Center.
    # So we pass start pos, it calculates center.
    build_straight_section(1, pos_straight_1, STRAIGHT_LEN, 0)
    
    # 2. Right Curve (100 to 200m)
    # Center of curvature is (50m, 0)
    # Angles: -90 (Bottom) to 90 (Top)
    
    center_of_curve_right_x = (STRAIGHT_LEN / 2.0)
    build_curve_section(2, -90, 90, center_of_curve_right_x, 0)
    
    # 3. Top Straight (200 to 300m)
    # Starts at x = 50m, y = R. Goes West (Yaw 180).
    start_x_top = (STRAIGHT_LEN / 2.0)
    pos_straight_2 = unreal.Vector(start_x_top, RADIUS, 0)
    build_straight_section(3, pos_straight_2, STRAIGHT_LEN, 180)
    
    # 4. Left Curve (300 to 400m)
    # Center of curvature (-50m, 0)
    # Angles: 90 (Top) to 270 (Bottom)
    
    center_of_curve_left_x = -(STRAIGHT_LEN / 2.0)
    build_curve_section(4, 90, 270, center_of_curve_left_x, 0)
    
    # 5. Finish Line
    # At end of Straight 1 (x=50m, y=-R) OR Start of Straight 1 (-50m)?
    # Standard usually has finish line at end of straight.
    # Let's put it at x = (STRAIGHT_LEN/2) - FinLineWidth/2, y = -R.
    
    fin_loc = unreal.Vector((STRAIGHT_LEN / 2.0), -RADIUS, 51)
    
    # Finish Line Rotation: Perpendicular to Track (Yaw 0).
    # Track Yaw 0. Perpendicular is Yaw 90 relative to Track? No.
    # Wait, our Start/Finish logic in 100m used Rot(-90, 0, 0).
    # Which mapped Y-axis (Span) to World Y-axis (Across track).
    # Since Straight 1 is aligned with World X, World Y is indeed across the track.
    
    create_decal(
        "FinishLine",
        fin_loc,
        unreal.Rotator(-90, 0, 0),
        DECAL_HEIGHT,
        TRACK_WIDTH / 2.0, # Span (Y)
        50.0 # Thickness (Z) -> 1m
    )
    
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
