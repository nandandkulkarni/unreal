"""
Asset Finder
Finds Static Meshes in a given package path
"""
import unreal
import sys

LOG_FILE = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\find_grass_mesh.log"
sys.stdout = open(LOG_FILE, 'w', encoding='utf-8')

# Search in the parent folder of the material
SEARCH_PATH = "/Game/Fab/Megascans/Plants/Ribbon_Grass_tbdpec3r"

print(f"Searching in: {SEARCH_PATH}")

asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()
filter = unreal.FARFilter()
filter.package_paths = [unreal.Name(SEARCH_PATH)]
filter.recursive_paths = True
filter.class_names = [unreal.Name("StaticMesh")]

assets = asset_reg.get_assets(filter)

print(f"Found {len(assets)} Static Meshes:")
for asset in assets:
    # Print Full Path
    print(f"  {asset.package_name}.{asset.asset_name}")

if len(assets) > 0:
    # Save the first one to a file for easy reading by next script
    with open(r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\grass_mesh_path.txt", "w") as f:
        f.write(str(assets[0].package_name) + "." + str(assets[0].asset_name))
