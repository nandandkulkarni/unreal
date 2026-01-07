"""
PCG Graph Configuration Script
Connects nodes, configures settings, and triggers grass generation
"""
import unreal
import sys

# ==============================================================================
# LOGGING
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\configure_pcg_graph.log"

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
print("CONFIGURING PCG GRAPH")
print("=" * 80)

# ==============================================================================
# CONFIGURATION
# ==============================================================================
PCG_GRAPH_PATH = "/Game/PCG/PCG_StadiumGrass"
GRASS_MESH_PATH = "/Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r/High/tbdpec3r_tier_1/StaticMeshes/SM_tbdpec3r_VarA"

# ==============================================================================
# STEP 1: LOAD GRAPH
# ==============================================================================
print("\n1. Loading PCG Graph...")
pcg_graph = unreal.load_asset(PCG_GRAPH_PATH)

if not pcg_graph:
    print(f"✗ Failed to load graph at {PCG_GRAPH_PATH}")
    sys.exit(1)

print(f"✓ Loaded graph: {type(pcg_graph)}")

# ==============================================================================
# STEP 2: INSPECT NODES
# ==============================================================================
print("\n2. Inspecting nodes...")

nodes = pcg_graph.nodes
print(f"Total nodes: {len(nodes)}")

input_node = pcg_graph.get_input_node()
output_node = pcg_graph.get_output_node()

print(f"Input node: {input_node}")
print(f"Output node: {output_node}")

# Identify our nodes
surface_sampler = None
mesh_spawner = None

for idx, node in enumerate(nodes):
    settings = node.get_settings()
    settings_type = type(settings).__name__
    print(f"\nNode {idx}:")
    print(f"  Type: {settings_type}")
    print(f"  Title: {node.node_title}")
    
    # Check input/output pins
    print(f"  Input Pins: {len(node.input_pins)}")
    for pin_idx, pin in enumerate(node.input_pins):
        try:
            label = pin.label if hasattr(pin, 'label') else f"Pin_{pin_idx}"
            print(f"    - {label}")
        except:
            print(f"    - [Pin {pin_idx}]")
    
    print(f"  Output Pins: {len(node.output_pins)}")
    for pin_idx, pin in enumerate(node.output_pins):
        try:
            label = pin.label if hasattr(pin, 'label') else f"Pin_{pin_idx}"
            print(f"    - {label}")
        except:
            print(f"    - [Pin {pin_idx}]")
    
    # Identify nodes
    if "SurfaceSampler" in settings_type:
        surface_sampler = node
        print("  → Identified as Surface Sampler")
    elif "StaticMeshSpawner" in settings_type:
        mesh_spawner = node
        print("  → Identified as Static Mesh Spawner")

# ==============================================================================
# STEP 3: CONNECT NODES
# ==============================================================================
print("\n3. Connecting nodes...")

if not surface_sampler or not mesh_spawner:
    print("✗ Could not identify both nodes")
    sys.exit(1)

# Standard PCG flow: Input → Surface Sampler → Mesh Spawner → Output
# Get pin labels
sampler_output_pins = surface_sampler.output_pins
spawner_input_pins = mesh_spawner.input_pins

# Get pin labels safely
if len(sampler_output_pins) > 0 and len(spawner_input_pins) > 0:
    # Use index 0 and try to get label, fallback to generic names
    try:
        sampler_out_label = sampler_output_pins[0].label if hasattr(sampler_output_pins[0], 'label') else "Out"
    except:
        sampler_out_label = "Out"
    
    try:
        spawner_in_label = spawner_input_pins[0].label if hasattr(spawner_input_pins[0], 'label') else "In"
    except:
        spawner_in_label = "In"
    
    print(f"Connecting: Surface Sampler.{sampler_out_label} → Mesh Spawner.{spawner_in_label}")
    
    try:
        # Connect Input → Surface Sampler
        if input_node:
            input_out_label = input_node.output_pins[0].label if len(input_node.output_pins) > 0 else "Out"
            sampler_in_label = surface_sampler.input_pins[0].label if len(surface_sampler.input_pins) > 0 else "In"
            
            print(f"Connecting: Input.{input_out_label} → Surface Sampler.{sampler_in_label}")
            pcg_graph.add_edge(input_node, input_out_label, surface_sampler, sampler_in_label)
            print("  ✓ Connected Input → Surface Sampler")
        
        # Connect Surface Sampler → Mesh Spawner
        pcg_graph.add_edge(surface_sampler, sampler_out_label, mesh_spawner, spawner_in_label)
        print("  ✓ Connected Surface Sampler → Mesh Spawner")
        
        # Connect Mesh Spawner → Output
        if output_node:
            spawner_out_label = mesh_spawner.output_pins[0].label if len(mesh_spawner.output_pins) > 0 else "Out"
            output_in_label = output_node.input_pins[0].label if len(output_node.input_pins) > 0 else "In"
            
            print(f"Connecting: Mesh Spawner.{spawner_out_label} → Output.{output_in_label}")
            pcg_graph.add_edge(mesh_spawner, spawner_out_label, output_node, output_in_label)
            print("  ✓ Connected Mesh Spawner → Output")
            
    except Exception as e:
        print(f"✗ Error connecting nodes: {e}")
        import traceback
        traceback.print_exc()
else:
    print("✗ Nodes don't have expected pins")

# ==============================================================================
# STEP 4: CONFIGURE MESH SPAWNER
# ==============================================================================
print("\n4. Configuring Static Mesh Spawner...")

try:
    spawner_settings = mesh_spawner.get_settings()
    print(f"Spawner settings type: {type(spawner_settings)}")
    
    # Try to set mesh via set_editor_property
    # Common property names: "Mesh", "StaticMesh", "MeshEntries"
    
    # Load the grass mesh
    grass_mesh = unreal.load_object(None, GRASS_MESH_PATH)
    if grass_mesh:
        print(f"✓ Loaded grass mesh: {grass_mesh.get_name()}")
        
        # Try different property names
        property_attempts = [
            ("mesh", grass_mesh),
            ("static_mesh", grass_mesh),
            ("meshes", [grass_mesh]),
        ]
        
        for prop_name, value in property_attempts:
            try:
                spawner_settings.set_editor_property(prop_name, value)
                print(f"  ✓ Set property '{prop_name}'")
                break
            except Exception as e:
                print(f"  ✗ Property '{prop_name}' failed: {e}")
    else:
        print(f"✗ Failed to load grass mesh")
        
except Exception as e:
    print(f"✗ Error configuring spawner: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# STEP 5: SAVE GRAPH
# ==============================================================================
print("\n5. Saving graph...")
try:
    unreal.EditorAssetLibrary.save_asset(PCG_GRAPH_PATH)
    print(f"✓ Saved: {PCG_GRAPH_PATH}")
except Exception as e:
    print(f"✗ Error saving: {e}")

# ==============================================================================
# STEP 6: FIND AND CONFIGURE PCG VOLUME
# ==============================================================================
print("\n6. Finding PCG Volume...")

all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
pcg_volume = None

for actor in all_actors:
    if actor.get_class().get_name() == "PCGVolume":
        pcg_volume = actor
        print(f"✓ Found PCG Volume: {actor.get_actor_label()}")
        break

if pcg_volume:
    # Get PCG Component
    pcg_comp = None
    for comp in pcg_volume.get_components_by_class(unreal.PCGComponent):
        pcg_comp = comp
        break
    
    if pcg_comp:
        print(f"✓ Found PCG Component")
        
        # Set the graph
        try:
            pcg_comp.set_graph(pcg_graph)
            print(f"  ✓ Assigned graph to component")
            
            # Trigger generation
            print("\n7. Triggering PCG generation...")
            pcg_comp.generate_local(True)  # True = force regenerate
            print("  ✓ Generation triggered")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("✗ No PCG Component found on volume")
else:
    print("✗ No PCG Volume found in scene")
    print("  You may need to run create_stadium_ground.py first")

print("\n" + "=" * 80)
print("CONFIGURATION COMPLETE")
print("=" * 80)
print("\nCheck the viewport for generated grass!")
print("If nothing appears, open the PCG Graph in the editor to debug.")
