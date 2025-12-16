import requests
import json

class UnrealController:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'
    
    def spawn_actor(self, actor_class, location=(0, 0, 100)):
        """Spawn a new actor in the level"""
        url = f'{self.base_url}/remote/object/call'
        
        # Call the editor's spawn actor function
        payload = {
            'objectPath': '/Script/Engine.Default__EditorLevelLibrary',
            'functionName': 'SpawnActorFromClass',
            'parameters': {
                'ActorClass': actor_class,
                'Location': {
                    'X': location[0],
                    'Y': location[1],
                    'Z': location[2]
                }
            },
            'generateTransaction': True
        }
        
        try:
            response = requests.put(url, json=payload)
            if response.status_code == 200:
                print(f"✓ Spawned actor at {location}")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"✗ Failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

if __name__ == "__main__":
    controller = UnrealController()
    
    print("Spawning reference cubes at waypoints...")
    
    # Spawn cubes at each waypoint position
    positions = [
        (0, 0, 150),      # Above the character
        (200, 0, 150),
        (200, 200, 150),
        (0, 200, 150)
    ]
    
    # Use a basic static mesh actor
    cube_class = '/Script/Engine.StaticMeshActor'
    
    for i, pos in enumerate(positions, 1):
        print(f"\nSpawning cube {i} at {pos}...")
        controller.spawn_actor(cube_class, pos)
