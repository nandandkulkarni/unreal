"""
Search for higher-level APIs that set keyframes without needing channel handles
Maybe there are transform-specific or binding-specific methods
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
    print("SEARCH FOR HIGH-LEVEL KEYFRAME APIS")
    print("=" * 80)
    
    # Check binding extensions for transform-specific methods
    print("\n[1] MovieSceneBindingExtensions:")
    info = describe_object("/Script/SequencerScripting.Default__MovieSceneBindingExtensions")
    if info:
        functions = info.get('Functions', [])
        for func in functions:
            name = func['Name']
            if any(kw in name.lower() for kw in ['transform', 'location', 'rotation', 'key', 'set']):
                print(f"  ✓ {name}")
                params = func.get('Parameters', [])
                if params:
                    for p in params:
                        print(f"      {p['Name']}: {p['Type']}")
    
    # Check if there's a MovieScene3DTransformSection with special methods
    print("\n[2] MovieScene3DTransformSection (if exposed):")
    section_types = [
        "/Script/MovieSceneTracks.Default__MovieScene3DTransformSection",
        "/Script/MovieSceneTracks.MovieScene3DTransformSection",
    ]
    for path in section_types:
        info = describe_object(path)
        if info:
            print(f"  Found: {path}")
            functions = info.get('Functions', [])
            relevant = [f for f in functions if any(kw in f['Name'].lower() for kw in ['key', 'transform', 'location'])]
            for func in relevant:
                print(f"    ✓ {func['Name']}")
    
    # Check LevelSequenceEditorBlueprintLibrary for recording/keying
    print("\n[3] LevelSequenceEditorBlueprintLibrary:")
    info = describe_object("/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary")
    if info:
        functions = info.get('Functions', [])
        for func in functions:
            name = func['Name']
            if any(kw in name.lower() for kw in ['key', 'record', 'bake', 'set']):
                print(f"  ✓ {name}")
                params = func.get('Parameters', [])
                if params:
                    for p in params[:3]:  # First 3 params
                        print(f"      {p['Name']}: {p['Type']}")
    
    # Check LevelSequenceEditorSubsystem
    print("\n[4] LevelSequenceEditorSubsystem:")
    info = describe_object("/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem")
    if info:
        functions = info.get('Functions', [])
        for func in functions:
            name = func['Name']
            if any(kw in name.lower() for kw in ['key', 'record', 'bake', 'transform', 'snap']):
                print(f"  ✓ {name}")
                params = func.get('Parameters', [])
                if params:
                    for p in params:
                        print(f"      {p['Name']}: {p['Type']}")

if __name__ == "__main__":
    main()
