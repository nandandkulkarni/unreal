"""
Geometric Abstract Garden - PCG Proof of Concept
Creates mathematical patterns using basic shapes (no external assets needed)

Patterns:
1. Fibonacci Spiral - Spheres
2. Concentric Squares - Cubes  
3. Radial Pillars - Cylinders
"""
import unreal
import math
import sys
import os
import datetime

# ==============================================================================
# LOGGING SETUP
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\pcg_gen.log"

class FileLogger:
    """Redirects print statements to both stdout and a file"""
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
        
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush() # Ensure it's written immediately

    def flush(self):
        self.terminal.flush()
        self.log.flush()

# Redirect stdout to our logger
sys.stdout = FileLogger(LOG_FILE_PATH)
# Helper print with timestamp
def log(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

print("=" * 80)
log("GEOMETRIC ABSTRACT GARDEN - PCG POC STARTED")
print("=" * 80)

# Configuration
FIBONACCI_COUNT = 20
SQUARE_RINGS = 5
PILLAR_COUNT = 12
BASE_SCALE = 100.0  # cm

# Golden ratio for Fibonacci spiral
PHI = 1.618033988749895

def cleanup_old_garden():
    """Remove any previous garden actors and lights"""
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    # Delete old static meshes
    all_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.StaticMeshActor)
    deleted = 0
    for actor in all_actors:
        if "Garden" in actor.get_actor_label():
            unreal.EditorLevelLibrary.destroy_actor(actor)
            deleted += 1
    
    # Delete ONLY garden lights (not all lights)
    lights = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.DirectionalLight)
    for light in lights:
        if "Garden" in light.get_actor_label():
            unreal.EditorLevelLibrary.destroy_actor(light)
            deleted += 1
    
    point_lights = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.PointLight)
    for light in point_lights:
        if "Garden" in light.get_actor_label():
            unreal.EditorLevelLibrary.destroy_actor(light)
            deleted += 1
    
    spot_lights = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.SpotLight)
    for light in spot_lights:
        if "Garden" in light.get_actor_label():
            unreal.EditorLevelLibrary.destroy_actor(light)
            deleted += 1
    
    # Delete old fog
    fog_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.ExponentialHeightFog)
    for fog in fog_actors:
        if "Garden" in fog.get_actor_label():
            unreal.EditorLevelLibrary.destroy_actor(fog)
            deleted += 1
    
    # Delete old cameras
    cameras = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.CameraActor)
    for camera in cameras:
        if "Garden" in camera.get_actor_label():
            unreal.EditorLevelLibrary.destroy_actor(camera)
            deleted += 1
    
    if deleted > 0:
        print(f"✓ Cleaned up {deleted} old garden actors/lights")

def apply_dynamic_color(actor, r, g, b, roughness=0.5, metallic=0.0):
    """Create a dynamic material instance and set its color and properties"""
    mesh_comp = actor.static_mesh_component
    
    # material index 0 is usually the main material
    dmi = mesh_comp.create_dynamic_material_instance(0)
    if dmi:
        # Standard parameters for BasicShapeMaterial
        dmi.set_vector_parameter_value("Color", unreal.LinearColor(r, g, b, 1.0))
        dmi.set_scalar_parameter_value("Roughness", roughness)
        dmi.set_scalar_parameter_value("Metallic", metallic)

def create_floor():
    """Create a large simple floor"""
    print("\n0. Creating Floor...")
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
    
    location = unreal.Vector(0, 0, -50) # Slightly below 0
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location
    )
    
    actor.set_actor_label("Garden_Floor")
    actor.set_folder_path(unreal.Name("Garden_System/Floor"))
    actor.static_mesh_component.set_static_mesh(cube_mesh)
    actor.set_actor_scale3d(unreal.Vector(200.0, 200.0, 0.5)) # 200m x 200m
    
    # Dark grey floor
    apply_dynamic_color(actor, 0.05, 0.05, 0.05)
    print("  ✓ Created large dark floor")

def create_pool():
    """Create a stylized rectangular pool"""
    print("\n0.5. Creating Pool...")
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
    
    # Position under the spiral (which is at 0,0)
    # Raising slightly above floor (-50) to -40
    location = unreal.Vector(0, 0, -40) 
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location
    )
    
    actor.set_actor_label("Garden_Pool")
    actor.set_folder_path(unreal.Name("Garden_System/Pool"))
    actor.static_mesh_component.set_static_mesh(cube_mesh)
    
    # 60m x 60m pool area
    actor.set_actor_scale3d(unreal.Vector(60.0, 60.0, 0.1)) 
    
    # Deep Blue, very shiny (Water-like)
    # R=0, G=0.1, B=0.3
    # Roughness = 0.05 (Wet)
    # Metallic = 0.3 (Slightly stylized metallic look for better reflections)
    apply_dynamic_color(actor, 0.0, 0.1, 0.3, roughness=0.05, metallic=0.3)
    print("  ✓ Created reflective pool")

def pseudo_noise(x, y):
    """Simple pseudo-random noise function for height map"""
    # Deterministic noise based on coordinates
    n = math.sin(x * 12.9898 + y * 78.233) * 43758.5453
    return n - math.floor(n)

def create_terrain():
    """Create a high-density digital terrain using individual static mesh actors"""
    print("\n0.6. Creating High-Res Terrain...")
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
    
    # Reduced grid for performance (still creates nice terrain)
    grid_size = 40        # 1600 actors
    spacing = 120.0       # Spacing between cubes
    max_height = 1200.0
    base_offset = unreal.Vector(4000, 0, 0)  # Position offset
    
    print(f"  Generating {grid_size*grid_size} terrain columns...")
    
    count = 0
    
    for x in range(grid_size):
        for y in range(grid_size):
            # Normalized coords centered
            nx = (x - grid_size/2) * 0.1
            ny = (y - grid_size/2) * 0.1
            
            # 1. Base Low Freq Hills
            h1 = math.sin(nx * 0.5) * math.cos(ny * 0.5)
            
            # 2. High Freq Detail (Ridge)
            h2 = math.cos(nx * 1.5 + ny) * 0.5
            
            # 3. Erosion-style ABS (Ridge creation)
            noise_val = h1 + (1.0 - abs(h2)) * 0.3
            
            # Normalize approx -1 to 1 range > 0 to 1
            height_val = (noise_val * 0.5) + 0.5
            height_val = max(0.0, min(1.0, height_val))  # Clamp
            
            z_scale = height_val * (max_height / 100.0)
            z_pos = (z_scale * 100.0) / 2.0
            
            # World position
            world_x = base_offset.x + (x - grid_size/2) * spacing
            world_y = base_offset.y + (y - grid_size/2) * spacing
            
            location = unreal.Vector(world_x, world_y, z_pos)
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.StaticMeshActor,
                location
            )
            
            actor.set_actor_label(f"Terrain_Column_{x}_{y}")
            actor.set_folder_path(unreal.Name("Garden_System/Terrain"))
            actor.static_mesh_component.set_static_mesh(cube_mesh)
            actor.set_actor_scale3d(unreal.Vector(1.1, 1.1, z_scale))
            
            # Biome coloring
            if height_val < 0.25:
                # Water - Deep Blue, Shiny
                apply_dynamic_color(actor, 0.0, 0.2, 0.8, roughness=0.1, metallic=0.0)
            elif height_val < 0.65:
                # Grass - Teal/Green, Matte
                apply_dynamic_color(actor, 0.1, 0.6, 0.4, roughness=0.8, metallic=0.0)
            else:
                # Snow - White, Semi-Rough
                apply_dynamic_color(actor, 0.9, 0.95, 1.0, roughness=0.5, metallic=0.0)
            
            count += 1
            
    print(f"  ✓ Created {count} high-res terrain columns")

def create_pathway():
    """Create a meandering path of stepping stones"""
    print("\n0.7. Creating Pathway...")
    cyl_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cylinder.Cylinder")
    
    # Path settings
    start_pos = unreal.Vector(1200, 0, 20)      # Edge of pool
    end_pos = unreal.Vector(3600, 0, 50)       # Edge of terrain
    steps = 40
    
    # Calculate vector from start to end
    path_vec = end_pos - start_pos
    total_dist = path_vec.length()
    step_size = total_dist / steps
    direction = path_vec.normal()
    
    for i in range(steps):
        # Progress (0.0 to 1.0)
        alpha = i / float(steps)
        
        # Base position (Linear Interpolation)
        base_loc = start_pos + (path_vec * alpha)
        
        # Meandering (Sine wave offset on Y axis)
        # 1.5 full waves (3 * PI)
        # Amplitude 300 units
        meander_offset = math.sin(alpha * math.pi * 3.0) * 300.0
        
        # Final location
        location = unreal.Vector(
            base_loc.x, 
            base_loc.y + meander_offset, 
            base_loc.z
        )
        
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor,
            location
        )
        
        actor.set_actor_label(f"Pathway_Step_{i}")
        actor.set_folder_path(unreal.Name("Garden_System/Pathways"))
        actor.static_mesh_component.set_static_mesh(cyl_mesh)
        
        # Flattened stone look
        actor.set_actor_scale3d(unreal.Vector(1.6, 1.6, 0.1))
        
        # Stone material (Grey, Rough)
        apply_dynamic_color(actor, 0.4, 0.4, 0.42, roughness=0.9, metallic=0.0)
        
    print(f"  ✓ Created {steps} stepping stones")

def create_fibonacci_spiral():
    """Create spheres in a Fibonacci spiral pattern"""
    print("\n1. Creating Fibonacci Spiral (Spheres)...")
    
    sphere_mesh = unreal.load_object(None, "/Engine/BasicShapes/Sphere.Sphere")
    if not sphere_mesh:
        print("  ✗ Failed to load sphere mesh")
        return
    
    # Materials for color variation
    materials = [
        "/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial",  # Default
    ]
    
    for i in range(FIBONACCI_COUNT):
        # Fibonacci spiral math
        angle = i * 137.5  # Golden angle in degrees
        radius = BASE_SCALE * math.sqrt(i) * 2.0
        
        x = radius * math.cos(math.radians(angle))
        y = radius * math.sin(math.radians(angle))
        z = 0
        
        # Scale variation (larger as we go out)
        scale = 0.5 + (i / FIBONACCI_COUNT) * 1.5
        
        # Spawn sphere
        location = unreal.Vector(x, y, z)
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor,
            location
        )
        
        actor.set_actor_label(f"Garden_Sphere_{i}")
        actor.set_folder_path(unreal.Name("Garden_System/Spiral"))
        actor.static_mesh_component.set_static_mesh(sphere_mesh)
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        
        # Color variation (Blue -> Cyan -> White)
        t = i / max(1, FIBONACCI_COUNT - 1)
        # Gradient: Blue (0,0,1) -> Cyan (0,1,1)
        r_val = 0.0
        g_val = t * 0.8
        b_val = 0.5 + t * 0.5
        
        apply_dynamic_color(actor, r_val, g_val, b_val)
        
    print(f"  ✓ Created {FIBONACCI_COUNT} spheres in Fibonacci spiral (Blue-Cyan gradient)")

def create_concentric_squares():
    """Create cubes in concentric square patterns"""
    print("\n2. Creating Concentric Squares (Cubes)...")
    
    cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
    if not cube_mesh:
        print("  ✗ Failed to load cube mesh")
        return
    
    cube_count = 0
    offset = unreal.Vector(3000, 0, 0)  # Offset from spiral
    
    for ring in range(1, SQUARE_RINGS + 1):
        side_length = ring * BASE_SCALE * 3
        cubes_per_side = ring * 2
        spacing = side_length / cubes_per_side if cubes_per_side > 0 else side_length
        
        # Four sides of the square
        positions = []
        
        # Top side (left to right)
        for i in range(cubes_per_side):
            x = -side_length/2 + i * spacing
            y = side_length/2
            positions.append((x, y))
        
        # Right side (top to bottom)
        for i in range(cubes_per_side):
            x = side_length/2
            y = side_length/2 - i * spacing
            positions.append((x, y))
        
        # Bottom side (right to left)
        for i in range(cubes_per_side):
            x = side_length/2 - i * spacing
            y = -side_length/2
            positions.append((x, y))
        
        # Left side (bottom to top)
        for i in range(cubes_per_side):
            x = -side_length/2
            y = -side_length/2 + i * spacing
            positions.append((x, y))
        
        # Spawn cubes at positions
        for x, y in positions:
            location = unreal.Vector(offset.x + x, offset.y + y, 0)
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.StaticMeshActor,
                location
            )
            
            actor.set_actor_label(f"Garden_Cube_Ring{ring}_{cube_count}")
            actor.set_folder_path(unreal.Name("Garden_System/Squares"))
            actor.static_mesh_component.set_static_mesh(cube_mesh)
            
            # Scale based on ring (smaller for outer rings)
            scale = 1.5 - (ring / SQUARE_RINGS) * 0.8
            actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
            
            # Alternating colors: Purple vs Gold
            if ring % 2 == 0:
                # Purple
                apply_dynamic_color(actor, 0.6, 0.1, 0.9)
            else:
                # Gold
                apply_dynamic_color(actor, 0.9, 0.7, 0.1)
            
            cube_count += 1
    
    print(f"  ✓ Created {cube_count} cubes in {SQUARE_RINGS} concentric squares (Purple/Gold)")

def create_radial_pillars():
    """Create cylinders as pillars in a radial pattern"""
    print("\n3. Creating Radial Pillars (Cylinders)...")
    
    cylinder_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cylinder.Cylinder")
    if not cylinder_mesh:
        print("  ✗ Failed to load cylinder mesh")
        return
    
    offset = unreal.Vector(-3000, 0, 0)  # Offset on other side
    radius = BASE_SCALE * 8
    
    for i in range(PILLAR_COUNT):
        angle = (i / PILLAR_COUNT) * 360
        x = radius * math.cos(math.radians(angle))
        y = radius * math.sin(math.radians(angle))
        
        # Height variation (wave pattern)
        height = 2.0 + math.sin(math.radians(angle * 2)) * 1.5
        
        location = unreal.Vector(offset.x + x, offset.y + y, 0)
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor,
            location
        )
        
        actor.set_actor_label(f"Garden_Pillar_{i}")
        actor.set_folder_path(unreal.Name("Garden_System/Pillars"))
        actor.static_mesh_component.set_static_mesh(cylinder_mesh)
        
        # Tall pillars with varying heights
        actor.set_actor_scale3d(unreal.Vector(0.8, 0.8, height))
        
        # Color: Orange to Red
        # Randomize slightly or use angle
        r = 1.0
        g = 0.5 - (0.3 * math.sin(math.radians(angle))) 
        b = 0.1
        apply_dynamic_color(actor, r, g, b)
        
    print(f"  ✓ Created {PILLAR_COUNT} radial pillars (Orange/Red)")

def add_lighting():
    """Add dramatic multi-light setup"""
    print("\n4. Adding Lighting...")
    
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    try:
        # Main directional light (key light from above)
        print("  Creating key directional light...")
        key_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.DirectionalLight,
            unreal.Vector(0, 0, 1000)
        )
        key_light.set_actor_label("Garden_KeyLight")
        key_light.set_folder_path(unreal.Name("Garden_System/Lighting"))
        key_light.set_actor_rotation(unreal.Rotator(pitch=-45, yaw=30, roll=0), teleport_physics=False)
        
        key_comp = key_light.light_component
        key_comp.set_intensity(8.0)
        key_comp.set_light_color(unreal.LinearColor(1.0, 0.95, 0.85))  # Warm white
        key_comp.set_editor_property("atmosphere_sun_light", True)
        key_comp.set_editor_property("cast_volumetric_shadow", True)
        print(f"    ✓ Key light: {key_light.get_actor_label()}")
        
        # Accent light for Fibonacci spiral (blue)
        print("  Creating spiral accent light...")
        spiral_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.PointLight,
            unreal.Vector(0, 0, 800)
        )
        spiral_light.set_actor_label("Garden_SpiralLight")
        spiral_light.set_folder_path(unreal.Name("Garden_System/Lighting"))
        spiral_comp = spiral_light.light_component
        spiral_comp.set_intensity(5000.0)
        spiral_comp.set_light_color(unreal.LinearColor(0.3, 0.5, 1.0))  # Blue
        spiral_comp.set_editor_property("attenuation_radius", 2000.0)
        print(f"    ✓ Spiral light: {spiral_light.get_actor_label()}")
        
        # Accent light for concentric squares (purple)
        print("  Creating squares accent light...")
        squares_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.PointLight,
            unreal.Vector(3000, 0, 800)
        )
        squares_light.set_actor_label("Garden_SquaresLight")
        squares_light.set_folder_path(unreal.Name("Garden_System/Lighting"))
        squares_comp = squares_light.light_component
        squares_comp.set_intensity(5000.0)
        squares_comp.set_light_color(unreal.LinearColor(0.8, 0.3, 1.0))  # Purple
        squares_comp.set_editor_property("attenuation_radius", 2000.0)
        print(f"    ✓ Squares light: {squares_light.get_actor_label()}")
        
        # Accent light for radial pillars (orange)
        print("  Creating pillars accent light...")
        pillars_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.PointLight,
            unreal.Vector(-3000, 0, 800)
        )
        pillars_light.set_actor_label("Garden_PillarsLight")
        pillars_light.set_folder_path(unreal.Name("Garden_System/Lighting"))
        pillars_comp = pillars_light.light_component
        pillars_comp.set_intensity(5000.0)
        pillars_comp.set_light_color(unreal.LinearColor(1.0, 0.5, 0.2))  # Orange

        # Sky Light for ambient fill and reflections
        print("  Creating Sky Light...")
        skylight = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SkyLight,
            unreal.Vector(0, 0, 2000)
        )
        skylight.set_actor_label("Garden_SkyLight")
        skylight.set_folder_path(unreal.Name("Garden_System/Lighting"))
        
        sky_comp = skylight.light_component
        sky_comp.set_mobility(unreal.ComponentMobility.MOVABLE)
        sky_comp.set_editor_property("real_time_capture", True)
        sky_comp.set_intensity(1.0)
        print(f"    ✓ Sky light: {skylight.get_actor_label()}")
        
        # Reflection Capture for the pool
        print("  Creating Reflection Capture...")
        ref_cap = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SphereReflectionCapture,
            unreal.Vector(0, 0, 100)
        )
        ref_cap.set_actor_label("Garden_ReflectionCapture")
        ref_cap.set_folder_path(unreal.Name("Garden_System/Lighting"))
        ref_comp = ref_cap.capture_component
        ref_comp.set_editor_property("influence_radius", 5000.0)
        print(f"    ✓ Reflection capture: {ref_cap.get_actor_label()}")
        
    except Exception as e:
        print(f"  ✗ ERROR creating lights: {e}")
        import traceback
        traceback.print_exc()

def add_atmosphere():
    """Create artistic atmosphere"""
    print("\n5. Adding Atmosphere...")
    
    try:
        # Create Sky Atmosphere (Required for SkyLight Real-time Capture)
        print("  Creating Sky Atmosphere...")
        sky_atm = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SkyAtmosphere,
            unreal.Vector(0, 0, 0)
        )
        sky_atm.set_actor_label("Garden_SkyAtmosphere")
        sky_atm.set_folder_path(unreal.Name("Garden_System/Lighting"))
        print(f"    ✓ Sky Atmosphere: {sky_atm.get_actor_label()}")

        # Create artistic atmosphere (subtle purple/gold twilight)
        fog = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.ExponentialHeightFog,
            unreal.Vector(0, 0, 0)
        )
        fog.set_actor_label("Garden_Atmosphere")
        fog.set_folder_path(unreal.Name("Garden_System/Lighting"))
        
        fog_comp = fog.component
        fog_comp.set_editor_property("fog_density", 0.03)
        fog_comp.set_editor_property("fog_inscattering_luminance", 
                                      unreal.LinearColor(0.6, 0.4, 0.8))  # Purple tint
        fog_comp.set_editor_property("volumetric_fog_scattering_distribution", 1.5)
        fog_comp.set_editor_property("volumetric_fog_albedo", unreal.Color(r=255, g=230, b=200))
        
        print(f"  ✓ Added purple-tinted volumetric fog")
        
    except Exception as e:
        print(f"  ✗ ERROR creating fog: {e}")
        import traceback
        traceback.print_exc()

def create_camera():
    """Add a camera to view the garden"""
    print("\n6. Adding Camera...")
    
    # Camera position to see all three patterns
    camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CameraActor,
        unreal.Vector(0, -4000, 2000)  # Behind and above
    )
    camera.set_actor_label("Garden_Camera")
    camera.set_folder_path(unreal.Name("Garden_System"))
    camera.set_actor_rotation(unreal.Rotator(pitch=-20, yaw=0, roll=0), teleport_physics=False)
    
    print("  ✓ Camera created")
    print("    (Select 'Garden_Camera' in outliner and press Pilot to view)")

    # SECOND CAMERA: Terrain Focus
    print("  Creating Terrain Camera...")
    terrain_cam_loc = unreal.Vector(0, -4000, 1500)
    terrain_cam = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CameraActor,
        terrain_cam_loc
    )
    terrain_cam.set_actor_label("Garden_Terrain_Camera")
    terrain_cam.set_folder_path(unreal.Name("Garden_System"))
    
    # Look at terrain center (4000, 0, 200)
    # Manual approximation: Delta=(4000, 4000, -1300) -> Yaw=45, Pitch=-13
    rotation = unreal.Rotator(-15, 45, 0) 
    terrain_cam.set_actor_rotation(rotation, teleport_physics=False)
    print("  ✓ Terrain Camera created (Garden_Terrain_Camera)")

# Main execution
print("\n" + "=" * 80)
print("GENERATING GARDEN...")
print("=" * 80)

try:
    cleanup_old_garden()
    # create_floor()
    # create_pool()
    create_terrain()
    # create_pathway()
    # create_fibonacci_spiral()
    # create_concentric_squares()
    # create_radial_pillars()
    add_lighting()
    # add_atmosphere()
    create_camera()
    
    print("\n" + "=" * 80)
    print("✓ GEOMETRIC ABSTRACT GARDEN COMPLETE!")
    print("=" * 80)
    print("\nView the garden:")
    print("  1. Select 'Garden_Camera' in World Outliner for Main View")
    print("  2. Select 'Garden_Terrain_Camera' to see the High-Res Terrain Hills")
    print("  3. Right-click → Pilot to fly around")
    print("\nPatterns created:")
    print(f"  • Fibonacci Spiral: {FIBONACCI_COUNT} spheres (blue accent) - center")
    print(f"  • Concentric Squares: {SQUARE_RINGS} rings of cubes (purple accent) - right")
    print(f"  • Radial Pillars: {PILLAR_COUNT} cylinders (orange accent) - left")
    print("  • Key light (warm) + 3 colored accent lights + volumetric fog")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
