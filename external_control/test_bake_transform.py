"""
Test BakeTransformWithSettings - this might be the missing piece!
This could record actor positions into sequence keyframes
"""
import requests
import json

BASE_URL = "http://localhost:30010/remote"

def call_function(object_path, function_name, parameters=None):
    """Call Unreal function via Remote Control API"""
    payload = {
        "objectPath": object_path,
        "functionName": function_name,
        "parameters": parameters or {}
    }
    
    response = requests.put(f"{BASE_URL}/object/call", json=payload)
    
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text

def describe_bake_transform():
    """Get info about BakeTransformWithSettings"""
    print("=" * 80)
    print("BakeTransformWithSettings function details")
    print("=" * 80)
    
    response = requests.put(
        f"{BASE_URL}/object/describe",
        json={"objectPath": "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem"}
    )
    
    if response.status_code == 200:
        info = response.json()
        functions = info.get('Functions', [])
        
        for func in functions:
            if 'Bake' in func['Name']:
                print(f"\n{func['Name']}:")
                print(f"  Description: {func.get('Description', 'N/A')}")
                print("  Parameters:")
                for param in func.get('Parameters', []):
                    print(f"    - {param['Name']}: {param['Type']}")
                print(f"  Returns: {func.get('ReturnType', 'void')}")

if __name__ == "__main__":
    describe_bake_transform()
