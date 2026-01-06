
import unreal
import os

LOG_FILE = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs\api_reflection.log"

def log(msg):
    unreal.log(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(str(msg) + '\n')

# Create/Clear log file
if not os.path.exists(os.path.dirname(LOG_FILE)):
    os.makedirs(os.path.dirname(LOG_FILE))
with open(LOG_FILE, 'w') as f:
    f.write("API Reflection Log\n")

log("="*50)
log("Unreal Python API Reflection")
log("="*50)

try:
    # Check SplineComponent
    list_properties(unreal.SplineComponent)
    
    # Check Actor component methods
    log("\n--- Actor Component Methods ---")
    actor = unreal.Actor() # Just wrapper reflection
    # Inspect Actor methods related to components
    comp_methods = [m for m in dir(unreal.Actor) if "component" in m.lower()]
    for m in sorted(comp_methods):
        log(m)
        
    log("\n--- EditorLevelLibrary ---")
    list_properties(unreal.EditorLevelLibrary)
    
except Exception as e:
    log(f"Error: {e}")

