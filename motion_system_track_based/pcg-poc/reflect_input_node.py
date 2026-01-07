import unreal
import sys

# Setup logging
log_path = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\reflect_input_node.log"
sys.stdout = open(log_path, 'w', encoding='utf-8')

print("="*80)
print("INSPECTING INPUT NODE IN GRAPH")
print("="*80)

# Load Graph
graph_path = "/Game/PCG/PCG_StadiumGrass_9925.PCG_StadiumGrass_9925"
pcg_graph = unreal.load_asset(graph_path)

if pcg_graph:
    print(f"Graph Loaded: {pcg_graph.get_name()}")
    
    # Kinda duplicate logic but robust finding
    input_node = None
    for node in pcg_graph.nodes:
        if "DataFromActor" in node.get_settings().get_class().get_name() or "GetActorData" in node.get_settings().get_class().get_name():
            input_node = node
            break
            
    if input_node:
        settings = input_node.get_settings()
        print(f"Found Input Node: {settings.get_class().get_name()}")
        
        # properties
        props = [p for p in dir(settings) if not p.startswith('_')]
        
        print("\n--- SETTINGS PROPERTIES ---")
        for p in props:
            try:
                val = getattr(settings, p)
                # If it's the actor_selector struct, print its fields too
                if p == 'actor_selector':
                    print(f"  {p}:")
                    s_props = [sp for sp in dir(val) if not sp.startswith('_')]
                    for sp in s_props:
                        try:
                            s_val = getattr(val, sp)
                            print(f"    - {sp}: {s_val}")
                        except:
                            pass
                else:
                    print(f"  {p}: {val}")
            except Exception as e:
                print(f"  {p}: <error: {e}>")

    else:
        print("Input Node NOT Found in graph!")
else:
    print(f"Could not load graph at {graph_path}")
