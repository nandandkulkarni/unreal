"""
Grass Spawner
1. Finds the Static Mesh for 'Ribbon_Grass_tbdpec3r'
2. Adds InstancedStaticMeshComponent to Stadium Ground
3. Spawns thousands of grass instances
"""
import unreal
import sys
import math
import random

# ==============================================================================
# LOGGING
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\spawn_grass.log"

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
print("SPAWNING 3D GRASS (ISM)")
print("=" * 80)

# ==============================================================================
# 1. FIND ASSET
# ==============================================================================
# Material Path: /Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r/High/tbdpec3r_tier_1/Materials/MI_tbdpec3r.MI_tbdpec3r
# Mesh should be in: /Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r
# or subfolders.

SEARCH_ROOT = "/Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r"
print(f"Searching for StaticMesh in: {SEARCH_ROOT}...")

editor_asset_lib = unreal.EditorAssetLibrary()
assets = editor_asset_lib.list_assets(SEARCH_ROOT, recursive=True, include_folder=True)

mesh_asset_path = None

for asset_path in assets:
    # Check if it's a StaticMesh
    # list_assets returns strings (package names)
    asset_data = unreal.EditorAssetLibrary.find_asset_data(asset_path)
    if asset_data.asset_class_path.asset_name == "StaticMesh":
        print(f"Found Mesh: {asset_path}")
        mesh_asset_path = asset_path
        break # Take the first one

if not mesh_asset_path:
    print("✗ Could not find any StaticMesh! Aborting.")
    sys.exit()

grass_mesh = unreal.load_object(None, mesh_asset_path)

# ==============================================================================
# 2. TARGET ACTOR
# ==============================================================================
# We want to attach to "Stadium_Ground_Rect"
target_actor = None
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
for actor in all_actors:
    if actor.get_actor_label() == "Stadium_Ground_Rect":
        target_actor = actor
        break

if not target_actor:
    print("✗ Stadium_Ground_Rect not found! Run create_stadium_ground.py first.")
    sys.exit()

print(f"Attaching to: {target_actor.get_actor_label()}")

# ==============================================================================
# 3. SETUP ISM
# ==============================================================================
# Remove existing ISMs?
comps = target_actor.get_components_by_class(unreal.InstancedStaticMeshComponent)
for comp in comps:
    target_actor.remove_instance_component(comp)
    comp.destroy_component(target_actor)

# Create New ISM
ism_comp = unreal.InstancedStaticMeshComponent()
ism_comp.set_static_mesh(grass_mesh)
target_actor.add_instance_component(ism_comp)
ism_comp.attach_to_component(target_actor.root_component, unreal.AttachmentTransformRules.keep_relative_transform())
ism_comp.register_component()

# ==============================================================================
# 4. SCATTER INSTANCES
# ==============================================================================
# The Stadium Ground is a Cube scaled to (Length/100, Width/100, 0.1)
# Dimensions:
# Scale X = STRAIGHT_LEN / 100
# Scale Y = STADIUM_WIDTH / 100
# 1 Cube Unit = 100 Unreal Units.
# So X extent = Scale X * 100 * 0.5?
# Actually, easier to work in Local Space of the Cube (which ranges -0.5 to 0.5? No, Cube is -50 to 50 local).

# Let's spawn in World Space (since we attach KeepRelative? No, let's use AddInstanceWorld)
# Bounds:
# Rect CenterL (0,0,-5)
# Rect Size: (STRAIGHT_LEN, STADIUM_WIDTH)
# Wait, the Rect only covers the Straight part?
# Checking create_stadium_ground.py:
# rect_actor.set_actor_scale3d(unreal.Vector(STRAIGHT_LEN/100.0, STADIUM_WIDTH/100.0, 0.1))
# Yes, the Rect is the center part.
# The Semicircles are separate actors ("Stadium_Ground_Right", "Stadium_Ground_Left").

# We should spawn grass on ALL of them.
target_actors = [target_actor]
for actor in all_actors:
    label = actor.get_actor_label()
    if label in ["Stadium_Ground_Right", "Stadium_Ground_Left"]:
        target_actors.append(actor)

DENSITY = 0.5 # Instances per square meter?
# If Low density, use 1 per m2.
# 100m x 70m = 7000 instances.
# Let's try 5000 instances per actor for now to test.

print(f"Spawning instances on {len(target_actors)} actors...")

total_instances = 0

for actor in target_actors:
    # Get Bounds
    origin, extent = actor.get_actor_bounds(False)
    # Extent is half-size
    
    # Create ISM on this actor
    # (We already did it for Rect, need to do for caps)
    if actor != target_actor:
        # Clean old
        comps = actor.get_components_by_class(unreal.InstancedStaticMeshComponent)
        for comp in comps:
            actor.remove_instance_component(comp)
            comp.destroy_component(actor)

        ism = unreal.InstancedStaticMeshComponent()
        ism.set_static_mesh(grass_mesh)
        actor.add_instance_component(ism)
        ism.attach_to_component(actor.root_component, unreal.AttachmentTransformRules.keep_relative_transform())
        ism.register_component()
        
        current_ism = ism
    else:
        current_ism = ism_comp

    # Spawn Loop
    # Simple bounding box scatter
    # We want to avoid spawning "off" the cylinder?
    # For now, box spawn is fine, we can reject if distance > radius for cylinders.
    
    is_cylinder = "Ground_Right" in actor.get_actor_label() or "Ground_Left" in actor.get_actor_label()
    
    num_to_spawn = 5000 # Cap
    
    for i in range(num_to_spawn):
        # Random Point in Box
        rx = random.uniform(-extent.x, extent.x)
        ry = random.uniform(-extent.y, extent.y)
        
        # World Pos
        world_x = origin.x + rx
        world_y = origin.y + ry
        world_z = origin.z + extent.z # Top surface
        
        # Check Cylinder
        if is_cylinder:
            # Check dist from actor center (ignoring Z)
            dist_sq = (world_x - origin.x)**2 + (world_y - origin.y)**2
            # Cylinder radius is X extent (roughly)
            # Extent is box bounds, so accurate for cylinder radius
            if dist_sq > (extent.x * extent.x):
                continue

        # Random Rotation
        yaw = random.uniform(0, 360)
        scale = random.uniform(0.8, 1.2)
        
        t = unreal.Transform(
            unreal.Vector(world_x, world_y, world_z),
            unreal.Rotator(0, yaw, 0),
            unreal.Vector(scale, scale, scale)
        )
        
        current_ism.add_instance_world_space(t)
        total_instances += 1

print(f"✓ Spawned {total_instances} grass clumps")
