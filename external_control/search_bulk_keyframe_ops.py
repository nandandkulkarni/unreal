"""
Search for batch/bulk keyframe operations or different keyframe setting methods
"""
import requests

BASE_URL = "http://localhost:30010/remote"

def describe_object(object_path):
    response = requests.put(
        f"{BASE_URL}/object/describe",
        json={"objectPath": object_path}
    )
    if response.status_code == 200:
        return response.json()
    return None

def main():
    print("=" * 80)
    print("SEARCH FOR BATCH/BULK KEYFRAME OPERATIONS")
    print("=" * 80)
    
    # Check MovieSceneScriptingFloatChannel for all methods
    print("\n[1] All methods on MovieSceneScriptingFloatChannel:")
    info = describe_object("/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel")
    
    if info:
        functions = info.get('Functions', [])
        print(f"    Total functions: {len(functions)}\n")
        for func in functions:
            name = func['Name']
            params = func.get('Parameters', [])
            param_str = ", ".join([p['Name'] for p in params]) if params else "(no params shown)"
            print(f"    - {name}: {param_str}")
    
    # Check if there's SetKeys (plural) or AddKeys
    print("\n[2] Looking for bulk operations...")
    bulk_methods = ['SetKeys', 'AddKeys', 'SetKeyValues', 'SetChannelData', 'SetCurve', 'ImportKeys']
    
    for method in bulk_methods:
        # Check if it exists
        for func in functions:
            if func['Name'].lower() == method.lower():
                print(f"\n  Found: {func['Name']}")
                for param in func.get('Parameters', []):
                    print(f"    - {param['Name']}: {param['Type']}")

if __name__ == "__main__":
    main()
