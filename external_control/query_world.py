import requests
import json

def query_object(path):
    """Query an object to see its properties"""
    url = 'http://localhost:30010/remote/object/describe'
    
    payload = {
        'objectPath': path
    }
    
    try:
        response = requests.put(url, json=payload)
        print(f"\n{'='*60}")
        print(f"Querying: {path}")
        print(f"Status: {response.status_code}")
        print(f"{'='*60}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            return data
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def call_function(path, function_name):
    """Call a function on an object"""
    url = 'http://localhost:30010/remote/object/call'
    
    payload = {
        'objectPath': path,
        'functionName': function_name,
        'generateTransaction': False
    }
    
    try:
        response = requests.put(url, json=payload)
        print(f"\n{'='*60}")
        print(f"Calling {function_name} on: {path}")
        print(f"Status: {response.status_code}")
        print(f"{'='*60}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            return data
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

print("="*60)
print("EXPLORING WORLD STRUCTURE")
print("="*60)

# Try different world/level paths
world_paths = [
    '/Game/Main',
    '/Script/Engine.World',
    '/Engine/Transient.World',
    '/Game/Main.Main',
]

for path in world_paths:
    query_object(path)

# Try to access the Engine
print("\n" + "="*60)
print("TRYING ENGINE PATHS")
print("="*60)

engine_paths = [
    '/Script/Engine.Default__World',
    '/Engine/Transient',
]

for path in engine_paths:
    query_object(path)

print("\n" + "="*60)
print("COMPLETED")
print("="*60)
