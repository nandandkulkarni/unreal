"""
Reflect on PCG Graph connection methods and available nodes
"""
import unreal
import sys

LOG_FILE_PATH = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\reflect_graph_connections.log"

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
print("PCG GRAPH CONNECTION REFLECTION")
print("=" * 80)

# Check PCGGraph methods for adding edges
print("\n1. PCGGraph methods:")
graph_methods = dir(unreal.PCGGraph)
edge_methods = [m for m in graph_methods if 'edge' in m.lower() or 'connect' in m.lower() or 'link' in m.lower()]

for m in edge_methods:
    print(f"  - {m}")
    
# Check for GetActorData settings class
print("\n2. Checking for GetActorData settings:")
classes = [
    "PCGGetActorDataSettings",
    "PCGWorldRayHitSettings", 
    "PCGVolumeSamplerSettings",
    "PCGProjectionSettings"
]

for cls_name in classes:
    cls = unreal.load_class(None, f"/Script/PCG.{cls_name}")
    if cls:
        print(f"  ✓ Found class: {cls_name}")
        # Inspect properties
        try:
            obj = unreal.new_object(cls)
            props = [p for p in dir(obj) if not p.startswith('_')]
            print(f"    Properties: {props[:5]}...")
        except:
            pass
    else:
        # Try struct/object directly
        try:
            cls = getattr(unreal, cls_name)
            print(f"  ✓ Found type via unreal module: {cls_name}")
        except:
            print(f"  ✗ Could not find: {cls_name}")

# Check Surface Sampler pins
print("\n3. Surface Sampler properties (looking for inputs):")
try:
    sampler_cls = unreal.PCGSurfaceSamplerSettings
    # Create temp object to check pins if possible, or just dir()
    temp_sampler = unreal.PCGSurfaceSamplerSettings()
    print(f"  Type: {type(temp_sampler)}")
    # We can't easily check pins without adding to a graph, but we can check properties
    print(f"  Properties: {[p for p in dir(temp_sampler) if not p.startswith('_')]}")
except Exception as e:
    print(f"  Error: {e}")
