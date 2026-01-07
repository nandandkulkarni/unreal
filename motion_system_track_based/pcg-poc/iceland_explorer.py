"""
Iceland Environment Asset Explorer
Discovers and lists all assets in the Iceland_Environment pack
"""
import unreal
import sys
import datetime

# ==============================================================================
# LOGGING SETUP
# ==============================================================================
LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\iceland_explorer.log"

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

def log(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

print("=" * 80)
log("ICELAND ENVIRONMENT ASSET EXPLORER")
print("=" * 80)

# ==============================================================================
# ASSET DISCOVERY
# ==============================================================================
def explore_iceland_assets():
    """Discover all assets in Iceland_Environment folder"""
    log("\nSearching Iceland_Environment assets...")
    
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    # Search in Iceland_Environment folder
    filter = unreal.ARFilter(
        package_paths=["/Game/Iceland_Environment"],
        recursive_paths=True
    )
    
    all_assets = asset_registry.get_assets(filter)
    
    # Categorize by type
    static_meshes = []
    materials = []
    textures = []
    landscapes = []
    foliage = []
    other = []
    
    for asset_data in all_assets:
        asset_class = str(asset_data.asset_class)
        asset_path = str(asset_data.package_name)
        asset_name = str(asset_data.asset_name)
        
        if asset_class == "StaticMesh":
            static_meshes.append((asset_name, asset_path))
        elif asset_class in ["Material", "MaterialInstance", "MaterialInstanceConstant"]:
            materials.append((asset_name, asset_path))
        elif asset_class in ["Texture2D", "TextureRenderTarget2D"]:
            textures.append((asset_name, asset_path))
        elif asset_class == "LandscapeGrassType":
            foliage.append((asset_name, asset_path))
        elif "Landscape" in asset_class:
            landscapes.append((asset_name, asset_path))
        else:
            other.append((asset_name, asset_class, asset_path))
    
    # Print results
    print("\n" + "=" * 80)
    print("ICELAND ENVIRONMENT ASSETS")
    print("=" * 80)
    
    print(f"\n📦 STATIC MESHES ({len(static_meshes)}):")
    for name, path in static_meshes[:20]:  # Show first 20
        print(f"  • {name}")
        print(f"    Path: {path}")
    if len(static_meshes) > 20:
        print(f"  ... and {len(static_meshes) - 20} more")
    
    print(f"\n🎨 MATERIALS ({len(materials)}):")
    for name, path in materials[:10]:
        print(f"  • {name}")
        print(f"    Path: {path}")
    if len(materials) > 10:
        print(f"  ... and {len(materials) - 10} more")
    
    print(f"\n🖼️  TEXTURES ({len(textures)}):")
    print(f"  Total: {len(textures)} textures")
    
    print(f"\n🌿 FOLIAGE ({len(foliage)}):")
    for name, path in foliage:
        print(f"  • {name}")
        print(f"    Path: {path}")
    
    print(f"\n🏔️  LANDSCAPES ({len(landscapes)}):")
    for name, path in landscapes:
        print(f"  • {name}")
        print(f"    Path: {path}")
    
    if other:
        print(f"\n📋 OTHER ASSETS ({len(other)}):")
        for name, asset_class, path in other[:10]:
            print(f"  • {name} ({asset_class})")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Assets Found: {len(all_assets)}")
    print(f"  • Static Meshes: {len(static_meshes)}")
    print(f"  • Materials: {len(materials)}")
    print(f"  • Textures: {len(textures)}")
    print(f"  • Foliage: {len(foliage)}")
    print(f"  • Landscapes: {len(landscapes)}")
    print(f"  • Other: {len(other)}")
    
    # Save useful paths for later scripts
    print("\n" + "=" * 80)
    print("USEFUL ASSET PATHS (for Python scripts)")
    print("=" * 80)
    
    if static_meshes:
        print("\nExample Static Mesh:")
        print(f'  "{static_meshes[0][1]}"')
    
    if materials:
        print("\nExample Material:")
        print(f'  "{materials[0][1]}"')
    
    if foliage:
        print("\nFoliage Assets:")
        for name, path in foliage:
            print(f'  "{path}"')
    
    return {
        'static_meshes': static_meshes,
        'materials': materials,
        'textures': textures,
        'foliage': foliage,
        'landscapes': landscapes
    }

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
try:
    assets = explore_iceland_assets()
    
    print("\n" + "=" * 80)
    print("✓ EXPLORATION COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Review the asset list above")
    print("  2. Use the asset paths in Python scripts")
    print("  3. Ready to create foliage placement script!")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
