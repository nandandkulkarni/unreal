"""
Record actor movements using Unreal's Take Recorder.
This creates a Level Sequence that can be played back with full GPU rendering.

SAVE LOCATION:
By default, Take Recorder saves to:
  Content/Cinematics/Takes/[Date]/[TakeName]
  
For example:
  /Game/Cinematics/Takes/2024-12-15/Scene_001_01

The recording creates:
  - A Level Sequence asset (the animation)
  - A Take Metadata asset (info about the take)
"""
import requests
import json
import time

class TakeRecorderController:
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
            print(f"  {function_name}: {resp.status_code}")
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"    Response: {resp.text[:300]}")
                return None
        except Exception as e:
            print(f"  Exception: {e}")
            return None

    def set_actor_location(self, actor_path, x, y, z):
        """Move actor to position"""
        url = f'{self.base_url}/remote/object/call'
        payload = {
            'objectPath': actor_path,
            'functionName': 'K2_SetActorLocation',
            'parameters': {'NewLocation': {'X': x, 'Y': y, 'Z': z}},
            'generateTransaction': True
        }
        try:
            return requests.put(url, json=payload, timeout=2).status_code == 200
        except:
            return False

    def set_actor_rotation(self, actor_path, pitch, yaw, roll):
        """Set actor rotation"""
        url = f'{self.base_url}/remote/object/call'
        payload = {
            'objectPath': actor_path,
            'functionName': 'K2_SetActorRotation',
            'parameters': {'NewRotation': {'Pitch': pitch, 'Yaw': yaw, 'Roll': roll}},
            'generateTransaction': True
        }
        try:
            return requests.put(url, json=payload, timeout=2).status_code == 200
        except:
            return False

    def is_take_recorder_recording(self):
        """Check if Take Recorder is currently recording"""
        result = self.call_function(
            '/Script/TakeRecorder.Default__TakeRecorderBlueprintLibrary',
            'IsRecording'
        )
        if result and 'ReturnValue' in result:
            return result['ReturnValue']
        return False

    def get_take_recorder_panel(self):
        """Get the Take Recorder panel"""
        result = self.call_function(
            '/Script/TakeRecorder.Default__TakeRecorderBlueprintLibrary',
            'GetTakeRecorderPanel'
        )
        return result

    def start_recording(self):
        """Start Take Recorder recording"""
        print("\nStarting Take Recorder...")
        
        # Method 1: Try TakeRecorderBlueprintLibrary
        result = self.call_function(
            '/Script/TakeRecorder.Default__TakeRecorderBlueprintLibrary',
            'StartRecording'
        )
        
        if result:
            print("  ✓ Take Recorder started!")
            return True
        
        print("  Take Recorder may need to be opened manually first.")
        print("  In Unreal: Window > Cinematics > Take Recorder")
        return False

    def stop_recording(self):
        """Stop Take Recorder recording"""
        print("\nStopping Take Recorder...")
        result = self.call_function(
            '/Script/TakeRecorder.Default__TakeRecorderBlueprintLibrary',
            'StopRecording'
        )
        if result:
            print("  ✓ Recording stopped!")
        return result is not None


def record_with_take_recorder():
    """Record movements using Take Recorder"""
    controller = TakeRecorderController()
    actor_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    
    print("="*60)
    print("TAKE RECORDER - MOVEMENT CAPTURE")
    print("="*60)
    print("""
SAVE LOCATION:
  Your recording will be saved to:
  Content/Cinematics/Takes/[Date]/[TakeName]

BEFORE RUNNING:
  1. Open Take Recorder: Window > Cinematics > Take Recorder
  2. Add the actor you want to record (BP_ThirdPersonCharacter_C_1)
  3. Set your take name/settings as desired
  4. Then run this script
""")
    print("="*60)
    
    input("\nPress Enter when Take Recorder is open and ready...")
    
    # Start recording
    if not controller.start_recording():
        print("\n⚠️  Could not start recording automatically.")
        print("   Please click the Record button in Take Recorder manually,")
        print("   then press Enter to continue...")
        input()
    
    print("\n📹 Recording movement sequence...")
    time.sleep(1)  # Give Take Recorder time to initialize
    
    # Define movement path
    positions = [
        (0, 0, 100, 0),      # x, y, z, yaw
        (300, 0, 100, 45),
        (300, 300, 100, 90),
        (0, 300, 100, 135),
        (0, 0, 100, 180),
    ]
    
    for i, (x, y, z, yaw) in enumerate(positions, 1):
        print(f"\n  Waypoint {i}/{len(positions)}: ({x}, {y}, {z}) @ {yaw}°")
        
        # Move actor
        controller.set_actor_location(actor_path, x, y, z)
        controller.set_actor_rotation(actor_path, 0, yaw, 0)
        
        # Wait for next keyframe
        time.sleep(1.5)
    
    # Stop recording
    print("\n" + "-"*40)
    controller.stop_recording()
    
    print("\n" + "="*60)
    print("✓ RECORDING COMPLETE!")
    print("="*60)
    print("""
YOUR RECORDING IS SAVED IN:
  Content Browser > Cinematics > Takes > [Today's Date]

TO PLAY BACK:
  1. Double-click the Level Sequence to open in Sequencer
  2. Press the Play button (or Spacebar)
  3. The animation will play with full GPU rendering!

TO RENDER TO VIDEO:
  1. Open the Level Sequence in Sequencer
  2. Click the clapperboard icon > Render Movie
  3. Choose your output settings and render
""")
    print("="*60)


if __name__ == '__main__':
    record_with_take_recorder()
