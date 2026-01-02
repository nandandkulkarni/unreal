"""
Track-Based Trigger Movie

Triggers a movie scene in Unreal Engine via Remote Control API.
Updated to work with folder-based track structure.

Usage:
    python trigger_movie.py dist/runners_overhead/
"""

import requests
import os
import sys
import json

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"


def trigger_movie(movie_folder: str):
    """
    Trigger movie scene in Unreal using folder-based tracks.
    
    Args:
        movie_folder: Path to movie folder (e.g., dist/runners_overhead/)
    
    Process:
        1. Verify meta.json exists
        2. Read run_scene.py script
        3. Inject movie folder path as environment variable
        4. Execute via Remote Control API
    """
    run_scene_path = os.path.join(os.path.dirname(__file__), "run_scene.py")
    
    # Verify movie folder exists
    movie_path = os.path.abspath(movie_folder)
    meta_path = os.path.join(movie_path, "meta.json")
    
    if not os.path.exists(meta_path):
        print(f"ERROR: meta.json not found in {movie_path}")
        return
    
    try:
        with open(run_scene_path, "r", encoding='utf-8') as f:
            script_content = f.read()
        
        # Inject movie folder path
        setup_code = f"import os\nos.environ['MOVIE_FOLDER_PATH'] = r'{movie_path}'\n"
        full_command = setup_code + script_content + f"\n\nrun_scene(r'{movie_path}')\n"
        
        payload = {
            "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
            "functionName": "ExecutePythonCommand",
            "parameters": {"PythonCommand": full_command}
        }
        
        print(f"--- Triggering Movie Scene: {movie_folder} ---")
        response = requests.put(REMOTE_CONTROL_URL, json=payload, timeout=60)
        print(f"Result: {response.json()}")
        
    except Exception as e:
        print(f"ERROR: Failed to trigger movie: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        trigger_movie(sys.argv[1])
    else:
        print("Usage: python trigger_movie.py <movie_folder>")
        print("Example: python trigger_movie.py dist/runners_overhead/")
