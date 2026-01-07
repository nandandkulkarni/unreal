"""
Configure PCG Mesh Using PCGMeshSelectorWeightedEntry Struct
"""
import unreal
import sys

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\final_mesh_config.log"

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
print("FINAL PCG MESH CONFIGURATION")
print("=" * 80)

GRASS_MESH_PATH = "/Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r/High/tbdpec3r_tier_1/StaticMeshes/SM_tbdpec3r_VarA"

# Load graph
pcg_assets = unreal.EditorAssetLibrary.list_assets("/Game/PCG", recursive=False)
pcg_graphs = [a for a in pcg_assets if "PCG_StadiumGrass" in a]
latest_graph_path = sorted(pcg_graphs)[-1]

print(f"\n1. Loading: {latest_graph_path}")
pcg_graph = unreal.load_asset(latest_graph_path)

# Find mesh spawner
nodes = pcg_graph.nodes
mesh_spawner = None
for node in nodes:
    if "StaticMeshSpawner" in type(node.get_settings()).__name__:
        mesh_spawner = node
        break

spawner_settings = mesh_spawner.get_settings()
mesh_selector = spawner_settings.mesh_selector_instance

print(f"✓ Found mesh selector")

# Load grass mesh
grass_mesh = unreal.load_object(None, GRASS_MESH_PATH)
print(f"\n2. Loaded grass mesh: {grass_mesh.get_name()}")

# Create PCGMeshSelectorWeightedEntry struct
print(f"\n3. Creating PCGMeshSelectorWeightedEntry...")

try:
    # Create the struct
    entry = unreal.PCGMeshSelectorWeightedEntry()
    print(f"   ✓ Created entry: {entry}")
    
    # Inspect the entry to see what properties it has
    entry_props = dir(entry)
    relevant = [p for p in entry_props if not p.startswith('_')]
    print(f"   Entry properties: {relevant}")
    
    # Try to set properties
    for prop in relevant:
        try:
            value = getattr(entry, prop)
            print(f"     {prop} = {value} (type: {type(value).__name__})")
        except:
            pass
    
    # Try to set the mesh
    print(f"\n4. Setting mesh on entry...")
    success = False
    
    for prop_name in ["mesh", "static_mesh", "descriptor", "mesh_entry"]:
        try:
            setattr(entry, prop_name, grass_mesh)
            print(f"   ✓ Set '{prop_name}' to grass mesh")
            success = True
            break
        except Exception as e:
            print(f"   ✗ '{prop_name}': {e}")
    
    if success:
        # Add entry to mesh_entries
        print(f"\n5. Adding entry to mesh_entries...")
        current_entries = list(mesh_selector.mesh_entries)
        current_entries.append(entry)
        mesh_selector.mesh_entries = current_entries
        print(f"   ✓ Added entry (total entries: {len(mesh_selector.mesh_entries)})")
        
        # Save
        print(f"\n6. Saving graph...")
        saved = unreal.EditorAssetLibrary.save_loaded_asset(pcg_graph)
        print(f"   {'✓' if saved else '✗'} Saved: {saved}")
        
        # Regenerate
        print(f"\n7. Regenerating PCG...")
        all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
        for actor in all_actors:
            if actor.get_class().get_name() == "PCGVolume" and "Stadium_Grass" in actor.get_actor_label():
                for comp in actor.get_components_by_class(unreal.PCGComponent):
                    comp.cleanup_local(True)
                    comp.generate_local(True)
                    print(f"   ✓ Regenerated on {actor.get_actor_label()}")
                    break
                break
        
        print(f"\n" + "=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        print("\n✅ Grass mesh configured successfully!")
        print("Check your viewport for PCG-generated grass.")
    else:
        print(f"\n⚠ Could not set mesh on entry")
        
except Exception as e:
    print(f"✗ Error creating entry: {e}")
    import traceback
    traceback.print_exc()
