"""
Check if MovieSceneScriptingFloatChannel or related classes have STATIC extension methods
Key insight: In Unreal, scripting extensions are STATIC helper classes
"""
import requests

BASE_URL = "http://localhost:30010/remote"

def try_describe(object_path):
    """Try to describe an object"""
    response = requests.put(
        f"{BASE_URL}/object/describe",
        json={"objectPath": object_path}
    )
    
    if response.status_code == 200:
        return True, response.json()
    return False, response.text

def main():
    print("=" * 80)
    print("SEARCHING FOR CHANNEL EXTENSION CLASSES")
    print("=" * 80)
    
    # Try various possible paths for channel extensions
    possible_paths = [
        "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
        "/Script/SequencerScripting.Default__MovieSceneScriptingChannel",
        "/Script/SequencerScripting.Default__MovieSceneScriptingChannelExtensions",
        "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannelExtensions",
        "/Script/SequencerScripting.Default__MovieSceneScriptingKeyExtensions",
        "/Script/SequencerScripting.MovieSceneScriptingFloatChannel",
        "/Script/SequencerScripting.MovieSceneScriptingChannel",
    ]
    
    for path in possible_paths:
        print(f"\n{'-'*80}")
        print(f"Trying: {path}")
        print(f"{'-'*80}")
        
        success, result = try_describe(path)
        
        if success:
            print(f"  ✓ EXISTS!")
            functions = result.get('Functions', [])
            print(f"  Functions: {len(functions)}")
            
            # Look for AddKey or similar
            for func in functions:
                name = func['Name']
                if 'add' in name.lower() or 'key' in name.lower():
                    print(f"\n  {name}:")
                    params = func.get('Parameters', [])
                    for param in params:
                        print(f"    - {param['Name']}: {param['Type']}")
        else:
            if "does not exist" in str(result):
                print(f"  [X] Does not exist")
            else:
                print(f"  [X] Error: {result[:100]}")

if __name__ == "__main__":
    main()
