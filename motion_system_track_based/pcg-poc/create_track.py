"""
400 Meter Oval Track - Fixed Version
1. Better cleanup (all tracks and splines)
2. Proper oval shape (parallel straights with connecting curves)
"""
import unreal
import math
import sys

# ==============================================================================
# LOGGING
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\create_track.log"

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
print("400 METER OVAL TRACK GENERATOR - FIXED")
print("=" * 80)

# ==============================================================================
# CONFIGURATION
# ==============================================================================
STRAIGHT_LENGTH = 10000.0  # 100 meters
TRACK_WIDTH = 6360.0  # Distance between parallel straights (to make curves = 100m)
# Curve radius: circumference = 2 * pi * r = 200m (two curves), so r = 100/pi ≈ 3183
CURVE_RADIUS = 100.0 * 100 / math.pi  # 100m arc length

START_POSITION = unreal.Vector(0, 0, 50)
ROAD_WIDTH = 400.0  # 4 meters wide
SEGMENT_SPACING = 200.0  # 2 meters between segments

# ==============================================================================
# CLEANUP - DELETE EVERYTHING
# ==============================================================================
def cleanup_all_tracks():
    """Remove ALL previous tracks, splines, and related actors"""
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    print("\nCleaning up old tracks...")
    
    # Get all actors
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    
    deleted = 0
    for actor in all_actors:
        label = actor.get_actor_label()
        # Delete anything with Track, Spline, or PCG in the name
        if any(keyword in label for keyword in ["Track", "Spline", "track", "spline", "PCG"]):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            deleted += 1
    
    if deleted > 0:
        print(f"✓ Deleted {deleted} old track/spline actor(s)")
    else:
        print("✓ No old tracks to clean up")

# ==============================================================================
# CREATE PROPER OVAL TRACK
# ==============================================================================
def create_oval_track():
    """Create proper oval: two parallel straights connected by semicircular curves"""
    
    print("\nGenerating oval track path...")
    print(f"  Straight sections: {STRAIGHT_LENGTH/100:.0f}m each")
    print(f"  Track width: {TRACK_WIDTH/100:.1f}m")
    print(f"  Curve radius: {CURVE_RADIUS/100:.1f}m")
    
    points = []
    
    # Calculate offsets to center the track at origin
    offset_x = STRAIGHT_LENGTH / 2  # Center horizontally
    offset_y = TRACK_WIDTH / 2       # Center vertically
    
    # SECTION 1: First straight (bottom, left to right)
    print("\n  Section 1: Bottom straight (100m)...")
    for i in range(50):
        t = i / 49.0
        x = t * STRAIGHT_LENGTH - offset_x
        y = 0 - offset_y
        z = 0
        points.append((x, y, z))
    
    # SECTION 2: Right curve (semicircle connecting bottom to top)
    print("  Section 2: Right curve (semicircle)...")
    for i in range(1, 50):
        t = i / 49.0
        angle = t * math.pi  # 0 to 180 degrees
        
        # Center of right curve
        center_x = STRAIGHT_LENGTH - offset_x
        center_y = TRACK_WIDTH / 2 - offset_y
        
        # Semicircle going from bottom straight to top straight
        x = center_x + (TRACK_WIDTH / 2) * math.cos(angle - math.pi/2)
        y = center_y + (TRACK_WIDTH / 2) * math.sin(angle - math.pi/2)
        z = 0
        points.append((x, y, z))
    
    # SECTION 3: Second straight (top, right to left - parallel to first)
    print("  Section 3: Top straight (100m, parallel to bottom)...")
    for i in range(1, 50):
        t = i / 49.0
        x = STRAIGHT_LENGTH - (t * STRAIGHT_LENGTH) - offset_x  # Going backwards
        y = TRACK_WIDTH - offset_y
        z = 0
        points.append((x, y, z))
    
    # SECTION 4: Left curve (semicircle connecting top back to bottom)
    print("  Section 4: Left curve (semicircle)...")
    for i in range(1, 50):
        t = i / 49.0
        angle = t * math.pi  # 0 to 180 degrees
        
        # Center of left curve
        center_x = 0 - offset_x
        center_y = TRACK_WIDTH / 2 - offset_y
        
        # Semicircle going from top straight back to bottom straight
        x = center_x + (TRACK_WIDTH / 2) * math.cos(angle + math.pi/2)
        y = center_y + (TRACK_WIDTH / 2) * math.sin(angle + math.pi/2)
        z = 0
        points.append((x, y, z))
    
    print(f"\n✓ Generated {len(points)} path points")
    print(f"✓ Track centered at origin (0, 0)")
    
    # Load cube mesh
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
    
    if not cube_mesh:
        print("✗ Could not load cube mesh")
        return
    
    print(f"\nCreating road segments...")
    
    # Create road segments
    created = 0
    for i, (x, y, z) in enumerate(points):
        location = unreal.Vector(
            START_POSITION.x + x,
            START_POSITION.y + y,
            START_POSITION.z + z
        )
        
        # Create mesh actor
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor,
            location
        )
        
        actor.set_actor_label(f"Track_Segment_{i}")
        actor.set_folder_path(unreal.Name("PCG_Track"))
        actor.static_mesh_component.set_static_mesh(cube_mesh)
        
        # Calculate rotation to next point
        if i < len(points) - 1:
            next_x, next_y, next_z = points[i + 1]
            dx = next_x - x
            dy = next_y - y
            angle = math.atan2(dy, dx)
            yaw = math.degrees(angle)
            actor.set_actor_rotation(unreal.Rotator(0, yaw, 0), teleport_physics=False)
        else:
            # Last segment points to first
            next_x, next_y, next_z = points[0]
            dx = next_x - x
            dy = next_y - y
            angle = math.atan2(dy, dx)
            yaw = math.degrees(angle)
            actor.set_actor_rotation(unreal.Rotator(0, yaw, 0), teleport_physics=False)
        
        # Scale to road dimensions
        actor.set_actor_scale3d(unreal.Vector(
            SEGMENT_SPACING / 100.0,  # Length
            ROAD_WIDTH / 100.0,        # Width
            0.1                         # Height
        ))
        
        # Apply dark grey material
        mesh_comp = actor.static_mesh_component
        dmi = mesh_comp.create_dynamic_material_instance(0)
        if dmi:
            dmi.set_vector_parameter_value("Color", unreal.LinearColor(0.2, 0.2, 0.2, 1.0))
            dmi.set_scalar_parameter_value("Roughness", 0.8)
        
        created += 1
        
        if created % 50 == 0:
            print(f"  Progress: {created}/{len(points)} segments")
    
    # Calculate actual track dimensions
    total_length = (2 * STRAIGHT_LENGTH) + (2 * math.pi * (TRACK_WIDTH / 2))
    
    print("\n" + "=" * 80)
    print("✓ OVAL TRACK CREATED!")
    print("=" * 80)
    print(f"Total Segments: {created}")
    print(f"Road Width: {ROAD_WIDTH/100:.1f}m")
    print(f"Track Layout:")
    print(f"  • Bottom straight: {STRAIGHT_LENGTH/100:.0f}m")
    print(f"  • Right curve: semicircle")
    print(f"  • Top straight: {STRAIGHT_LENGTH/100:.0f}m (parallel)")
    print(f"  • Left curve: semicircle")
    print(f"Total Track Length: ~{total_length/100:.0f}m")
    print(f"Location: Origin at Z=0.5m")
    print(f"Folder: PCG_Track")
    print(f"\n✓ Log saved to: {LOG_FILE_PATH}")

# ==============================================================================
# MAIN
# ==============================================================================
try:
    cleanup_all_tracks()
    create_oval_track()
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
