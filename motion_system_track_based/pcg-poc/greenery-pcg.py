"""
Greenery PCG - Procedural Nature Scene Generator
Uses real Unreal Engine foliage and nature assets

Features:
- Trees (various types)
- Grass and ground cover
- Rocks and boulders
- Bushes and shrubs
- Natural placement with variation
"""
import unreal
import math
import random
import sys
import datetime

# ==============================================================================
# LOGGING SETUP
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\greenery_gen.log"

class FileLogger:
    """Redirects print statements to both stdout and a file"""
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
log("GREENERY PCG - PROCEDURAL NATURE SCENE")
print("=" * 80)

# ==============================================================================
# CONFIGURATION
# ==============================================================================
SCENE_SIZE = 10000.0  # 100m x 100m area
TREE_COUNT = 50
ROCK_COUNT = 30
BUSH_COUNT = 40

# Seed for reproducible randomness
random.seed(42)

# ==============================================================================
# ASSET DISCOVERY
# ==============================================================================
def find_foliage_assets():
    """Search for available foliage and nature assets in the project"""
    log("Searching for foliage assets...")
    
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    # Search for static meshes that might be foliage
    filter = unreal.ARFilter(
        class_names=["StaticMesh"],
        recursive_paths=True
    )
    
    all_assets = asset_registry.get_assets(filter)
    
    # Categorize assets by name patterns
    trees = []
    rocks = []
    bushes = []
    grass = []
    
    for asset_data in all_assets:
        asset_name = str(asset_data.asset_name).lower()
        package_path = str(asset_data.package_name)
        
        # Look for common foliage naming patterns
        if any(keyword in asset_name for keyword in ['tree', 'pine', 'oak', 'birch', 'palm']):
            trees.append(package_path)
        elif any(keyword in asset_name for keyword in ['rock', 'stone', 'boulder']):
            rocks.append(package_path)
        elif any(keyword in asset_name for keyword in ['bush', 'shrub', 'hedge']):
            bushes.append(package_path)
        elif any(keyword in asset_name for keyword in ['grass', 'fern', 'plant']):
            grass.append(package_path)
    
    log(f"  Found {len(trees)} tree assets")
    log(f"  Found {len(rocks)} rock assets")
    log(f"  Found {len(bushes)} bush assets")
    log(f"  Found {len(grass)} grass assets")
    
    return {
        'trees': trees[:10],  # Limit to first 10 of each
        'rocks': rocks[:10],
        'bushes': bushes[:10],
        'grass': grass[:10]
    }

# ==============================================================================
# CLEANUP
# ==============================================================================
def cleanup_old_greenery():
    """Remove any previous greenery actors"""
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    all_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.StaticMeshActor)
    deleted = 0
    for actor in all_actors:
        if "Greenery" in actor.get_actor_label():
            unreal.EditorLevelLibrary.destroy_actor(actor)
            deleted += 1
    
    # Delete old lights
    lights = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.DirectionalLight)
    for light in lights:
        if "Greenery" in light.get_actor_label():
            unreal.EditorLevelLibrary.destroy_actor(light)
            deleted += 1
    
    if deleted > 0:
        log(f"✓ Cleaned up {deleted} old greenery actors")

# ==============================================================================
# TERRAIN
# ==============================================================================
def create_ground():
    """Create a large ground plane"""
    log("\n1. Creating Ground Plane...")
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
    
    location = unreal.Vector(0, 0, -50)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location
    )
    
    actor.set_actor_label("Greenery_Ground")
    actor.set_folder_path(unreal.Name("Greenery_System/Ground"))
    actor.static_mesh_component.set_static_mesh(cube_mesh)
    actor.set_actor_scale3d(unreal.Vector(100.0, 100.0, 0.5))
    
    # Green-brown ground color
    mesh_comp = actor.static_mesh_component
    dmi = mesh_comp.create_dynamic_material_instance(0)
    if dmi:
        dmi.set_vector_parameter_value("Color", unreal.LinearColor(0.2, 0.3, 0.15, 1.0))
        dmi.set_scalar_parameter_value("Roughness", 0.9)
    
    log("  ✓ Created ground plane")

# ==============================================================================
# PLACEMENT HELPERS
# ==============================================================================
def get_random_position(radius):
    """Get a random position within a circular area"""
    angle = random.uniform(0, 2 * math.pi)
    r = random.uniform(0, radius)
    x = r * math.cos(angle)
    y = r * math.sin(angle)
    return unreal.Vector(x, y, 0)

def place_foliage_item(mesh_path, position, label_prefix, folder, scale_range=(0.8, 1.2)):
    """Place a single foliage item with random rotation and scale"""
    mesh = unreal.load_object(None, mesh_path)
    if not mesh:
        return None
    
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        position
    )
    
    actor.set_actor_label(label_prefix)
    actor.set_folder_path(unreal.Name(folder))
    actor.static_mesh_component.set_static_mesh(mesh)
    
    # Random rotation (only around Z axis for natural look)
    rotation = unreal.Rotator(0, random.uniform(0, 360), 0)
    actor.set_actor_rotation(rotation, teleport_physics=False)
    
    # Random scale variation
    scale = random.uniform(scale_range[0], scale_range[1])
    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    
    return actor

# ==============================================================================
# FOLIAGE PLACEMENT
# ==============================================================================
def place_trees(tree_assets):
    """Place trees randomly across the scene"""
    if not tree_assets:
        log("\n2. Skipping trees (no assets found)")
        return
    
    log(f"\n2. Placing {TREE_COUNT} trees...")
    
    placed = 0
    for i in range(TREE_COUNT):
        # Choose random tree asset
        mesh_path = random.choice(tree_assets)
        
        # Random position
        position = get_random_position(SCENE_SIZE / 2)
        
        actor = place_foliage_item(
            mesh_path,
            position,
            f"Greenery_Tree_{i}",
            "Greenery_System/Trees",
            scale_range=(0.8, 1.5)
        )
        
        if actor:
            placed += 1
    
    log(f"  ✓ Placed {placed} trees")

def place_rocks(rock_assets):
    """Place rocks randomly across the scene"""
    if not rock_assets:
        log("\n3. Skipping rocks (no assets found)")
        return
    
    log(f"\n3. Placing {ROCK_COUNT} rocks...")
    
    placed = 0
    for i in range(ROCK_COUNT):
        mesh_path = random.choice(rock_assets)
        position = get_random_position(SCENE_SIZE / 2)
        
        actor = place_foliage_item(
            mesh_path,
            position,
            f"Greenery_Rock_{i}",
            "Greenery_System/Rocks",
            scale_range=(0.5, 2.0)
        )
        
        if actor:
            placed += 1
    
    log(f"  ✓ Placed {placed} rocks")

def place_bushes(bush_assets):
    """Place bushes randomly across the scene"""
    if not bush_assets:
        log("\n4. Skipping bushes (no assets found)")
        return
    
    log(f"\n4. Placing {BUSH_COUNT} bushes...")
    
    placed = 0
    for i in range(BUSH_COUNT):
        mesh_path = random.choice(bush_assets)
        position = get_random_position(SCENE_SIZE / 2)
        
        actor = place_foliage_item(
            mesh_path,
            position,
            f"Greenery_Bush_{i}",
            "Greenery_System/Bushes",
            scale_range=(0.7, 1.3)
        )
        
        if actor:
            placed += 1
    
    log(f"  ✓ Placed {placed} bushes")

# ==============================================================================
# LIGHTING
# ==============================================================================
def add_outdoor_lighting():
    """Add natural outdoor lighting"""
    log("\n5. Adding Outdoor Lighting...")
    
    # Directional light (sun)
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(0, 0, 1000)
    )
    sun.set_actor_label("Greenery_Sun")
    sun.set_folder_path(unreal.Name("Greenery_System/Lighting"))
    sun.set_actor_rotation(unreal.Rotator(pitch=-45, yaw=45, roll=0), teleport_physics=False)
    
    sun_comp = sun.light_component
    sun_comp.set_intensity(10.0)
    sun_comp.set_light_color(unreal.LinearColor(1.0, 0.98, 0.9))
    
    # Sky light
    skylight = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyLight,
        unreal.Vector(0, 0, 2000)
    )
    skylight.set_actor_label("Greenery_SkyLight")
    skylight.set_folder_path(unreal.Name("Greenery_System/Lighting"))
    
    sky_comp = skylight.light_component
    sky_comp.set_intensity(1.5)
    
    log("  ✓ Added sun and sky lighting")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
print("\n" + "=" * 80)
print("GENERATING GREENERY SCENE...")
print("=" * 80)

try:
    cleanup_old_greenery()
    
    # Discover available assets
    assets = find_foliage_assets()
    
    # If no assets found, use basic shapes as fallback
    if not any(assets.values()):
        log("\n⚠ No foliage assets found - using basic shapes as fallback")
        assets = {
            'trees': ["/Engine/BasicShapes/Cylinder.Cylinder"],
            'rocks': ["/Engine/BasicShapes/Sphere.Sphere"],
            'bushes': ["/Engine/BasicShapes/Cube.Cube"],
            'grass': []
        }
    
    create_ground()
    place_trees(assets['trees'])
    place_rocks(assets['rocks'])
    place_bushes(assets['bushes'])
    add_outdoor_lighting()
    
    print("\n" + "=" * 80)
    print("✓ GREENERY SCENE COMPLETE!")
    print("=" * 80)
    print(f"\nGenerated:")
    print(f"  • {TREE_COUNT} trees")
    print(f"  • {ROCK_COUNT} rocks")
    print(f"  • {BUSH_COUNT} bushes")
    print(f"  • Natural outdoor lighting")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
