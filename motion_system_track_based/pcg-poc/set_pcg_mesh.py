"""
Configure PCG Mesh Selector with Grass Mesh
Sets the mesh in the PCGMeshSelectorWeighted instance
"""
import unreal
import sys

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\set_pcg_mesh.log"

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
print("CONFIGURE PCG MESH SELECTOR")
print("=" * 80)

GRASS_MESH_PATH = "/Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r/High/tbdpec3r_tier_1/StaticMeshes/SM_tbdpec3r_VarA"

# Find latest PCG graph
pcg_assets = unreal.EditorAssetLibrary.list_assets("/Game/PCG", recursive=False)
pcg_graphs = [a for a in pcg_assets if "PCG_StadiumGrass" in a]
latest_graph_path = sorted(pcg_graphs)[-1]

print(f"\n1. Loading graph: {latest_graph_path}")
pcg_graph = unreal.load_asset(latest_graph_path)

# Find mesh spawner node
nodes = pcg_graph.nodes
mesh_spawner = None

for node in nodes:
    if "StaticMeshSpawner" in type(node.get_settings()).__name__:
        mesh_spawner = node
        break

if not mesh_spawner:
    print("✗ No mesh spawner found")
    sys.exit(1)

print("✓ Found mesh spawner")

spawner_settings = mesh_spawner.get_settings()

# Get the mesh selector instance
mesh_selector = spawner_settings.mesh_selector_instance
print(f"\n2. Mesh Selector: {type(mesh_selector).__name__}")

# Inspect the mesh selector
print("\n3. Inspecting mesh selector properties...")
selector_props = dir(mesh_selector)
mesh_props = [p for p in selector_props if 'mesh' in p.lower() and not p.startswith('_')]
print(f"   Mesh-related properties: {mesh_props}")

for prop in mesh_props:
    try:
        value = getattr(mesh_selector, prop)
        print(f"   {prop} = {value} (type: {type(value).__name__})")
    except:
        pass

# Load grass mesh
grass_mesh = unreal.load_object(None, GRASS_MESH_PATH)
if not grass_mesh:
    print(f"\n✗ Failed to load grass mesh")
    sys.exit(1)

print(f"\n4. Loaded grass mesh: {grass_mesh.get_name()}")

# Try to configure the mesh selector
print("\n5. Configuring mesh selector...")

# Try different property names for PCGMeshSelectorWeighted
success = False
for prop_name in ["mesh_entries", "weighted_meshes", "meshes", "mesh_list"]:
    try:
        # Try to get current value
        current = getattr(mesh_selector, prop_name)
        print(f"   Found property '{prop_name}': {current}")
        
        # Try to set it
        setattr(mesh_selector, prop_name, [grass_mesh])
        print(f"   ✓ Set '{prop_name}' to grass mesh")
        success = True
        break
    except Exception as e:
        print(f"   ✗ '{prop_name}': {e}")

if not success:
    print("\n   Trying via set_editor_property...")
    for prop_name in ["mesh_entries", "weighted_meshes", "meshes"]:
        try:
            mesh_selector.set_editor_property(prop_name, [grass_mesh])
            print(f"   ✓ Set '{prop_name}' via set_editor_property")
            success = True
            break
        except Exception as e:
            print(f"   ✗ '{prop_name}': {e}")

# Save graph
print("\n6. Saving graph...")
saved = unreal.EditorAssetLibrary.save_loaded_asset(pcg_graph)
print(f"{'✓' if saved else '✗'} Graph save: {saved}")

# Regenerate PCG
print("\n7. Regenerating PCG...")
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
for actor in all_actors:
    if actor.get_class().get_name() == "PCGVolume" and "Stadium_Grass" in actor.get_actor_label():
        for comp in actor.get_components_by_class(unreal.PCGComponent):
            comp.cleanup_local(True)
            comp.generate_local(True)
            print(f"✓ Regenerated PCG on {actor.get_actor_label()}")
            break
        break

print("\n" + "=" * 80)
print("COMPLETE")
print("=" * 80)
if success:
    print("\n✅ Mesh configured successfully!")
    print("Check your viewport for grass generation.")
else:
    print("\n⚠ Could not configure mesh automatically")
    print("Manual steps required:")
    print(f"1. Open {latest_graph_path}")
    print("2. Double-click Static Mesh Spawner node")
    print("3. In 'Mesh Selector', add the grass mesh manually")
