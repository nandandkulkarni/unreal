"""
Run Square Path test and render the result
"""
import requests
import time

REMOTE_CONTROL_URL = "http://localhost:30010/remote/object/call"

def execute_python_command(command):
    """Execute Python command in Unreal via Remote Control"""
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": command}
    }
    response = requests.put(REMOTE_CONTROL_URL, headers={'Content-Type': 'application/json'}, json=payload)
    return response.json()

# Run the Square Path Return test
print("\n" + "="*80)
print("Running Square Path Return Test")
print("="*80 + "\n")

test_command = """
import sys
sys.path.append('C:/UnrealProjects/Coding/unreal')
sys.path.append('C:/UnrealProjects/Coding/unreal/tests')

from tests.run_integrated_test import run_single_test

# Square Path Return test
test_case = {
    "name": "Square Path Return",
    "commands": [
        {"type": "move_forward", "distance": 500.0, "duration": 2.0},
        {"type": "turn", "angle": 90.0, "duration": 1.0},
        {"type": "move_forward", "distance": 500.0, "duration": 2.0},
        {"type": "turn", "angle": 90.0, "duration": 1.0},
        {"type": "move_forward", "distance": 500.0, "duration": 2.0},
        {"type": "turn", "angle": 90.0, "duration": 1.0},
        {"type": "move_forward", "distance": 500.0, "duration": 2.0},
        {"type": "turn", "angle": 90.0, "duration": 1.0}
    ],
    "expected_final_position": {"x": 0.0, "y": 0.0, "z": 6.88},
    "expected_final_rotation": {"yaw": 0.0},
    "keep_sequence": True
}

result = run_single_test(test_case, test_number=99)
print(f"Test Result: {result['status']}")
if result['status'] == 'PASSED':
    print(f"Sequence: {result.get('sequence_name', 'Unknown')}")
    result.get('sequence_name', '')
else:
    print(f"Error: {result.get('errors', 'Unknown error')}")
    ''
"""

result = execute_python_command(test_command)
print(f"Test execution result: {result}")

# Get the sequence name from Unreal log
time.sleep(2)
import subprocess
log_output = subprocess.run(
    ['powershell', '-Command', 
     'Get-Content "C:\\Users\\user\\AppData\\Local\\UnrealEngine\\5.7\\Saved\\Logs\\Film5.log" -Tail 100 | Select-String "Sequence:" | Select-Object -Last 1'],
    capture_output=True, text=True
)
print(f"\nLog output:\n{log_output.stdout}")

# Now render it
print("\n" + "="*80)
print("Queueing Render Job")
print("="*80 + "\n")

render_command = """
import unreal

# Get latest sequence
sequences = unreal.EditorAssetLibrary.list_assets('/Game/Sequences', recursive=False, include_folder=False)
sequences = [s for s in sequences if 'TestSequence_Square_Path_Return' in s]
if sequences:
    latest_sequence = sorted(sequences)[-1]
    sequence_name = latest_sequence.split('/')[-1]
    
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    queue = subsystem.get_queue()
    queue.delete_all_jobs()
    
    job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.sequence = unreal.SoftObjectPath(latest_sequence)
    job.map = unreal.SoftObjectPath("/Game/Main")
    job.job_name = f"{sequence_name}_Render"
    
    config = job.get_configuration()
    output_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    output_setting.output_directory = unreal.DirectoryPath(f"C:/UnrealProjects/Coding/unreal/output/{sequence_name}")
    output_setting.file_name_format = "{sequence_name}_{frame_number}"
    output_setting.output_resolution = unreal.IntPoint(1920, 1080)
    output_setting.output_frame_rate = unreal.FrameRate(30, 1)
    
    config.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
    config.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
    
    print(f"Render queued for: {sequence_name}")
    print(f"Output: C:/UnrealProjects/Coding/unreal/output/{sequence_name}")
    sequence_name
else:
    print("No sequence found")
    ''
"""

result = execute_python_command(render_command)
print(f"\nRender queue result: {result}")

print("\n" + "="*80)
print("NEXT STEP: Open Movie Render Queue and click 'Render (Local)'")
print("  Window → Cinematics → Movie Render Queue")
print("="*80)
