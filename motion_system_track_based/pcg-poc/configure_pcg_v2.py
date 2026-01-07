"""
PCG Graph Configuration Script V2
Uses pin indices and property reflection
"""
import unreal
import sys

# ==============================================================================
# LOGGING
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\configure_pcg_v2.log"

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
print("CONFIGURING PCG GRAPH V2")
print("=" * 80)

# ==============================================================================
# STEP 1: ENSURE STADIUM GROUND EXISTS
# ==============================================================================
print("\n1. Checking for Stadium Ground...")

all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
has_stadium = False

for actor in all_actors:
    if "Stadium_Ground" in actor.get_actor_label():
        has_stadium = True
        break

if not has_stadium:
    print("✗ Stadium Ground not found. Creating it...")
    # Run the stadium ground script
    exec(open(r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\create_stadium_ground.py").read())
else:
    print("✓ Stadium Ground exists")

# ==============================================================================
# STEP 2: LOAD GRAPH & NODES
# ==============================================================================
print("\n2. Loading PCG Graph...")

PCG_GRAPH_PATH = "/Game/PCG/PCG_StadiumGrass"
GRASS_MESH_PATH = "/Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r/High/tbdpec3r_tier_1/StaticMeshes/SM_tbdpec3r_VarA"

pcg_graph = unreal.load_asset(PCG_GRAPH_PATH)
if not pcg_graph:
    print(f"✗ Failed to load graph")
    sys.exit(1)

print(f"✓ Loaded graph")

nodes = pcg_graph.nodes
input_node = pcg_graph.get_input_node()
output_node = pcg_graph.get_output_node()

# Identify nodes
surface_sampler = None
mesh_spawner = None

for node in nodes:
    settings_type = type(node.get_settings()).__name__
    if "SurfaceSampler" in settings_type:
        surface_sampler = node
    elif "StaticMeshSpawner" in settings_type:
        mesh_spawner = node

if not surface_sampler or not mesh_spawner:
    print("✗ Could not identify nodes")
    sys.exit(1)

print(f"✓ Identified Surface Sampler and Mesh Spawner")

# ==============================================================================
# STEP 3: CONNECT NODES (Using Generic Pin Names)
# ==============================================================================
print("\n3. Connecting nodes...")

try:
    # PCG standard pin names are usually "In", "Out", "Output", etc.
    # Try common variations
    
    # Input → Surface Sampler
    print("  Connecting Input → Surface Sampler...")
    try:
        pcg_graph.add_edge(input_node, "Out", surface_sampler, "In")
        print("    ✓ Connected")
    except Exception as e:
        print(f"    ⚠ {e}")
    
    # Surface Sampler → Mesh Spawner
    print("  Connecting Surface Sampler → Mesh Spawner...")
    try:
        pcg_graph.add_edge(surface_sampler, "Out", mesh_spawner, "In")
        print("    ✓ Connected")
    except Exception as e:
        print(f"    ⚠ {e}")
    
    # Mesh Spawner → Output
    print("  Connecting Mesh Spawner → Output...")
    try:
        pcg_graph.add_edge(mesh_spawner, "Out", output_node, "In")
        print("    ✓ Connected")
    except Exception as e:
        print(f"    ⚠ {e}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# ==============================================================================
# STEP 4: CONFIGURE MESH SPAWNER (Reflection)
# ==============================================================================
print("\n4. Configuring Static Mesh Spawner...")

spawner_settings = mesh_spawner.get_settings()
grass_mesh = unreal.load_object(None, GRASS_MESH_PATH)

if grass_mesh:
    print(f"✓ Loaded grass mesh")
    
    # Reflect on available properties
    print("\n  Discovering properties...")
    props = dir(spawner_settings)
    mesh_props = [p for p in props if 'mesh' in p.lower() and not p.startswith('_')]
    print(f"  Found mesh-related properties: {mesh_props}")
    
    # Try each one
    for prop in mesh_props:
        try:
            spawner_settings.set_editor_property(prop, grass_mesh)
            print(f"  ✓ Set '{prop}' = grass mesh")
            break
        except:
            pass

# ==============================================================================
# STEP 5: SAVE & ASSIGN TO VOLUME
# ==============================================================================
print("\n5. Saving graph...")
unreal.EditorAssetLibrary.save_asset(PCG_GRAPH_PATH)
print("✓ Saved")

print("\n6. Finding PCG Volume...")
pcg_volume = None
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    if actor.get_class().get_name() == "PCGVolume":
        pcg_volume = actor
        break

if pcg_volume:
    print(f"✓ Found PCG Volume")
    
    pcg_comp = None
    for comp in pcg_volume.get_components_by_class(unreal.PCGComponent):
        pcg_comp = comp
        break
    
    if pcg_comp:
        pcg_comp.set_graph(pcg_graph)
        print("  ✓ Assigned graph")
        
        print("\n7. Triggering generation...")
        pcg_comp.generate_local(True)
        print("  ✓ Generation triggered!")
    else:
        print("✗ No PCG Component")
else:
    print("✗ No PCG Volume")

print("\n" + "=" * 80)
print("DONE - Check viewport for grass!")
print("=" * 80)
