"""
Remote Video Rendering Trigger
Attempts to trigger video render from outside Unreal via Remote Control API

Note: Movie Pipeline rendering may not be fully controllable via Remote Control.
This script tries multiple approaches to trigger the render remotely.
"""

import requests
import json
import time

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object"

def call_function(object_path, function_name, parameters=None):
    """Call a function on an Unreal object via Remote Control"""
    payload = {
        "objectPath": object_path,
        "functionName": function_name
    }
    
    if parameters:
        payload["parameters"] = parameters
    
    url = f"{REMOTE_CONTROL_URL}/call"
    
    try:
        response = requests.put(url, json=payload)
        print(f"Called {function_name}: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  Result: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"  Error: {response.text}")
            return None
    except Exception as e:
        print(f"  Exception: {e}")
        return None

def execute_python_script(script_path):
    """Try to execute Python script via Remote Control"""
    # Method 1: Try to call Python execution function
    result = call_function(
        "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "ExecutePythonScript",
        {"PythonScript": script_path}
    )
    
    if result:
        print("✓ Python script execution triggered")
        return True
    
    return False

def trigger_movie_pipeline_render():
    """Try to trigger Movie Pipeline render via Remote Control API calls"""
    
    print("\n=== Attempting Movie Pipeline Render via Remote Control ===\n")
    
    # Try to access Movie Pipeline Queue Subsystem
    print("1. Trying to access MoviePipelineQueueSubsystem...")
    
    # This is tricky - we need to create the render job via function calls
    # Let's try a different approach: call a custom Python function if we can
    
    # Method 1: Try to execute the render script
    print("\n2. Trying to execute render_sequence_to_video.py remotely...")
    script_path = "C:/U/CinematicPipeline_Scripts/render_sequence_to_video.py"
    
    if execute_python_script(script_path):
        return True
    
    # Method 2: Try to use ExecutePythonCommand (might be blocked)
    print("\n3. Trying ExecutePythonCommand...")
    
    python_code = """
import unreal

# Load sequence
sequence_path = "/Game/CharacterWalkSequence"
sequence_asset = unreal.load_asset(sequence_path)

# Get Movie Pipeline subsystem
subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
queue = subsystem.get_queue()

# Create new job
job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
job.sequence = unreal.SoftObjectPath(sequence_path)
job.map = unreal.SoftObjectPath("/Game/Main")

# Configure output settings
config = job.get_configuration()
output_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
output_setting.output_directory = unreal.DirectoryPath("C:/U/CinematicPipeline/Saved/VideoCaptures")
output_setting.file_name_format = "{sequence_name}"
output_setting.output_resolution = unreal.IntPoint(1920, 1080)
output_setting.output_frame_rate = unreal.FrameRate(30, 1)

# Add Apple ProRes codec
video_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineAppleProResOutput)

# Start render
print("Starting render...")
subsystem.render_queue_with_executor(unreal.MoviePipelinePIEExecutor.static_class())
print("Render triggered!")
"""
    
    result = call_function(
        "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "ExecutePythonCommand",
        {"PythonCommand": python_code}
    )
    
    if result:
        print("✓ Python command execution triggered")
        return True
    
    # Method 3: Try to call functions on Movie Pipeline subsystem directly
    print("\n4. Trying to call Movie Pipeline functions directly...")
    
    # This requires knowing the exact object path and available functions
    # Let's try to describe the subsystem first
    describe_url = f"{REMOTE_CONTROL_URL}/describe"
    describe_payload = {
        "objectPath": "/Script/MovieRenderPipelineCore.Default__MoviePipelineQueueSubsystem"
    }
    
    try:
        response = requests.put(describe_url, json=describe_payload)
        if response.status_code == 200:
            print("Found MoviePipelineQueueSubsystem!")
            info = response.json()
            print(f"Available functions: {json.dumps(info.get('Functions', []), indent=2)}")
            
            # Try to call render function if it exists
            # Note: This likely won't work because we need to create the job first
            
        else:
            print(f"Could not describe MoviePipelineQueueSubsystem: {response.status_code}")
    except Exception as e:
        print(f"Exception describing subsystem: {e}")
    
    return False

def main():
    print("=" * 60)
    print("Remote Video Rendering Trigger")
    print("=" * 60)
    
    # First, verify Remote Control is running
    try:
        response = requests.get("http://localhost:30010/remote/info")
        if response.status_code != 200:
            print("❌ Remote Control server is not running!")
            print("   Start it in Unreal: WebControl.StartServer")
            return
    except:
        print("❌ Cannot connect to Remote Control server!")
        print("   Start it in Unreal: WebControl.StartServer")
        return
    
    print("✓ Remote Control server is running\n")
    
    # Attempt to trigger render
    success = trigger_movie_pipeline_render()
    
    if success:
        print("\n✓ Render triggered successfully!")
        print("  Check Unreal Editor for render preview window")
        print("  Output will be saved to: C:/U/CinematicPipeline/Saved/VideoCaptures")
    else:
        print("\n❌ Could not trigger render remotely")
        print("\nREASON:")
        print("  Movie Pipeline rendering requires complex setup (job creation,")
        print("  configuration, executor) that cannot be easily triggered via")
        print("  Remote Control API's simple function calls.")
        print("\nWORKAROUND:")
        print("  Run render_sequence_to_video.py inside Unreal:")
        print("  Tools → Execute Python Script → render_sequence_to_video.py")
        print("\nALTERNATIVE:")
        print("  Create a Blueprint or C++ function that wraps the render")
        print("  logic, then expose it via Remote Control for simple remote trigger.")

if __name__ == "__main__":
    main()
