import requests
import json
import time

class UnrealController:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'
        
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
            return response.status_code == 200
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def set_actor_rotation(self, actor_path, pitch, yaw, roll):
        """Set an actor's rotation"""
        url = f'{self.base_url}/remote/object/call'
        
        payload = {
            'objectPath': actor_path,
            'functionName': 'K2_SetActorRotation',
            'parameters': {
                'NewRotation': {
                    'Pitch': pitch,
                    'Yaw': yaw,
                    'Roll': roll
                }
            },
            'generateTransaction': True
        }
        
        try:
            response = requests.put(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def invalidate_viewport(self):
        """Try different methods to invalidate/refresh the viewport"""
        url = f'{self.base_url}/remote/object/call'
        
        methods = [
            # Method 1: Invalidate Level Editor viewport
            {
                'name': 'RedrawAllViewports',
                'objectPath': '/Script/UnrealEd.Default__LevelEditorSubsystem',
                'functionName': 'EditorInvalidateViewports'
            },
            # Method 2: Request redraw
            {
                'name': 'RequestRedraw',
                'objectPath': '/Script/UnrealEd.Default__UnrealEditorSubsystem',
                'functionName': 'RequestRedrawActiveViewport'
            },
            # Method 3: Refresh editor
            {
                'name': 'RefreshEditor',
                'objectPath': '/Script/UnrealEd.Default__EditorLevelLibrary',
                'functionName': 'EditorRefreshLevel'
            }
        ]
        
        for method in methods:
            payload = {
                'objectPath': method['objectPath'],
                'functionName': method['functionName'],
                'generateTransaction': False
            }
            
            try:
                response = requests.put(url, json=payload)
                if response.status_code == 200:
                    print(f"✓ {method['name']} succeeded")
                    return True
                else:
                    print(f"✗ {method['name']}: {response.json().get('errorMessage', 'Failed')}")
            except Exception as e:
                print(f"✗ {method['name']}: {e}")
        
        return False

if __name__ == "__main__":
    controller = UnrealController()
    actor_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    
    print("="*60)
    print("TESTING VIEWPORT REFRESH METHODS")
    print("="*60)
    
    positions = [
        (0, 0, 100),
        (300, 0, 100),
        (300, 300, 100),
        (0, 300, 100),
        (0, 0, 100)
    ]
    
    yaw = 0
    
    for i, (x, y, z) in enumerate(positions, 1):
        print(f"\n--- Waypoint {i}: ({x}, {y}, {z}) @ {yaw}° ---")
        
        # Move and rotate
        controller.set_actor_location(actor_path, x, y, z)
        controller.set_actor_rotation(actor_path, 0, yaw, 0)
        print(f"✓ Position/rotation updated")
        
        # Try to refresh viewport
        print("Attempting viewport refresh...")
        controller.invalidate_viewport()
        
        yaw = (yaw + 45) % 360
        time.sleep(2)
    
    print("\n" + "="*60)
    print("✓ TEST COMPLETE")
    print("="*60)
