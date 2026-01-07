"""
Diagnose Why PCG Grass Isn't Appearing
"""
import unreal
import sys

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\diagnose_no_grass.log"

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
print("DIAGNOSE: WHY NO GRASS?")
print("=" * 80)

# ==============================================================================
# 1. CHECK PCG VOLUME
# ==============================================================================
print("\n1. Checking PCG Volume...")

all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
pcg_volume = None

for actor in all_actors:
    if actor.get_class().get_name() == "PCGVolume" and "Stadium_Grass" in actor.get_actor_label():
        pcg_volume = actor
        break

if not pcg_volume:
    print("✗ No PCG Volume found!")
else:
    print(f"✓ Found: {pcg_volume.get_actor_label()}")
    print(f"  Location: {pcg_volume.get_actor_location()}")
    print(f"  Scale: {pcg_volume.get_actor_scale3d()}")
    print(f"  Rotation: {pcg_volume.get_actor_rotation()}")
    
    # Get bounds
    bounds = pcg_volume.get_actor_bounds(False)
    print(f"  Bounds Origin: {bounds[0]}")
    print(f"  Bounds Extent: {bounds[1]}")

# ==============================================================================
# 2. CHECK STADIUM GROUND ACTORS
# ==============================================================================
print("\n2. Checking Stadium Ground actors...")

stadium_actors = []
for actor in all_actors:
    if "Stadium_Ground" in actor.get_actor_label():
        stadium_actors.append(actor)
        print(f"  ✓ {actor.get_actor_label()}")
        print(f"    Location: {actor.get_actor_location()}")
        print(f"    Bounds: {actor.get_actor_bounds(False)}")

if not stadium_actors:
    print("  ✗ No stadium ground actors found!")

# ==============================================================================
# 3. CHECK PCG COMPONENT
# ==============================================================================
print("\n3. Checking PCG Component...")

if pcg_volume:
    pcg_comp = None
    for comp in pcg_volume.get_components_by_class(unreal.PCGComponent):
        pcg_comp = comp
        break
    
    if pcg_comp:
        print(f"  ✓ Found PCG Component")
        
        # Check graph assignment
        graph_instance = pcg_comp.get_editor_property("graph_instance")
        print(f"  Graph Instance: {graph_instance}")
        
        # Check if generated
        is_generated = pcg_comp.get_editor_property("generated")
        print(f"  Generated: {is_generated}")
        
        # Check generation settings
        print(f"\n  Component properties:")
        props_to_check = ["generate_on_load", "is_partitioned", "serialization_mode"]
        for prop in props_to_check:
            try:
                value = pcg_comp.get_editor_property(prop)
                print(f"    {prop}: {value}")
            except:
                pass
    else:
        print("  ✗ No PCG Component found")

# ==============================================================================
# 4. CHECK PCG GRAPH CONFIGURATION
# ==============================================================================
print("\n4. Checking PCG Graph configuration...")

pcg_assets = unreal.EditorAssetLibrary.list_assets("/Game/PCG", recursive=False)
pcg_graphs = [a for a in pcg_assets if "PCG_StadiumGrass" in a]
if pcg_graphs:
    latest_graph_path = sorted(pcg_graphs)[-1]
    pcg_graph = unreal.load_asset(latest_graph_path)
    
    print(f"  ✓ Graph: {pcg_graph.get_name()}")
    
    # Check nodes
    nodes = pcg_graph.nodes
    print(f"  Total nodes: {len(nodes)}")
    
    for node in nodes:
        settings = node.get_settings()
        settings_type = type(settings).__name__
        print(f"\n  Node: {settings_type}")
        
        if "SurfaceSampler" in settings_type:
            # Check surface sampler settings
            print(f"    Checking Surface Sampler settings...")
            sampler_props = ["points_per_squared_meter", "point_extent_min", "unbounded"]
            for prop in sampler_props:
                try:
                    value = settings.get_editor_property(prop)
                    print(f"      {prop}: {value}")
                except:
                    pass
        
        elif "StaticMeshSpawner" in settings_type:
            # Check mesh spawner
            mesh_selector = settings.mesh_selector_instance
            mesh_entries = mesh_selector.mesh_entries
            print(f"    Mesh entries count: {len(mesh_entries)}")
            
            if len(mesh_entries) > 0:
                entry = mesh_entries[0]
                descriptor = entry.get_editor_property("descriptor")
                mesh = descriptor.get_editor_property("static_mesh")
                print(f"    ✓ Mesh configured: {mesh.get_name() if mesh else 'None'}")
            else:
                print(f"    ✗ No mesh entries!")

# ==============================================================================
# 5. FORCE REGENERATION
# ==============================================================================
print("\n5. Forcing PCG regeneration...")

if pcg_volume and pcg_comp:
    print("  Cleaning up...")
    pcg_comp.cleanup_local(True)
    
    print("  Generating...")
    pcg_comp.generate_local(True)
    
    print("  ✓ Regeneration triggered")
    print("\n  Check viewport now!")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
print("\nPossible issues if still no grass:")
print("1. PCG Volume doesn't overlap stadium ground")
print("2. Surface Sampler density too low")
print("3. PCG Component not set to generate")
print("4. Stadium ground actors not being sampled")
