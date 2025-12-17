"""
Get the FULL signature of AddKey on the Default__ class
This might be a STATIC version we can use!
"""
import requests
import json

BASE_URL = "http://localhost:30010/remote"

def describe_object(object_path):
    """Get detailed info"""
    response = requests.put(
        f"{BASE_URL}/object/describe",
        json={"objectPath": object_path}
    )
    
    if response.status_code == 200:
        return response.json()
    return None

def main():
    print("=" * 80)
    print("GET ADDKEY METHOD SIGNATURE")
    print("=" * 80)
    
    class_path = "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel"
    
    info = describe_object(class_path)
    
    if not info:
        print("Failed to describe")
        return
    
    functions = info.get('Functions', [])
    
    for func in functions:
        if func['Name'] == 'AddKey':
            print(f"\nAddKey Method Details:")
            print(f"  Return Type: {func.get('ReturnType', 'void')}")
            print(f"\n  Parameters:")
            for param in func.get('Parameters', []):
                print(f"    - {param['Name']}")
                print(f"      Type: {param['Type']}")
                if 'Description' in param:
                    print(f"      Description: {param['Description']}")
            break
    
    # Print ALL functions for context
    print(f"\n\nAll Functions on this class:")
    for func in functions:
        print(f"  - {func['Name']}")

if __name__ == "__main__":
    main()
