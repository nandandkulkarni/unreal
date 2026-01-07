"""
Grand Canyon Terrain Generator
Fetches real-world elevation data using lat/lon coordinates and generates 3D terrain

Uses Open-Elevation API to get elevation data for the Grand Canyon
"""
import unreal
import math
import sys
import datetime
try:
    import requests
    import json
except ImportError:
    print("ERROR: 'requests' library not available in Unreal Python environment")
    print("You may need to install it or use a different approach")
    sys.exit(1)

# ==============================================================================
# LOGGING SETUP
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\grand_canyon.log"

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

def log(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

print("=" * 80)
log("GRAND CANYON TERRAIN GENERATOR")
print("=" * 80)

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# Grand Canyon coordinates (South Rim area)
CENTER_LAT = 36.0544  # South Rim
CENTER_LON = -112.1401
AREA_SIZE_KM = 5.0  # 5km x 5km area

# Grid resolution
GRID_SIZE = 50  # 50x50 = 2500 elevation queries (be mindful of API limits)

# Scaling
HORIZONTAL_SCALE = 100.0  # Unreal units per meter
VERTICAL_SCALE = 1.0      # Vertical exaggeration (1.0 = realistic)

# ==============================================================================
# ELEVATION DATA FETCHING
# ==============================================================================
def fetch_elevation_batch(locations):
    """
    Fetch elevation data for multiple lat/lon points using Open-Elevation API
    locations: list of {"latitude": lat, "longitude": lon} dicts
    Returns: list of elevations in meters
    """
    url = "https://api.open-elevation.com/api/v1/lookup"
    
    try:
        log(f"  Fetching elevation for {len(locations)} points...")
        response = requests.post(
            url,
            json={"locations": locations},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            elevations = [point["elevation"] for point in data["results"]]
            return elevations
        else:
            log(f"  ✗ API Error: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        log(f"  ✗ Error fetching elevation: {e}")
        return None

def generate_elevation_grid():
    """Generate a grid of lat/lon points and fetch their elevations"""
    log(f"\n1. Generating {GRID_SIZE}x{GRID_SIZE} elevation grid...")
    
    # Calculate lat/lon offsets (approximate, 1 degree ≈ 111km)
    km_per_degree_lat = 111.0
    km_per_degree_lon = 111.0 * math.cos(math.radians(CENTER_LAT))
    
    lat_offset = (AREA_SIZE_KM / 2) / km_per_degree_lat
    lon_offset = (AREA_SIZE_KM / 2) / km_per_degree_lon
    
    # Generate grid points
    locations = []
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            # Normalize to -1 to 1
            nx = (x / (GRID_SIZE - 1)) * 2 - 1
            ny = (y / (GRID_SIZE - 1)) * 2 - 1
            
            lat = CENTER_LAT + (ny * lat_offset)
            lon = CENTER_LON + (nx * lon_offset)
            
            locations.append({"latitude": lat, "longitude": lon})
    
    log(f"  Generated {len(locations)} coordinate points")
    log(f"  Area: {CENTER_LAT-lat_offset:.4f} to {CENTER_LAT+lat_offset:.4f}°N")
    log(f"        {CENTER_LON-lon_offset:.4f} to {CENTER_LON+lon_offset:.4f}°W")
    
    # Fetch elevations (in batches to avoid overwhelming the API)
    BATCH_SIZE = 100
    all_elevations = []
    
    for i in range(0, len(locations), BATCH_SIZE):
        batch = locations[i:i+BATCH_SIZE]
        elevations = fetch_elevation_batch(batch)
        
        if elevations is None:
            log("  ✗ Failed to fetch elevation data")
            return None
        
        all_elevations.extend(elevations)
        log(f"  Progress: {len(all_elevations)}/{len(locations)} points")
    
    # Reshape into 2D grid
    elevation_grid = []
    for y in range(GRID_SIZE):
        row = all_elevations[y * GRID_SIZE:(y + 1) * GRID_SIZE]
        elevation_grid.append(row)
    
    # Stats
    flat_elevations = [e for row in elevation_grid for e in row]
    min_elev = min(flat_elevations)
    max_elev = max(flat_elevations)
    
    log(f"  ✓ Elevation data fetched")
    log(f"    Min elevation: {min_elev:.1f}m")
    log(f"    Max elevation: {max_elev:.1f}m")
    log(f"    Relief: {max_elev - min_elev:.1f}m")
    
    return elevation_grid, min_elev, max_elev

# ==============================================================================
# TERRAIN GENERATION
# ==============================================================================
def create_terrain_mesh(elevation_grid, min_elev, max_elev):
    """Create terrain mesh from elevation grid using individual static mesh actors"""
    log("\n2. Creating terrain mesh...")
    
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
    
    # Calculate spacing
    total_width = AREA_SIZE_KM * 1000 * HORIZONTAL_SCALE  # Convert km to Unreal units
    spacing = total_width / (GRID_SIZE - 1)
    
    log(f"  Grid spacing: {spacing:.1f} units")
    log(f"  Total size: {total_width:.1f} x {total_width:.1f} units")
    
    created = 0
    
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            elevation = elevation_grid[y][x]
            
            # Normalize elevation (0 to 1)
            elev_normalized = (elevation - min_elev) / (max_elev - min_elev) if max_elev > min_elev else 0
            
            # World position
            world_x = (x - GRID_SIZE/2) * spacing
            world_y = (y - GRID_SIZE/2) * spacing
            world_z = elevation * HORIZONTAL_SCALE * VERTICAL_SCALE
            
            location = unreal.Vector(world_x, world_y, world_z / 2)  # Divide by 2 for cube center
            
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.StaticMeshActor,
                location
            )
            
            actor.set_actor_label(f"Terrain_{x}_{y}")
            actor.set_folder_path(unreal.Name("GrandCanyon/Terrain"))
            actor.static_mesh_component.set_static_mesh(cube_mesh)
            
            # Scale: horizontal = spacing, vertical = elevation
            z_scale = (world_z / 100.0) if world_z > 0 else 0.1  # Minimum scale
            actor.set_actor_scale3d(unreal.Vector(spacing/100.0, spacing/100.0, z_scale))
            
            # Color based on elevation (Grand Canyon colors)
            apply_canyon_color(actor, elev_normalized)
            
            created += 1
            
            if created % 100 == 0:
                log(f"  Progress: {created}/{GRID_SIZE * GRID_SIZE} columns")
    
    log(f"  ✓ Created {created} terrain columns")

def apply_canyon_color(actor, elevation_normalized):
    """Apply Grand Canyon-style coloring based on elevation"""
    mesh_comp = actor.static_mesh_component
    dmi = mesh_comp.create_dynamic_material_instance(0)
    
    if dmi:
        # Grand Canyon color layers
        if elevation_normalized < 0.3:
            # River level - dark brown/grey
            color = unreal.LinearColor(0.2, 0.15, 0.1, 1.0)
        elif elevation_normalized < 0.5:
            # Lower canyon - red rock
            color = unreal.LinearColor(0.6, 0.2, 0.1, 1.0)
        elif elevation_normalized < 0.7:
            # Mid canyon - orange/tan
            color = unreal.LinearColor(0.7, 0.4, 0.2, 1.0)
        else:
            # Rim - lighter tan/beige
            color = unreal.LinearColor(0.8, 0.6, 0.4, 1.0)
        
        dmi.set_vector_parameter_value("Color", color)
        dmi.set_scalar_parameter_value("Roughness", 0.9)

# ==============================================================================
# LIGHTING & CAMERA
# ==============================================================================
def add_lighting():
    """Add Arizona-style outdoor lighting"""
    log("\n3. Adding lighting...")
    
    # Directional light (sun)
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(0, 0, 1000)
    )
    sun.set_actor_label("GrandCanyon_Sun")
    sun.set_folder_path(unreal.Name("GrandCanyon/Lighting"))
    sun.set_actor_rotation(unreal.Rotator(pitch=-45, yaw=45, roll=0), teleport_physics=False)
    
    sun_comp = sun.light_component
    sun_comp.set_intensity(10.0)
    sun_comp.set_light_color(unreal.LinearColor(1.0, 0.95, 0.85))  # Warm sunlight
    
    log("  ✓ Added sun lighting")

def add_camera():
    """Add camera for viewing the canyon"""
    log("\n4. Adding camera...")
    
    # Position camera to view the canyon
    camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CameraActor,
        unreal.Vector(0, -3000, 1500)
    )
    camera.set_actor_label("GrandCanyon_Camera")
    camera.set_folder_path(unreal.Name("GrandCanyon"))
    camera.set_actor_rotation(unreal.Rotator(pitch=-20, yaw=0, roll=0), teleport_physics=False)
    
    log("  ✓ Camera created")

# ==============================================================================
# CLEANUP
# ==============================================================================
def cleanup_old_terrain():
    """Remove previous Grand Canyon terrain"""
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    all_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    deleted = 0
    for actor in all_actors:
        label = actor.get_actor_label()
        if "GrandCanyon" in label or "Terrain_" in label:
            unreal.EditorLevelLibrary.destroy_actor(actor)
            deleted += 1
    
    if deleted > 0:
        log(f"✓ Cleaned up {deleted} old actors")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
print("\n" + "=" * 80)
print("GENERATING GRAND CANYON TERRAIN...")
print("=" * 80)

try:
    cleanup_old_terrain()
    
    # Fetch elevation data
    result = generate_elevation_grid()
    if result is None:
        log("\n✗ Failed to generate terrain - could not fetch elevation data")
        sys.exit(1)
    
    elevation_grid, min_elev, max_elev = result
    
    # Create terrain
    create_terrain_mesh(elevation_grid, min_elev, max_elev)
    
    # Add scene elements
    add_lighting()
    add_camera()
    
    print("\n" + "=" * 80)
    print("✓ GRAND CANYON TERRAIN COMPLETE!")
    print("=" * 80)
    print(f"\nTerrain Info:")
    print(f"  • Location: Grand Canyon South Rim")
    print(f"  • Area: {AREA_SIZE_KM}km x {AREA_SIZE_KM}km")
    print(f"  • Resolution: {GRID_SIZE}x{GRID_SIZE} grid")
    print(f"  • Elevation: {min_elev:.1f}m to {max_elev:.1f}m")
    print(f"\nSelect 'GrandCanyon_Camera' and Pilot to view!")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
