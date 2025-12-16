import requests

paths_to_test = [
    '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C',
    '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_2',
    '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_2',
    '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_1',
    '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1',
]

print("Testing different actor path variations...\n")

for path in paths_to_test:
    response = requests.put(
        'http://localhost:30010/remote/object/call',
        json={
            'objectPath': path,
            'functionName': 'K2_GetActorLocation'
        }
    )
    status = "✓ FOUND!" if response.status_code == 200 else "✗"
    print(f"{status} {path} - Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"\n{'='*60}")
        print(f"SUCCESS! The correct path is:")
        print(f"{path}")
        print(f"{'='*60}\n")
        break
