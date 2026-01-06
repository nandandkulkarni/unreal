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
        actor.static_mesh_component.set_static_mesh(sphere_mesh)
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        
        # Color variation based on position
        hue = (i / FIBONACCI_COUNT) * 360
        # You could set custom material here with color
        
    print(f"  ✓ Created {FIBONACCI_COUNT} spheres in Fibonacci spiral")

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
            actor.static_mesh_component.set_static_mesh(cube_mesh)
            
            # Scale based on ring (smaller for outer rings)
            scale = 1.5 - (ring / SQUARE_RINGS) * 0.8
            actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
            
            cube_count += 1
    
    print(f"  ✓ Created {cube_count} cubes in {SQUARE_RINGS} concentric squares")

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
        actor.static_mesh_component.set_static_mesh(cylinder_mesh)
        
        # Tall pillars with varying heights
        actor.set_actor_scale3d(unreal.Vector(0.8, 0.8, height))
        
    print(f"  ✓ Created {PILLAR_COUNT} radial pillars")

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
        pillars_comp = pillars_light.light_component
        pillars_comp.set_intensity(5000.0)
        pillars_comp.set_light_color(unreal.LinearColor(1.0, 0.5, 0.2))  # Orange

        
        
    except Exception as e:
        print(f"  ✗ ERROR creating lights: {e}")
        import traceback
        traceback.print_exc()

def add_atmosphere():
    """Create artistic atmosphere"""
    print("\n5. Adding Atmosphere...")
    
    try:
        # Create artistic atmosphere (subtle purple/gold twilight)
        fog = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.ExponentialHeightFog,
            unreal.Vector(0, 0, 0)
        )
        fog.set_actor_label("Garden_Atmosphere")
        
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
    camera.set_actor_rotation(unreal.Rotator(pitch=-20, yaw=0, roll=0), teleport_physics=False)
    
    print("  ✓ Camera created")
    print("    (Select 'Garden_Camera' in outliner and press Pilot to view)")

# Main execution
print("\n" + "=" * 80)
print("GENERATING GARDEN...")
print("=" * 80)

try:
    cleanup_old_garden()
    create_fibonacci_spiral()
    create_concentric_squares()
    create_radial_pillars()
    add_lighting()
    add_atmosphere()
    create_camera()
    
    print("\n" + "=" * 80)
    print("✓ GEOMETRIC ABSTRACT GARDEN COMPLETE!")
    print("=" * 80)
    print("\nView the garden:")
    print("  1. Select 'Garden_Camera' in World Outliner")
    print("  2. Right-click → Pilot 'Garden_Camera'")
    print("  3. Or use Perspective viewport to fly around")
    print("\nPatterns created:")
    print(f"  • Fibonacci Spiral: {FIBONACCI_COUNT} spheres (blue accent) - center")
    print(f"  • Concentric Squares: {SQUARE_RINGS} rings of cubes (purple accent) - right")
    print(f"  • Radial Pillars: {PILLAR_COUNT} cylinders (orange accent) - left")
    print("  • Key light (warm) + 3 colored accent lights + volumetric fog")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
