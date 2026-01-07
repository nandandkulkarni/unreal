import unreal
import sys

log_path = r"C:\UnrealProjects\coding\unreal\motion_system_track_based\pcg-poc\debug_enums.log"
sys.stdout = open(log_path, 'w', encoding='utf-8')

print("Checking PCGActorFilter...")
try:
    e = unreal.PCGActorFilter
    print(f"Enum Class: {e}")
    print("Values:")
    for x in dir(e):
        if x.isupper():
             val = getattr(e, x)
             print(f"  {x}: {val}")
except Exception as ex:
    print(f"Error: {ex}")
