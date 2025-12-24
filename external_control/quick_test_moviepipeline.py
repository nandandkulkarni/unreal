"""Quick test of actual MoviePipeline access"""
import requests

cmd = """
import unreal
try:
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    print(f"SUCCESS: Got subsystem type {type(subsystem)}")
except Exception as e:
    print(f"ERROR: {e}")
"""

payload = {
    'objectPath': '/Script/PythonScriptPlugin.Default__PythonScriptLibrary',
    'functionName': 'ExecutePythonCommand',
    'parameters': {'PythonCommand': cmd}
}

response = requests.put('http://localhost:30010/remote/object/call', json=payload)
print(response.json())
