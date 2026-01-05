"""
Diagnostic: List all available functions in AAANKPoseBlueprintLibrary

This will show us exactly what functions are accessible from Python.
"""

import unreal
import os
from datetime import datetime

LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc"
LOG_FILE = os.path.join(LOG_DIR, "diagnostic_functions.log")

def log(message):
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def diagnose():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    
    log("=" * 80)
    log("DIAGNOSTIC: AAANKPoseBlueprintLibrary Functions")
    log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 80)
    log("")
    
    try:
        lib = unreal.AAANKPoseBlueprintLibrary
        log(f"✓ Library class found: {lib}")
        log("")
        
        log("All available attributes and methods:")
        log("-" * 80)
        
        all_members = dir(lib)
        public_members = [m for m in all_members if not m.startswith('_')]
        
        log(f"Total public members: {len(public_members)}")
        log("")
        
        for i, member in enumerate(public_members, 1):
            try:
                attr = getattr(lib, member)
                log(f"{i:3d}. {member:40s} - {type(attr)}")
            except Exception as e:
                log(f"{i:3d}. {member:40s} - Error: {e}")
        
        log("")
        log("=" * 80)
        log("Looking specifically for PoseSearch functions...")
        log("=" * 80)
        
        pose_functions = [m for m in public_members if 'animation' in m.lower() or 
                         'database' in m.lower() or 'pose' in m.lower() or 
                         'build' in m.lower() or 'clear' in m.lower()]
        
        if pose_functions:
            log(f"\nFound {len(pose_functions)} potential PoseSearch-related functions:")
            for func in pose_functions:
                log(f"  - {func}")
        else:
            log("\n❌ No PoseSearch-related functions found")
            log("\nThis means:")
            log("1. Plugin did not compile successfully")
            log("2. OR Unreal Editor was not restarted after compilation")
            log("3. OR there were C++ compilation errors")
        
        log("")
        log(f"Full diagnostic saved to: {LOG_FILE}")
        
    except Exception as e:
        log(f"✗ Error accessing library: {e}")

if __name__ == "__main__":
    diagnose()
