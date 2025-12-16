import requests
import json
import time

class UnrealController:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'
        
    def set_actor_location(self, actor_path, x, y, z):
        url = f'{self.base_url}/remote/object/call'
        payload = {
            'objectPath': actor_path,
            'functionName': 'K2_SetActorLocation',
            'parameters': {'NewLocation': {'X': x, 'Y': y, 'Z': z}},
            'generateTransaction': True
        }
        response = requests.put(url, json=payload)
        return response.status_code == 200
    
    def set_actor_rotation(self, actor_path, pitch, yaw, roll):
        url = f'{self.base_url}/remote/object/call'
        payload = {
            'objectPath': actor_path,
            'functionName': 'K2_SetActorRotation',
            'parameters': {'NewRotation': {'Pitch': pitch, 'Yaw': yaw, 'Roll': roll}},
            'generateTransaction': True
        }
        response = requests.put(url, json=payload)
        return response.status_code == 200
    
    def redraw_viewports(self):
        """Method 1: LevelEditorSubsystem.EditorInvalidateViewports"""
        url = f'{self.base_url}/remote/object/call'
        payload = {
            'objectPath': '/Script/UnrealEd.Default__LevelEditorSubsystem',
            'functionName': 'EditorInvalidateViewports',
            'generateTransaction': False
        }
        try:
            response = requests.put(url, json=payload)
            if response.status_code == 200:
                print("    ✓ RedrawViewports succeeded")
                return True
            else:
                print(f"    ✗ RedrawViewports failed: {response.json().get('errorMessage', 'Unknown')}")
                return False
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return False

if __name__ == "__main__":
    controller = UnrealController()
    actor_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    
    print("="*60)
    print("METHOD 1: LevelEditorSubsystem.EditorInvalidateViewports")
    print("="*60)
    
    positions = [(0, 0, 100), (300, 0, 100), (300, 300, 100), (0, 300, 100), (0, 0, 100)]
    yaw = 0
    
    for i, (x, y, z) in enumerate(positions, 1):
        print(f"\nWaypoint {i}: ({x}, {y}, {z}) @ {yaw}°")
        controller.set_actor_location(actor_path, x, y, z)
        controller.set_actor_rotation(actor_path, 0, yaw, 0)
        controller.redraw_viewports()
        yaw = (yaw + 45) % 360
        time.sleep(2)
    
    print("\n" + "="*60)
    print("COMPLETE - Did you see the character move?")
    print("="*60)
