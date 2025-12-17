"""
Enumerate available functions on LevelSequenceEditorBlueprintLibrary
to find the correct method for playing sequences
"""

import requests
import json

UNREAL_URL = "http://localhost:30010/remote/object/describe"

def describe_object(object_path):
    """Get all available functions/properties on an object"""
    
    payload = {
        "objectPath": object_path
    }
    
    try:
        response = requests.put(UNREAL_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("=" * 80)
    print("ENUMERATING LEVEL SEQUENCE FUNCTIONS")
    print("=" * 80)
    
    # Objects to check
    objects = [
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "/Script/SequencerScripting.Default__SequencerTools",
        "/Script/LevelSequence.Default__LevelSequencePlayer"
    ]
    
    for obj_path in objects:
        print(f"\n{'=' * 80}")
        print(f"Object: {obj_path}")
        print('=' * 80)
        
        result = describe_object(obj_path)
        
        if "error" in result:
            print(f"✗ Error: {result['error']}")
        else:
            print(json.dumps(result, indent=2))
            
            # Extract and display functions
            if "Functions" in result:
                print("\n--- Available Functions ---")
                for func in result["Functions"]:
                    print(f"  • {func['Name']}")
            
            if "Properties" in result:
                print("\n--- Available Properties ---")
                for prop in result["Properties"]:
                    print(f"  • {prop['Name']}")

if __name__ == "__main__":
    print("\nMake sure:")
    print("  1. Unreal Engine is running")
    print("  2. WebControl.StartServer is active")
    print()
    
    main()
