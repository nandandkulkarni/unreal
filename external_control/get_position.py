import requests
import json

class UnrealController:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'
        
    def get_actor_location(self, actor_path):
        """Get the current location of an actor"""
        url = f'{self.base_url}/remote/object/call'
        
        payload = {
            'objectPath': actor_path,
            'functionName': 'K2_GetActorLocation',
            'generateTransaction': False
        }
        
        try:
            response = requests.put(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                if 'ReturnValue' in data:
                    loc = data['ReturnValue']
                    return (loc['X'], loc['Y'], loc['Z'])
                return None
            else:
                print(f"✗ Failed to get location: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"✗ Error: {e}")
            return None

if __name__ == "__main__":
    controller = UnrealController()
    actor_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    
    print("Getting current character position...")
    location = controller.get_actor_location(actor_path)
    
    if location:
        print(f"\n✓ Character is at:")
        print(f"   X = {location[0]:.2f}")
        print(f"   Y = {location[1]:.2f}")
        print(f"   Z = {location[2]:.2f}")
    else:
        print("\n✗ Could not get character position")
