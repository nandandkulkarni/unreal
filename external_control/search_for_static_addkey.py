"""
Check if there are any static/helper methods that can add keys
by taking primitives (section path + channel name + keyframe data)
"""
import requests
import json

BASE_URL = "http://localhost:30010/remote"

def describe_object(path):
    result = requests.put(f"{BASE_URL}/object/describe", json={"objectPath": path})
    return result.json() if result.status_code == 200 else None

# Check various subsystems for helper methods
subsystems = [
    "/Script/SequencerScripting.Default__SequencerTools",
    "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem",
    "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
]

for subsystem in subsystems:
    print(f"\n{'='*80}")
    print(f"Checking: {subsystem.split('.')[-1]}")
    print('='*80)
    
    info = describe_object(subsystem)
    if not info:
        print("  Failed to describe")
        continue
    
    funcs = info.get('Functions', [])
    
    # Look for anything related to keys
    key_funcs = [f for f in funcs if 'key' in f['Name'].lower()]
    
    if key_funcs:
        print(f"\n  Found {len(key_funcs)} key-related methods:")
        for func in key_funcs[:10]:
            params = func.get('Parameters', [])
            param_str = ', '.join([f"{p['Name']}:{p['Type']}" for p in params])
            print(f"    - {func['Name']}({param_str})")
    else:
        print("  No key-related methods found")
