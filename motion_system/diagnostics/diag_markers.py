import unreal

def check_markers():
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    markers = [a for a in actors if a.tags.count("MotionSystemDebug") > 0]
    
    print(f"Found {len(markers)} markers:")
    for m in markers:
        loc = m.get_actor_location()
        label = m.get_actor_label()
        print(f"  - {label} at {loc}")
        
    if len(markers) == 0:
        print("No markers found! Check if they are being filtered or not spawned.")

check_markers()
