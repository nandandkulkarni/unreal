"""
Pure Unreal Python Script - Complete Scene Setup

This script runs INSIDE Unreal Engine's Python interpreter.
It creates a complete cinematic scene:
1. Deletes old Test* sequences, cameras, and mannequins
2. Creates a new sequence with timestamp
3. Creates a camera
4. Creates a mannequin
5. Adds both to the sequence

Usage: Open this file in VS Code and press Ctrl+Enter to run
"""
import unreal
from datetime import datetime
import os

# Setup logging
log_dir = r"C:\RemoteProjects\reference\unreal\direct"
log_file = os.path.join(log_dir, "scene_setup.log")

def log(message):
    """Print and write to log file"""
    print(message)
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Warning: Could not write to log: {e}")

try:
    log("=" * 60)
    log("Complete Cinematic Scene Setup")
    log("=" * 60)
    
    # Get timestamp and find next sequence number
    timestamp = datetime.now().strftime("%y_%m_%d_%H_%M_%S")
    
    # Find existing Test* sequences to determine next number
    sequences_path = "/Game/Sequences"
    next_num = 1
    
    if unreal.EditorAssetLibrary.does_directory_exist(sequences_path):
        assets = unreal.EditorAssetLibrary.list_assets(sequences_path, recursive=False)
        existing_nums = []
        for asset_path in assets:
            asset_name = asset_path.split('/')[-1].split('.')[0]
            if asset_name.startswith("TestSequence_"):
                # Extract number from name like TestSequence_25_12_18_02_20_42_001
                parts = asset_name.split('_')
                if len(parts) >= 8:  # Has timestamp and number
                    try:
                        num = int(parts[-1])
                        existing_nums.append(num)
                    except:
                        pass
        
        if existing_nums:
            next_num = max(existing_nums) + 1
    
    # Format number with leading zeros
    sequence_name = f"TestSequence_{timestamp}_{next_num:03d}"
    camera_name = f"TestCamera_{timestamp}_{next_num:03d}"
    mannequin_name = f"TestMannequin_{timestamp}_{next_num:03d}"
    
    log(f"\nCreating scene #{next_num}")
    log(f"  Sequence: {sequence_name}")
    log(f"  Camera: {camera_name}")
    log(f"  Mannequin: {mannequin_name}")
    
    # ===== STEP 1: Delete old Test* assets =====
    log("\n" + "=" * 60)
    log("STEP 1: Cleaning up old Test* assets")
    log("=" * 60)
    
    # Close any currently open sequences first
    log("\nClosing any open sequences...")
    try:
        current_seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        if current_seq:
            log(f"  Closing: {current_seq.get_name()}")
            unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
            log("✓ Closed open sequence")
        else:
            log("  No sequence currently open")
    except Exception as e:
        log(f"  Could not close sequence: {e}")
    
    # Delete old sequences
    log("\nDeleting old Test* sequences...")
    sequences_path = "/Game/Sequences"
    deleted_sequences = 0
    
    if unreal.EditorAssetLibrary.does_directory_exist(sequences_path):
        assets = unreal.EditorAssetLibrary.list_assets(sequences_path, recursive=False)
        for asset_path in assets:
            asset_name = asset_path.split('/')[-1].split('.')[0]
            if asset_name.startswith("Test"):
                try:
                    unreal.EditorAssetLibrary.delete_asset(asset_path)
                    log(f"  Deleted sequence: {asset_name}")
                    deleted_sequences += 1
                except Exception as e:
                    log(f"  Failed to delete {asset_name}: {e}")
    
    if deleted_sequences > 0:
        log(f"✓ Deleted {deleted_sequences} old sequence(s)")
    else:
        log("  No old sequences found")
    
    # Delete old actors
    log("\nDeleting old Test* actors...")
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor_subsystem.get_all_level_actors()
    deleted_actors = 0
    
    for actor in all_actors:
        actor_label = actor.get_actor_label()
        if actor_label.startswith("TestCamera") or actor_label.startswith("TestMannequin"):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            log(f"  Deleted actor: {actor_label}")
            deleted_actors += 1
    
    if deleted_actors > 0:
        log(f"✓ Deleted {deleted_actors} old actor(s)")
    else:
        log("  No old actors found")
    
    # ===== STEP 2: Create new sequence =====
    log("\n" + "=" * 60)
    log("STEP 2: Creating new sequence")
    log("=" * 60)
    
    sequence_path = f"/Game/Sequences/{sequence_name}"
    factory = unreal.LevelSequenceFactoryNew()
    sequence = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        sequence_name,
        "/Game/Sequences",
        unreal.LevelSequence,
        factory
    )
    
    if sequence:
        log(f"✓ Sequence created: {sequence_name}")
        
        # Set sequence properties
        fps = 30
        duration_seconds = 10
        duration_frames = int(fps * duration_seconds)
        
        # Set playback range
        sequence.set_playback_start(0)
        sequence.set_playback_end(duration_frames)
        sequence.set_display_rate(unreal.FrameRate(numerator=int(fps), denominator=1))
        
        log(f"  FPS: {fps}")
        log(f"  Duration: {duration_seconds}s ({duration_frames} frames)")
    else:
        log("✗ ERROR: Failed to create sequence")
        raise Exception("Sequence creation failed")
    
    # ===== STEP 3: Create camera =====
    log("\n" + "=" * 60)
    log("STEP 3: Creating camera")
    log("=" * 60)
    
    camera_location = unreal.Vector(0, -500, 200)
    # Rotate camera to face origin: Pitch=-22 (look down), Yaw=90 (face +Y direction)
    camera_rotation = unreal.Rotator(pitch=-22.0, yaw=90.0, roll=0.0)
    
    camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CineCameraActor,
        camera_location,
        camera_rotation
    )
    
    if camera:
        camera.set_actor_label(camera_name)
        
        # Set camera properties
        camera_component = camera.get_cine_camera_component()
        camera_component.set_editor_property("current_focal_length", 50.0)
        camera_component.set_editor_property("current_aperture", 2.8)
        
        log(f"✓ Camera created: {camera_name}")
        log(f"  Location: {camera_location}")
        log(f"  Rotation: {camera_rotation}")
        log(f"  Focal Length: 50mm")
        log(f"  Aperture: f/2.8")
    else:
        log("✗ ERROR: Failed to create camera")
        raise Exception("Camera creation failed")
    
    # ===== STEP 4: Create mannequin =====
    log("\n" + "=" * 60)
    log("STEP 4: Creating mannequin")
    log("=" * 60)
    
    mannequin_location = unreal.Vector(0, 0, 90)  # Z=90 so character stands on ground
    mannequin_rotation = unreal.Rotator(0, 0, 0)
    
    # Load the skeletal mesh asset directly
    skeletal_mesh = unreal.load_object(None, "/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple")
    
    if not skeletal_mesh:
        # Try alternative path
        skeletal_mesh = unreal.load_object(None, "/Game/ThirdPerson/Characters/Mannequins/Meshes/SKM_Quinn_Simple.SKM_Quinn_Simple")
    
    if skeletal_mesh:
        # Spawn a SkeletalMeshActor
        mannequin = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.SkeletalMeshActor,
            mannequin_location,
            mannequin_rotation
        )
        
        if mannequin:
            mannequin.set_actor_label(mannequin_name)
            
            # Set the skeletal mesh on the component
            skel_comp = mannequin.skeletal_mesh_component
            skel_comp.set_skeletal_mesh(skeletal_mesh)
            
            log(f"✓ Mannequin created: {mannequin_name}")
            log(f"  Location: {mannequin_location}")
            log(f"  Mesh: {skeletal_mesh.get_name()}")
        else:
            log("✗ ERROR: Failed to spawn mannequin")
            raise Exception("Mannequin spawn failed")
    else:
        log("✗ ERROR: Could not load skeletal mesh")
        raise Exception("Skeletal mesh not found")
    
    # ===== STEP 5: Add camera to sequence =====
    log("\n" + "=" * 60)
    log("STEP 5: Adding camera to sequence")
    log("=" * 60)
    
    camera_binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, camera)
    
    if camera_binding:
        log(f"✓ Camera added to sequence: {str(camera_binding.get_display_name())}")
        
        # Add transform track for camera movement
        camera_transform_track = unreal.MovieSceneBindingExtensions.add_track(
            camera_binding, 
            unreal.MovieScene3DTransformTrack
        )
        camera_transform_section = unreal.MovieSceneTrackExtensions.add_section(camera_transform_track)
        unreal.MovieSceneSectionExtensions.set_range(camera_transform_section, 0, duration_frames)
        
        # Add camera movement keyframes - follow the mannequin and get closer
        log("\nAdding camera movement keyframes...")
        camera_transform_sections = unreal.MovieSceneTrackExtensions.get_sections(camera_transform_track)
        if camera_transform_sections:
            cam_section = camera_transform_sections[0]
            cam_channels = cam_section.get_all_channels()
            cam_location_channels = cam_channels[0:3]  # X, Y, Z channels
            
            # Frame 0: Start at (0, -500, 200)
            cam_location_channels[0].add_key(unreal.FrameNumber(0), 0.0)     # X = 0
            cam_location_channels[1].add_key(unreal.FrameNumber(0), -500.0)  # Y = -500
            cam_location_channels[2].add_key(unreal.FrameNumber(0), 200.0)   # Z = 200
            log("  Frame 0: (0, -500, 200)")
            
            # Frame 100: Move to (0, -300, 220)
            cam_location_channels[0].add_key(unreal.FrameNumber(100), 0.0)    # X = 0
            cam_location_channels[1].add_key(unreal.FrameNumber(100), -300.0) # Y = -300
            cam_location_channels[2].add_key(unreal.FrameNumber(100), 220.0)  # Z = 220
            log("  Frame 100: (0, -300, 220)")
            
            # Frame 200: Move to (0, 100, 250)
            cam_location_channels[0].add_key(unreal.FrameNumber(200), 0.0)   # X = 0
            cam_location_channels[1].add_key(unreal.FrameNumber(200), 100.0) # Y = 100
            cam_location_channels[2].add_key(unreal.FrameNumber(200), 250.0) # Z = 250
            log("  Frame 200: (0, 100, 250)")
            
            # Frame 300: End very close at (0, 400, 280)
            cam_location_channels[0].add_key(unreal.FrameNumber(300), 0.0)   # X = 0
            cam_location_channels[1].add_key(unreal.FrameNumber(300), 400.0) # Y = 400
            cam_location_channels[2].add_key(unreal.FrameNumber(300), 280.0) # Z = 280
            log("  Frame 300: (0, 400, 280)")
            
            # Count the keys in each channel
            x_keys = cam_location_channels[0].get_keys()
            y_keys = cam_location_channels[1].get_keys()
            z_keys = cam_location_channels[2].get_keys()
            log(f"  Keyframe count - X: {len(x_keys)}, Y: {len(y_keys)}, Z: {len(z_keys)}")
            
            log("✓ Camera movement: 4 keyframes added")
        
        # Add camera cut track
        camera_cut_track = sequence.add_track(unreal.MovieSceneCameraCutTrack)
        camera_cut_section = camera_cut_track.add_section()
        camera_cut_section.set_range(0, duration_frames)
        
        # Set camera binding - using MovieSceneObjectBindingID with guid as editor property
        try:
            binding_id = unreal.MovieSceneObjectBindingID()
            binding_id.set_editor_property('guid', camera_binding.get_id())
            camera_cut_section.set_camera_binding_id(binding_id)
            log("✓ Camera cut track added with binding")
        except Exception as e:
            log(f"⚠ Warning: Could not set camera binding: {e}")
    else:
        log("⚠ Warning: Failed to add camera binding")
    
    # ===== STEP 6: Add mannequin to sequence =====
    log("\n" + "=" * 60)
    log("STEP 6: Adding mannequin to sequence")
    log("=" * 60)
    
    mannequin_binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, mannequin)
    
    if mannequin_binding:
        log(f"✓ Mannequin added to sequence: {str(mannequin_binding.get_display_name())}")
        
        # Add transform track
        transform_track = unreal.MovieSceneBindingExtensions.add_track(
            mannequin_binding,
            unreal.MovieScene3DTransformTrack
        )
        
        if transform_track:
            section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
            unreal.MovieSceneSectionExtensions.set_range(section, 0, duration_frames)
            log("✓ Transform track added")
        
        # Add skeletal animation track
        anim_track = unreal.MovieSceneBindingExtensions.add_track(
            mannequin_binding,
            unreal.MovieSceneSkeletalAnimationTrack
        )
        
        if anim_track:
            anim_section = unreal.MovieSceneTrackExtensions.add_section(anim_track)
            unreal.MovieSceneSectionExtensions.set_range(anim_section, 0, duration_frames)
            log("✓ Skeletal animation track added")
        
        # Add movement keyframes
        log("\nAdding movement keyframes...")
        transform_sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
        if transform_sections:
            transform_section = transform_sections[0]
            
            # Get the transform channels
            channels = transform_section.get_all_channels()
            location_channels = channels[0:3]  # X, Y, Z channels
            
            # Add keyframes for movement (move forward along Y axis)
            # Start position: (0, 0, 0) at frame 0
            # End position: (0, 500, 0) at frame 300 (10 seconds)
            
            # Frame 0: Start at origin with Z=90
            location_channels[0].add_key(unreal.FrameNumber(0), 0.0)   # X = 0
            location_channels[1].add_key(unreal.FrameNumber(0), 0.0)   # Y = 0
            location_channels[2].add_key(unreal.FrameNumber(0), 90.0)  # Z = 90
            
            # Frame 100: Go up high (0, 166, 500)
            location_channels[0].add_key(unreal.FrameNumber(100), 0.0)    # X = 0
            location_channels[1].add_key(unreal.FrameNumber(100), 166.0)  # Y = 166
            location_channels[2].add_key(unreal.FrameNumber(100), 500.0)  # Z = 500 (up)
            
            # Frame 200: Come down (0, 333, 150)
            location_channels[0].add_key(unreal.FrameNumber(200), 0.0)    # X = 0
            location_channels[1].add_key(unreal.FrameNumber(200), 333.0)  # Y = 333
            location_channels[2].add_key(unreal.FrameNumber(200), 150.0)  # Z = 150 (down)
            
            # Frame 300: Go up again (0, 500, 450)
            location_channels[0].add_key(unreal.FrameNumber(300), 0.0)    # X = 0
            location_channels[1].add_key(unreal.FrameNumber(300), 500.0)  # Y = 500
            location_channels[2].add_key(unreal.FrameNumber(300), 450.0)  # Z = 450 (up again)
            
            log("✓ Movement keyframes added: 4 frames with up-down-up motion")
    else:
        log("⚠ Warning: Failed to add mannequin binding")
    
    # ===== STEP 7: Save and open sequence =====
    log("\n" + "=" * 60)
    log("STEP 7: Finalizing")
    log("=" * 60)
    
    # Save sequence
    saved = unreal.EditorAssetLibrary.save_loaded_asset(sequence)
    if saved:
        log("✓ Sequence saved")
    
    # Open in Sequencer
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
    log("✓ Sequence opened in Sequencer")
    
    # Wait 2 seconds to allow UI to update
    import time
    time.sleep(2)
    
    # Refresh the current sequence to update UI
    unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
    
    # Set playback position to frame 0
    unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
    
    # Play the sequence
    unreal.LevelSequenceEditorBlueprintLibrary.play()
    log("✓ Sequence playing from frame 0")
    
    # ===== COMPLETE =====
    log("\n" + "=" * 60)
    log("✓ SCENE SETUP COMPLETE!")
    log("=" * 60)
    log(f"Sequence: {sequence_name}")
    log(f"Camera: {camera_name}")
    log(f"Mannequin: {mannequin_name}")
    log(f"Duration: {duration_seconds}s @ {fps}fps")
    log("=" * 60)
    log("\nCheck Sequencer to see your complete scene!")
    
except Exception as e:
    log("\n" + "=" * 60)
    log("✗ FATAL ERROR")
    log("=" * 60)
    log("Error type: " + type(e).__name__)
    log("Error message: " + str(e))
    
    import traceback
    log("\nFull traceback:")
    for line in traceback.format_exc().split('\n'):
        if line:
            log("  " + line)
    log("=" * 60)

print("\nDone!")
