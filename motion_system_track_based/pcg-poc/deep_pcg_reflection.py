"""
Deep PCG Property Reflection
Discovers hidden properties on PCG objects using get_editor_property
"""
import unreal
import sys

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\deep_pcg_reflection.log"

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
print("DEEP PCG PROPERTY REFLECTION")
print("=" * 80)

# ==============================================================================
# LOAD GRAPH
# ==============================================================================
print("\nLoading graph...")
pcg_graph = unreal.load_asset("/Game/PCG/PCG_StadiumGrass")

if not pcg_graph:
    print("✗ Failed to load graph")
    sys.exit(1)

nodes = pcg_graph.nodes

# Find spawner
mesh_spawner_node = None
for node in nodes:
    if "StaticMeshSpawner" in type(node.get_settings()).__name__:
        mesh_spawner_node = node
        break

if not mesh_spawner_node:
    print("✗ No spawner found")
    sys.exit(1)

spawner_settings = mesh_spawner_node.get_settings()

# ==============================================================================
# DISCOVER PIN PROPERTIES
# ==============================================================================
print("\n" + "=" * 80)
print("PIN OBJECT ANALYSIS")
print("=" * 80)

if len(mesh_spawner_node.input_pins) > 0:
    pin = mesh_spawner_node.input_pins[0]
    print(f"\nPin Type: {type(pin)}")
    print(f"Pin Class: {pin.get_class().get_name()}")
    
    # Try to get all properties
    print("\nTrying common pin properties:")
    props_to_try = ["label", "name", "pin_name", "properties", "pin_id", "tooltip"]
    
    for prop in props_to_try:
        try:
            value = pin.get_editor_property(prop)
            print(f"  ✓ {prop} = {value}")
        except Exception as e:
            print(f"  ✗ {prop}: {e}")

# ==============================================================================
# DISCOVER SPAWNER SETTINGS PROPERTIES
# ==============================================================================
print("\n" + "=" * 80)
print("SPAWNER SETTINGS ANALYSIS")
print("=" * 80)

print(f"\nSettings Type: {type(spawner_settings)}")
print(f"Settings Class: {spawner_settings.get_class().get_name()}")

# Try common mesh-related properties
print("\nTrying mesh properties:")
mesh_props = [
    "mesh", "static_mesh", "meshes", "mesh_entries",
    "mesh_list", "mesh_selector", "mesh_descriptor",
    "instance_packer_settings", "mesh_spawner_settings",
    "mesh_entry", "mesh_parameters"
]

for prop in mesh_props:
    try:
        value = spawner_settings.get_editor_property(prop)
        print(f"  ✓ {prop} = {value} (type: {type(value)})")
    except Exception as e:
        # Only print if it's not a "property not found" error
        if "Failed to find property" not in str(e):
            print(f"  ? {prop}: {e}")

# ==============================================================================
# TRY ALTERNATIVE APPROACHES
# ==============================================================================
print("\n" + "=" * 80)
print("ALTERNATIVE APPROACHES")
print("=" * 80)

# 1. Check if settings has a parent class with properties
print("\n1. Checking parent classes...")
try:
    parent_class = spawner_settings.get_class().get_super_class()
    print(f"Parent class: {parent_class.get_name()}")
except:
    pass

# 2. Try to access via settings_interface
print("\n2. Checking settings_interface...")
try:
    settings_interface = mesh_spawner_node.settings_interface
    print(f"Settings interface: {settings_interface}")
    print(f"Type: {type(settings_interface)}")
except Exception as e:
    print(f"Error: {e}")

# 3. Check if we can enumerate properties via reflection
print("\n3. Attempting property enumeration...")
try:
    # Try to get property list from class
    cls = spawner_settings.get_class()
    print(f"Class: {cls}")
    
    # This might work in some UE versions
    if hasattr(cls, 'get_properties'):
        props = cls.get_properties()
        print(f"Properties: {props}")
except Exception as e:
    print(f"Error: {e}")

# ==============================================================================
# TEST NODE.ADD_EDGE_TO
# ==============================================================================
print("\n" + "=" * 80)
print("TESTING NODE.ADD_EDGE_TO")
print("=" * 80)

surface_sampler = None
for node in nodes:
    if "SurfaceSampler" in type(node.get_settings()).__name__:
        surface_sampler = node
        break

if surface_sampler and mesh_spawner_node:
    print("\nTrying to connect using node.add_edge_to()...")
    try:
        # Signature might be: add_edge_to(to_node, from_pin_label, to_pin_label)
        # Or: add_edge_to(to_node)
        # Let's try
        result = surface_sampler.add_edge_to(mesh_spawner_node)
        print(f"  ✓ Result: {result}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("REFLECTION COMPLETE")
print("=" * 80)
