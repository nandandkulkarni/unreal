

import unreal
import inspect
import sys

LOG_PATH = "c:/UnrealProjects/coding/unreal/motion_system_track_based/pcg-poc/inspect.log"

def log(msg):
    print(f"[INSPECT] {msg}")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")
    
# Clear log
with open(LOG_PATH, "w") as f:
    f.write("Inspection Start\n")


log("=== Unreal Python API Inspection ===")

# 1. Check Component Creation Method
log("Checking ComponentCreationMethod...")
if hasattr(unreal, "ComponentCreationMethod"):
    log("  unreal.ComponentCreationMethod EXISTS")
    for x in dir(unreal.ComponentCreationMethod):
        if not x.startswith("_"):
            log(f"    {x}")
else:
    log("  unreal.ComponentCreationMethod DOES NOT EXIST")
    # Search for anything similar
    for x in dir(unreal):
        if "CreationMethod" in x:
            log(f"    Found similar: {x}")

# 2. Check StaticMeshActor methods for adding components
log("\nChecking StaticMeshActor component methods...")
actor_cls = unreal.StaticMeshActor
methods = dir(actor_cls)
for m in methods:
    if "component" in m.lower() and ("add" in m.lower() or "attach" in m.lower()):
        log(f"  {m}")

# 3. Check correct way to add component
log("\nChecking Actor.add_instance_component...")
if hasattr(unreal.Actor, "add_instance_component"):
    log("  unreal.Actor.add_instance_component EXISTS")
else:
    log("  unreal.Actor.add_instance_component DOES NOT EXIST")

log("\nChecking Attachment Rules...")
if hasattr(unreal, "AttachmentTransformRules"):
    log("  unreal.AttachmentTransformRules EXISTS")
else:
    log("  unreal.AttachmentTransformRules DOES NOT EXIST")

if hasattr(unreal, "AttachmentRule"):
    log("  unreal.AttachmentRule EXISTS")
    for x in dir(unreal.AttachmentRule):
        if not x.startswith("_"):
            log(f"    {x}")

log("\nInspection Complete.")
