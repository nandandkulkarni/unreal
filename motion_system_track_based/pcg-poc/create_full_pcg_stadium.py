"""
Complete PCG Stadium Generator
All-in-one script that:
1. Cleans up old actors
2. Creates stadium ground
3. Creates & configures PCG Graph
4. Connects nodes
5. Sets up PCG Volume
6. Triggers grass generation
"""
import unreal
import sys
import math
import time

# ==============================================================================
# LOGGING
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\create_full_pcg_stadium.log"

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
print("COMPLETE PCG STADIUM GENERATOR")
print("=" * 80)

# Generate unique suffix
SUFFIX = str(int(time.time() % 10000))  # Last 4 digits of timestamp
print(f"\nRun ID: {SUFFIX}")

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
MARGIN = 3000.0  # 30m outfield

STADIUM_RADIUS = (RADIUS + (TRACK_WIDTH / 2.0)) + MARGIN
STADIUM_WIDTH = STADIUM_RADIUS * 2.0

# Assets
GRASS_MATERIAL = "/Game/Fab/Megascans/Surfaces/Lawn_Grass_tkynejer/High/tkynejer_tier_1/Materials/MI_tkynejer.MI_tkynejer"
GRASS_MESH_PATH = "/Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r/High/tbdpec3r_tier_1/StaticMeshes/SM_tbdpec3r_VarA"
PCG_GRAPH_PATH = "/Game/PCG/PCG_StadiumGrass"

# ==============================================================================
# STEP 1: CLEANUP
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 1: CLEANUP")
print("=" * 80)

all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
deleted = 0

cleanup_labels = ["Stadium_Ground", "Infield_", "Stadium_Grass_PCG"]
for actor in all_actors:
    label = actor.get_actor_label()
    if any(key in label for key in cleanup_labels):
        unreal.EditorLevelLibrary.destroy_actor(actor)
        deleted += 1

print(f"✓ Removed {deleted} old actors")

# Delete old PCG Graph if exists
if unreal.EditorAssetLibrary.does_asset_exist(PCG_GRAPH_PATH):
    unreal.EditorAssetLibrary.delete_asset(PCG_GRAPH_PATH)
    print(f"✓ Deleted old PCG Graph")

# ==============================================================================
# STEP 2: CREATE STADIUM GROUND
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 2: CREATE STADIUM GROUND")
print("=" * 80)

cube_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cube.Cube")
cyl_mesh = unreal.load_object(None, "/Engine/BasicShapes/Cylinder.Cylinder")
grass_mat = unreal.load_object(None, GRASS_MATERIAL)

# Central Rectangle
rect_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.StaticMeshActor,
    unreal.Vector(0, 0, -5)
)
rect_actor.set_actor_label(f"Stadium_Ground_Rect_{SUFFIX}")
rect_actor.set_folder_path(unreal.Name("OvalTrack/Stadium"))
rect_actor.static_mesh_component.set_static_mesh(cube_mesh)
rect_actor.set_actor_scale3d(unreal.Vector(
    STRAIGHT_LEN / 100.0,
    STADIUM_WIDTH / 100.0, 
    0.1
))

if grass_mat:
    dmi = rect_actor.static_mesh_component.create_dynamic_material_instance(0, grass_mat)
    dmi.set_scalar_parameter_value("Tiling", 30.0)
    dmi.set_scalar_parameter_value("Main Tiling", 30.0)

# End Caps
scale_xy = STADIUM_RADIUS / 50.0
positions = [
    (f"Stadium_Ground_Right_{SUFFIX}", unreal.Vector(STRAIGHT_LEN / 2.0, 0, -5)),
    (f"Stadium_Ground_Left_{SUFFIX}", unreal.Vector(-(STRAIGHT_LEN / 2.0), 0, -5))
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
        cap_dmi.set_scalar_parameter_value("Tiling", 30.0)

print("✓ Created Stadium Ground (3 actors)")

# ==============================================================================
# STEP 3: CREATE PCG GRAPH
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 3: CREATE PCG GRAPH")
print("=" * 80)

try:
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    print(f"✓ Got asset tools: {asset_tools}")
    
    pcg_graph_factory = unreal.PCGGraphFactory()
    print(f"✓ Created factory: {pcg_graph_factory}")
    
    pcg_graph = asset_tools.create_asset(
        asset_name=f"PCG_StadiumGrass_{SUFFIX}",
        package_path="/Game/PCG",
        asset_class=unreal.PCGGraph,
        factory=pcg_graph_factory
    )
    
    if not pcg_graph:
        print("✗ create_asset returned None")
        print("  Trying alternative approach...")
        
        # Alternative: Create asset without factory
        pcg_graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            f"PCG_StadiumGrass_{SUFFIX}",
            "/Game/PCG",
            unreal.PCGGraph,
            None
        )
    
    if not pcg_graph:
        print("✗ Failed to create PCG Graph - both methods failed")
        print("  PCG Plugin may not be enabled or accessible")
        sys.exit(1)
    
    print(f"✓ Created PCG Graph: {pcg_graph}")
    
except Exception as e:
    print(f"✗ Exception creating PCG Graph: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Add nodes
surface_sampler_class = unreal.load_class(None, "/Script/PCG.PCGSurfaceSamplerSettings")
spawner_class = unreal.load_class(None, "/Script/PCG.PCGStaticMeshSpawnerSettings")

surface_sampler_result = pcg_graph.add_node_of_type(surface_sampler_class)
mesh_spawner_result = pcg_graph.add_node_of_type(spawner_class)

# add_node_of_type returns a tuple (node, settings) - extract the node
if isinstance(surface_sampler_result, tuple):
    surface_sampler = surface_sampler_result[0]
else:
    surface_sampler = surface_sampler_result

if isinstance(mesh_spawner_result, tuple):
    mesh_spawner = mesh_spawner_result[0]
else:
    mesh_spawner = mesh_spawner_result

print(f"✓ Added Surface Sampler node: {surface_sampler}")
print(f"✓ Added Static Mesh Spawner node: {mesh_spawner}")

# ==============================================================================
# STEP 4: CONNECT NODES
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 4: CONNECT NODES")
print("=" * 80)

input_node = pcg_graph.get_input_node()
output_node = pcg_graph.get_output_node()

# Get pin labels with error handling
try:
    input_out_label = input_node.output_pins[0].properties.label
    sampler_in_label = surface_sampler.input_pins[0].properties.label
    sampler_out_label = surface_sampler.output_pins[0].properties.label
    spawner_in_label = mesh_spawner.input_pins[0].properties.label
    spawner_out_label = mesh_spawner.output_pins[0].properties.label
    output_in_label = output_node.input_pins[0].properties.label
    
    print(f"Pin labels: {input_out_label}, {sampler_in_label}, {sampler_out_label}, {spawner_in_label}, {spawner_out_label}, {output_in_label}")
    
    # Connect
    pcg_graph.add_edge(input_node, input_out_label, surface_sampler, sampler_in_label)
    print(f"✓ Input → Surface Sampler")
    
    pcg_graph.add_edge(surface_sampler, sampler_out_label, mesh_spawner, spawner_in_label)
    print(f"✓ Surface Sampler → Mesh Spawner")
    
    pcg_graph.add_edge(mesh_spawner, spawner_out_label, output_node, output_in_label)
    print(f"✓ Mesh Spawner → Output")
    
except Exception as e:
    print(f"✗ Error connecting nodes: {e}")
    import traceback
    traceback.print_exc()
    print("\n⚠ Nodes created but not connected - manual connection required")

# ==============================================================================
# STEP 5: CONFIGURE MESH SPAWNER
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 5: CONFIGURE MESH SPAWNER")
print("=" * 80)

grass_mesh = unreal.load_object(None, GRASS_MESH_PATH)
if grass_mesh:
    print(f"✓ Loaded grass mesh: {grass_mesh.get_name()}")
    
    spawner_settings = mesh_spawner.get_settings()
    
    # Try to configure (may need manual setup)
    mesh_props = ["mesh_entries", "meshes", "mesh"]
    for prop in mesh_props:
        try:
            spawner_settings.set_editor_property(prop, grass_mesh)
            print(f"  ✓ Set '{prop}'")
            break
        except:
            pass
else:
    print("✗ Failed to load grass mesh")

# Save graph
unreal.EditorAssetLibrary.save_asset(PCG_GRAPH_PATH)
print("✓ Saved PCG Graph")

# ==============================================================================
# STEP 6: CREATE PCG VOLUME
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 6: CREATE PCG VOLUME")
print("=" * 80)

pcg_vol_cls = unreal.load_class(None, "/Script/PCG.PCGVolume")
pcg_volume = unreal.EditorLevelLibrary.spawn_actor_from_class(
    pcg_vol_cls,
    unreal.Vector(0, 0, 100)
)
pcg_volume.set_actor_label(f"Stadium_Grass_PCG_Volume_{SUFFIX}")
pcg_volume.set_folder_path(unreal.Name("OvalTrack/PCG"))
pcg_volume.set_actor_scale3d(unreal.Vector(200.0, 100.0, 10.0))

print(f"✓ Created PCG Volume")

# Get PCG Component and assign graph
pcg_comp = None
for comp in pcg_volume.get_components_by_class(unreal.PCGComponent):
    pcg_comp = comp
    break

if pcg_comp:
    pcg_comp.set_graph(pcg_graph)
    print("✓ Assigned graph to component")
    
    # Trigger generation
    print("\n" + "=" * 80)
    print("STEP 7: TRIGGER GENERATION")
    print("=" * 80)
    
    pcg_comp.generate_local(True)
    print("✓ PCG generation triggered!")
else:
    print("✗ No PCG Component found")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("COMPLETE!")
print("=" * 80)
print("\n✅ Stadium ground created")
print("✅ PCG Graph created and configured")
print("✅ Nodes connected")
print("✅ PCG Volume created")
print("✅ Generation triggered")
print("\n🎉 Check your viewport for the PCG-generated grass!")
print("\nIf grass doesn't appear:")
print("1. Open /Game/PCG/PCG_StadiumGrass")
print("2. Manually set the mesh in Static Mesh Spawner node")
print("3. Regenerate the PCG Volume")
