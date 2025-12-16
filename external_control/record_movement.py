"""
Record actor movements to Unreal Sequencer via Remote Control API.
This creates keyframes that can be played back as a cinematic.
"""
import requests
import json
import time

class UnrealSequencerController:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}'
    
    def call_function(self, object_path, function_name, parameters=None):
        """Call a function on a UObject"""
        url = f'{self.base_url}/remote/object/call'
        payload = {
            'objectPath': object_path,
            'functionName': function_name,
            'generateTransaction': True
        }
        if parameters:
            payload['parameters'] = parameters
        
        try:
            resp = requests.put(url, json=payload, timeout=5)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"  Call failed: {resp.status_code} - {resp.text[:200]}")
                return None
        except Exception as e:
            print(f"  Exception: {e}")
            return None

    def set_property(self, object_path, property_name, value):
        """Set a property on a UObject"""
        url = f'{self.base_url}/remote/object/property'
        payload = {
            'objectPath': object_path,
            'propertyName': property_name,
            'propertyValue': value,
            'access': 'WRITE_TRANSACTION_ACCESS'
        }
        
        try:
            resp = requests.put(url, json=payload, timeout=5)
            return resp.status_code == 200
        except Exception as e:
            print(f"  Exception: {e}")
            return False

    def get_property(self, object_path, property_name):
        """Get a property from a UObject"""
        url = f'{self.base_url}/remote/object/property'
        payload = {
            'objectPath': object_path,
            'propertyName': property_name,
            'access': 'READ_ACCESS'
        }
        
        try:
            resp = requests.put(url, json=payload, timeout=5)
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            print(f"  Exception: {e}")
            return None

    def set_actor_location(self, actor_path, x, y, z):
        """Move actor to position"""
        return self.call_function(actor_path, 'K2_SetActorLocation', {
            'NewLocation': {'X': x, 'Y': y, 'Z': z}
        })

    def set_actor_rotation(self, actor_path, pitch, yaw, roll):
        """Set actor rotation"""
        return self.call_function(actor_path, 'K2_SetActorRotation', {
            'NewRotation': {'Pitch': pitch, 'Yaw': yaw, 'Roll': roll}
        })

    def start_recording(self):
        """Start Sequencer recording via Take Recorder"""
        # Try to start Take Recorder
        result = self.call_function(
            '/Script/TakeRecorder.Default__TakeRecorderBlueprintLibrary',
            'StartRecording'
        )
        return result is not None

    def stop_recording(self):
        """Stop Sequencer recording"""
        result = self.call_function(
            '/Script/TakeRecorder.Default__TakeRecorderBlueprintLibrary', 
            'StopRecording'
        )
        return result is not None


class SimpleMovementRecorder:
    """
    Alternative approach: Record movement data to a JSON file,
    then create a Python script that plays it back.
    """
    def __init__(self):
        self.keyframes = []
        self.start_time = None
    
    def start(self):
        self.keyframes = []
        self.start_time = time.time()
        print("Recording started...")
    
    def add_keyframe(self, x, y, z, pitch=0, yaw=0, roll=0):
        elapsed = time.time() - self.start_time
        self.keyframes.append({
            'time': elapsed,
            'location': {'X': x, 'Y': y, 'Z': z},
            'rotation': {'Pitch': pitch, 'Yaw': yaw, 'Roll': roll}
        })
        print(f"  Keyframe at {elapsed:.2f}s: ({x}, {y}, {z})")
    
    def stop(self):
        print(f"Recording stopped. {len(self.keyframes)} keyframes captured.")
        return self.keyframes
    
    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump({
                'actor_path': '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1',
                'keyframes': self.keyframes
            }, f, indent=2)
        print(f"Saved to {filename}")


def record_movement():
    """Record a movement sequence"""
    controller = UnrealSequencerController()
    recorder = SimpleMovementRecorder()
    
    actor_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    
    print("="*60)
    print("RECORDING MOVEMENT SEQUENCE")
    print("="*60)
    
    positions = [
        (0, 0, 100, 0),      # x, y, z, yaw
        (300, 0, 100, 45),
        (300, 300, 100, 90),
        (0, 300, 100, 135),
        (0, 0, 100, 180),
    ]
    
    recorder.start()
    
    for i, (x, y, z, yaw) in enumerate(positions, 1):
        print(f"\nWaypoint {i}...")
        
        # Move the actor
        controller.set_actor_location(actor_path, x, y, z)
        controller.set_actor_rotation(actor_path, 0, yaw, 0)
        
        # Record the keyframe
        recorder.add_keyframe(x, y, z, 0, yaw, 0)
        
        time.sleep(1)  # Wait between keyframes
    
    recorder.stop()
    recorder.save('movement_recording.json')
    
    print("\n" + "="*60)
    print("✓ RECORDING COMPLETE!")
    print("="*60)
    print("\nRun 'python playback_movement.py' to play it back")


if __name__ == '__main__':
    record_movement()
