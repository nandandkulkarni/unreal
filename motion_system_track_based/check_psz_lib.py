import unreal
OUTPUT = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\aaank_lib_check.txt"
try:
    avail = hasattr(unreal, 'AAANKPoseBlueprintLibrary')
    msg = f"AAANKPoseBlueprintLibrary available: {avail}"
    if avail:
        msg += f"\nMethods: {dir(unreal.AAANKPoseBlueprintLibrary)}"
    
    with open(OUTPUT, 'w') as f: f.write(msg)
except Exception as e:
    with open(OUTPUT, 'w') as f: f.write(f"Error: {e}")
