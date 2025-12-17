"""
Investigate BakeTransformWithSettings - this might create keyframes from actor positions!
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

def call_function(object_path, function_name, parameters=None):
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

def main():
    print("=" * 80)
    print("INVESTIGATE BakeTransformWithSettings")
    print("=" * 80)
    
    # Get full details
    info = describe_object("/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem")
    
    if not info:
        print("Failed to get info")
        return
    
    functions = info.get('Functions', [])
    
    for func in functions:
        if 'Bake' in func['Name']:
            print(f"\n{func['Name']}:")
            print(f"  Description: {func.get('Description', 'N/A')}")
            print(f"  Return: {func.get('ReturnType', 'void')}")
            print(f"  Parameters:")
            for param in func.get('Parameters', []):
                print(f"    - {param['Name']}: {param['Type']}")
                if 'Description' in param:
                    print(f"        {param['Description']}")
    
    # Try to find what FBakingAnimationKeySettings looks like
    print("\n" + "="*80)
    print("Trying to understand BakingAnimationKeySettings structure...")
    print("="*80)
    
    # Try calling it with empty params to see what it expects
    print("\n[Test Call] Attempting with empty parameters...")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem",
        "BakeTransformWithSettings",
        {}
    )
    
    if not success:
        print(f"  Error (expected): {result[:300]}")
    else:
        print(f"  Unexpected success: {result}")

if __name__ == "__main__":
    main()
