"""
Remote Video Rendering Trigger v2
Calls Movie Pipeline functions step-by-step via Remote Control API

This uses the same approach as remote_camera_fix_and_test.py:
calling individual Unreal functions via HTTP API instead of executing Python code.
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
        print(f"  {function_name}: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result:
                print(f"    Result: {json.dumps(result, indent=6)}")
            return result
        else:
            print(f"    Error: {response.text}")
            return None
    except Exception as e:
        print(f"    Exception: {e}")
        return None

def describe_object(object_path):
    """Describe an object to see available functions"""
    url = f"{REMOTE_CONTROL_URL}/describe"
    payload = {"objectPath": object_path}
    
    try:
        response = requests.put(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Could not describe {object_path}: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def trigger_render_step_by_step():
    """Trigger render by calling Movie Pipeline functions one by one"""
    
    print("=" * 60)
    print("Remote Video Rendering - Step-by-Step Function Calls")
    print("=" * 60)
    
    # Movie Pipeline Queue Subsystem object path (found via Unreal Python console)
    # The instance number (_0, _1, etc) may vary
    subsystem_paths = [
        "/Engine/Transient.DisplayClusterEditorEngine_0:MoviePipelineQueueSubsystem_0",
        "/Engine/Transient.DisplayClusterEditorEngine_0:MoviePipelineQueueSubsystem_1",
        "/Engine/Transient.DisplayClusterEditorEngine_1:MoviePipelineQueueSubsystem_0",
    ]
    
    print("\n1. Finding MoviePipelineQueueSubsystem...")
    subsystem_path = None
    
    for path in subsystem_paths:
        info = describe_object(path)
        if info:
            subsystem_path = path
            print(f"   ✓ Found at: {path}")
            break
    
    if not subsystem_path:
        print("   ✗ Could not find MoviePipelineQueueSubsystem")
        return False
    
    print("\n2. Describing MoviePipelineQueueSubsystem...")
    info = describe_object(subsystem_path)
    
    if info:
        print("   Available functions:")
        functions = info.get("Functions", [])
        for func in functions:
            print(f"   - {func.get('Name')}")
        print()
    
    # Step 1: Get the queue
    print("3. Getting render queue...")
    queue_result = call_function(subsystem_path, "GetQueue")
    
    if not queue_result:
        print("   ✗ Could not get queue")
        return False
    
    queue_path = queue_result.get("ReturnValue")
    print(f"   ✓ Queue path: {queue_path}")
    
    # Step 2: Describe the queue to see its functions
    print("\n4. Describing the queue object...")
    queue_info = describe_object(queue_path)
    if queue_info:
        print("   Available functions on queue:")
        functions = queue_info.get("Functions", [])
        for func in functions:
            print(f"   - {func.get('Name')}")
        print()
    
    # Step 3: Allocate new job on the QUEUE (not subsystem)
    print("5. Allocating new render job on queue...")
    job_result = call_function(queue_path, "AllocateNewJob")
    
    if not job_result:
        print("   ✗ Could not allocate job")
        return False
    
    # Step 4: Try to call RenderQueueWithExecutor on subsystem
    print("\n6. Starting render with PIE executor...")
    print("   WARNING: This may crash Remote Control server...")
    render_result = call_function(subsystem_path, "RenderQueueWithExecutor")
    
    if render_result:
        print("\n✓ Render triggered!")
        print("  Check Unreal Editor for render preview window")
        return True
    
    print("\n❌ Render did not trigger")
    print("\nREASON:")
    print("  Movie Pipeline requires complex job configuration that")
    print("  cannot be set via simple Remote Control function calls.")
    print("\nTrying alternative approaches...")
    
    # Alternative: Try IsRendering
    print("\n7. Checking render status...")
    status = call_function(subsystem_path, "IsRendering")
    
    return False

def main():
    print("Checking Remote Control server...")
    
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
    
    success = trigger_render_step_by_step()
    
    if not success:
        print("\n" + "=" * 60)
        print("CONCLUSION:")
        print("=" * 60)
        print("Movie Pipeline rendering requires:")
        print("  1. Creating a job (AllocateNewJob)")
        print("  2. Setting sequence, map, and configuration")
        print("  3. Adding output settings (resolution, format, etc.)")
        print("  4. Calling RenderQueueWithExecutor")
        print("\nSteps 2-3 require setting object properties,")
        print("which Remote Control API supports, but is complex.")
        print("\nBEST APPROACH:")
        print("  Run render_sequence_to_video.py inside Unreal")
        print("\nOR create a Blueprint wrapper function")
        print("  (see create_render_blueprint.py for instructions)")

if __name__ == "__main__":
    main()
