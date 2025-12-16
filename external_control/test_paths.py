import requests
import json

def test_actor_path(path):
    """Test if an actor exists and can be controlled"""
    url = 'http://localhost:30010/remote/object/call'
    
    payload = {
        'objectPath': path,
        'functionName': 'K2_GetActorLocation',
        'generateTransaction': False
    }
    
    try:
        response = requests.put(url, json=payload)
        print(f"\nTesting: {path}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

# Test the most likely paths
print("="*60)
print("TESTING ACTOR PATHS")
print("="*60)

paths_to_test = [
    '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter',
    '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_0',
    '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_0',
    '/Game/ThirdPerson/Maps/Main.Main:PersistentLevel.BP_ThirdPersonCharacter',
]

for path in paths_to_test:
    if test_actor_path(path):
        print(f"\n{'='*60}")
        print(f"✓✓✓ SUCCESS! Found the actor at:")
        print(f"{path}")
        print(f"{'='*60}\n")
        break
