"""
Close any currently open sequence in Unreal
"""
import requests

BASE_URL = "http://localhost:30010/remote/object/call"

def call_function(object_path, function_name, parameters=None):
    """Call a function on an Unreal object via Remote Control API"""
    payload = {
        "objectPath": object_path,
        "functionName": function_name
    }
    
    if parameters:
        payload["parameters"] = parameters
    
    response = requests.put(BASE_URL, json=payload)
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text

print("Closing sequence via Remote API...")

# First check if a sequence is open
success, result = call_function(
    "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
    "GetCurrentLevelSequence"
)

if success:
    current = result.get('ReturnValue', '')
    if current:
        print(f"Found open sequence: {current}")
        
        # Close it
        success, result = call_function(
            "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
            "CloseLevelSequence"
        )
        
        if success:
            print("✓ Sequence closed successfully")
        else:
            print(f"✗ Failed to close: {result}")
    else:
        print("No sequence currently open")
else:
    print(f"✗ Failed to check for open sequence: {result}")

