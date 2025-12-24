import requests
import os
import sys

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"

def trigger_movie(json_relative_path):
    run_scene_path = r"C:\UnrealProjects\Coding\unreal\motion_system\run_scene.py"
    
    # Absolute path to JSON
    json_path = os.path.abspath(os.path.join(os.getcwd(), json_relative_path))
    
    try:
        with open(run_scene_path, "r", encoding='utf-8') as f:
            script_content = f.read()
            
        # Add environment setting and execution call
        setup_code = f"import os\nos.environ['MOVIE_JSON_PATH'] = r'{json_path}'\n"
        full_command = setup_code + script_content + "\n\nrun_scene(r'" + json_path + "')\n"
        
        payload = {
            "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
            "functionName": "ExecutePythonCommand",
            "parameters": {"PythonCommand": full_command}
        }
        
        print(f"--- Triggering Movie Scene: {json_relative_path} ---")
        response = requests.put(REMOTE_CONTROL_URL, json=payload, timeout=60)
        print(f"Result: {response.json()}")
        
    except Exception as e:
        print(f"ERROR: Failed to trigger movie: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        trigger_movie(sys.argv[1])
    else:
        trigger_movie("movies/scene_03_cinematic.json")
