import requests
import json
import time

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
                location = data.get('ReturnValue', {})
                return location
            else:
                print(f"✗ Failed to get location: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Error: {e}")
            return None
    
    def set_actor_location(self, actor_path, x, y, z):
        """Move an actor to a specific location"""
        url = f'{self.base_url}/remote/object/call'
        
        payload = {
            'objectPath': actor_path,
            'functionName': 'K2_SetActorLocation',
            'parameters': {
                'NewLocation': {
                    'X': x,
                    'Y': y,
                    'Z': z
                }
            },
            'generateTransaction': True
        }
        
        try:
            response = requests.put(url, json=payload)
            if response.status_code == 200:
                print(f"✓ Moved actor to ({x}, {y}, {z})")
                
                # Verify the move by reading back the location
                time.sleep(0.1)  # Small delay to ensure position updates
                actual_loc = self.get_actor_location(actor_path)
                if actual_loc:
                    actual_x = actual_loc.get('X', 0)
                    actual_y = actual_loc.get('Y', 0)
                    actual_z = actual_loc.get('Z', 0)
                    print(f"  → Confirmed position: ({actual_x:.1f}, {actual_y:.1f}, {actual_z:.1f})")
                
                return True
            else:
                print(f"✗ Failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

if __name__ == "__main__":
    controller = UnrealController()
    
    # CORRECT PATH FOUND!
    actor_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    
    print("Moving character in a square...")
    
    # Move to different positions
    positions = [
        (0, 0, 100),
        (200, 0, 100),
        (200, 200, 100),
        (0, 200, 100),
        (0, 0, 100)
    ]
    
    for x, y, z in positions:
        controller.set_actor_location(actor_path, x, y, z)
        time.sleep(1)
    
    print("Done!")
