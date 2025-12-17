"""
Search for static extensions that can add keys to channels
The key insight: we need STATIC methods that take channel as parameter, not instance methods
"""
import requests
import json

BASE_URL = "http://localhost:30010/remote"

def describe_object(object_path):
    """Get all methods on an object"""
    response = requests.put(
        f"{BASE_URL}/object/describe",
        json={"objectPath": object_path}
    )
    
    if response.status_code == 200:
        return response.json()
    return None

def main():
    print("=" * 80)
    print("SEARCHING FOR STATIC CHANNEL METHODS")
    print("=" * 80)
    
    # Check various extension classes
    extension_classes = [
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "/Script/SequencerScripting.Default__MovieSceneTrackExtensions",
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "/Script/SequencerScripting.Default__MovieSceneBindingExtensions",
    ]
    
    for class_path in extension_classes:
        print(f"\n{'='*80}")
        print(f"Class: {class_path.split('.')[-1]}")
        print(f"{'='*80}")
        
        info = describe_object(class_path)
        if not info:
            print("  [X] Failed to describe")
            continue
        
        functions = info.get('Functions', [])
        
        # Look for functions related to keys, values, or channels
        relevant_functions = []
        for func in functions:
            name = func['Name']
            if any(keyword in name.lower() for keyword in ['key', 'value', 'channel', 'transform', 'location', 'rotation']):
                relevant_functions.append(func)
        
        if relevant_functions:
            print(f"  Found {len(relevant_functions)} relevant functions:")
            for func in relevant_functions:
                print(f"\n  {func['Name']}:")
                params = func.get('Parameters', [])
                if params:
                    print(f"    Parameters:")
                    for param in params:
                        print(f"      - {param['Name']}: {param['Type']}")
                else:
                    print(f"    (no parameters)")
                ret = func.get('ReturnType', 'void')
                if ret != 'void':
                    print(f"    Returns: {ret}")
        else:
            print("  No relevant functions found")

if __name__ == "__main__":
    main()
