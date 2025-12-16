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
                # The response contains the return value
                if 'ReturnValue' in data:
                    loc = data['ReturnValue']
                    return (loc['X'], loc['Y'], loc['Z'])
                return None
            else:
                print(f"✗ Failed to get location: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Error: {e}")
            return None
        
    def set_actor_location(self, actor_path, x, y, z):
        """Move an actor to a specific location (instant teleport)"""
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
                return True
            else:
                print(f"✗ Failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def set_actor_rotation(self, actor_path, pitch, yaw, roll):
        """Set an actor's rotation (Pitch=up/down, Yaw=left/right, Roll=tilt)"""
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
            if response.status_code == 200:
                return True
            else:
                print(f"✗ Failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

if __name__ == "__main__":
    controller = UnrealController()
    
    # CORRECT PATH
    actor_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    
    print("="*60)
    print("REMOTE CHARACTER CONTROL TEST")
    print("="*60)
    print("\n⚠️  IMPORTANT: Make sure Unreal is in EDIT MODE (NOT playing)")
    print("   Do NOT click the Play button!")
    print("\n💡 TIP: In Unreal, click on the character in the World Outliner")
    print("   or viewport, then press 'F' to focus the camera on it.\n")
    print("="*60)
    
    # Get initial location
    print("\n1. Getting initial location...")
    initial_loc = controller.get_actor_location(actor_path)
    if initial_loc:
        print(f"   Initial position: X={initial_loc[0]:.1f}, Y={initial_loc[1]:.1f}, Z={initial_loc[2]:.1f}")
    else:
        print("   ✗ Could not get initial location")
    
    # Move to different positions with rotation
    positions = [
        (0, 0, 100),
        (200, 0, 100),
        (200, 200, 100),
        (0, 200, 100),
        (0, 0, 100)
    ]
    
    print("\n2. Moving character through waypoints with rotation...")
    yaw = 0  # Starting rotation
    
    for i, (x, y, z) in enumerate(positions, 1):
        print(f"\n   Waypoint {i}: Moving to ({x}, {y}, {z}) with rotation {yaw}°...")
        
        # Move position
        if controller.set_actor_location(actor_path, x, y, z):
            time.sleep(0.5)  # Wait for Unreal to update
            
            # Set rotation
            controller.set_actor_rotation(actor_path, pitch=0, yaw=yaw, roll=0)
            print(f"   ↻ Rotated to {yaw}° (Yaw)")
            
            # Verify the move
            current_loc = controller.get_actor_location(actor_path)
            if current_loc:
                actual_x, actual_y, actual_z = current_loc
                print(f"   ✓ Confirmed at: X={actual_x:.1f}, Y={actual_y:.1f}, Z={actual_z:.1f}")
                
                # Check if we're close to target (within 1 unit)
                if abs(actual_x - x) < 1 and abs(actual_y - y) < 1 and abs(actual_z - z) < 1:
                    print(f"   ✓ Position verified!")
                else:
                    print(f"   ⚠️  Position mismatch!")
            else:
                print(f"   ⚠️  Could not verify position")
        
        # Rotate 45 degrees for next waypoint
        yaw = (yaw + 45) % 360
        
        time.sleep(2)  # Longer wait so you can see the movement in viewport
    
    # Get final location
    print("\n3. Getting final location...")
    final_loc = controller.get_actor_location(actor_path)
    if final_loc:
        print(f"   Final position: X={final_loc[0]:.1f}, Y={final_loc[1]:.1f}, Z={final_loc[2]:.1f}")
    
    print("\n" + "="*60)
    print("✓ TEST COMPLETE!")
    print("="*60)
    print("\nNOTE: The character 'teleports' instantly to each position.")
    print("This is different from 'walking' which would animate the movement.")
    print("="*60)
