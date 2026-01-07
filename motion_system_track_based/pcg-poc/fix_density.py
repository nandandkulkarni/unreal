"""
Fix PCG Grass Density
Increase Surface Sampler points per square meter
"""
import unreal
import sys

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\fix_density.log"

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
print("FIX PCG GRASS DENSITY")
print("=" * 80)

# Target density (points per square meter)
TARGET_DENSITY = 25.0  # 25 grass instances per square meter = good coverage

# Load graph
pcg_assets = unreal.EditorAssetLibrary.list_assets("/Game/PCG", recursive=False)
pcg_graphs = [a for a in pcg_assets if "PCG_StadiumGrass" in a]
latest_graph_path = sorted(pcg_graphs)[-1]

print(f"\n1. Loading: {latest_graph_path}")
pcg_graph = unreal.load_asset(latest_graph_path)

# Find surface sampler
nodes = pcg_graph.nodes
surface_sampler = None

for node in nodes:
    settings = node.get_settings()
    if "SurfaceSampler" in type(settings).__name__:
        surface_sampler = settings
        break

if not surface_sampler:
    print("✗ No Surface Sampler found")
    sys.exit(1)

print("✓ Found Surface Sampler")

# Check current density
current_density = surface_sampler.get_editor_property("points_per_squared_meter")
print(f"\n2. Current density: {current_density} points/m²")

# Set new density
print(f"\n3. Setting density to {TARGET_DENSITY} points/m²...")
surface_sampler.set_editor_property("points_per_squared_meter", TARGET_DENSITY)

# Verify
new_density = surface_sampler.get_editor_property("points_per_squared_meter")
print(f"   ✓ New density: {new_density} points/m²")

# Calculate expected points
# Stadium is roughly 200m x 100m = 20,000 m²
expected_points = 20000 * new_density
print(f"   Expected grass instances: ~{int(expected_points):,}")

# Save graph
print(f"\n4. Saving graph...")
saved = unreal.EditorAssetLibrary.save_loaded_asset(pcg_graph)
print(f"   {'✓' if saved else '✗'} Saved")

# Regenerate PCG
print(f"\n5. Regenerating PCG...")
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
print(f"\n✅ Density increased from {current_density} to {new_density} points/m²")
print(f"🌱 Check your viewport - grass should now be visible!")
print(f"\nNote: If grass is too dense or sparse, adjust TARGET_DENSITY in the script")
print(f"  - Sparse grass: 5-10 points/m²")
print(f"  - Medium grass: 15-25 points/m²")
print(f"  - Dense grass: 30-50 points/m²")
