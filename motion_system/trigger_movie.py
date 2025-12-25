import requests
import os
import sys
import json

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"

def load_movie_data(movie_path):
    """Load movie data from either .json or .py file"""
    if movie_path.endswith('.py'):
        # Load Python file with MOVIE constant
        import importlib.util
        spec = importlib.util.spec_from_file_location("movie_module", movie_path)
        movie_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(movie_module)
        return movie_module.MOVIE
    else:
        # Load JSON file
        with open(movie_path, 'r', encoding='utf-8') as f:
            return json.load(f)

def trigger_movie(movie_relative_path):
    run_scene_path = r"C:\UnrealProjects\Coding\unreal\motion_system\run_scene.py"
    
    # Absolute path to movie file
    movie_path = os.path.abspath(os.path.join(os.getcwd(), movie_relative_path))
    
    try:
        # Load movie data
        movie_data = load_movie_data(movie_path)
        
        # Convert to JSON string for passing to Unreal
        movie_json_str = json.dumps(movie_data)
        
        # Create a temporary JSON file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
            json.dump(movie_data, tmp)
            temp_json_path = tmp.name
        
        with open(run_scene_path, "r", encoding='utf-8') as f:
            script_content = f.read()
            
        # Add environment setting and execution call
        setup_code = f"import os\nos.environ['MOVIE_JSON_PATH'] = r'{temp_json_path}'\n"
        full_command = setup_code + script_content + "\n\nrun_scene(r'" + temp_json_path + "')\n"
        
        payload = {
            "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
            "functionName": "ExecutePythonCommand",
            "parameters": {"PythonCommand": full_command}
        }
        
        print(f"--- Triggering Movie Scene: {movie_relative_path} ---")
        response = requests.put(REMOTE_CONTROL_URL, json=payload, timeout=60)
        print(f"Result: {response.json()}")
        
        # Clean up temp file
        try:
            os.unlink(temp_json_path)
        except:
            pass
        
    except Exception as e:
        print(f"ERROR: Failed to trigger movie: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        trigger_movie(sys.argv[1])
    else:
        trigger_movie("movies/json_tandem_run_square.py")

