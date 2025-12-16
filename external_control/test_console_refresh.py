import requests
import json
import time

class UnrealController:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'

    def execute_console_command(self, command):
        """Execute a console command in Unreal"""
        url = f'{self.base_url}/remote/object/call'
        
        # Try calling KismetSystemLibrary.ExecuteConsoleCommand
        payload = {
            'objectPath': '/Script/Engine.Default__KismetSystemLibrary',
            'functionName': 'ExecuteConsoleCommand',
            'parameters': {
                'WorldContextObject': '/Game/Main.Main',
                'Command': command
            },
            'generateTransaction': False
        }
        
        try:
            resp = requests.put(url, json=payload, timeout=2)
            print(f"ExecuteConsoleCommand response: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Response: {resp.text}")
            return resp.status_code == 200
        except Exception as e:
            print(f"Exception: {e}")
            return False

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

    def force_viewport_refresh(self):
        """Try multiple methods to force viewport refresh"""
        # Method 1: Try Slate.Redraw console command
        print("  Trying Slate.Redraw...")
        self.execute_console_command("Slate.Redraw")
        
        # Method 2: Try redraws via other commands
        print("  Trying EditorViewports.Redraw...")
        self.execute_console_command("EditorViewports.Redraw")

if __name__ == "__main__":
    controller = UnrealController()
    actor_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    
    print("="*60)
    print("TESTING CONSOLE COMMAND VIEWPORT REFRESH")
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
        print(f"\nWaypoint {i}: Moving to ({x}, {y}, {z}) rotation {yaw}°...")
        
        # Move
        controller.set_actor_location(actor_path, x, y, z)
        controller.set_actor_rotation(actor_path, 0, yaw, 0)
        
        # Force viewport refresh
        controller.force_viewport_refresh()
        
        print(f"✓ Moved and attempted refresh")
        
        yaw = (yaw + 45) % 360
        time.sleep(2)
    
    print("\n" + "="*60)
    print("✓ COMPLETE!")
    print("="*60)
