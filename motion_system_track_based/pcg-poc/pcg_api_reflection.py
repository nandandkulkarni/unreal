"""
PCG Python API Reflection Script
Introspects PCG-related classes to discover available methods and properties
"""
import unreal
import sys
import inspect

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\pcg_api_reflection.log"

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
print("PCG PYTHON API REFLECTION")
print("=" * 80)

def inspect_class(cls, class_name):
    """Introspect a class and print all methods and properties"""
    print(f"\n{'='*80}")
    print(f"CLASS: {class_name}")
    print(f"{'='*80}")
    
    # Get all attributes
    all_attrs = dir(cls)
    
    # Categorize
    methods = []
    properties = []
    
    for attr in all_attrs:
        if attr.startswith('_'):
            continue
            
        try:
            obj = getattr(cls, attr)
            if callable(obj):
                methods.append(attr)
            else:
                properties.append(attr)
        except:
            pass
    
    # Print methods
    print(f"\nMETHODS ({len(methods)}):")
    for method in sorted(methods):
        try:
            sig = inspect.signature(getattr(cls, method))
            print(f"  {method}{sig}")
        except:
            print(f"  {method}(...)")
    
    # Print properties
    print(f"\nPROPERTIES ({len(properties)}):")
    for prop in sorted(properties):
        print(f"  {prop}")

# ==============================================================================
# INSPECT KEY PCG CLASSES
# ==============================================================================

classes_to_inspect = [
    ("unreal.PCGGraph", unreal.PCGGraph),
    ("unreal.PCGNode", unreal.PCGNode),
    ("unreal.PCGSettings", unreal.PCGSettings),
    ("unreal.PCGComponent", unreal.PCGComponent),
]

# Try to load additional classes
try:
    pcg_surface_sampler = unreal.load_class(None, "/Script/PCG.PCGSurfaceSamplerSettings")
    if pcg_surface_sampler:
        classes_to_inspect.append(("PCGSurfaceSamplerSettings", pcg_surface_sampler))
except:
    pass

try:
    pcg_mesh_spawner = unreal.load_class(None, "/Script/PCG.PCGStaticMeshSpawnerSettings")
    if pcg_mesh_spawner:
        classes_to_inspect.append(("PCGStaticMeshSpawnerSettings", pcg_mesh_spawner))
except:
    pass

for class_name, cls in classes_to_inspect:
    try:
        inspect_class(cls, class_name)
    except Exception as e:
        print(f"\n✗ Error inspecting {class_name}: {e}")

# ==============================================================================
# TEST SPECIFIC METHODS
# ==============================================================================
print("\n" + "=" * 80)
print("TESTING SPECIFIC METHODS")
print("=" * 80)

# Load the graph we created
print("\nLoading PCG_StadiumGrass...")
try:
    pcg_graph = unreal.load_asset("/Game/PCG/PCG_StadiumGrass")
    if pcg_graph:
        print(f"✓ Loaded: {type(pcg_graph)}")
        
        # Try different methods to get nodes
        print("\nTrying to access nodes...")
        
        # Method 1: get_nodes()
        if hasattr(pcg_graph, 'get_nodes'):
            print("  ✓ Has get_nodes()")
            try:
                nodes = pcg_graph.get_nodes()
                print(f"    Nodes: {len(nodes)}")
            except Exception as e:
                print(f"    ✗ Error calling: {e}")
        else:
            print("  ✗ No get_nodes() method")
        
        # Method 2: nodes property
        if hasattr(pcg_graph, 'nodes'):
            print("  ✓ Has 'nodes' property")
            try:
                nodes = pcg_graph.nodes
                print(f"    Type: {type(nodes)}")
                print(f"    Length: {len(nodes) if hasattr(nodes, '__len__') else 'N/A'}")
            except Exception as e:
                print(f"    ✗ Error accessing: {e}")
        else:
            print("  ✗ No 'nodes' property")
            
        # Method 3: get_graph()
        if hasattr(pcg_graph, 'get_graph'):
            print("  ✓ Has get_graph()")
        
        # Check for edge methods
        print("\nChecking edge methods...")
        if hasattr(pcg_graph, 'add_edge'):
            print("  ✓ Has add_edge()")
            # Try to get signature
            try:
                sig = inspect.signature(pcg_graph.add_edge)
                print(f"    Signature: {sig}")
            except:
                pass
        else:
            print("  ✗ No add_edge() method")
            
    else:
        print("✗ Failed to load graph")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("REFLECTION COMPLETE")
print("=" * 80)
