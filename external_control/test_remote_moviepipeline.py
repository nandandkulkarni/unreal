"""Simple test of Remote Control and MoviePipeline"""
import requests

# Test 1: Basic connection
print("Test 1: Basic Remote Control connection...")
payload = {
    'objectPath': '/Script/PythonScriptPlugin.Default__PythonScriptLibrary',
    'functionName': 'ExecutePythonCommand',
    'parameters': {'PythonCommand': 'print("Hello from Unreal"); 2 + 2'}
}
response = requests.put('http://localhost:30010/remote/object/call', json=payload)
print(f"Result: {response.json()}\n")

# Test 2: Check if MoviePipeline class exists
print("Test 2: Checking MoviePipelineQueueSubsystem attribute...")
payload = {
    'objectPath': '/Script/PythonScriptPlugin.Default__PythonScriptLibrary',
    'functionName': 'ExecutePythonCommand',
    'parameters': {'PythonCommand': "import unreal; hasattr(unreal, 'MoviePipelineQueueSubsystem')"}
}
response = requests.put('http://localhost:30010/remote/object/call', json=payload)
print(f"hasattr result: {response.json()}\n")

# Test 3: Try to actually access the subsystem
print("Test 3: Trying to access MoviePipelineQueueSubsystem...")
payload = {
    'objectPath': '/Script/PythonScriptPlugin.Default__PythonScriptLibrary',
    'functionName': 'ExecutePythonCommand',
    'parameters': {'PythonCommand': """
import unreal
try:
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    print(f"SUCCESS: Got subsystem {type(subsystem).__name__}")
    "SUCCESS"
except AttributeError as e:
    print(f"ATTRIBUTE ERROR: {e}")
    "ATTRIBUTE_ERROR"
except Exception as e:
    print(f"ERROR: {e}")
    "ERROR"
"""}
}
response = requests.put('http://localhost:30010/remote/object/call', json=payload)
print(f"Access result: {response.json()}\n")

print("Check Unreal log for detailed output:")
print("  C:\\Users\\user\\AppData\\Local\\UnrealEngine\\5.7\\Saved\\Logs\\Film5_2.log")
