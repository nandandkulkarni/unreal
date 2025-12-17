"""
Find available Movie Pipeline objects/subsystems via Remote Control
"""

import requests
import json

REMOTE_CONTROL_URL = "http://localhost:30010/remote"

def search_for_movie_pipeline():
    """Search for Movie Pipeline related objects"""
    
    print("Searching for Movie Pipeline objects...\n")
    
    # Try different object path patterns
    test_paths = [
        # Subsystems
        "/Script/MovieRenderPipelineCore.Default__MoviePipelineQueueSubsystem",
        "/Script/UnrealEd.Default__MoviePipelineQueueSubsystem",
        "/Engine/Transient.MoviePipelineQueueSubsystem",
        "/Engine/Subsystems/MoviePipelineQueueSubsystem",
        
        # Try accessing via EditorSubsystem
        "/Script/UnrealEd.Default__EditorSubsystem",
        
        # Try the sequence editor
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem",
    ]
    
    for path in test_paths:
        print(f"Trying: {path}")
        url = f"{REMOTE_CONTROL_URL}/object/describe"
        payload = {"objectPath": path}
        
        try:
            response = requests.put(url, json=payload)
            if response.status_code == 200:
                info = response.json()
                print(f"  ✓ FOUND!")
                print(f"  Functions: {[f.get('Name') for f in info.get('Functions', [])]}")
                print()
            else:
                print(f"  ✗ Not found")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Try to call a known working object to see the pattern
    print("\n" + "=" * 60)
    print("Checking pattern from working LevelSequenceEditor...")
    print("=" * 60)
    
    url = f"{REMOTE_CONTROL_URL}/object/describe"
    payload = {"objectPath": "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem"}
    
    try:
        response = requests.put(url, json=payload)
        if response.status_code == 200:
            info = response.json()
            print(f"✓ Object exists!")
            print(f"\nFull info:")
            print(json.dumps(info, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    try:
        requests.get("http://localhost:30010/remote/info")
        print("✓ Remote Control server is running\n")
    except:
        print("❌ Remote Control server not running!")
        exit(1)
    
    search_for_movie_pipeline()
