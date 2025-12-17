"""
Create Two Character Cinematic Scene
Run this INSIDE UNREAL: Tools → Execute Python Script

Creates:
- 2 characters walking same path (side by side)
- Camera tracking both characters
- 10-second sequence
"""

import unreal

def delete_existing_sequence():
    """Delete old sequence if it exists"""
    sequence_path = "/Game/TwoCharacterSequence"
    existing = unreal.load_asset(sequence_path)
    if existing:
        print(f"Deleting existing sequence: {sequence_path}")
        unreal.EditorAssetLibrary.delete_asset(sequence_path)

def create_two_character_sequence():
    """Create complete cinematic with 2 characters"""
    
    print("=" * 60)
    print("Creating Two Character Cinematic Scene")
    print("=" * 60)
    
    # Delete old sequence
    delete_existing_sequence()
    
    # Create new Level Sequence
    print("\n1. Creating Level Sequence...")
    sequence_path = "/Game/TwoCharacterSequence"
    sequence = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "TwoCharacterSequence",
        "/Game",
        unreal.LevelSequence,
        unreal.LevelSequenceFactoryNew()
    )
    
    # Set sequence length (10 seconds at 30fps = 300 frames)
    sequence.set_playback_end(300)
    sequence.set_display_rate(unreal.FrameRate(30, 1))
    
    print(f"   ✓ Created: {sequence_path}")
    
    # Get world
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    # Spawn 2 characters
    print("\n2. Spawning characters...")
    character_class = unreal.load_class(None, "/Script/Engine.Character")
    
    # Character 1 - left side
    character1_location = unreal.Vector(0, -100, 0)
    character1 = world.spawn_actor(character_class, character1_location, unreal.Rotator())
    character1.set_actor_label("Character1")
    print(f"   ✓ Spawned Character 1 at Y=-100")
    
    # Character 2 - right side (200cm away)
    character2_location = unreal.Vector(0, 100, 0)
    character2 = world.spawn_actor(character_class, character2_location, unreal.Rotator())
    character2.set_actor_label("Character2")
    print(f"   ✓ Spawned Character 2 at Y=100")
    
    # Add characters to sequence
    print("\n3. Adding characters to sequence...")
    character1_binding = sequence.add_possessable(character1)
    character2_binding = sequence.add_possessable(character2)
    print("   ✓ Characters bound to sequence")
    
    # Define waypoints (same for both, just offset by 200cm in Y)
    waypoints = [
        unreal.Vector(0, 0, 0),
        unreal.Vector(500, 0, 0),
        unreal.Vector(500, 500, 0),
        unreal.Vector(0, 500, 0),
        unreal.Vector(0, 0, 0)
    ]
    
    offset_y_char1 = -100
    offset_y_char2 = 100
    
    # Create animation for Character 1
    print("\n4. Creating animation for Character 1...")
    character1_track = character1_binding.add_track(unreal.MovieScene3DTransformTrack)
    character1_section = character1_track.add_section()
    character1_section.set_range(0, 300)
    
    frames_per_waypoint = 300 // (len(waypoints) - 1)
    
    for i, waypoint in enumerate(waypoints):
        frame = i * frames_per_waypoint
        location = unreal.Vector(waypoint.x, waypoint.y + offset_y_char1, waypoint.z)
        
        # Set location keyframe
        channel_x = character1_section.get_channels_by_type(unreal.MovieSceneScriptingDoubleChannel)[0]
        channel_y = character1_section.get_channels_by_type(unreal.MovieSceneScriptingDoubleChannel)[1]
        channel_z = character1_section.get_channels_by_type(unreal.MovieSceneScriptingDoubleChannel)[2]
        
        channel_x.add_key(unreal.FrameNumber(frame), location.x, interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
        channel_y.add_key(unreal.FrameNumber(frame), location.y, interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
        channel_z.add_key(unreal.FrameNumber(frame), location.z, interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    
    print(f"   ✓ Added {len(waypoints)} waypoints for Character 1")
    
    # Create animation for Character 2 (same waypoints, different offset)
    print("\n5. Creating animation for Character 2...")
    character2_track = character2_binding.add_track(unreal.MovieScene3DTransformTrack)
    character2_section = character2_track.add_section()
    character2_section.set_range(0, 300)
    
    for i, waypoint in enumerate(waypoints):
        frame = i * frames_per_waypoint
        location = unreal.Vector(waypoint.x, waypoint.y + offset_y_char2, waypoint.z)
        
        # Set location keyframe
        channel_x = character2_section.get_channels_by_type(unreal.MovieSceneScriptingDoubleChannel)[0]
        channel_y = character2_section.get_channels_by_type(unreal.MovieSceneScriptingDoubleChannel)[1]
        channel_z = character2_section.get_channels_by_type(unreal.MovieSceneScriptingDoubleChannel)[2]
        
        channel_x.add_key(unreal.FrameNumber(frame), location.x, interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
        channel_y.add_key(unreal.FrameNumber(frame), location.y, interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
        channel_z.add_key(unreal.FrameNumber(frame), location.z, interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    
    print(f"   ✓ Added {len(waypoints)} waypoints for Character 2")
    
    # Create camera
    print("\n6. Creating cinematic camera...")
    camera_class = unreal.load_class(None, "/Script/CinematicCamera.CineCameraActor")
    camera_location = unreal.Vector(-800, 0, 300)  # Pulled back to see both
    camera_rotation = unreal.Rotator(-10, 0, 0)
    camera = world.spawn_actor(camera_class, camera_location, camera_rotation)
    camera.set_actor_label("CinematicCamera")
    
    # Wider FOV to capture both characters
    camera_component = camera.get_cine_camera_component()
    camera_component.set_editor_property('field_of_view', 70.0)
    
    print("   ✓ Camera created with wide FOV")
    
    # Add camera to sequence
    camera_binding = sequence.add_possessable(camera)
    
    # Create camera track
    camera_track = camera_binding.add_track(unreal.MovieScene3DTransformTrack)
    camera_section = camera_track.add_section()
    camera_section.set_range(0, 300)
    
    # Camera orbital movement (follows center point between characters)
    print("\n7. Setting up camera movement...")
    num_camera_keyframes = 5
    for i in range(num_camera_keyframes):
        frame = int((i / (num_camera_keyframes - 1)) * 300)
        angle = (i / (num_camera_keyframes - 1)) * 360
        
        radius = 800
        center_x = 250  # Middle of path
        center_y = 0    # Centered between both characters
        
        import math
        cam_x = center_x + radius * math.cos(math.radians(angle))
        cam_y = center_y + radius * math.sin(math.radians(angle))
        cam_z = 300
        
        location = unreal.Vector(cam_x, cam_y, cam_z)
        
        # Calculate rotation to look at center
        direction = unreal.Vector(center_x - cam_x, center_y - cam_y, 0 - cam_z)
        rotation = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(0, 0, 0), direction)
        
        # Set keyframes
        channels = camera_section.get_channels_by_type(unreal.MovieSceneScriptingDoubleChannel)
        channels[0].add_key(unreal.FrameNumber(frame), location.x)  # X
        channels[1].add_key(unreal.FrameNumber(frame), location.y)  # Y
        channels[2].add_key(unreal.FrameNumber(frame), location.z)  # Z
        channels[3].add_key(unreal.FrameNumber(frame), rotation.roll)
        channels[4].add_key(unreal.FrameNumber(frame), rotation.pitch)
        channels[5].add_key(unreal.FrameNumber(frame), rotation.yaw)
    
    print(f"   ✓ Added {num_camera_keyframes} camera keyframes")
    
    # Add Camera Cut track
    print("\n8. Adding Camera Cut track...")
    camera_cut_track = sequence.add_track(unreal.MovieSceneCameraCutTrack)
    camera_cut_section = camera_cut_track.add_section()
    camera_cut_section.set_range(0, 300)
    
    # Set camera binding
    camera_binding_id = camera_cut_section.get_editor_property('camera_binding_id')
    camera_binding_id.guid = camera_binding.get_id()
    
    print("   ✓ Camera cut track added")
    
    # Save everything
    print("\n9. Saving assets...")
    unreal.EditorAssetLibrary.save_loaded_asset(sequence)
    
    print("\n" + "=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print(f"\nSequence created: {sequence_path}")
    print("- 2 characters walking side by side")
    print("- Same waypoint path")
    print("- Camera tracking both")
    print("\nNext steps:")
    print("1. Test playback: python remote_camera_fix_and_test.py")
    print("2. Render video: render_sequence_to_video.py (in Unreal)")
    print("=" * 60)

if __name__ == "__main__":
    create_two_character_sequence()
