"""
Pure Unreal Python Script - Add Keyframe to Mannequin

This script runs INSIDE Unreal Engine's Python interpreter.
It adds a keyframe to TestMannequin1's transform track at 5 seconds.
"""
import unreal

# Configuration
MANNEQUIN_NAME = "TestMannequin1"
KEYFRAME_TIME_SECONDS = 5.0

try:
    print("=" * 60)
    print("Adding Keyframe to Mannequin Track")
    print("=" * 60)
    
    # Find the most recent Test* sequence
    print("\nFinding most recent Test* sequence...")
    sequences_path = "/Game/Sequences"
    
    if not unreal.EditorAssetLibrary.does_directory_exist(sequences_path):
        print("✗ ERROR: Sequences directory not found: " + sequences_path)
    else:
        assets = unreal.EditorAssetLibrary.list_assets(sequences_path, recursive=False)
        
        test_sequences = []
        for asset_path in assets:
            asset_name = asset_path.split('/')[-1].split('.')[0]
            if asset_name.startswith("Test"):
                test_sequences.append(asset_path)
        
        if len(test_sequences) == 0:
            print("✗ ERROR: No sequences starting with 'Test' found")
        else:
            sequence_path = test_sequences[-1]
            sequence = unreal.load_asset(sequence_path)
            
            if sequence:
                print("✓ Using sequence: " + sequence.get_name())
                
                # Get sequence settings
                display_rate = unreal.MovieSceneSequenceExtensions.get_display_rate(sequence)
                fps = display_rate.numerator / display_rate.denominator
                keyframe_time_frames = int(KEYFRAME_TIME_SECONDS * fps)
                
                print("  FPS: " + str(fps))
                print("  Keyframe time: " + str(KEYFRAME_TIME_SECONDS) + "s (" + str(keyframe_time_frames) + " frames)")
                
                # Find the mannequin binding
                print("\nFinding mannequin binding...")
                bindings = unreal.MovieSceneSequenceExtensions.get_bindings(sequence)
                mannequin_binding = None
                
                for binding in bindings:
                    if str(binding.get_display_name()) == MANNEQUIN_NAME:
                        mannequin_binding = binding
                        print("✓ Found binding: " + str(binding.get_display_name()))
                        break
                
                if not mannequin_binding:
                    print("✗ ERROR: Mannequin binding not found: " + MANNEQUIN_NAME)
                    print("  Run run_add_mannequin.py first to add the mannequin to the sequence")
                else:
                    # Get the transform track
                    print("\nFinding transform track...")
                    tracks = unreal.MovieSceneBindingExtensions.get_tracks(mannequin_binding)
                    print("  Total tracks: " + str(len(tracks)))
                    
                    transform_track = None
                    for track in tracks:
                        track_class = track.get_class().get_name()
                        print("  Track type: " + track_class)
                        if "Transform" in track_class or isinstance(track, unreal.MovieScene3DTransformTrack):
                            transform_track = track
                            print("✓ Found transform track")
                            break
                    
                    if not transform_track:
                        print("  Transform track not found, creating one...")
                        transform_track = unreal.MovieSceneBindingExtensions.add_track(
                            mannequin_binding,
                            unreal.MovieScene3DTransformTrack
                        )
                        if transform_track:
                            print("✓ Created new transform track")
                        else:
                            print("✗ ERROR: Failed to create transform track")
                    
                    if transform_track:
                        # Get or add section
                        print("\nGetting section...")
                        sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
                        print("  Total sections: " + str(len(sections)))
                        
                        if len(sections) == 0:
                            print("  No sections found, creating one...")
                            section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
                            if section:
                                # Set section range to cover the sequence
                                playback_start = unreal.MovieSceneSequenceExtensions.get_playback_start(sequence)
                                playback_end = unreal.MovieSceneSequenceExtensions.get_playback_end(sequence)
                                unreal.MovieSceneSectionExtensions.set_range(section, playback_start, playback_end)
                                print("✓ Created section with range: " + str(playback_start) + " to " + str(playback_end))
                            else:
                                print("✗ ERROR: Failed to create section")
                        else:
                            section = sections[0]
                            print("✓ Got existing section")
                        
                        if section:
                            # Get the actor to get its current transform
                            print("\nGetting mannequin actor...")
                            editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
                            all_actors = editor_actor_subsystem.get_all_level_actors()
                            
                            mannequin_actor = None
                            for actor in all_actors:
                                if actor.get_actor_label() == MANNEQUIN_NAME:
                                    mannequin_actor = actor
                                    break
                            
                            if not mannequin_actor:
                                print("✗ ERROR: Mannequin actor not found in level")
                            else:
                                # Get current transform
                                current_location = mannequin_actor.get_actor_location()
                                current_rotation = mannequin_actor.get_actor_rotation()
                                current_scale = mannequin_actor.get_actor_scale3d()
                                
                                print("✓ Current transform:")
                                print("  Location: " + str(current_location))
                                print("  Rotation: " + str(current_rotation))
                                print("  Scale: " + str(current_scale))
                                
                                # Move the actor to a new position for the keyframe
                                new_location = unreal.Vector(current_location.x + 200.0, current_location.y, current_location.z)
                                mannequin_actor.set_actor_location(new_location, False, False)
                                
                                print("\nNew position for keyframe:")
                                print("  Location: " + str(new_location))
                                
                                # Get channels and add keyframe
                                print("\nAdding keyframe at " + str(KEYFRAME_TIME_SECONDS) + " seconds...")
                                
                                # Get all channels from the section
                                channels = unreal.MovieSceneSectionExtensions.get_all_channels(section)
                                print("  Found " + str(len(channels)) + " channels")
                                
                                if len(channels) < 3:
                                    print("✗ ERROR: Not enough channels found")
                                else:
                                    # Channels are: X, Y, Z, Rot X, Rot Y, Rot Z, Scale X, Scale Y, Scale Z
                                    # Add keyframe to Location X (channel 0) - move 200 units forward
                                    frame_time = unreal.FrameNumber(keyframe_time_frames)
                                    
                                    # Add key to X channel (move forward)
                                    x_channel = channels[0]
                                    new_x = current_location.x + 200.0
                                    
                                    # Use DoubleChannel instead of FloatChannel
                                    key = unreal.MovieSceneScriptingDoubleChannel.add_key(
                                        x_channel,
                                        frame_time,
                                        new_x,
                                        0.0  # SubFrame
                                    )
                                    
                                    if key:
                                        print("✓ Keyframe added to X channel")
                                        print("  Frame: " + str(keyframe_time_frames))
                                        print("  Value: " + str(new_x))
                                    else:
                                        print("✗ ERROR: Failed to add keyframe")
                                    
                                    # Also add keys for Y and Z to keep them constant
                                    y_channel = channels[1]
                                    z_channel = channels[2]
                                    
                                    unreal.MovieSceneScriptingDoubleChannel.add_key(
                                        y_channel, frame_time, current_location.y, 0.0
                                    )
                                    unreal.MovieSceneScriptingDoubleChannel.add_key(
                                        z_channel, frame_time, current_location.z, 0.0
                                    )
                                    
                                    # Verify keyframe was added
                                    print("\nVerifying keyframe...")
                                    keys = unreal.MovieSceneScriptingDoubleChannel.get_keys(x_channel)
                                    print("  Total keys in X channel: " + str(len(keys)))
                                    
                                    # Check if our keyframe is there
                                    keyframe_found = False
                                    for key in keys:
                                        # Use get_time method on the key directly
                                        key_time = key.get_time()
                                        key_frame = key_time.frame_number.value
                                        if key_frame == keyframe_time_frames:
                                            key_value = key.get_value()
                                            keyframe_found = True
                                            print("  ✓ Keyframe verified at frame " + str(key_frame))
                                            print("    Value: " + str(key_value))
                                            break
                                    
                                    if not keyframe_found:
                                        print("  ✗ WARNING: Keyframe not found in channel!")
                                    
                                    # Save the sequence
                                    print("\nSaving sequence...")
                                    saved = unreal.EditorAssetLibrary.save_loaded_asset(sequence)
                                    if saved:
                                        print("✓ Sequence saved")
                                    
                                    print("=" * 60)
                                    print("✓ Keyframe successfully added!")
                                    print("  Sequence: " + sequence.get_name())
                                    print("  Time: " + str(KEYFRAME_TIME_SECONDS) + "s (frame " + str(keyframe_time_frames) + ")")
                                    print("  New X position: " + str(new_x))
                                    print("=" * 60)
                        else:
                            print("✗ ERROR: No valid section found")
            else:
                print("✗ ERROR: Failed to load sequence")

except Exception as e:
    print("\n" + "=" * 60)
    print("✗ FATAL ERROR")
    print("=" * 60)
    print("Error type: " + type(e).__name__)
    print("Error message: " + str(e))
    
    import traceback
    print("\nFull traceback:")
    for line in traceback.format_exc().split('\n'):
        if line:
            print("  " + line)
    print("=" * 60)

print("\nDone!")
