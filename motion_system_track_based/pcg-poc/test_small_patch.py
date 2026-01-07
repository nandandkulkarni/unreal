"""
Create Small Test PCG Patch (10m x 10m)
Test grass generation on a small area first
"""
import unreal
import sys

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\test_small_patch.log"

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
print("CREATE SMALL TEST PCG PATCH (10m x 10m)")
print("=" * 80)

try:
    # Test parameters
    TEST_SIZE = 10.0  # 10 meters
    TEST_DENSITY = 25.0  # 25 points/m² = 2,500 grass instances for 100m²

    # ==============================================================================
    # 1. UPDATE SURFACE SAMPLER DENSITY
    # ==============================================================================
    print("\n1. Setting Surface Sampler density...")

    pcg_assets = unreal.EditorAssetLibrary.list_assets("/Game/PCG", recursive=False)
    pcg_graphs = [a for a in pcg_assets if "PCG_StadiumGrass" in a]
    
    if not pcg_graphs:
        print("✗ No PCG graphs found!")
        sys.exit(1)
    
    latest_graph_path = sorted(pcg_graphs)[-1]
    print(f"   Loading: {latest_graph_path}")

    pcg_graph = unreal.load_asset(latest_graph_path)
    if not pcg_graph:
        print("✗ Failed to load graph")
        sys.exit(1)

    # Find surface sampler
    nodes = pcg_graph.nodes
    surface_sampler = None

    for node in nodes:
        settings = node.get_settings()
        if "SurfaceSampler" in type(settings).__name__:
            surface_sampler = settings
            break

    if surface_sampler:
        surface_sampler.set_editor_property("points_per_squared_meter", TEST_DENSITY)
        print(f"   ✓ Set density to {TEST_DENSITY} points/m²")
        
        # Save graph
        unreal.EditorAssetLibrary.save_loaded_asset(pcg_graph)
        print(f"   ✓ Saved graph")
    else:
        print("   ✗ No Surface Sampler found")

    # ==============================================================================
    # 2. CREATE SMALL TEST VOLUME
    # ==============================================================================
    print(f"\n2. Creating test PCG Volume ({TEST_SIZE}m x {TEST_SIZE}m)...")

    pcg_vol_cls = unreal.load_class(None, "/Script/PCG.PCGVolume")
    if not pcg_vol_cls:
        print("   ✗ Could not load PCGVolume class")
        sys.exit(1)
    
    test_volume = unreal.EditorLevelLibrary.spawn_actor_from_class(
        pcg_vol_cls,
        unreal.Vector(0, 0, 100)  # Center of stadium
    )

    if not test_volume:
        print("   ✗ Failed to spawn test volume")
        sys.exit(1)

    test_volume.set_actor_label("Test_Grass_Patch_10x10")
    test_volume.set_folder_path(unreal.Name("OvalTrack/PCG"))

    # Scale: 10m x 10m x 10m
    scale = TEST_SIZE  # 10m = scale of 10
    test_volume.set_actor_scale3d(unreal.Vector(scale, scale, scale))

    print(f"   ✓ Created test volume at (0, 0, 100)")
    print(f"   ✓ Size: {TEST_SIZE}m x {TEST_SIZE}m")

    # ==============================================================================
    # 3. ASSIGN GRAPH TO TEST VOLUME
    # ==============================================================================
    print(f"\n3. Assigning PCG Graph...")

    test_comp = None
    for comp in test_volume.get_components_by_class(unreal.PCGComponent):
        test_comp = comp
        break

    if test_comp:
        test_comp.set_graph(pcg_graph)
        print(f"   ✓ Assigned graph to test volume")
        
        # Generate
        print(f"\n4. Generating test patch...")
        test_comp.generate_local(True)
        print(f"   ✓ Generation triggered!")
        
        # Calculate expected instances
        area = TEST_SIZE * TEST_SIZE
        expected = int(area * TEST_DENSITY)
        print(f"\n   Expected grass instances: ~{expected:,}")
        print(f"   (Area: {area}m² × Density: {TEST_DENSITY} points/m²)")
    else:
        print("   ✗ No PCG Component found on test volume")

    print(f"\n" + "=" * 80)
    print("TEST PATCH CREATED!")
    print("=" * 80)
    print(f"\n✅ Small 10m x 10m test patch created at center (0, 0)")
    print(f"🌱 Check your viewport for grass!")
    print(f"\nIf you see grass:")
    print(f"  - Adjust density if needed (currently {TEST_DENSITY} points/m²)")
    print(f"  - Scale up to full stadium using fix_density.py")
    print(f"\nIf no grass:")
    print(f"  - Check that test volume overlaps stadium ground")
    print(f"  - Try increasing density further")

except Exception as e:
    print(f"\n" + "=" * 80)
    print("ERROR!")
    print("=" * 80)
    print(f"\n✗ Exception: {e}")
    import traceback
    traceback.print_exc()
    print(f"\nScript failed - see error above")
