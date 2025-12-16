"""
Create Complete Cinematic Sequence
Run this inside Unreal Engine using Tools > Execute Python Script

This script does EVERYTHING in one go:
- Deletes old sequence and camera
- Creates new sequence with character walking animation
- Adds cinematic camera with orbital tracking movement
- Configures depth of field and professional camera settings
- Ready to play and render!
"""

import unreal
from datetime import datetime
import os
import math

# Setup logging with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = rf"C:\U\CinematicPipeline_Scripts\logs\cinematic_{timestamp}.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_message(message, level="INFO"):
    """Log to both Unreal and a file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    formatted_msg = f"[{timestamp}] [{level}] {message}"
    
    # Log to Unreal
    if level == "ERROR":
        unreal.log_error(message)
    elif level == "WARNING":
        unreal.log_warning(message)
    else:
        unreal.log(message)
    
    # Log to file
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(formatted_msg + '\n')
    except Exception as e:
        unreal.log_error(f"Failed to write to log file: {e}")

def create_complete_cinematic():
    """Create complete cinematic sequence with character and camera"""
    
    log_message("=" * 80)
    log_message("CREATING COMPLETE CINEMATIC SEQUENCE")
    log_message("=" * 80)
    
    # ========================================================================
    # STEP 1: Clean up old assets
    # ========================================================================
    log_message("\n[STEP 1/5] Cleaning up old assets...")
    
    sequence_path = '/Game/Sequences/CharacterWalkSequence'
    sequence_full_path = sequence_path + '.CharacterWalkSequence'
    
    # Delete old sequence if it exists
    if unreal.EditorAssetLibrary.does_asset_exist(sequence_full_path):
        log_message("Found old sequence, deleting...")
        unreal.EditorAssetLibrary.delete_asset(sequence_full_path)
        log_message("✓ Old sequence deleted")
    
    # Delete any old camera actors in the level
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    for actor in all_actors:
        if isinstance(actor, unreal.CineCameraActor):
            unreal.EditorLevelLibrary.destroy_actor(actor)
            log_message(f"✓ Deleted old camera: {actor.get_name()}")
    
    log_message("✓ Cleanup complete")
    
    # ========================================================================
    # STEP 2: Find character in level
    # ========================================================================
    log_message("\n[STEP 2/5] Finding character in level...")
    
    character_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    log_message(f"Searching for character at: {character_path}")
    
    character = unreal.load_object(None, character_path)
    
    if not character:
        log_message("Character not found at default path, searching all level actors...", "WARNING")
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        log_message(f"Found {len(actors)} total actors in level")
        
        for a in actors:
            if 'ThirdPersonCharacter' in a.get_name():
                character = a
                log_message(f"✓ Found character by name search: {a.get_name()}")
                break
    
    if not character:
        log_message("ERROR: Character not found in level!", "ERROR")
        return
    
    log_message(f"✓ Character found: {character.get_name()}")
    log_message(f"  - Class: {character.get_class().get_name()}")
    
    # ========================================================================
    # STEP 3: Create Level Sequence with character animation
    # ========================================================================
    log_message("\n[STEP 3/5] Creating Level Sequence with animation...")
    
    # Create the sequence
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    sequence = asset_tools.create_asset(
        'CharacterWalkSequence',
        '/Game/Sequences',
        unreal.LevelSequence,
        unreal.LevelSequenceFactoryNew()
    )
    
    log_message(f"✓ Sequence created: {sequence.get_name()}")
    
    # Configure sequence parameters
    start_frame = 0
    end_frame = 240
    fps = 24
    
    sequence.set_display_rate(unreal.FrameRate(fps, 1))
    sequence.set_tick_resolution_directly(unreal.FrameRate(24000, 1))
    sequence.set_playback_start(start_frame)
    sequence.set_playback_end(end_frame)
    
    log_message(f"✓ Sequence parameters: {start_frame}-{end_frame} frames @ {fps}fps (10 seconds)")
    
    # Add character to sequence
    character_binding = sequence.add_possessable(character)
    log_message(f"✓ Character added: {character_binding.get_display_name()}")
    
    # Add skeletal animation track
    anim_track = character_binding.add_track(unreal.MovieSceneSkeletalAnimationTrack)
    anim_section = anim_track.add_section()
    anim_section.set_range(start_frame, end_frame)
    
    # Load and set walking animation
    anim_path = '/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd.MF_Unarmed_Walk_Fwd'
    walk_anim = unreal.load_object(None, anim_path)
    if walk_anim:
        anim_section_params = anim_section.params
        anim_section_params.set_editor_property('Animation', walk_anim)
        log_message(f"✓ Walking animation assigned: {walk_anim.get_name()}")
    else:
        log_message(f"WARNING: Could not load animation at {anim_path}", "WARNING")
    
    # Add transform track for character movement
    transform_track = character_binding.add_track(unreal.MovieScene3DTransformTrack)
    transform_section = transform_track.add_section()
    transform_section.set_range(start_frame, end_frame)
    
    # Get channels
    channels = transform_section.get_all_channels()
    location_channels = channels[0:3]  # X, Y, Z
    rotation_channels = channels[3:6]  # Roll, Pitch, Yaw
    
    # Define character waypoints (square path)
    waypoints = [
        (0.0, 0, 0, 100, 0),       # Start
        (2.5, 300, 0, 100, 90),    # Right
        (5.0, 300, 300, 100, 180), # Up
        (7.5, 0, 300, 100, 270),   # Left
        (10.0, 0, 0, 100, 0)       # Back to start
    ]
    
    log_message(f"Adding {len(waypoints)} character waypoints...")
    for i, (time_sec, x, y, z, yaw) in enumerate(waypoints, 1):
        frame = int(time_sec * fps)
        location_channels[0].add_key(unreal.FrameNumber(frame), x)
        location_channels[1].add_key(unreal.FrameNumber(frame), y)
        location_channels[2].add_key(unreal.FrameNumber(frame), z)
        rotation_channels[2].add_key(unreal.FrameNumber(frame), yaw)
        log_message(f"  Keyframe {i}: Frame {frame} - pos({x}, {y}, {z}) yaw={yaw}°")
    
    log_message("✓ Character animation complete")
    
    # ========================================================================
    # STEP 4: Create and configure camera
    # ========================================================================
    log_message("\n[STEP 4/5] Creating cinematic camera...")
    
    # Spawn camera actor
    camera_location = unreal.Vector(-200, -300, 250)
    camera_rotation = unreal.Rotator(-15, 30, 0)
    
    camera_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CineCameraActor,
        camera_location,
        camera_rotation
    )
    
    log_message(f"✓ Camera spawned: {camera_actor.get_name()}")
    
    # Configure camera settings
    camera_component = camera_actor.get_cine_camera_component()
    camera_component.filmback.sensor_width = 36.0
    camera_component.filmback.sensor_height = 24.0
    camera_component.current_focal_length = 50.0
    camera_component.focus_settings.focus_method = unreal.CameraFocusMethod.MANUAL
    camera_component.current_aperture = 2.8
    camera_component.focus_settings.manual_focus_distance = 400.0
    
    log_message("✓ Camera configured: 50mm lens, f/2.8, cinematic DOF")
    
    # Add camera to sequence
    camera_binding = sequence.add_possessable(camera_actor)
    log_message(f"✓ Camera added to sequence: {camera_binding.get_display_name()}")
    
    # ========================================================================
    # STEP 5: Add camera cut and animation
    # ========================================================================
    log_message("\n[STEP 5/5] Setting up camera animation...")
    
    # Add Camera Cut track
    camera_cut_track = sequence.add_track(unreal.MovieSceneCameraCutTrack)
    camera_cut_section = camera_cut_track.add_section()
    camera_cut_section.set_range(start_frame, end_frame)
    
    # Set camera binding - use the correct method for UE 5.7
    try:
        # Create binding ID with the camera's GUID
        binding_id = unreal.MovieSceneObjectBindingID()
        binding_id.guid = camera_binding.get_id()
        camera_cut_section.set_camera_binding_id(binding_id)
        log_message("✓ Camera Cut track created - camera is active view")
    except Exception as e:
        log_message(f"Camera binding failed: {e}", "ERROR")
        log_message("You'll need to manually set the camera in the Camera Cuts track", "WARNING")
    
    # Add camera transform track
    cam_transform_track = camera_binding.add_track(unreal.MovieScene3DTransformTrack)
    cam_transform_section = cam_transform_track.add_section()
    cam_transform_section.set_range(start_frame, end_frame)
    
    # Get camera channels
    cam_channels = cam_transform_section.get_all_channels()
    cam_location_channels = cam_channels[0:3]
    cam_rotation_channels = cam_channels[3:6]
    
    # Define camera path (smooth orbital tracking)
    camera_keyframes = [
        (0.0, -200, -300, 250, -15, 30),
        (2.5, 100, -300, 280, -18, 45),
        (5.0, 400, 100, 300, -20, 135),
        (7.5, 200, 500, 280, -18, 225),
        (10.0, -200, 400, 250, -15, 315)
    ]
    
    log_message(f"Adding {len(camera_keyframes)} camera keyframes (orbital tracking)...")
    for i, (time_sec, x, y, z, pitch, yaw) in enumerate(camera_keyframes, 1):
        frame = int(time_sec * fps)
        cam_location_channels[0].add_key(unreal.FrameNumber(frame), x)
        cam_location_channels[1].add_key(unreal.FrameNumber(frame), y)
        cam_location_channels[2].add_key(unreal.FrameNumber(frame), z)
        cam_rotation_channels[1].add_key(unreal.FrameNumber(frame), pitch)
        cam_rotation_channels[2].add_key(unreal.FrameNumber(frame), yaw)
        log_message(f"  Camera keyframe {i}: Frame {frame}")
    
    log_message("✓ Camera animation complete - smooth orbital movement")
    
    # ========================================================================
    # FINAL: Save and open
    # ========================================================================
    log_message("\n[FINAL] Saving sequence...")
    
    save_result = unreal.EditorAssetLibrary.save_asset(sequence.get_path_name())
    if save_result:
        log_message("✓ Sequence saved successfully")
    else:
        log_message("Failed to save sequence", "WARNING")
    
    log_message("\n" + "=" * 80)
    log_message("✓✓✓ COMPLETE CINEMATIC SEQUENCE CREATED! ✓✓✓")
    log_message("=" * 80)
    log_message("What was created:")
    log_message("  • Character walking animation (10 seconds, square path)")
    log_message("  • Smooth orbital camera tracking")
    log_message("  • Cinematic depth of field (f/2.8)")
    log_message("  • Professional 50mm focal length")
    log_message("  • Ready to play and render!")
    log_message("")
    log_message(f"Sequence: {sequence.get_path_name()}")
    log_message(f"Log file: {LOG_FILE}")
    log_message("=" * 80)
    
    # Open in Sequencer
    log_message("\nOpening sequence in Sequencer...")
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
    log_message("✓ Sequencer opened - hit Play to see your cinematic!")

# Run it
log_message("\n" + "=" * 80)
log_message("COMPLETE CINEMATIC SCRIPT STARTED")
log_message("=" * 80)
create_complete_cinematic()
log_message("\n" + "=" * 80)
log_message("COMPLETE CINEMATIC SCRIPT FINISHED")
log_message("=" * 80 + "\n")
