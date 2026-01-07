"""
PCG Graph Creator (Experimental)
Attempts to create a PCG Graph programmatically using Python API
Based on UE5 PCG Python API research
"""
import unreal
import sys

# ==============================================================================
# LOGGING
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\create_pcg_grass.log"

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
print("CREATING PCG GRAPH VIA PYTHON (EXPERIMENTAL)")
print("=" * 80)

# ==============================================================================
# CONFIGURATION
# ==============================================================================
GRASS_MESH_PATH = "/Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r/High/tbdpec3r_tier_1/StaticMeshes/SM_tbdpec3r_VarA"
PCG_GRAPH_NAME = "PCG_StadiumGrass"
PCG_GRAPH_PATH = f"/Game/PCG/{PCG_GRAPH_NAME}"

# ==============================================================================
# STEP 1: CREATE PCG GRAPH ASSET
# ==============================================================================
print("\n1. Creating PCG Graph Asset...")

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

# Check if already exists
if unreal.EditorAssetLibrary.does_asset_exist(PCG_GRAPH_PATH):
    print(f"  Graph already exists at {PCG_GRAPH_PATH}, deleting...")
    unreal.EditorAssetLibrary.delete_asset(PCG_GRAPH_PATH)

# Create new PCG Graph
try:
    pcg_graph_factory = unreal.PCGGraphFactory()
    
    pcg_graph = asset_tools.create_asset(
        asset_name=PCG_GRAPH_NAME,
        package_path="/Game/PCG",
        asset_class=unreal.PCGGraph,
        factory=pcg_graph_factory
    )
    
    if pcg_graph:
        print(f"✓ Created PCG Graph: {PCG_GRAPH_PATH}")
    else:
        print("✗ Failed to create PCG Graph")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error creating graph: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# STEP 2: EXPLORE AVAILABLE NODE TYPES
# ==============================================================================
print("\n2. Exploring available PCG node types...")

# Try to find PCG node classes
try:
    # Common PCG node types we might need
    node_types_to_try = [
        "PCGSurfaceSamplerSettings",
        "PCGStaticMeshSpawnerSettings",
        "PCGDensityFilterSettings",
        "PCGPointSamplerSettings",
        "PCGSpawnActorSettings",
    ]
    
    available_nodes = []
    for node_type in node_types_to_try:
        try:
            node_class = unreal.load_class(None, f"/Script/PCG.{node_type}")
            if node_class:
                available_nodes.append(node_type)
                print(f"  ✓ Found: {node_type}")
        except:
            print(f"  ✗ Not found: {node_type}")
    
    if not available_nodes:
        print("  ⚠ No standard PCG node types found via load_class")
        print("  Attempting alternative approach...")
        
except Exception as e:
    print(f"  Error exploring nodes: {e}")

# ==============================================================================
# STEP 3: ADD NODES TO GRAPH
# ==============================================================================
print("\n3. Adding nodes to PCG Graph...")

try:
    # Method 1: Try add_node_of_type with class reference
    print("  Attempting to add Surface Sampler node...")
    
    # Try to get the settings class
    surface_sampler_class = unreal.load_class(None, "/Script/PCG.PCGSurfaceSamplerSettings")
    
    if surface_sampler_class:
        sampler_node = pcg_graph.add_node_of_type(surface_sampler_class)
        if sampler_node:
            print(f"  ✓ Added Surface Sampler node")
        else:
            print(f"  ✗ add_node_of_type returned None")
    else:
        print("  ✗ Could not load PCGSurfaceSamplerSettings class")
        
    # Try to add Static Mesh Spawner
    print("  Attempting to add Static Mesh Spawner node...")
    spawner_class = unreal.load_class(None, "/Script/PCG.PCGStaticMeshSpawnerSettings")
    
    if spawner_class:
        spawner_node = pcg_graph.add_node_of_type(spawner_class)
        if spawner_node:
            print(f"  ✓ Added Static Mesh Spawner node")
            
            # Try to set the mesh
            # spawner_node might have a 'settings' property
            if hasattr(spawner_node, 'settings'):
                settings = spawner_node.settings
                print(f"    Node settings type: {type(settings)}")
                
                # Try to set mesh entries
                if hasattr(settings, 'mesh_entries'):
                    print("    Attempting to set mesh...")
                    # This part is highly experimental
                    
        else:
            print(f"  ✗ add_node_of_type returned None for spawner")
    else:
        print("  ✗ Could not load PCGStaticMeshSpawnerSettings class")
        
except Exception as e:
    print(f"✗ Error adding nodes: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# STEP 4: INSPECT GRAPH STRUCTURE
# ==============================================================================
print("\n4. Inspecting created graph...")

try:
    # Get nodes
    nodes = pcg_graph.get_nodes()
    print(f"  Total nodes in graph: {len(nodes)}")
    
    for idx, node in enumerate(nodes):
        print(f"  Node {idx}: {type(node).__name__}")
        if hasattr(node, 'get_settings'):
            settings = node.get_settings()
            print(f"    Settings: {type(settings).__name__}")
            
except Exception as e:
    print(f"  Error inspecting graph: {e}")

# ==============================================================================
# STEP 5: SAVE ASSET
# ==============================================================================
print("\n5. Saving PCG Graph asset...")

try:
    unreal.EditorAssetLibrary.save_asset(PCG_GRAPH_PATH)
    print(f"✓ Saved: {PCG_GRAPH_PATH}")
except Exception as e:
    print(f"✗ Error saving: {e}")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"PCG Graph Asset: {PCG_GRAPH_PATH}")
print("\nNEXT STEPS:")
print("1. Open the PCG Graph in the editor")
print("2. Manually add/configure nodes if Python API is limited")
print("3. Assign the graph to the PCGVolume in the scene")
print("4. Trigger generation")
print("\nThis script demonstrates the current limitations of PCG Python API.")
print("Full node configuration may require Blueprint or manual editor work.")
