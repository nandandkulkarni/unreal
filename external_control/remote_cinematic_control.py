"""
Create Cinematic Sequence via Remote Control API
Uses Remote Control to call Unreal functions directly (no Python script execution needed)

This demonstrates what Remote Control API CAN do in UE 5.7
"""

import requests
import json
import time

class UnrealRemoteController:
    def __init__(self, host='localhost', port=30010):
        self.base_url = f'http://{host}:{port}/remote/object/call'
    
    def call_function(self, object_path, function_name, parameters=None):
        """Call a function on an Unreal object"""
        payload = {
            'objectPath': object_path,
            'functionName': function_name,
            'parameters': parameters or {},
            'generateTransaction': False
        }
        
        try:
            response = requests.put(self.base_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.text
        except Exception as e:
            return False, str(e)
    
    def create_sequence_asset(self, asset_name, package_path):
        """Create a Level Sequence asset"""
        print(f"Creating Level Sequence: {package_path}/{asset_name}")
        
        # Call EditorAssetLibrary to create asset
        success, result = self.call_function(
            '/Script/UnrealEd.Default__EditorAssetLibrary',
            'MakeDirectory',
            {'DirectoryPath': package_path}
        )
        
        if success:
            print(f"✓ Directory created/verified: {package_path}")
        
        # Note: Creating complex assets like LevelSequence requires factory classes
        # which aren't directly accessible via Remote Control
        print("Note: Asset creation requires factory classes not exposed to Remote Control")
        return False, "Asset creation requires Python API inside Unreal"
    
    def move_character(self, character_path, x, y, z):
        """Move character to location"""
        print(f"Moving character to ({x}, {y}, {z})")
        
        success, result = self.call_function(
            character_path,
            'K2_SetActorLocation',
            {
                'NewLocation': {'X': x, 'Y': y, 'Z': z},
                'bSweep': False,
                'bTeleport': True
            }
        )
        
        if success:
            print(f"✓ Character moved successfully")
            return True
        else:
            print(f"✗ Failed to move character: {result}")
            return False
    
    def rotate_character(self, character_path, yaw):
        """Rotate character"""
        success, result = self.call_function(
            character_path,
            'K2_SetActorRotation',
            {
                'NewRotation': {'Pitch': 0, 'Yaw': yaw, 'Roll': 0},
                'bTeleportPhysics': True
            }
        )
        
        if success:
            print(f"✓ Character rotated to {yaw}°")
            return True
        return False
    
    def play_sequence(self, sequence_path):
        """Play a Level Sequence"""
        print(f"Playing sequence: {sequence_path}")
        
        # Use LevelSequenceEditorBlueprintLibrary to open/play sequence
        success, result = self.call_function(
            '/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary',
            'OpenLevelSequence',
            {'LevelSequence': sequence_path}
        )
        
        if success:
            print("✓ Sequence opened")
            
            # Play it
            success2, result2 = self.call_function(
                '/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary',
                'Play'
            )
            
            if success2:
                print("✓ Sequence playing!")
                return True
        
        print(f"✗ Failed: {result}")
        return False
    
    def demonstrate_character_animation(self, character_path):
        """Demonstrate moving character through waypoints via Remote Control"""
        print("\n" + "=" * 60)
        print("DEMONSTRATING REMOTE CHARACTER CONTROL")
        print("=" * 60)
        print("This shows what Remote Control API CAN do:\n")
        
        waypoints = [
            (0, 0, 100, 0),
            (300, 0, 100, 90),
            (300, 300, 100, 180),
            (0, 300, 100, 270),
            (0, 0, 100, 0)
        ]
        
        for i, (x, y, z, yaw) in enumerate(waypoints, 1):
            print(f"\n[Waypoint {i}/{len(waypoints)}]")
            
            if self.move_character(character_path, x, y, z):
                self.rotate_character(character_path, yaw)
                time.sleep(1)  # Wait between moves
            else:
                print("✗ Failed to complete animation")
                return False
        
        print("\n" + "=" * 60)
        print("✓ Character animation complete via Remote Control!")
        print("=" * 60)
        return True

def main():
    print("=" * 60)
    print("CINEMATIC CREATION VIA REMOTE CONTROL API")
    print("=" * 60)
    print("\nThis script demonstrates:")
    print("  ✓ Moving actors remotely")
    print("  ✓ Rotating actors remotely")
    print("  ✓ Playing sequences remotely")
    print("  ✗ Creating sequences (requires Python API inside Unreal)")
    print("\n" + "=" * 60)
    
    print("\nPrerequisites:")
    print("  1. Unreal Engine running")
    print("  2. Run in console: WebControl.StartServer")
    print("  3. Level with BP_ThirdPersonCharacter_C loaded")
    print("  4. Sequence created (run create_complete_cinematic.py in Unreal)")
    print("")
    
    controller = UnrealRemoteController()
    
    # Character path
    character_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    
    # Demonstrate character movement via Remote Control
    print("\n" + "=" * 60)
    print("STEP 1: Animate character through waypoints")
    print("=" * 60)
    controller.demonstrate_character_animation(character_path)
    
    # Play existing sequence
    print("\n" + "=" * 60)
    print("STEP 2: Play cinematic sequence (if it exists)")
    print("=" * 60)
    sequence_path = '/Game/Sequences/CharacterWalkSequence.CharacterWalkSequence'
    controller.play_sequence(sequence_path)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✓ Remote Control API works for:")
    print("  - Moving/rotating actors")
    print("  - Playing sequences")
    print("  - Calling Blueprint functions")
    print("\n✗ Remote Control API cannot:")
    print("  - Create complex assets (Level Sequences)")
    print("  - Execute arbitrary Python scripts")
    print("\n💡 Solution:")
    print("  - Create sequences with Python inside Unreal")
    print("  - Use Remote Control to trigger playback & control")
    print("=" * 60)

if __name__ == "__main__":
    main()
