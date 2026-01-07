"""
Verify PCG Graph Configuration - Check all created objects
"""
import unreal
import sys

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\verify_pcg_config.log"

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
print("VERIFY PCG CONFIGURATION")
print("=" * 80)

GRASS_MESH_PATH = "/Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r/High/tbdpec3r_tier_1/StaticMeshes/SM_tbdpec3r_VarA"

# ==============================================================================
# 1. VERIFY PCG GRAPH EXISTS AND IS VALID
# ==============================================================================
print("\n1. Verifying PCG Graph...")

pcg_assets = unreal.EditorAssetLibrary.list_assets("/Game/PCG", recursive=False)
pcg_graphs = [a for a in pcg_assets if "PCG_StadiumGrass" in a]

if not pcg_graphs:
    print("   ✗ NO PCG GRAPHS FOUND!")
    sys.exit(1)

latest_graph_path = sorted(pcg_graphs)[-1]
print(f"   Graph path: {latest_graph_path}")

pcg_graph = unreal.load_asset(latest_graph_path)
if not pcg_graph:
    print("   ✗ Failed to load graph")
    sys.exit(1)

print(f"   ✓ Graph loaded: {pcg_graph.get_name()}")
print(f"   Graph type: {type(pcg_graph)}")
print(f"   Graph class: {pcg_graph.get_class().get_name()}")

# ==============================================================================
# 2. VERIFY NODES EXIST
# ==============================================================================
print("\n2. Verifying PCG Nodes...")

nodes = pcg_graph.nodes
print(f"   Total nodes: {len(nodes)}")

surface_sampler = None
mesh_spawner = None

for node in nodes:
    settings = node.get_settings()
    settings_type = type(settings).__name__
    print(f"\n   Node: {settings_type}")
    
    if "SurfaceSampler" in settings_type:
        surface_sampler = settings
        print(f"     ✓ Surface Sampler found")
    elif "StaticMeshSpawner" in settings_type:
        mesh_spawner = settings
        print(f"     ✓ Mesh Spawner found")

if not surface_sampler:
    print("\n   ✗ NO SURFACE SAMPLER!")
if not mesh_spawner:
    print("\n   ✗ NO MESH SPAWNER!")

# ==============================================================================
# 3. VERIFY SURFACE SAMPLER CONFIGURATION
# ==============================================================================
if surface_sampler:
    print("\n3. Verifying Surface Sampler Configuration...")
    
    try:
        density = surface_sampler.get_editor_property("points_per_squared_meter")
        print(f"   Density: {density} points/m²")
        
        unbounded = surface_sampler.get_editor_property("unbounded")
        print(f"   Unbounded: {unbounded}")
        
        if density < 1.0:
            print(f"   ⚠ WARNING: Density very low ({density})")
        if not unbounded:
            print(f"   ⚠ WARNING: Not unbounded - needs actors to sample")
            
    except Exception as e:
        print(f"   ✗ Error reading sampler properties: {e}")

# ==============================================================================
# 4. VERIFY MESH SPAWNER CONFIGURATION
# ==============================================================================
if mesh_spawner:
    print("\n4. Verifying Mesh Spawner Configuration...")
    
    try:
        mesh_selector = mesh_spawner.mesh_selector_instance
        print(f"   Mesh selector type: {type(mesh_selector).__name__}")
        
        mesh_entries = mesh_selector.mesh_entries
        print(f"   Mesh entries count: {len(mesh_entries)}")
        
        if len(mesh_entries) == 0:
            print(f"   ✗ NO MESH ENTRIES! Grass cannot spawn without a mesh!")
        else:
            for i, entry in enumerate(mesh_entries):
                print(f"\n   Entry {i}:")
                print(f"     Type: {type(entry)}")
                
                # Try to get descriptor
                try:
                    descriptor = entry.get_editor_property("descriptor")
                    print(f"     Descriptor: {descriptor}")
                    
                    # Try to get mesh from descriptor
                    try:
                        mesh = descriptor.get_editor_property("static_mesh")
                        if mesh:
                            print(f"     ✓ Mesh: {mesh.get_name()}")
                            print(f"     ✓ Mesh path: {mesh.get_path_name()}")
                            
                            # Verify it's the correct mesh
                            if GRASS_MESH_PATH in mesh.get_path_name():
                                print(f"     ✓ CORRECT GRASS MESH!")
                            else:
                                print(f"     ✗ WRONG MESH! Expected {GRASS_MESH_PATH}")
                        else:
                            print(f"     ✗ NO MESH IN DESCRIPTOR!")
                    except Exception as e:
                        print(f"     ✗ Error getting mesh from descriptor: {e}")
                        
                except Exception as e:
                    print(f"     ✗ Error getting descriptor: {e}")
                    
    except Exception as e:
        print(f"   ✗ Error reading spawner properties: {e}")

# ==============================================================================
# 5. VERIFY PCG VOLUME AND COMPONENT
# ==============================================================================
print("\n5. Verifying PCG Volume and Component...")

all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
pcg_volumes = []

for actor in all_actors:
    if actor.get_class().get_name() == "PCGVolume":
        label = actor.get_actor_label()
        if "Test" in label or "Patch" in label:
            pcg_volumes.append(actor)
            print(f"\n   Volume: {label}")
            print(f"     Location: {actor.get_actor_location()}")
            print(f"     Scale: {actor.get_actor_scale3d()}")
            
            # Get component
            for comp in actor.get_components_by_class(unreal.PCGComponent):
                print(f"\n     PCG Component found:")
                
                # Check graph assignment
                try:
                    graph_instance = comp.get_editor_property("graph_instance")
                    print(f"       Graph instance: {graph_instance}")
                except:
                    pass
                
                # Check generation trigger
                try:
                    trigger = comp.get_editor_property("generation_trigger")
                    print(f"       Generation trigger: {trigger}")
                    
                    if trigger != unreal.PCGComponentGenerationTrigger.GENERATE_ON_DEMAND:
                        print(f"       ⚠ WARNING: Trigger not set to GENERATE_ON_DEMAND!")
                except Exception as e:
                    print(f"       Error reading trigger: {e}")
                
                # Check if generated
                try:
                    generated = comp.get_editor_property("generated")
                    print(f"       Generated: {generated}")
                    
                    if not generated:
                        print(f"       ⚠ WARNING: PCG has not generated yet!")
                except:
                    pass

            # Check for generated ISMs (Instanced Static Meshes)
            print(f"\n     Checking for generated Geometry (ISMs/HISMs)...")
            isms = actor.get_components_by_class(unreal.InstancedStaticMeshComponent)
            hisms = actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
            all_mesh_comps = isms + hisms
            
            if not all_mesh_comps:
                print(f"       ✗ NO INSTANCED MESH COMPONENTS FOUND!")
                print(f"         This explains why no grass is visible.")
                print(f"         'Generated: True' means the graph ran, but it produced 0 artifacts.")
            else:
                print(f"       ✓ Found {len(all_mesh_comps)} mesh components")
                for i, mesh_comp in enumerate(all_mesh_comps):
                    count = mesh_comp.get_instance_count()
                    mesh_name = "None"
                    if mesh_comp.static_mesh:
                        mesh_name = mesh_comp.static_mesh.get_name()
                        
                    print(f"         Component {i}: {mesh_comp.get_class().get_name()}")
                    print(f"           Mesh: {mesh_name}")
                    print(f"           Instance Count: {count}")
                    
                    if count == 0:
                        print(f"           ⚠ WARNING: Component has 0 instances!")

if not pcg_volumes:
    print("\n   ✗ NO PCG VOLUMES FOUND!")

# ==============================================================================
# 6. VERIFY GROUND PLANE
# ==============================================================================
print("\n6. Verifying Ground Plane...")

ground_found = False
for actor in all_actors:
    label = actor.get_actor_label()
    if "PCG_Test_Ground" in label:
        ground_found = True
        print(f"   ✓ Ground: {label}")
        print(f"     Location: {actor.get_actor_location()}")
        print(f"     Scale: {actor.get_actor_scale3d()}")
        
        # Check if it has a mesh
        if hasattr(actor, 'static_mesh_component'):
            mesh = actor.static_mesh_component.get_editor_property("static_mesh")
            if mesh:
                print(f"     ✓ Has mesh: {mesh.get_name()}")
            else:
                print(f"     ✗ NO MESH ON GROUND!")

if not ground_found:
    print("   ✗ NO GROUND PLANE FOUND!")
    print("   ⚠ Surface Sampler may not find anything to sample!")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)

print("\nSummary:")
print(f"  PCG Graph: {'✓' if pcg_graph else '✗'}")
print(f"  Surface Sampler: {'✓' if surface_sampler else '✗'}")
print(f"  Mesh Spawner: {'✓' if mesh_spawner else '✗'}")
print(f"  PCG Volumes: {len(pcg_volumes)}")
print(f"  Ground Plane: {'✓' if ground_found else '✗'}")
