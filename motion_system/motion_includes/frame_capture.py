"""
Frame Capture Utility - Capture frames from sequences for visual verification
"""
import unreal
from logger import log
import os


def capture_frame(sequence, frame_number, output_path, width=1920, height=1080):
    """
    Capture a single frame from a sequence at specified frame number.
    
    Args:
        sequence: LevelSequence object
        frame_number: Frame number to capture
        output_path: Full path for output image (e.g., "C:/path/frame_0000.png")
        width: Image width in pixels
        height: Image height in pixels
    
    Returns:
        output_path if successful, None otherwise
    """
    try:
        # Open sequence in editor
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
        
        # Set to specific frame
        unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(frame_number)
        
        # Ensure viewport is locked to camera cuts
        unreal.LevelSequenceEditorBlueprintLibrary.set_lock_camera_cut_to_viewport(True)
        
        # Force refresh
        unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
        
        # Small delay to ensure render
        import time
        time.sleep(0.5)
        
        # Capture screenshot
        unreal.AutomationLibrary.take_high_res_screenshot(width, height, output_path)
        
        log(f"  ✓ Captured frame {frame_number} -> {output_path}")
        return output_path
        
    except Exception as e:
        log(f"  ✗ Failed to capture frame {frame_number}: {e}")
        import traceback
        log(traceback.format_exc())
        return None


def capture_verification_frames(sequence, frames, output_dir, movie_name):
    """
    Capture multiple frames for verification.
    
    Args:
        sequence: LevelSequence object
        frames: List of frame numbers to capture
        output_dir: Base output directory (e.g., "dist/frames")
        movie_name: Name of movie (used for subdirectory)
    
    Returns:
        List of captured image paths
    """
    if not frames:
        return []
    
    # Create output directory
    movie_dir = os.path.join(output_dir, movie_name)
    os.makedirs(movie_dir, exist_ok=True)
    
    log(f"\n{'='*60}")
    log(f"CAPTURING VERIFICATION FRAMES")
    log(f"{'='*60}")
    log(f"Output directory: {movie_dir}")
    log(f"Frames to capture: {frames}")
    
    captured_paths = []
    for frame in frames:
        output_path = os.path.join(movie_dir, f"frame_{frame:04d}.png")
        result = capture_frame(sequence, frame, output_path)
        if result:
            captured_paths.append(result)
    
    log(f"\n✓ Captured {len(captured_paths)}/{len(frames)} frames")
    return captured_paths
