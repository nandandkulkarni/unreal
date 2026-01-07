"""
Final PCG Grass Configuration
Uses discovered API: pin.properties.label and pcg_graph.add_edge()
"""
import unreal
import sys

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\final_pcg_config.log"

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
print("FINAL PCG GRASS CONFIGURATION")
print("=" * 80)

PCG_GRAPH_PATH = "/Game/PCG/PCG_StadiumGrass"
GRASS_MESH_PATH = "/Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r/High/tbdpec3r_tier_1/StaticMeshes/SM_tbdpec3r_VarA"

# ==============================================================================
# 1. LOAD GRAPH
# ==============================================================================
print("\n1. Loading PCG Graph...")
pcg_graph = unreal.load_asset(PCG_GRAPH_PATH)
if not pcg_graph:
    print("✗ Failed to load graph")
    sys.exit(1)
print("✓ Loaded graph")

# ==============================================================================
# 2. IDENTIFY NODES
# ==============================================================================
print("\n2. Identifying nodes...")
nodes = pcg_graph.nodes
input_node = pcg_graph.get_input_node()
output_node = pcg_graph.get_output_node()

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

print(f"✓ Surface Sampler: {surface_sampler.get_name()}")
print(f"✓ Mesh Spawner: {mesh_spawner.get_name()}")

# ==============================================================================
# 3. CONNECT NODES
# ==============================================================================
print("\n3. Connecting nodes...")

# Get pin labels using pin.properties.label
input_out_label = input_node.output_pins[0].properties.label
sampler_in_label = surface_sampler.input_pins[0].properties.label
sampler_out_label = surface_sampler.output_pins[0].properties.label
spawner_in_label = mesh_spawner.input_pins[0].properties.label
spawner_out_label = mesh_spawner.output_pins[0].properties.label
output_in_label = output_node.input_pins[0].properties.label

print(f"  Pin labels: Input.{input_out_label} → Sampler.{sampler_in_label} → Sampler.{sampler_out_label} → Spawner.{spawner_in_label} → Spawner.{spawner_out_label} → Output.{output_in_label}")

try:
    # Connect: Input → Surface Sampler
    pcg_graph.add_edge(input_node, input_out_label, surface_sampler, sampler_in_label)
    print("  ✓ Input → Surface Sampler")
    
    # Connect: Surface Sampler → Mesh Spawner
    pcg_graph.add_edge(surface_sampler, sampler_out_label, mesh_spawner, spawner_in_label)
    print("  ✓ Surface Sampler → Mesh Spawner")
    
    # Connect: Mesh Spawner → Output
    pcg_graph.add_edge(mesh_spawner, spawner_out_label, output_node, output_in_label)
    print("  ✓ Mesh Spawner → Output")
    
except Exception as e:
    print(f"✗ Error connecting: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 4. CONFIGURE MESH SPAWNER (Find correct property)
# ==============================================================================
print("\n4. Configuring Mesh Spawner...")

grass_mesh = unreal.load_object(None, GRASS_MESH_PATH)
if not grass_mesh:
    print("✗ Failed to load grass mesh")
else:
    print(f"✓ Loaded grass mesh: {grass_mesh.get_name()}")
    
    spawner_settings = mesh_spawner.get_settings()
    
    # Try all possible property names
    mesh_property_names = [
        "mesh_entries", "mesh_entry", "meshes", "mesh", "static_mesh",
        "mesh_list", "mesh_selector", "mesh_descriptor", "mesh_parameters"
    ]
    
    configured = False
    for prop_name in mesh_property_names:
        try:
            # Try to get the property first to see if it exists
            current_value = spawner_settings.get_editor_property(prop_name)
            print(f"  Found property '{prop_name}': {type(current_value)}")
            
            # Try to set it
            spawner_settings.set_editor_property(prop_name, grass_mesh)
            print(f"  ✓ Set '{prop_name}' = grass mesh")
            configured = True
            break
        except Exception as e:
            # Only print if it's not a "property not found" error
            if "Failed to find property" not in str(e):
                print(f"  ? '{prop_name}': {e}")
    
    if not configured:
        print("  ⚠ Could not find mesh property - may need manual configuration")

# ==============================================================================
# 5. SAVE GRAPH
# ==============================================================================
print("\n5. Saving graph...")
unreal.EditorAssetLibrary.save_asset(PCG_GRAPH_PATH)
print("✓ Saved")

# ==============================================================================
# 6. CREATE/FIND PCG VOLUME & ASSIGN GRAPH
# ==============================================================================
print("\n6. Setting up PCG Volume...")

# Find existing volume
pcg_volume = None
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    if actor.get_class().get_name() == "PCGVolume":
        pcg_volume = actor
        break

# Create if not found
if not pcg_volume:
    print("  Creating new PCG Volume...")
    pcg_vol_cls = unreal.load_class(None, "/Script/PCG.PCGVolume")
    if pcg_vol_cls:
        pcg_volume = unreal.EditorLevelLibrary.spawn_actor_from_class(
            pcg_vol_cls,
            unreal.Vector(0, 0, 100)
        )
        pcg_volume.set_actor_label("Stadium_Grass_PCG_Volume")
        pcg_volume.set_folder_path(unreal.Name("OvalTrack/PCG"))
        
        # Scale to cover stadium (approx 200m x 100m)
        pcg_volume.set_actor_scale3d(unreal.Vector(200.0, 100.0, 10.0))
        print("  ✓ Created PCG Volume")
    else:
        print("  ✗ Could not create PCG Volume")

if pcg_volume:
    print(f"✓ PCG Volume: {pcg_volume.get_actor_label()}")
    
    # Get PCG Component
    pcg_comp = None
    for comp in pcg_volume.get_components_by_class(unreal.PCGComponent):
        pcg_comp = comp
        break
    
    if pcg_comp:
        # Assign graph
        pcg_comp.set_graph(pcg_graph)
        print("  ✓ Assigned graph to component")
        
        # Trigger generation
        print("\n7. Triggering PCG generation...")
        pcg_comp.generate_local(True)
        print("  ✓ Generation triggered!")
        print("\n🎉 PCG grass generation initiated - check viewport!")
    else:
        print("  ✗ No PCG Component on volume")
else:
    print("✗ No PCG Volume available")

print("\n" + "=" * 80)
print("CONFIGURATION COMPLETE")
print("=" * 80)
print("\nNext steps if grass doesn't appear:")
print("1. Open /Game/PCG/PCG_StadiumGrass in editor")
print("2. Manually configure Static Mesh Spawner mesh property")
print("3. Check PCG Volume bounds cover the stadium ground")
