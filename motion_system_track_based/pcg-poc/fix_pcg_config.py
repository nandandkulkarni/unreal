"""
PCG Configuration Diagnostic and Fix Script
Checks and fixes:
1. Static Mesh Spawner mesh configuration
2. Surface Sampler actor targeting
3. PCG Volume regeneration
"""
import unreal
import sys

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\fix_pcg_config.log"

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
print("PCG CONFIGURATION DIAGNOSTIC & FIX")
print("=" * 80)

GRASS_MESH_PATH = "/Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r/High/tbdpec3r_tier_1/StaticMeshes/SM_tbdpec3r_VarA"

# ==============================================================================
# STEP 1: FIND LATEST PCG GRAPH
# ==============================================================================
print("\n1. Finding latest PCG Graph...")

pcg_assets = unreal.EditorAssetLibrary.list_assets("/Game/PCG", recursive=False)
pcg_graphs = [a for a in pcg_assets if "PCG_StadiumGrass" in a]

if not pcg_graphs:
    print("✗ No PCG graphs found!")
    sys.exit(1)

# Get the most recent one (highest number)
latest_graph_path = sorted(pcg_graphs)[-1]
print(f"✓ Found graph: {latest_graph_path}")

pcg_graph = unreal.load_asset(latest_graph_path)
if not pcg_graph:
    print("✗ Failed to load graph")
    sys.exit(1)

print(f"✓ Loaded graph: {pcg_graph.get_name()}")

# ==============================================================================
# STEP 2: INSPECT & FIX STATIC MESH SPAWNER
# ==============================================================================
print("\n2. Checking Static Mesh Spawner configuration...")

nodes = pcg_graph.nodes
mesh_spawner = None

for node in nodes:
    settings_type = type(node.get_settings()).__name__
    if "StaticMeshSpawner" in settings_type:
        mesh_spawner = node
        break

if not mesh_spawner:
    print("✗ No Static Mesh Spawner node found")
else:
    print(f"✓ Found Static Mesh Spawner node")
    
    spawner_settings = mesh_spawner.get_settings()
    print(f"  Settings type: {type(spawner_settings)}")
    
    # Try to inspect current mesh configuration
    print("\n  Inspecting spawner properties...")
    
    # Get all properties
    all_props = dir(spawner_settings)
    mesh_related = [p for p in all_props if 'mesh' in p.lower() and not p.startswith('_')]
    
    print(f"  Mesh-related properties found: {mesh_related}")
    
    # Try to read each property
    for prop in mesh_related:
        try:
            value = getattr(spawner_settings, prop)
            print(f"    {prop} = {value} (type: {type(value)})")
        except Exception as e:
            print(f"    {prop}: Cannot read - {e}")
    
    # Load grass mesh
    grass_mesh = unreal.load_object(None, GRASS_MESH_PATH)
    if grass_mesh:
        print(f"\n  ✓ Loaded grass mesh: {grass_mesh.get_name()}")
        
        # Try to set mesh using different approaches
        print("\n  Attempting to configure mesh...")
        
        # Approach 1: Try common property names
        success = False
        for prop_name in ["mesh_selector", "meshes", "mesh", "static_mesh_list"]:
            try:
                setattr(spawner_settings, prop_name, grass_mesh)
                print(f"    ✓ Set via attribute '{prop_name}'")
                success = True
                break
            except Exception as e:
                print(f"    ✗ '{prop_name}': {e}")
        
        if not success:
            print("    ⚠ Could not set mesh via standard properties")
            print("    This may require manual configuration in the editor")
    else:
        print(f"  ✗ Failed to load grass mesh from {GRASS_MESH_PATH}")

# ==============================================================================
# STEP 3: CHECK SURFACE SAMPLER CONFIGURATION
# ==============================================================================
print("\n3. Checking Surface Sampler configuration...")

surface_sampler = None
for node in nodes:
    settings_type = type(node.get_settings()).__name__
    if "SurfaceSampler" in settings_type:
        surface_sampler = node
        break

if surface_sampler:
    print(f"✓ Found Surface Sampler node")
    sampler_settings = surface_sampler.get_settings()
    
    # Check if it has actor filter or target settings
    print("\n  Inspecting sampler properties...")
    all_props = dir(sampler_settings)
    relevant = [p for p in all_props if any(k in p.lower() for k in ['actor', 'target', 'filter', 'bound']) and not p.startswith('_')]
    
    print(f"  Relevant properties: {relevant}")
    
    for prop in relevant:
        try:
            value = getattr(sampler_settings, prop)
            print(f"    {prop} = {value}")
        except:
            pass
else:
    print("✗ No Surface Sampler node found")

# ==============================================================================
# STEP 4: SAVE GRAPH
# ==============================================================================
print("\n4. Saving graph changes...")
saved = unreal.EditorAssetLibrary.save_loaded_asset(pcg_graph)
if saved:
    print("✓ Graph saved")
else:
    print("✗ Failed to save graph")

# ==============================================================================
# STEP 5: FIND AND REGENERATE PCG VOLUME
# ==============================================================================
print("\n5. Finding PCG Volume...")

all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
pcg_volume = None

for actor in all_actors:
    if actor.get_class().get_name() == "PCGVolume":
        label = actor.get_actor_label()
        if "Stadium_Grass" in label:
            pcg_volume = actor
            print(f"✓ Found PCG Volume: {label}")
            break

if pcg_volume:
    # Get PCG Component
    pcg_comp = None
    for comp in pcg_volume.get_components_by_class(unreal.PCGComponent):
        pcg_comp = comp
        break
    
    if pcg_comp:
        print(f"  ✓ Found PCG Component")
        
        # Check current graph assignment
        current_graph = pcg_comp.get_editor_property("graph_instance")
        print(f"  Current graph: {current_graph}")
        
        # Ensure our graph is assigned
        pcg_comp.set_graph(pcg_graph)
        print(f"  ✓ Assigned graph: {pcg_graph.get_name()}")
        
        # Cleanup old generation
        print("\n  Cleaning up old PCG data...")
        pcg_comp.cleanup_local(True)
        print("  ✓ Cleaned up")
        
        # Regenerate
        print("\n  Triggering PCG generation...")
        pcg_comp.generate_local(True)
        print("  ✓ Generation triggered!")
    else:
        print("  ✗ No PCG Component on volume")
else:
    print("✗ No PCG Volume found with 'Stadium_Grass' in name")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
print("\nNext steps if grass still doesn't appear:")
print("1. Open the PCG Graph in editor: " + latest_graph_path)
print("2. Double-click the Static Mesh Spawner node")
print("3. Manually set the 'Meshes' or 'Mesh Selector' property")
print("4. In the PCG Volume, click 'Generate' to regenerate")
