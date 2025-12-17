"""
Quick test: Can we spawn an actor remotely?
"""
import requests
import json

def call_function(object_path, function_name, parameters=None):
    payload = {"objectPath": object_path, "functionName": function_name}
    if parameters:
        payload["parameters"] = parameters
    
    response = requests.put("http://localhost:30010/remote/object/call", json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return None

# Test 1: Spawn an actor
print("Test 1: Spawning Character...")
result = call_function(
    "/Script/UnrealEd.Default__EditorActorSubsystem",
    "SpawnActorFromClass",
    {"ActorClass": "/Script/Engine.Character", "Location": {"X": 0, "Y": 0, "Z": 100}}
)

if result:
    print(f"SUCCESS! Actor: {result.get('ReturnValue')}")
else:
    print("FAILED")

# Test 2: Create camera
print("\nTest 2: Creating camera in sequence...")
result = call_function(
    "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem",
    "CreateCamera",
    {"bSpawnable": True}
)

if result:
    print(f"SUCCESS! Camera created")
else:
    print("FAILED")

# Test 3: Add spawnable
print("\nTest 3: Adding spawnable to sequence...")
result = call_function(
    "/Script/LevelSequenceEditor.Default__LevelSequenceEditorSubsystem",
    "AddSpawnableFromClass",
    {"ClassToSpawn": "/Script/Engine.Character"}
)

if result:
    print(f"SUCCESS! Spawnable added")
else:
    print("FAILED")
