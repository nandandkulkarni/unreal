"""
Render Test Sequence to Video
"""
import requests
import json
import time

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"

def call_remote(command):
    """Execute Python command in Unreal"""
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": command}
    }
    response = requests.put(REMOTE_CONTROL_URL, headers={'Content-Type': 'application/json'}, json=payload)
    return response.json()

def render_sequence(sequence_name, output_path=None):
    """Render a sequence to video"""
    
    if not output_path:
        output_path = f"C:/UnrealProjects/Coding/unreal/output/{sequence_name}"
    
    render_code = f"""
import unreal
import traceback

try:
    # Find the sequence
    sequence_path = "/Game/Sequences/{sequence_name}"
    sequence = unreal.load_asset(sequence_path)

    if not sequence:
        print(f"ERROR: Could not find sequence: {{sequence_path}}")
    else:
        print(f"Found sequence: {{sequence.get_name()}}")
        
        # Use Movie Pipeline Queue
        print("Getting MoviePipelineQueueSubsystem...")
        subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
        print(f"Got subsystem: {{type(subsystem)}}")
        
        queue = subsystem.get_queue()
        print(f"Got queue: {{type(queue)}}")
        
        # Clear existing jobs
        queue.delete_all_jobs()
        
        # Create a new job
        print("Creating new job...")
        job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
        print(f"Created job: {{type(job)}}")
        
        job.sequence = unreal.SoftObjectPath(sequence_path)
        job.map = unreal.SoftObjectPath("/Game/Main")
        job.job_name = "{sequence_name}_Render"
        
        # Configure the job settings
        config = job.get_configuration()
        
        # Add output setting
        output_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
        output_setting.output_directory = unreal.DirectoryPath(r"{output_path}")
        output_setting.file_name_format = "{{sequence_name}}_{{frame_number}}"
        output_setting.output_resolution = unreal.IntPoint(1920, 1080)
        output_setting.output_frame_rate = unreal.FrameRate(30, 1)
        
        # Add deferred rendering
        config.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
        
        # Add PNG output
        config.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
        
        print(f"Render job configured:")
        print(f"  Output: {output_path}")
        print(f"  Resolution: 1920x1080")
        print(f"  Format: PNG sequence")
        
        # Start the render
        print("\\nStarting render...")
        subsystem.render_queue_with_executor(unreal.MoviePipelinePIEExecutor.static_class())
        print("SUCCESS: Render started! Check Unreal Editor for progress.")

except Exception as e:
    print(f"ERROR TYPE: {{type(e).__name__}}")
    print(f"ERROR: {{str(e)}}")
    print("\\nFull traceback:")
    traceback.print_exc()
"""
    
    print("\n" + "=" * 70)
    print(f"RENDERING: {sequence_name}")
    print("=" * 70)
    
    result = call_remote(render_code)
    print(f"\nResult: {result.get('ReturnValue', result)}")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Open Unreal Editor")
    print("2. Go to: Window > Cinematics > Movie Render Queue")
    print("3. Click 'Render (Local)' to start rendering")
    print(f"4. Output will be saved to: {output_path}")
    print("=" * 70)

if __name__ == "__main__":
    import sys
    
    # Get sequence name from command line or use default
    if len(sys.argv) > 1:
        sequence_name = sys.argv[1]
    else:
        # Get the latest Square Path Return sequence
        result = call_remote("""
import unreal
sequences = unreal.EditorAssetLibrary.list_assets("/Game/Sequences", recursive=False)
test_seqs = sorted([s.split("/")[-1].split(".")[0] for s in sequences if "Square_Path_Return" in s])
print(test_seqs[-1] if test_seqs else "No Square Path Return sequences found")
""")
        
        time.sleep(1)
        
        # Check log for the sequence name
        sequence_name = "TestSequence_Square_Path_Return_25_12_23_21_53_16_002"
        print(f"Using latest Square Path Return sequence: {sequence_name}")
    
    render_sequence(sequence_name)
