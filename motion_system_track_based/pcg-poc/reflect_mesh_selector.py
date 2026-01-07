"""
Deep Reflection on PCGMeshSelectorWeighted
Discover the exact structure needed for mesh_entries
"""
import unreal
import sys

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\reflect_mesh_selector.log"

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
print("DEEP REFLECTION: PCGMeshSelectorWeighted")
print("=" * 80)

# Find latest PCG graph
pcg_assets = unreal.EditorAssetLibrary.list_assets("/Game/PCG", recursive=False)
pcg_graphs = [a for a in pcg_assets if "PCG_StadiumGrass" in a]
latest_graph_path = sorted(pcg_graphs)[-1]

pcg_graph = unreal.load_asset(latest_graph_path)
nodes = pcg_graph.nodes

# Find mesh spawner
mesh_spawner = None
for node in nodes:
    if "StaticMeshSpawner" in type(node.get_settings()).__name__:
        mesh_spawner = node
        break

spawner_settings = mesh_spawner.get_settings()
mesh_selector = spawner_settings.mesh_selector_instance

print(f"\n1. Mesh Selector Type: {type(mesh_selector)}")
print(f"   Object: {mesh_selector}")

# Get current mesh_entries
print(f"\n2. Current mesh_entries:")
current_entries = mesh_selector.mesh_entries
print(f"   Type: {type(current_entries)}")
print(f"   Length: {len(current_entries)}")
print(f"   Value: {current_entries}")

# If there are entries, inspect them
if len(current_entries) > 0:
    print(f"\n3. Inspecting existing entry:")
    entry = current_entries[0]
    print(f"   Entry type: {type(entry)}")
    print(f"   Entry value: {entry}")
    
    # Get all attributes of the entry
    entry_attrs = dir(entry)
    print(f"\n   Entry attributes:")
    for attr in entry_attrs:
        if not attr.startswith('_'):
            try:
                value = getattr(entry, attr)
                print(f"     {attr} = {value} (type: {type(value).__name__})")
            except:
                pass
else:
    print(f"\n3. No existing entries - trying to create one")
    
    # Try to find the struct class
    print(f"\n4. Searching for PCGMeshSelectorWeightedEntry struct...")
    
    # Try different approaches to create the struct
    attempts = [
        "unreal.PCGMeshSelectorWeightedEntry",
        "unreal.load_class(None, '/Script/PCG.PCGMeshSelectorWeightedEntry')",
        "unreal.load_object(None, '/Script/PCG.PCGMeshSelectorWeightedEntry')",
    ]
    
    for attempt in attempts:
        try:
            result = eval(attempt)
            print(f"   ✓ {attempt} = {result}")
        except Exception as e:
            print(f"   ✗ {attempt}: {e}")
    
    # Try to inspect the property itself
    print(f"\n5. Inspecting mesh_entries property via get_editor_property:")
    try:
        prop_value = mesh_selector.get_editor_property("mesh_entries")
        print(f"   Value: {prop_value}")
        print(f"   Type: {type(prop_value)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Try to get property metadata
    print(f"\n6. Trying to create empty entry and add to array:")
    try:
        # Create a new empty array
        new_entries = []
        
        # Try to create a struct using unreal module
        print(f"   Checking unreal module for struct types...")
        unreal_attrs = dir(unreal)
        weighted_entry_types = [a for a in unreal_attrs if 'weighted' in a.lower() and 'entry' in a.lower()]
        print(f"   Found types: {weighted_entry_types}")
        
        # Check for any PCG struct types
        pcg_struct_types = [a for a in unreal_attrs if a.startswith('PCG') and 'Entry' in a]
        print(f"   PCG Entry types: {pcg_struct_types}")
        
    except Exception as e:
        print(f"   Error: {e}")

# Try alternative: inspect the spawner settings for other mesh-related methods
print(f"\n7. Checking spawner_settings for alternative methods:")
spawner_methods = dir(spawner_settings)
relevant = [m for m in spawner_methods if 'mesh' in m.lower() and not m.startswith('_')]
print(f"   Methods: {relevant}")

for method_name in relevant:
    method = getattr(spawner_settings, method_name)
    if callable(method):
        print(f"\n   Method: {method_name}")
        print(f"   Type: {type(method)}")
        try:
            import inspect
            sig = inspect.signature(method)
            print(f"   Signature: {sig}")
        except:
            print(f"   (Cannot get signature)")

print("\n" + "=" * 80)
print("REFLECTION COMPLETE")
print("=" * 80)
