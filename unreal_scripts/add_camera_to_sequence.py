"""
Add Cinematic Camera to Walking Sequence
Run this inside Unreal Engine using Tools > Execute Python Script

Adds a smooth tracking camera with orbital movement, depth of field,
and professional framing to make the sequence YouTube-ready.
"""

import unreal
from datetime import datetime
import os
import math

# Setup logging with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = rf"C:\U\CinematicPipeline_Scripts\logs\add_camera_{timestamp}.log"
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

def add_camera_to_sequence():
    """Add a cinematic tracking camera to the existing sequence"""
    
    log_message("=" * 80)
    log_message("Adding Cinematic Camera to Sequence")
    log_message("=" * 80)
    
    # Load the existing sequence
    sequence_path = '/Game/Sequences/CharacterWalkSequence.CharacterWalkSequence'
    log_message(f"Loading sequence: {sequence_path}")
    
    sequence = unreal.load_object(None, sequence_path)
    if not sequence:
        log_message("Failed to load sequence! Make sure it exists.", "ERROR")
        return
    
    log_message(f"✓ Sequence loaded: {sequence.get_name()}")
    
    # Get sequence parameters
    start_frame = 0
    end_frame = 240
    fps = 24
    
    log_message(f"Sequence parameters: {start_frame}-{end_frame} frames @ {fps}fps")
    
    # Spawn a Cine Camera Actor in the level
    log_message("Spawning Cine Camera Actor in level...")
    camera_location = unreal.Vector(-200, -500, 300)  # Behind and above the starting point
    camera_rotation = unreal.Rotator(0, 0, 0)
    
    camera_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CineCameraActor,
        camera_location,
        camera_rotation
    )
    
    if not camera_actor:
        log_message("Failed to spawn camera actor", "ERROR")
        return
    
    log_message(f"✓ Camera spawned: {camera_actor.get_name()}")
    log_message(f"  - Initial position: {camera_location}")
    
    # Configure camera settings for cinematic look
    log_message("Configuring camera settings...")
    camera_component = camera_actor.get_cine_camera_component()
    
    # Set filmback for cinematic aspect ratio
    camera_component.filmback.sensor_width = 36.0
    camera_component.filmback.sensor_height = 24.0
    log_message("  - Filmback: 36x24mm (35mm Full Frame)")
    
    # Set focal length for nice framing (50mm is "normal" lens)
    camera_component.current_focal_length = 50.0
    log_message("  - Focal length: 50mm")
    
    # Enable and configure depth of field
    camera_component.focus_settings.focus_method = unreal.CameraFocusMethod.MANUAL
    camera_component.current_aperture = 2.8  # Wide aperture for shallow DOF
    camera_component.focus_settings.manual_focus_distance = 400.0  # Focus on character
    log_message("  - Depth of Field: f/2.8, focus distance 400cm")
    
    log_message("✓ Camera configured")
    
    # Add camera to sequence as a possessable
    log_message("Adding camera to sequence...")
    camera_binding = sequence.add_possessable(camera_actor)
    log_message(f"✓ Camera binding created: {camera_binding.get_display_name()}")
    
    # Add Camera Cut track to use this camera
    log_message("Creating Camera Cut track...")
    camera_cut_track = sequence.add_track(unreal.MovieSceneCameraCutTrack)
    log_message("✓ Camera Cut track added to sequence")
    
    camera_cut_section = camera_cut_track.add_section()
    log_message("✓ Camera Cut section created")
    
    camera_cut_section.set_range(start_frame, end_frame)
    log_message(f"✓ Camera Cut range set: {start_frame}-{end_frame}")
    
    # Set the camera cut to use our camera
    try:
        camera_binding_id = unreal.MovieSceneObjectBindingID()
        camera_binding_id.set_guid(camera_binding.get_id())
        camera_cut_section.set_camera_binding_id(camera_binding_id)
        log_message("✓ Camera binding ID set - this camera is now the active view")
    except Exception as e:
        log_message(f"Error setting camera binding: {e}", "ERROR")
        log_message("Trying alternative method...", "WARNING")
        # Alternative: just set the camera directly if available
        if hasattr(camera_cut_section, 'set_camera_actor'):
            camera_cut_section.set_camera_actor(camera_actor)
            log_message("✓ Camera set using direct method")
    
    # Add Transform track for camera movement
    log_message("Creating camera movement animation...")
    transform_track = camera_binding.add_track(unreal.MovieScene3DTransformTrack)
    transform_section = transform_track.add_section()
    transform_section.set_range(start_frame, end_frame)
    
    # Get transform channels
    channels = transform_section.get_all_channels()
    location_channels = channels[0:3]  # X, Y, Z
    rotation_channels = channels[3:6]  # Roll, Pitch, Yaw
    
    log_message("Creating smooth tracking camera path with orbital movement...")
    
    # Define camera path - follows character with slight orbital arc
    # Character path: (0,0) -> (300,0) -> (300,300) -> (0,300) -> (0,0)
    camera_keyframes = [
        # Time, X, Y, Z, Pitch, Yaw
        (0.0, -200, -300, 250, -15, 30),      # Start: Behind-left, looking down at character
        (2.5, 100, -300, 280, -18, 45),       # Follow right, slight orbit
        (5.0, 400, 100, 300, -20, 135),       # Continue orbit, higher
        (7.5, 200, 500, 280, -18, 225),       # Keep orbiting
        (10.0, -200, 400, 250, -15, 315)      # Complete orbit, back to similar angle
    ]
    
    log_message(f"Adding {len(camera_keyframes)} camera keyframes...")
    
    for i, (time_sec, x, y, z, pitch, yaw) in enumerate(camera_keyframes, 1):
        frame_number = int(time_sec * fps)
        
        # Set location keyframes
        location_channels[0].add_key(unreal.FrameNumber(frame_number), x)
        location_channels[1].add_key(unreal.FrameNumber(frame_number), y)
        location_channels[2].add_key(unreal.FrameNumber(frame_number), z)
        
        # Set rotation keyframes (pitch and yaw)
        rotation_channels[1].add_key(unreal.FrameNumber(frame_number), pitch)  # Pitch
        rotation_channels[2].add_key(unreal.FrameNumber(frame_number), yaw)     # Yaw
        
        log_message(f"  Keyframe {i}/{len(camera_keyframes)}: Frame {frame_number} - pos({x}, {y}, {z}) rot(P:{pitch}° Y:{yaw}°)")
    
    log_message("✓ Camera animation complete - smooth orbital tracking shot")
    
    # Save the sequence
    log_message("Saving sequence with camera...")
    save_result = unreal.EditorAssetLibrary.save_asset(sequence.get_path_name())
    if save_result:
        log_message("✓ Sequence saved successfully")
    else:
        log_message("Failed to save sequence", "WARNING")
    
    log_message("=" * 80)
    log_message("✓✓✓ CINEMATIC CAMERA ADDED SUCCESSFULLY! ✓✓✓")
    log_message("=" * 80)
    log_message("Camera features:")
    log_message("  • Smooth orbital tracking movement around character")
    log_message("  • Cinematic depth of field (f/2.8 aperture)")
    log_message("  • Professional 50mm focal length")
    log_message("  • Dynamic camera angles throughout sequence")
    log_message("")
    log_message("Play the sequence to see the cinematic camera in action!")
    log_message(f"Log file: {LOG_FILE}")
    log_message("=" * 80)
    
    # Open the sequence in Sequencer
    log_message("Opening sequence in Sequencer...")
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
    log_message("✓ Sequencer opened - hit Play to preview!")

# Run it
log_message("\n" + "=" * 80)
log_message("CAMERA SETUP SCRIPT STARTED")
log_message("=" * 80)
add_camera_to_sequence()
log_message("=" * 80)
log_message("CAMERA SETUP SCRIPT COMPLETED")
log_message("=" * 80 + "\n")
