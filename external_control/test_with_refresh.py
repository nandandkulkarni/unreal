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
            print(f"[ERROR] Error: {e}")
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
    
    def toggle_selection(self, actor_path):
        """Toggle actor selection to force viewport refresh"""
        url = f'{self.base_url}/remote/object/call'
        
        # Select
        payload = {
            'objectPath': '/Script/UnrealEd.Default__EditorActorSubsystem',
            'functionName': 'SetActorSelectionState',
            'parameters': {
                'Actor': actor_path,
                'bShouldBeSelected': True
            },
            'generateTransaction': True
        }
        
        try:
            requests.put(url, json=payload)
            time.sleep(0.05)
            
            # Deselect
            payload['parameters']['bShouldBeSelected'] = False
            requests.put(url, json=payload)
            return True
        except Exception as e:
            print(f"[ERROR] Error toggling selection: {e}")
            return False

if __name__ == "__main__":
    controller = UnrealController()
    actor_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    
    print("="*60)
    print("MOVING CHARACTER WITH VIEWPORT REFRESH")
    print("="*60)
    print("\n[TIP] Watch the viewport - forcing visual refresh after each move\n")
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
        print(f"\nWaypoint {i}: Moving to ({x}, {y}, {z}) rotation {yaw} deg...")
        
        # Move
        controller.set_actor_location(actor_path, x, y, z)
        controller.set_actor_rotation(actor_path, 0, yaw, 0)
        
        # Force viewport refresh by toggling selection
        controller.toggle_selection(actor_path)
        
        print(f"[OK] Moved and refreshed viewport")
        
        yaw = (yaw + 45) % 360
        time.sleep(2)
    
    print("\n" + "="*60)
    print("[OK] COMPLETE!")
    print("="*60)
