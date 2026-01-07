"""
Deep Reflection on add_edge_to method
"""
import unreal
import sys
import inspect

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\add_edge_to_reflection.log"

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
print("ADD_EDGE_TO METHOD REFLECTION")
print("=" * 80)

# Load graph and get nodes
pcg_graph = unreal.load_asset("/Game/PCG/PCG_StadiumGrass")
nodes = pcg_graph.nodes

surface_sampler = None
mesh_spawner = None

for node in nodes:
    settings_type = type(node.get_settings()).__name__
    if "SurfaceSampler" in settings_type:
        surface_sampler = node
    elif "StaticMeshSpawner" in settings_type:
        mesh_spawner = node

print(f"\nSurface Sampler: {surface_sampler}")
print(f"Mesh Spawner: {mesh_spawner}")

# ==============================================================================
# INSPECT add_edge_to METHOD
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD SIGNATURE INSPECTION")
print("=" * 80)

if surface_sampler:
    method = surface_sampler.add_edge_to
    print(f"\nMethod: {method}")
    print(f"Type: {type(method)}")
    
    # Try to get signature
    try:
        sig = inspect.signature(method)
        print(f"\nSignature: {sig}")
        
        for param_name, param in sig.parameters.items():
            print(f"  Parameter: {param_name}")
            print(f"    Kind: {param.kind}")
            print(f"    Default: {param.default}")
            print(f"    Annotation: {param.annotation}")
    except Exception as e:
        print(f"\nCouldn't get signature via inspect: {e}")
    
    # Try help()
    print("\n" + "-" * 80)
    print("HELP OUTPUT:")
    print("-" * 80)
    try:
        help(method)
    except:
        pass

# ==============================================================================
# TEST DIFFERENT PARAMETER COMBINATIONS
# ==============================================================================
print("\n" + "=" * 80)
print("TESTING PARAMETER COMBINATIONS")
print("=" * 80)

if surface_sampler and mesh_spawner:
    # Get pin labels
    sampler_out_pin = surface_sampler.output_pins[0]
    spawner_in_pin = mesh_spawner.input_pins[0]
    
    sampler_out_label = sampler_out_pin.properties.label
    spawner_in_label = spawner_in_pin.properties.label
    
    print(f"\nSampler output pin label: '{sampler_out_label}'")
    print(f"Spawner input pin label: '{spawner_in_label}'")
    
    # Test 1: Just to_node
    print("\n1. Testing: add_edge_to(to_node)")
    try:
        result = surface_sampler.add_edge_to(mesh_spawner)
        print(f"   ✓ Success! Result: {result}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: to_node + from_label
    print("\n2. Testing: add_edge_to(to_node, from_label)")
    try:
        result = surface_sampler.add_edge_to(mesh_spawner, sampler_out_label)
        print(f"   ✓ Success! Result: {result}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: to_node + from_label + to_label
    print("\n3. Testing: add_edge_to(to_node, from_label, to_label)")
    try:
        result = surface_sampler.add_edge_to(mesh_spawner, sampler_out_label, spawner_in_label)
        print(f"   ✓ Success! Result: {result}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Named parameters
    print("\n4. Testing: add_edge_to(to=to_node, from_pin_label=..., to_pin_label=...)")
    try:
        result = surface_sampler.add_edge_to(
            to=mesh_spawner,
            from_pin_label=sampler_out_label,
            to_pin_label=spawner_in_label
        )
        print(f"   ✓ Success! Result: {result}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 5: Just named 'to'
    print("\n5. Testing: add_edge_to(to=to_node)")
    try:
        result = surface_sampler.add_edge_to(to=mesh_spawner)
        print(f"   ✓ Success! Result: {result}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

# ==============================================================================
# ALSO TEST PCGGraph.add_edge
# ==============================================================================
print("\n" + "=" * 80)
print("TESTING PCGGraph.add_edge")
print("=" * 80)

if surface_sampler and mesh_spawner:
    print("\nTesting: pcg_graph.add_edge(from_node, from_label, to_node, to_label)")
    try:
        result = pcg_graph.add_edge(
            surface_sampler,
            sampler_out_label,
            mesh_spawner,
            spawner_in_label
        )
        print(f"   ✓ Success! Result: {result}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

print("\n" + "=" * 80)
print("REFLECTION COMPLETE")
print("=" * 80)
